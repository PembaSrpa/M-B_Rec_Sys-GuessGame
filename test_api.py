"""
Test all API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8001"


def print_response(title, response):
    """Pretty print API response"""
    print("\n" + "="*60)
    print(title)
    print("="*60)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
    else:
        print(f"Error: {response.text}")


def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("TEST 1: Health Check", response)


def test_list_movies():
    """Test listing movies"""
    response = requests.get(f"{BASE_URL}/api/movies?limit=5")
    print_response("TEST 2: List Movies (Top 5)", response)


def test_list_books():
    """Test listing books"""
    response = requests.get(f"{BASE_URL}/api/books?limit=5")
    print_response("TEST 3: List Books (Top 5)", response)


def test_movie_recommendations():
    """Test movie recommendations"""
    payload = {
        "content_type": "movie",
        "genres": ["Action", "Sci-Fi"],
        "decade": "2020s",
        "mood": "intense",
        "top_n": 3
    }

    response = requests.post(
        f"{BASE_URL}/api/recommendations",
        json=payload
    )
    print_response("TEST 4: Movie Recommendations (Action + Sci-Fi + 2020s)", response)


def test_book_recommendations():
    """Test book recommendations"""
    payload = {
        "content_type": "book",
        "genres": ["Fiction"],
        "min_rating": 4.0,
        "top_n": 3
    }

    response = requests.post(
        f"{BASE_URL}/api/recommendations",
        json=payload
    )
    print_response("TEST 5: Book Recommendations (Fiction, Rating >= 4.0)", response)


def test_similar_movies():
    """Test similar movies endpoint"""
    # First get a movie ID
    movies_response = requests.get(f"{BASE_URL}/api/movies?limit=1")

    if movies_response.status_code == 200:
        movies = movies_response.json()['movies']
        if movies:
            movie_id = movies[0]['id']
            movie_title = movies[0]['title']

            response = requests.get(
                f"{BASE_URL}/api/movies/{movie_id}/similar?top_n=3"
            )
            print_response(f"TEST 6: Similar to '{movie_title}'", response)
        else:
            print("\n[SKIP] TEST 6: No movies in database")
    else:
        print("\n[ERROR] TEST 6: Failed to fetch movies")


def test_trending_movies():
    """Test trending movies"""
    response = requests.get(f"{BASE_URL}/api/trending/movies?top_n=5")
    print_response("TEST 7: Trending Movies (Top 5)", response)


def test_guessing_game_start():
    """Test starting guessing game"""
    response = requests.post(f"{BASE_URL}/api/game/start")
    print_response("TEST 8: Start Guessing Game", response)

    return response.json() if response.status_code == 200 else None


def test_guessing_game_full():
    """Test full guessing game flow"""
    print("\n" + "="*60)
    print("TEST 9: Full Guessing Game Flow")
    print("="*60)

    # Start game
    start_response = requests.post(f"{BASE_URL}/api/game/start")

    if start_response.status_code != 200:
        print("[ERROR] Failed to start game")
        return

    game_data = start_response.json()
    session_id = game_data['session_id']

    print(f"\n[*] Session started: {session_id[:8]}...")
    print(f"[*] Question 1: {game_data['question']}")
    print(f"[*] Options: {game_data['options']}")

    # Get all character IDs for first answer
    chars_response = requests.get(f"{BASE_URL}/api/game/characters")

    if chars_response.status_code != 200:
        print("[ERROR] Failed to get characters")
        return

    candidate_ids = [c['id'] for c in chars_response.json()['characters']]

    # Simulate answering questions
    answers = [
        ('anime', 'First answer: anime'),
        ('male', 'Second answer: male'),
        ('hero', 'Third answer: hero')
    ]

    question_num = 1

    for answer, description in answers:
        print(f"\n[*] {description}")

        payload = {
            "session_id": session_id,
            "question_number": question_num,
            "answer": answer,
            "candidate_ids": candidate_ids
        }

        response = requests.post(
            f"{BASE_URL}/api/game/answer",
            json=payload
        )

        if response.status_code != 200:
            print(f"[ERROR] Failed to answer question: {response.text}")
            break

        result = response.json()

        if result['status'] == 'continue':
            print(f"[*] Remaining candidates: {result['remaining_candidates']}")
            print(f"[*] Next question: {result['question']}")
            print(f"[*] Options: {result['options']}")

            candidate_ids = result['candidate_ids']
            question_num = result['question_number']
        else:
            # Game made a guess
            print(f"\n[*] Game finished after {result['total_questions']} questions")
            print(f"[*] Top guesses:")
            for i, guess in enumerate(result['guesses'], 1):
                print(f"  {i}. {guess['name']} ({guess['type']})")
                print(f"     From: {guess['source']}")
                print(f"     Confidence: {guess['confidence']}%")
            break


def test_list_characters():
    """Test listing all characters"""
    response = requests.get(f"{BASE_URL}/api/game/characters")
    print_response("TEST 10: List All Characters", response)


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("RUNNING ALL API TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")

    try:
        # Basic tests
        test_health()
        test_list_movies()
        test_list_books()

        # Recommendation tests
        test_movie_recommendations()
        test_book_recommendations()
        test_similar_movies()
        test_trending_movies()

        # Guessing game tests
        test_list_characters()
        test_guessing_game_full()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API!")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")


if __name__ == "__main__":
    run_all_tests()
