from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.sql import operators
from app.database import get_db
from app.models import Game, User
from app.schemas import UserCreate, UserLogin
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