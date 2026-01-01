import os
from dotenv import load_dotenv
from app.services.tmdb_service import TMDBService
from app.services.books_service import GoogleBooksService
from app.database.db import SessionLocal, init_db
from app.database.crud import save_movies_bulk, save_books_bulk
import json
from app.database.models import Character

load_dotenv()


def seed_movies(pages=25):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("[ERROR] TMDB_API_KEY not found")
        return

    print("[*] Seeding movies...")
    tmdb = TMDBService(api_key)
    movies_df = tmdb.fetch_popular_movies(pages=pages)

    if not movies_df.empty:
        db = SessionLocal()
        try:
            save_movies_bulk(db, movies_df)
            print(f"[SUCCESS] Seeded {len(movies_df)} movies")
        finally:
            db.close()


def seed_books(books_per_genre=25):
    print("[*] Seeding books...")
    service = GoogleBooksService()
    books_df = service.fetch_diverse_collection(books_per_genre=books_per_genre)

    if not books_df.empty:
        db = SessionLocal()
        try:
            save_books_bulk(db, books_df)
            print(f"[SUCCESS] Seeded {len(books_df)} books")
        finally:
            db.close()


def seed_characters():
    print("[*] Seeding characters...")

    seed_file = 'data/characters_seed.json'
    tagged_file = 'data/characters_tagged.json'

    characters = []

    if os.path.exists(tagged_file):
        with open(tagged_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            characters = data['characters']
    elif os.path.exists(seed_file):
        with open(seed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            characters = data['characters']
    else:
        print("[ERROR] No character data found")
        return

    db = SessionLocal()
    try:
        for char_data in characters:
            existing = db.query(Character).filter(
                Character.name == char_data['name']
            ).first()

            if not existing:
                character = Character(
                    name=char_data['name'],
                    type=char_data['type'],
                    alignment=char_data.get('alignment'),
                    traits=char_data.get('traits', []),
                    genres=char_data.get('genres', []),
                    popularity_score=char_data.get('popularity_score'),
                    source=char_data.get('source'),
                    image_url=char_data.get('image_url'),
                    additional_info={
                        'gender': char_data.get('gender')
                    }
                )
                db.add(character)

        db.commit()
        count = db.query(Character).count()
        print(f"[SUCCESS] Seeded {count} characters")

    finally:
        db.close()


def main():
    print("\n" + "="*60)
    print("SEEDING PRODUCTION DATABASE")
    print("="*60 + "\n")

    print("[*] Creating tables...")
    init_db()

    seed_movies(pages=25)
    seed_books(books_per_genre=25)
    seed_characters()

    print("\n" + "="*60)
    print("SEEDING COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
