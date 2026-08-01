import httpx
from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Game
from app.config import settings

TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/token"
IGDB_GAMES_URL = "https://api.igdb.com/v4/games"


def get_access_token() -> str:
    response = httpx.post(TWITCH_AUTH_URL, params={
        "client_id": settings.igdb_client_id,
        "client_secret": settings.igdb_client_secret,
        "grant_type": "client_credentials"
    })
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_games(token: str, offset: int = 0, limit: int = 500) -> list[dict]:
    headers = {
        "Client-ID": settings.igdb_client_id,
        "Authorization": f"Bearer {token}"
    }
    # IGDB uses its own query language (IGDB Query Language / IGDB-QL)
    body = f"""
        fields name, genres.name, platforms.name, rating, aggregated_rating,
               summary, first_release_date, cover.url, tags;
        where rating != null;
        limit {limit};
        offset {offset};
    """
    response = httpx.post(IGDB_GAMES_URL, headers=headers, content=body)
    response.raise_for_status()
    return response.json()


def upsert_game(db: Session, game_data: dict):
    existing = db.query(Game).filter(Game.external_id == game_data["id"]).first()

    genres = [g["name"] for g in game_data.get("genres", [])]
    platforms = [p["name"] for p in game_data.get("platforms", [])]
    released = None
    if game_data.get("first_release_date"):
        released = date.fromtimestamp(game_data["first_release_date"])
    cover_url = None
    if game_data.get("cover", {}).get("url"):
        cover_url = "https:" + game_data["cover"]["url"].replace("t_thumb", "t_cover_big")

    if existing:
        existing.title = game_data["name"]
        existing.genres = genres
        existing.platforms = platforms
        existing.rating = game_data.get("rating", 0) / 10 if game_data.get("rating") else None
        existing.released_date = released
        existing.background_image = cover_url
    else:
        new_game = Game(
            external_id=game_data["id"],  # reusing this column name for the external ID
            title=game_data["name"],
            genres=genres,
            platforms=platforms,
            rating=game_data.get("rating", 0) / 10 if game_data.get("rating") else None,
            released_date=released,
            background_image=cover_url
        )
        db.add(new_game)


def run_sync(total_games: int = 2000):
    token = get_access_token()
    db = SessionLocal()
    try:
        for offset in range(0, total_games, 500):
            games = fetch_games(token, offset=offset, limit=500)
            print(f"Fetched {len(games)} games at offset {offset}")
            for game in games:
                upsert_game(db, game)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_sync()