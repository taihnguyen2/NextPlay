from pydantic import BaseModel

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