from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ARRAY, ForeignKey, CheckConstraint, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class GameStatus(str, enum.Enum):
    played = "played"
    backlog = "backlog"
    not_interested = "not_interested"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    genres = Column(ARRAY(String))
    platforms = Column(ARRAY(String))
    rating = Column(Numeric(3, 1))
    metacritic = Column(Integer)
    playtime_hours = Column(Integer)
    tags = Column(ARRAY(String))
    released_date = Column(Date)
    background_image = Column(String)
    last_synced_at = Column(DateTime, server_default=func.now())

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    preferred_genres = Column(ARRAY(String))
    preferred_platforms = Column(ARRAY(String))
    mood_tags = Column(ARRAY(String))
    updated_at = Column(DateTime, server_default=func.now())

class UserGameStatus(Base):
    __tablename__ = "user_game_status"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    status = Column(Enum(GameStatus), nullable=False)
    user_rating = Column(Integer, CheckConstraint("user_rating BETWEEN 1 AND 10"))
    updated_at = Column(DateTime, server_default=func.now())