from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Movie, Book, Character
from typing import List, Dict
import pandas as pd
from datetime import datetime

def save_movies_bulk(db: Session, movies_df: pd.DataFrame) -> int:
    print(f"[*] Bulk saving {len(movies_df)} movies...")
    count = 0
    for _, row in movies_df.iterrows():
        existing = db.query(Movie).filter(Movie.tmdb_id == int(row['tmdb_id'])).first()
        data = {
            'title': row['title'],
            'overview': row.get('overview'),
            'genres': row.get('genre_names', []),
            'release_year': int(row['release_year']) if pd.notna(row['release_year']) else None,
            'decade': int(row['decade']) if pd.notna(row['decade']) else None,
            'vote_average': float(row['vote_average']) if pd.notna(row['vote_average']) else None,
            'vote_count': int(row['vote_count']) if pd.notna(row['vote_count']) else None,
            'popularity': float(row['popularity']) if pd.notna(row['popularity']) else None,
            'poster_path': row.get('poster_path'),
            'original_language': row.get('original_language'),
            'updated_at': datetime.utcnow()
        }
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            new_movie = Movie(tmdb_id=int(row['tmdb_id']), **data)
            db.add(new_movie)

        count += 1
        if count % 100 == 0:
            db.commit()
            print(f"  Processed {count}/{len(movies_df)}")
    db.commit()
    return count

def save_books_bulk(db: Session, books_df: pd.DataFrame) -> int:
    print(f"[*] Bulk saving {len(books_df)} books...")
    count = 0
    for _, row in books_df.iterrows():
        existing = db.query(Book).filter(Book.google_books_id == row['google_books_id']).first()
        data = {
            'title': row['title'],
            'authors': row.get('authors', []),
            'description': row.get('description'),
            'categories': row.get('categories', []),
            'published_date': row.get('published_date'),
            'decade': int(row['decade']) if pd.notna(row['decade']) else None,
            'page_count': int(row['page_count']) if pd.notna(row['page_count']) else None,
            'average_rating': float(row['average_rating']) if pd.notna(row['average_rating']) else None,
            'ratings_count': int(row['ratings_count']) if pd.notna(row['ratings_count']) else None,
            'thumbnail': row.get('thumbnail'),
            'publisher': row.get('publisher'),
            'updated_at': datetime.utcnow()
        }
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            new_book = Book(google_books_id=row['google_books_id'], **data)
            db.add(new_book)

        count += 1
        if count % 100 == 0:
            db.commit()
            print(f"  Processed {count}/{len(books_df)}")
    db.commit()
    return count

def get_movie_stats(db: Session) -> Dict:
    return {'total_movies': db.query(func.count(Movie.id)).scalar()}

def get_book_stats(db: Session) -> Dict:
    return {'total_books': db.query(func.count(Book.id)).scalar()}

def get_all_movies(db: Session, limit: int = 100) -> List[Movie]:
    return db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()

def get_all_books(db: Session, limit: int = 100) -> List[Book]:
    return db.query(Book).order_by(
        Book.average_rating.desc(),
        Book.ratings_count.desc()
    ).limit(limit).all()
