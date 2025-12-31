"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ============================================================
# RECOMMENDATION SCHEMAS
# ============================================================

class RecommendationRequest(BaseModel):
    """Request model for getting recommendations"""
    content_type: str = Field(..., description="'movie' or 'book'")
    genres: Optional[List[str]] = Field(None, description="Preferred genres")
    decade: Optional[str] = Field(None, description="Preferred decade (e.g., '2010s')")
    mood: Optional[str] = Field(None, description="Mood: intense, light-hearted, thought-provoking")
    setting: Optional[str] = Field(None, description="Setting: modern, futuristic, historical")
    min_rating: Optional[float] = Field(None, ge=0, le=10, description="Minimum rating (0-10)")
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "movie",
                "genres": ["Action", "Sci-Fi"],
                "decade": "2020s",
                "mood": "intense",
                "top_n": 5
            }
        }


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    id: int
    title: str
    overview: Optional[str]
    genres: List[str]
    release_year: Optional[int]
    vote_average: Optional[float]
    popularity: Optional[float]
    poster_path: Optional[str]
    score: float
    match_reason: str


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    recommendations: List[Dict[str, Any]]
    match_quality: str
    total_candidates: int


class SimilarRequest(BaseModel):
    """Request model for similar items"""
    item_id: int = Field(..., description="ID of the reference item")
    top_n: int = Field(5, ge=1, le=20, description="Number of similar items")


# ============================================================
# GUESSING GAME SCHEMAS
# ============================================================

class GameStartResponse(BaseModel):
    """Response when starting a new game"""
    session_id: str
    question: str
    options: List[Any]
    question_number: int
    total_candidates: int


class GameAnswerRequest(BaseModel):
    """Request to answer a question"""
    session_id: str
    question_number: int
    answer: str
    candidate_ids: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "question_number": 1,
                "answer": "anime",
                "candidate_ids": [1, 2, 3, 4, 5]
            }
        }


class GuessItem(BaseModel):
    """Single guess item"""
    id: int
    name: str
    type: str
    source: str
    confidence: float
    image_url: Optional[str]


class GameAnswerResponse(BaseModel):
    """Response after answering a question"""
    status: str  # 'continue' or 'guess'
    question: Optional[str] = None
    options: Optional[List[Any]] = None
    question_number: Optional[int] = None
    remaining_candidates: Optional[int] = None
    candidate_ids: Optional[List[int]] = None
    guesses: Optional[List[Dict[str, Any]]] = None
    total_questions: Optional[int] = None


# ============================================================
# GENERAL SCHEMAS
# ============================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    database_connected: bool
    total_movies: int
    total_books: int
    total_characters: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
