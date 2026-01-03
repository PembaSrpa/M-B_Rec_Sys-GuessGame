import os
import json
import pandas as pd
from dotenv import load_dotenv
from app.services.tmdb_service import TMDBService
from app.services.books_service import GoogleBooksService
from app.database.db import SessionLocal
from app.database.crud import save_movies_bulk, save_books_bulk
from app.database.models import Character

load_dotenv()

def expand_all_to_1k():
    db = SessionLocal()

    print("Expanding Movies...")
    tmdb = TMDBService(os.getenv("TMDB_API_KEY"))
    movies_df = tmdb.fetch_1k_movies()
    if not movies_df.empty:
        save_movies_bulk(db, movies_df)

    print("Expanding Books...")
    books_service = GoogleBooksService(os.getenv("GOOGLE_BOOKS_API_KEY"))
    books_df = books_service.fetch_1k_books()
    if not books_df.empty:
        save_books_bulk(db, books_df)

    print("Loading Characters...")
    with open('data/anime_characters_raw.json', 'r', encoding='utf-8') as f:
        chars = json.load(f)
    for c in chars:
        if not db.query(Character).filter(Character.name == c['name']).first():
            db.add(Character(
                name=c['name'],
                type="Anime",
                popularity_score=c.get('favorites', 0),
                image_url=c.get('image_url'),
                traits=["Anime"],
                source="Jikan API"
            ))
    db.commit()
    db.close()

if __name__ == "__main__":
    expand_all_to_1k()
