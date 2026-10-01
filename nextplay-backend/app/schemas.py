from pydantic import BaseModel
from app.models import GameStatus

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Preferences(BaseModel):
    preferred_genres: list[str]
    preferred_platforms: list[str]
    mood_tags: list[str]

class Game_Status_Update(BaseModel):
    status: GameStatus
    user_rating: int | None = None