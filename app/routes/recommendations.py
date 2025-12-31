"""
API routes for movie/book recommendations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    SimilarRequest
)
from app.models.recommendations import RecommendationEngine

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized movie or book recommendations

    - **content_type**: 'movie' or 'book'
    - **genres**: List of preferred genres
    - **decade**: Preferred time period
    - **mood**: User's current mood
    - **setting**: Preferred setting type
    - **min_rating**: Minimum quality threshold
    """
    try:
        engine = RecommendationEngine(db)

        if request.content_type == 'movie':
            result = engine.recommend_movies(
                genres=request.genres,
                decade=request.decade,
                mood=request.mood,
                setting=request.setting,
                min_rating=request.min_rating,
                top_n=request.top_n
            )
        elif request.content_type == 'book':
            # Books use same logic, just different table
            result = engine.recommend_movies(  # Will create recommend_books() method
                genres=request.genres,
                decade=request.decade,
                mood=request.mood,
                setting=request.setting,
                min_rating=request.min_rating,
                top_n=request.top_n
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="content_type must be 'movie' or 'book'"
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/{movie_id}/similar")
async def get_similar_movies(
    movie_id: int,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get movies similar to a specific movie
    """
    try:
        engine = RecommendationEngine(db)
        similar = engine.get_similar_movies(movie_id, top_n=top_n)

        return {
            "reference_movie_id": movie_id,
            "similar_movies": similar
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/movies")
async def get_trending_movies(
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get currently trending movies
    """
    try:
        engine = RecommendationEngine(db)
        trending = engine.get_trending_recommendations(top_n=top_n)

        return {
            "trending": trending
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies")
async def list_movies(
    limit: int = 20,
    genre: str = None,
    db: Session = Depends(get_db)
):
    """
    List all movies (optionally filtered by genre)
    """
    from app.database.crud import get_all_movies, get_movies_by_genre

    try:
        if genre:
            movies = get_movies_by_genre(db, genre, limit=limit)
        else:
            movies = get_all_movies(db, limit=limit)

        result = []
        for movie in movies:
            result.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'genres': movie.genres,
                'release_year': movie.release_year,
                'vote_average': movie.vote_average,
                'popularity': movie.popularity,
                'poster_path': movie.poster_path
            })

        return {
            'movies': result,
            'count': len(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books")
async def list_books(
    limit: int = 20,
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    List all books (optionally filtered by category)
    """
    from app.database.crud import get_all_books, get_books_by_category

    try:
        if category:
            books = get_books_by_category(db, category, limit=limit)
        else:
            books = get_all_books(db, limit=limit)

        result = []
        for book in books:
            result.append({
                'id': book.id,
                'google_books_id': book.google_books_id,
                'title': book.title,
                'authors': book.authors,
                'description': book.description,
                'categories': book.categories,
                'average_rating': book.average_rating,
                'thumbnail': book.thumbnail
            })

        return {
            'books': result,
            'count': len(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
