from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.database.models import Character
import uuid
from sqlalchemy import cast, String


class CharacterGuessingGame:
    def __init__(self, db: Session):
        self.db = db
        self.question_tree = self._build_question_tree()

    def _build_question_tree(self) -> List[Dict]:
        """
        Define the decision tree of questions
        Order matters - most discriminating questions first
        """
        return [
            {
                "id": 1,
                "question": "Is this character from anime or a real actor?",
                "field": "type",
                "type": "exact",
                "options": ["anime", "actor"]
            },
            {
                "id": 2,
                "question": "What gender is this character?",
                "field": "additional_info.gender",
                "type": "nested",
                "options": ["male", "female"]
            },
            {
                "id": 3,
                "question": "Is this character a hero, villain, or anti-hero?",
                "field": "alignment",
                "type": "exact",
                "options": ["hero", "villain", "anti-hero"],
                "condition": {"type": "anime"}  # Only for anime characters
            },
            {
                "id": 4,
                "question": "Which trait best describes this character?",
                "field": "traits",
                "type": "contains",
                "options": ["funny", "serious", "determined", "intelligent",
                           "mysterious", "strong", "charismatic"]
            },
            {
                "id": 5,
                "question": "What genre is their main work?",
                "field": "genres",
                "type": "contains",
                "options": ["action", "comedy", "drama", "thriller",
                           "sci-fi", "adventure", "mystery"]
            },
            {
                "id": 6,
                "question": "How popular/famous is this character?",
                "field": "popularity_score",
                "type": "range",
                "options": {
                    "Extremely famous (everyone knows them)": (95, 100),
                    "Very famous": (90, 94),
                    "Well-known": (85, 89),
                    "Moderately known": (0, 84)
                }
            }
        ]

    def start_game(self) -> Dict:
        """
        Initialize a new game session

        Returns:
            {
                'session_id': 'uuid',
                'question': 'First question text',
                'options': [...],
                'question_number': 1
            }
        """
        session_id = str(uuid.uuid4())

        # Get all characters as initial candidates
        all_characters = self.db.query(Character).all()
        candidate_ids = [char.id for char in all_characters]

        print(f"[*] Started new game session: {session_id}")
        print(f"[*] Initial candidates: {len(candidate_ids)}")

        # Get first question
        first_question = self.question_tree[0]

        return {
            'session_id': session_id,
            'question': first_question['question'],
            'options': first_question['options'],
            'question_number': 1,
            'total_candidates': len(candidate_ids)
        }

    def answer_question(
        self,
        session_id: str,
        question_number: int,
        answer: str,
        candidate_ids: List[int]
    ) -> Dict:
        """
        Process answer and return next question or guess

        Args:
            session_id: Current session ID
            question_number: Which question was answered (1-based)
            answer: User's answer
            candidate_ids: Current list of candidate IDs

        Returns:
            {
                'status': 'continue' or 'guess',
                'question': '...' (if continue),
                'options': [...] (if continue),
                'guesses': [...] (if guess),
                'question_number': N
            }
        """
        # Get the question that was answered
        question = self.question_tree[question_number - 1]

        print(f"[*] Session {session_id[:8]}...")
        print(f"[*] Question {question_number}: {question['question']}")
        print(f"[*] Answer: {answer}")
        print(f"[*] Candidates before filtering: {len(candidate_ids)}")

        # Filter candidates based on answer
        new_candidates = self._filter_candidates(
            candidate_ids,
            question,
            answer
        )

        print(f"[*] Candidates after filtering: {len(new_candidates)}")

        # Decide if we should guess or continue
        if len(new_candidates) <= 3 or question_number >= 6:
            # Make guess
            return self._make_guess(new_candidates, question_number)

        # Continue with next question
        next_question_idx = question_number

        # Skip conditional questions if needed
        while next_question_idx < len(self.question_tree):
            next_q = self.question_tree[next_question_idx]

            # Check if question has conditions
            if 'condition' in next_q:
                # Check if condition is met
                if not self._check_condition(next_q['condition'], new_candidates):
                    next_question_idx += 1
                    continue

            break

        if next_question_idx >= len(self.question_tree):
            # No more questions, make guess
            return self._make_guess(new_candidates, question_number)

        next_q = self.question_tree[next_question_idx]

        return {
            'status': 'continue',
            'question': next_q['question'],
            'options': next_q['options'],
            'question_number': next_question_idx + 1,
            'remaining_candidates': len(new_candidates),
            'candidate_ids': new_candidates  # Pass to next call
        }

    def _filter_candidates(
        self,
        candidate_ids: List[int],
        question: Dict,
        answer: str
    ) -> List[int]:
        # Get current candidates
        candidates = self.db.query(Character).filter(
            Character.id.in_(candidate_ids)
        ).all()

        filtered = []
        field = question['field']
        q_type = question['type']

        for char in candidates:
            match = False

            if q_type == 'exact':
                # Exact field match
                value = getattr(char, field, None)
                if value == answer:
                    match = True

            elif q_type == 'nested':
                # Nested field (e.g., additional_info.gender)
                if field == 'additional_info.gender':
                    gender = char.additional_info.get('gender') if char.additional_info else None
                    if gender == answer:
                        match = True

            elif q_type == 'contains':
                # List field contains answer
                value = getattr(char, field, [])
                if isinstance(value, list) and answer in value:
                    match = True

            elif q_type == 'range':
                # Numeric range
                value = getattr(char, field, 0)
                ranges = question['options']
                if answer in ranges:
                    min_val, max_val = ranges[answer]
                    if min_val <= value <= max_val:
                        match = True

            if match:
                filtered.append(char.id)

        # Fallback: if no matches, return all (avoid dead end)
        return filtered if filtered else candidate_ids

    def _check_condition(self, condition: Dict, candidate_ids: List[int]) -> bool:
        if not candidate_ids:
            return False

        # Get a sample candidate
        sample = self.db.query(Character).filter(
            Character.id == candidate_ids[0]
        ).first()

        if not sample:
            return False

        # Check condition
        for field, value in condition.items():
            if getattr(sample, field, None) != value:
                return False

        return True

    def _make_guess(self, candidate_ids: List[int], questions_asked: int) -> Dict:
        """
        Make final guess(es) based on remaining candidates
        """
        candidates = self.db.query(Character).filter(
            Character.id.in_(candidate_ids)
        ).order_by(Character.popularity_score.desc()).limit(3).all()

        guesses = []
        for char in candidates:
            confidence = self._calculate_confidence(len(candidate_ids))
            guesses.append({
                'id': char.id,
                'name': char.name,
                'type': char.type,
                'source': char.source,
                'confidence': confidence,
                'image_url': char.image_url
            })

        print(f"[*] Making guess with {len(candidates)} candidates")
        print(f"[*] Top guess: {guesses[0]['name'] if guesses else 'None'}")

        return {
            'status': 'guess',
            'guesses': guesses,
            'total_questions': questions_asked
        }

    def _calculate_confidence(self, num_candidates: int) -> float:
        """
        Calculate confidence score (0-100) based on candidates remaining
        """
        if num_candidates == 1:
            return 95.0
        elif num_candidates == 2:
            return 80.0
        elif num_candidates == 3:
            return 65.0
        elif num_candidates <= 5:
            return 50.0
        else:
            return 35.0
