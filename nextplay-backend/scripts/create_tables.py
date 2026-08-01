from app.database import Base, engine
from app.models import User, Game, UserPreferences, UserGameStatus

Base.metadata.create_all(bind=engine)
print("Tables created successfully")