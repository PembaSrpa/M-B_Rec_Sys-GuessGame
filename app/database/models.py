from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base class for all models
Base = declarative_base()

class Movie(Base):
    """
    Table to store movie data from TMDB
    """
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)  # TMDB's ID
    title = Column(String(500), nullable=False)
    overview = Column(Text)  # Movie description
    genres = Column(JSON)  # ["action", "sci-fi", "thriller"]
    release_date = Column(String(50))
    release_year = Column(Integer, index=True)
    decade = Column(Integer, index=True)  # 1990, 2000, 2010, 2020
    vote_average = Column(Float)  # Rating 0-10
    vote_count = Column(Integer)  # Number of votes
    popularity = Column(Float)  # TMDB popularity score
    poster_path = Column(String(500))  # URL to poster image
    backdrop_path = Column(String(500))
    original_language = Column(String(10))
    runtime = Column(Integer)  # Minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Movie(title='{self.title}', year={self.release_year})>"


class Book(Base):
    """
    Table to store book data from Google Books API
    """
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    google_books_id = Column(String(100), unique=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(JSON)  # ["Author 1", "Author 2"]
    description = Column(Text)
    categories = Column(JSON)  # ["Fiction", "Fantasy"]
    published_date = Column(String(50))
    decade = Column(Integer, index=True)
    page_count = Column(Integer)
    average_rating = Column(Float)
    ratings_count = Column(Integer)
    thumbnail = Column(String(500))  # Cover image URL
    language = Column(String(10))
    publisher = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Book(title='{self.title}', authors={self.authors})>"


class Character(Base):
    """
    Table to store characters for the guessing game
    Manually seeded with tagged data
    """
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    type = Column(String(20), index=True)  # 'anime' or 'actor'
    alignment = Column(String(20))  # 'hero', 'villain', 'anti-hero'
    traits = Column(JSON)  # ["funny", "powerful", "intelligent"]
    genres = Column(JSON)  # ["action", "comedy"]
    appearance = Column(JSON)  # {"hair_color": "black", "features": [...]}
    popularity_score = Column(Float, index=True)  # 0-100
    source = Column(String(200))  # Anime name or actor's famous work
    image_url = Column(String(500))
    additional_info = Column(JSON)  # Extra metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Character(name='{self.name}', type='{self.type}')>"


class GameSession(Base):
    """
    Table to track guessing game sessions
    """
    __tablename__ = 'game_sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    answers = Column(JSON)  # Array of {"question_id": 1, "answer": "anime"}
    remaining_candidates = Column(JSON)  # List of character IDs still possible
    final_character_id = Column(Integer, nullable=True)  # User's actual character
    guessed_character_id = Column(Integer, nullable=True)  # Our guess
    was_correct = Column(Boolean, nullable=True)
    total_questions = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<GameSession(session_id='{self.session_id}')>"
