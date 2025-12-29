"""
Quick script to view movies in database
"""
from app.database.db import SessionLocal
from app.database.crud import get_all_movies, get_movies_by_genre

db = SessionLocal()

print("\n" + "="*60)
print("TOP 10 MOVIES IN DATABASE")
print("="*60 + "\n")

movies = get_all_movies(db, limit=10)

for i, movie in enumerate(movies, 1):
    print(f"{i}. {movie.title} ({movie.release_year})")
    print(f"   Rating: {movie.vote_average}/10 | Popularity: {movie.popularity:.0f}")
    print(f"   Genres: {', '.join(movie.genres)}")
    print()

print("="*60)
print("ACTION MOVIES")
print("="*60 + "\n")

action_movies = get_movies_by_genre(db, 'Action', limit=5)

for i, movie in enumerate(action_movies, 1):
    print(f"{i}. {movie.title} ({movie.release_year}) - {movie.vote_average}/10")

db.close()
