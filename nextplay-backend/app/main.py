from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.sql import operators
from app.database import get_db
from app.models import Game

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