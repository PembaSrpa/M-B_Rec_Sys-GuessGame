from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database.db import get_db, engine
from app.database.models import Base
from app.routes import recommendations, guessing
from app.schemas import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="Movie/Book Recommendation API",
    description="Content-based recommendation system with character guessing game",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://movie-recommendation-frontend.vercel.app",
    ],
    # Use regex to allow all Vercel subdomains
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendations.router)
app.include_router(guessing.router)


@app.get("/", response_model=dict)
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Movie/Book Recommendation & Guessing Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "recommendations": "/api/recommendations",
            "similar_movies": "/api/movies/{id}/similar",
            "trending": "/api/trending/movies",
            "list_movies": "/api/movies",
            "list_books": "/api/books",
            "start_game": "/api/game/start",
            "answer_question": "/api/game/answer",
            "list_characters": "/api/game/characters",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint with database statistics
    """
    from app.database.models import Movie, Book, Character

    try:
        # Test database connection
        total_movies = db.query(Movie).count()
        total_books = db.query(Book).count()
        total_characters = db.query(Character).count()

        return {
            "status": "healthy",
            "message": "API is running",
            "database_connected": True,
            "total_movies": total_movies,
            "total_books": total_books,
            "total_characters": total_characters
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e),
            "database_connected": False,
            "total_movies": 0,
            "total_books": 0,
            "total_characters": 0
        }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print("[*] Starting Movie Recommendation API...")
    print("[*] Database tables initialized")
    print("[*] API documentation available at /docs")
