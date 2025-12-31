"""
CRUD operations - Create, Read, Update, Delete for database
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database.models import Movie, Book, Character, GameSession
from typing import List, Dict
import pandas as pd
from datetime import datetime


def save_movies_bulk(db: Session, movies_df: pd.DataFrame) -> int:
    """
    Save multiple movies to database efficiently

    Args:
        db: Database session
        movies_df: DataFrame with movie data

    Returns:
        Number of movies saved
    """
    print(f"[*] Saving {len(movies_df)} movies to database...")

    movies_added = 0
    movies_updated = 0

    for idx, row in movies_df.iterrows():
        # Check if movie already exists
        existing_movie = db.query(Movie).filter(
            Movie.tmdb_id == int(row['tmdb_id'])
        ).first()

        if existing_movie:
            # Update existing movie
            existing_movie.title = row['title']
            existing_movie.overview = row.get('overview')
            existing_movie.genres = row.get('genre_names', [])
            existing_movie.release_year = int(row['release_year']) if pd.notna(row['release_year']) else None
            existing_movie.decade = int(row['decade']) if pd.notna(row['decade']) else None
            existing_movie.vote_average = float(row['vote_average']) if pd.notna(row['vote_average']) else None
            existing_movie.vote_count = int(row['vote_count']) if pd.notna(row['vote_count']) else None
            existing_movie.popularity = float(row['popularity']) if pd.notna(row['popularity']) else None
            existing_movie.poster_path = row.get('poster_path')
            existing_movie.backdrop_path = row.get('backdrop_path')
            existing_movie.original_language = row.get('original_language')
            existing_movie.updated_at = datetime.utcnow()

            movies_updated += 1
        else:
            # Create new movie
            movie = Movie(
                tmdb_id=int(row['tmdb_id']),
                title=row['title'],
                overview=row.get('overview'),
                genres=row.get('genre_names', []),
                release_date=row['release_date'].strftime('%Y-%m-%d') if pd.notna(row['release_date']) else None,
                release_year=int(row['release_year']) if pd.notna(row['release_year']) else None,
                decade=int(row['decade']) if pd.notna(row['decade']) else None,
                vote_average=float(row['vote_average']) if pd.notna(row['vote_average']) else None,
                vote_count=int(row['vote_count']) if pd.notna(row['vote_count']) else None,
                popularity=float(row['popularity']) if pd.notna(row['popularity']) else None,
                poster_path=row.get('poster_path'),
                backdrop_path=row.get('backdrop_path'),
                original_language=row.get('original_language')
            )

            db.add(movie)
            movies_added += 1

        # Commit every 50 movies to avoid memory issues
        if (movies_added + movies_updated) % 50 == 0:
            db.commit()
            print(f"  Progress: {movies_added + movies_updated}/{len(movies_df)}")

    # Final commit
    db.commit()

    print(f"[SUCCESS] Added: {movies_added}, Updated: {movies_updated}")
    return movies_added + movies_updated


def get_all_movies(db: Session, limit: int = 100) -> List[Movie]:
    """
    Get all movies from database
    """
    return db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()


def get_movies_by_genre(db: Session, genre: str, limit: int = 20) -> List[Movie]:
    """
    Get movies by genre
    Example: get_movies_by_genre(db, 'Action')
    """
    from sqlalchemy import cast, String

    # Convert JSON array to string and search for genre
    movies = db.query(Movie).filter(
        cast(Movie.genres, String).contains(genre)
    ).order_by(Movie.popularity.desc()).limit(limit).all()

    return movies


def get_movies_by_decade(db: Session, decade: int, limit: int = 20) -> List[Movie]:
    """
    Get movies from a specific decade
    Example: get_movies_by_decade(db, 2010)
    """
    return db.query(Movie).filter(
        Movie.decade == decade
    ).order_by(Movie.popularity.desc()).limit(limit).all()


def get_movie_stats(db: Session) -> Dict:
    """
    Get statistics about movies in database
    """
    total_movies = db.query(func.count(Movie.id)).scalar()

    # Count by decade
    decades = db.query(
        Movie.decade,
        func.count(Movie.id)
    ).group_by(Movie.decade).order_by(Movie.decade.desc()).all()

    # Average rating
    avg_rating = db.query(func.avg(Movie.vote_average)).scalar()

    return {
        'total_movies': total_movies,
        'decades': {decade: count for decade, count in decades if decade},
        'average_rating': round(float(avg_rating), 2) if avg_rating else 0
    }


def search_movies(db: Session, query: str, limit: int = 10) -> List[Movie]:
    """
    Search movies by title
    """
    search_pattern = f"%{query}%"
    return db.query(Movie).filter(
        Movie.title.ilike(search_pattern)
    ).order_by(Movie.popularity.desc()).limit(limit).all()

def save_books_bulk(db: Session, books_df: pd.DataFrame) -> int:
    """
    Save multiple books to database
    """
    print(f"[*] Saving {len(books_df)} books to database...")

    books_added = 0
    books_updated = 0

    for idx, row in books_df.iterrows():
        # Check if book exists
        existing = db.query(Book).filter(
            Book.google_books_id == row['google_books_id']
        ).first()

        if existing:
            # Update existing
            existing.title = row['title']
            existing.authors = row.get('authors', [])
            existing.description = row.get('description')
            existing.categories = row.get('categories', [])
            existing.published_date = row.get('published_date')
            existing.decade = int(row['decade']) if pd.notna(row['decade']) else None
            existing.page_count = int(row['page_count']) if pd.notna(row['page_count']) else None
            existing.average_rating = float(row['average_rating']) if pd.notna(row['average_rating']) else None
            existing.ratings_count = int(row['ratings_count']) if pd.notna(row['ratings_count']) else None
            existing.thumbnail = row.get('thumbnail')
            existing.publisher = row.get('publisher')
            existing.updated_at = datetime.utcnow()

            books_updated += 1
        else:
            # Create new
            book = Book(
                google_books_id=row['google_books_id'],
                title=row['title'],
                authors=row.get('authors', []),
                description=row.get('description'),
                categories=row.get('categories', []),
                published_date=row.get('published_date'),
                decade=int(row['decade']) if pd.notna(row['decade']) else None,
                page_count=int(row['page_count']) if pd.notna(row['page_count']) else None,
                average_rating=float(row['average_rating']) if pd.notna(row['average_rating']) else None,
                ratings_count=int(row['ratings_count']) if pd.notna(row['ratings_count']) else None,
                thumbnail=row.get('thumbnail'),
                language=row.get('language'),
                publisher=row.get('publisher')
            )

            db.add(book)
            books_added += 1

        # Commit every 50
        if (books_added + books_updated) % 50 == 0:
            db.commit()
            print(f"  Progress: {books_added + books_updated}/{len(books_df)}")

    db.commit()

    print(f"[SUCCESS] Added: {books_added}, Updated: {books_updated}")
    return books_added + books_updated


def get_all_books(db: Session, limit: int = 100) -> List[Book]:
    """
    Get all books from database
    """
    return db.query(Book).order_by(
        Book.average_rating.desc(),
        Book.ratings_count.desc()
    ).limit(limit).all()


def get_books_by_category(db: Session, category: str, limit: int = 20) -> List[Book]:
    """
    Get books by category
    """
    from sqlalchemy import cast, String

    return db.query(Book).filter(
        cast(Book.categories, String).contains(category)
    ).order_by(Book.average_rating.desc()).limit(limit).all()


def get_book_stats(db: Session) -> Dict:
    """
    Get statistics about books in database
    """
    total_books = db.query(func.count(Book.id)).scalar()

    avg_rating = db.query(func.avg(Book.average_rating)).scalar()

    return {
        'total_books': total_books,
        'average_rating': round(float(avg_rating), 2) if avg_rating else 0
    }
