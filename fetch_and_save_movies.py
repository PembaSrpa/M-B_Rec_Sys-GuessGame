"""
Script to fetch movies from TMDB and save to database
"""
import os
from dotenv import load_dotenv
from app.services.tmdb_service import TMDBService
from app.database.db import SessionLocal
from app.database.crud import save_movies_bulk, get_movie_stats

# Load environment variables
load_dotenv()

def main():
    print("\n" + "="*60)
    print("FETCH AND SAVE MOVIES TO DATABASE")
    print("="*60 + "\n")

    # Get API key
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("[ERROR] TMDB_API_KEY not found in .env file!")
        return

    # Initialize TMDB service
    tmdb = TMDBService(api_key)

    # Fetch movies (5 pages = 100 movies)
    print("[STEP 1] Fetching movies from TMDB API...\n")
    movies_df = tmdb.fetch_popular_movies(pages=5)

    if movies_df.empty:
        print("[ERROR] No movies fetched!")
        return

    print(f"\n[INFO] Fetched {len(movies_df)} movies")
    print(f"[INFO] Year range: {movies_df['release_year'].min():.0f} - {movies_df['release_year'].max():.0f}")
    print(f"[INFO] Average rating: {movies_df['vote_average'].mean():.1f}/10")

    # Save to database
    print(f"\n[STEP 2] Saving to database...\n")
    db = SessionLocal()

    try:
        saved_count = save_movies_bulk(db, movies_df)
        print(f"\n[SUCCESS] Saved {saved_count} movies to database!")

        # Show stats
        print(f"\n[STEP 3] Database Statistics:\n")
        stats = get_movie_stats(db)
        print(f"  Total movies in DB: {stats['total_movies']}")
        print(f"  Average rating: {stats['average_rating']}/10")
        print(f"\n  Movies by decade:")
        for decade, count in stats['decades'].items():
            print(f"    {decade}s: {count} movies")

    except Exception as e:
        print(f"[ERROR] Failed to save movies: {e}")
        db.rollback()
    finally:
        db.close()

    print("\n" + "="*60)
    print("[DONE] Process completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
