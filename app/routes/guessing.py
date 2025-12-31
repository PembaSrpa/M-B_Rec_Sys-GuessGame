"""
API routes for character guessing game
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas import (
    GameStartResponse,
    GameAnswerRequest,
    GameAnswerResponse
)
from app.models.guessing_game import CharacterGuessingGame

router = APIRouter(prefix="/api/game", tags=["guessing-game"])


@router.post("/start", response_model=GameStartResponse)
async def start_game(db: Session = Depends(get_db)):
    """
    Start a new guessing game session

    Returns the first question and a unique session ID
    """
    try:
        game = CharacterGuessingGame(db)
        result = game.start_game()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=GameAnswerResponse)
async def answer_question(
    request: GameAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Answer a question in the guessing game

    - **session_id**: Current game session ID
    - **question_number**: Which question is being answered
    - **answer**: User's answer
    - **candidate_ids**: Current list of possible character IDs

    Returns either the next question or final guess
    """
    try:
        game = CharacterGuessingGame(db)

        result = game.answer_question(
            session_id=request.session_id,
            question_number=request.question_number,
            answer=request.answer,
            candidate_ids=request.candidate_ids
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/characters")
async def list_characters(db: Session = Depends(get_db)):
    """
    List all available characters in the game
    """
    from app.database.models import Character

    try:
        characters = db.query(Character).order_by(
            Character.popularity_score.desc()
        ).all()

        result = []
        for char in characters:
            result.append({
                'id': char.id,
                'name': char.name,
                'type': char.type,
                'source': char.source,
                'popularity_score': char.popularity_score,
                'image_url': char.image_url
            })

        return {
            'characters': result,
            'count': len(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
