"""
Test the recommendation engine with different scenarios
"""
from app.database.db import SessionLocal
from app.models.recommendations import RecommendationEngine


def print_recommendations(result: dict, scenario: str):
    """Pretty print recommendations"""
    print("\n" + "="*60)
    print(f"SCENARIO: {scenario}")
    print("="*60)
    print(f"Match Quality: {result['match_quality'].upper()}")
    print(f"Total Candidates: {result['total_candidates']}")
    print(f"\nTop Recommendations:\n")

    for i, movie in enumerate(result['recommendations'], 1):
        print(f"{i}. {movie['title']} ({movie['release_year']})")
        print(f"   Score: {movie['score']}/10 | Rating: {movie['vote_average']}/10")
        print(f"   Genres: {', '.join(movie['genres'])}")
        print(f"   Why: {movie['match_reason']}")
        print()


def main():
    db = SessionLocal()
    engine = RecommendationEngine(db)

    # Test Scenario 1: Action + Recent
    result1 = engine.recommend_movies(
        genres=['Action', 'Thriller'],
        decade='2020s',
        mood='intense',
        top_n=5
    )
    print_recommendations(result1, "Action lover wants recent intense movies")

    # Test Scenario 2: Comedy + Family Friendly
    result2 = engine.recommend_movies(
        genres=['Comedy', 'Family'],
        mood='light-hearted',
        min_rating=7.0,
        top_n=5
    )
    print_recommendations(result2, "Family movie night - Comedy with good ratings")

    # Test Scenario 3: Sci-Fi from 2010s
    result3 = engine.recommend_movies(
        genres=['Science Fiction'],
        decade='2010s',
        setting='futuristic',
        top_n=5
    )
    print_recommendations(result3, "Sci-Fi fan wants futuristic 2010s movies")

    # Test Scenario 4: Just mood (no specific genre)
    result4 = engine.recommend_movies(
        mood='thought-provoking',
        min_rating=7.5,
        top_n=5
    )
    print_recommendations(result4, "Wants something thought-provoking and highly rated")

    # Test Scenario 5: Impossible preferences (should use fallback)
    result5 = engine.recommend_movies(
        genres=['Documentary', 'Western'],  # Rare combination
        decade='1960s',  # We don't have these
        top_n=5
    )
    print_recommendations(result5, "Impossible preferences - should show best available")

    db.close()


if __name__ == "__main__":
    main()
