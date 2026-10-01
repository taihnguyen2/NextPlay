from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func, select
from sqlalchemy.sql import operators
from app.database import get_db
from app.models import Game, User, UserPreferences, UserGameStatus
from app.schemas import UserCreate, UserLogin, Preferences, Game_Status_Update
from app.auth import hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"status": "ok", "db_check": result}

@app.get("/games")
def filter_games(genre: str | None = None, platform: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Game)

    if platform:
        platform_string = func.array_to_string(Game.platforms, ",").ilike(f"%{platform}%")
        query = query.filter(platform_string)
    
    if genre:
        genre_string = func.array_to_string(Game.genres, ",").ilike(f"%{genre}%")
        query = query.filter(genre_string)

    result = query.all()
    return result

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    new_user = User(email = user.email, password_hash = hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

@app.post("/login")
def login(credentials: UserLogin, db : Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    verify = verify_password(credentials.password, user.password_hash)
    if not verify:
        raise HTTPException (
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password"
        )
    
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

@app.post("/preferences")
def set_preferences(prefs: Preferences, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserPreferences).filter(current_user.id == UserPreferences.user_id).first()
    if existing:
        existing.preferred_genres = prefs.preferred_genres
        existing.mood_tags = prefs.mood_tags
        existing.preferred_platforms = prefs.preferred_platforms
        db.commit()
        saved_prefs = existing
    else:
        new_prefs = UserPreferences(user_id = current_user.id, preferred_genres = prefs.preferred_genres, mood_tags = prefs.mood_tags, preferred_platforms = prefs.preferred_platforms)
        db.add(new_prefs)
        db.commit()
        db.refresh(new_prefs)
        saved_prefs = new_prefs
    return saved_prefs

@app.get("/recommendations")
def get_recommendations(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    preferences = db.query(UserPreferences).filter(current_user.id == UserPreferences.user_id).first()

    if preferences is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User preferences not set"
        )
    
    result = db.query(UserGameStatus.game_id).filter(UserGameStatus.user_id == current_user.id, UserGameStatus.status.in_(['not_interested', 'played'])).all()
    game_ids = [row.game_id for row in result]
    candidate_games = db.query(Game).filter(Game.id.notin_(game_ids)).all()
    scored_games = []
    for game in candidate_games:
        score = 0
        genre_set = set(game.genres)
        pref_genre_set = set(preferences.preferred_genres)
        overlap = genre_set & pref_genre_set
        if len(genre_set) > 0:
            genre_score = len(overlap)/len(genre_set)
        else:
            genre_score = 0
        score += genre_score * 40

        platform_set = set(game.platforms)
        pref_plat_set = set(preferences.preferred_platforms)
        if(platform_set & pref_plat_set):
            score += 20
        
        game_rating = float(game.rating) / 10
        score += game_rating * 25

        scored_games.append((score, game))
    scored_games.sort(key = lambda x: x[0], reverse = True)
    limit_games = scored_games[offset: offset + limit]
    return [game for score, game in limit_games]

@app.post("/games/{game_id}/status")
def set_game_status(
    game_id: int,
    status_data: Game_Status_Update,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(UserGameStatus).filter(current_user.id == UserGameStatus.user_id, game_id == UserGameStatus.game_id).first()
    
    if existing:
        existing.status = status_data.status
        existing.user_rating = status_data.user_rating
        db.commit()
        saved_status = existing
    else:
        new_status = UserGameStatus(
            user_id = current_user.id,
            game_id = game_id,
            status = status_data.status,
            user_rating = status_data.user_rating
        )
        db.add(new_status)
        db.commit()
        db.refresh(new_status)
        saved_status = new_status
    
    
    return saved_status