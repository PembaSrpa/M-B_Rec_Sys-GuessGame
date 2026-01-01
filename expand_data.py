import os
from dotenv import load_dotenv
from app.services.tmdb_service import TMDBService
from app.services.books_service import GoogleBooksService
from app.database.db import SessionLocal
from app.database.crud import save_movies_bulk, save_books_bulk, get_movie_stats, get_book_stats

load_dotenv()


def expand_movies(target_total=500):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("[ERROR] TMDB_API_KEY not found!")
        return

    print("\n" + "="*60)
    print("EXPANDING MOVIE DATABASE")
    print("="*60 + "\n")

    db = SessionLocal()
    current_stats = get_movie_stats(db)
    current_total = current_stats['total_movies']
    db.close()

    print(f"Current movies: {current_total}")
    print(f"Target: {target_total}")

    if current_total >= target_total:
        print(f"Already have {current_total} movies. Skipping.")
        return

    needed = target_total - current_total
    pages_needed = (needed // 20) + 1

    print(f"Need to fetch: {needed} movies ({pages_needed} pages)\n")

    tmdb = TMDBService(api_key)

    all_movies = []
    start_page = (current_total // 20) + 1

    for page in range(start_page, start_page + pages_needed):
        print(f"Fetching page {page}...")
        movies_df = tmdb.fetch_popular_movies(pages=1)

        if not movies_df.empty:
            all_movies.append(movies_df)

    if all_movies:
        import pandas as pd
        combined = pd.concat(all_movies, ignore_index=True)
        combined = combined.drop_duplicates(subset=['tmdb_id'])

        print(f"\nFetched {len(combined)} new unique movies")

        db = SessionLocal()
        try:
            save_movies_bulk(db, combined)
            new_stats = get_movie_stats(db)
            print(f"\nTotal movies now: {new_stats['total_movies']}")
        finally:
            db.close()


def expand_books(target_total=200):
    print("\n" + "="*60)
    print("EXPANDING BOOK DATABASE")
    print("="*60 + "\n")

    db = SessionLocal()
    current_stats = get_book_stats(db)
    current_total = current_stats['total_books']
    db.close()

    print(f"Current books: {current_total}")
    print(f"Target: {target_total}")

    if current_total >= target_total:
        print(f"Already have {current_total} books. Skipping.")
        return

    service = GoogleBooksService()

    books_per_genre = 25
    print(f"\nFetching {books_per_genre} books per genre...")

    books_df = service.fetch_diverse_collection(books_per_genre=books_per_genre)

    if not books_df.empty:
        print(f"\nFetched {len(books_df)} unique books")

        db = SessionLocal()
        try:
            save_books_bulk(db, books_df)
            new_stats = get_book_stats(db)
            print(f"\nTotal books now: {new_stats['total_books']}")
        finally:
            db.close()


def expand_characters_from_files():
    print("\n" + "="*60)
    print("LOADING TAGGED CHARACTERS")
    print("="*60 + "\n")

    import json
    from app.database.models import Character

    tagged_file = 'data/characters_tagged.json'

    if not os.path.exists(tagged_file):
        print(f"[SKIP] {tagged_file} not found")
        print("Run: python tag_characters.py first")
        return

    with open(tagged_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    characters = data['characters']
    print(f"Found {len(characters)} characters in file")

    db = SessionLocal()

    try:
        added = 0
        updated = 0

        for char_data in characters:
            existing = db.query(Character).filter(
                Character.name == char_data['name']
            ).first()

            if existing:
                existing.type = char_data['type']
                existing.alignment = char_data.get('alignment')
                existing.traits = char_data.get('traits', [])
                existing.genres = char_data.get('genres', [])
                existing.popularity_score = char_data.get('popularity_score')
                existing.source = char_data.get('source')
                existing.image_url = char_data.get('image_url')
                existing.additional_info = {
                    'gender': char_data.get('gender')
                }
                updated += 1
            else:
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
                added += 1

        db.commit()

        total = db.query(Character).count()
        print(f"\nAdded: {added}, Updated: {updated}")
        print(f"Total characters: {total}")

    finally:
        db.close()


def main():
    print("\n" + "="*60)
    print("DATA EXPANSION UTILITY")
    print("="*60)

    expand_movies(target_total=500)
    expand_books(target_total=200)
    expand_characters_from_files()

    print("\n" + "="*60)
    print("EXPANSION COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
