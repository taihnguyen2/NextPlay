from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    igdb_client_id: str
    igdb_client_secret: str
    jwt_secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()