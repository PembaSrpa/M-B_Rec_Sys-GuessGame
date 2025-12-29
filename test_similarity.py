"""
Test similarity-based recommendations
"""
from app.database.db import SessionLocal
from app.models.recommendations import RecommendationEngine
from app.database.crud import get_all_movies


def main():
    db = SessionLocal()
    engine = RecommendationEngine(db)

    # Get a sample movie to find similar ones
    all_movies = get_all_movies(db, limit=10)

    if not all_movies:
        print("[ERROR] No movies in database!")
        return

    # Test with first action movie
    test_movie = None
    for movie in all_movies:
        if 'Action' in movie.genres:
            test_movie = movie
            break

    if not test_movie:
        test_movie = all_movies[0]

    print("\n" + "="*60)
    print("FINDING SIMILAR MOVIES")
    print("="*60)
    print(f"\nReference Movie: {test_movie.title} ({test_movie.release_year})")
    print(f"Genres: {', '.join(test_movie.genres)}")
    print(f"Rating: {test_movie.vote_average}/10")
    print("\nSimilar Movies:\n")

    # Get similar movies
    similar = engine.get_similar_movies(test_movie.id, top_n=5)

    for i, movie in enumerate(similar, 1):
        print(f"{i}. {movie['title']} ({movie['release_year']})")
        print(f"   Similarity: {movie['similarity_score']}/10")
        print(f"   Genres: {', '.join(movie['genres'])}")
        print(f"   Rating: {movie['vote_average']}/10")
        print(f"   Why similar: {movie['match_reason']}")
        print()

    # Test trending recommendations
    print("\n" + "="*60)
    print("TRENDING MOVIES")
    print("="*60 + "\n")

    trending = engine.get_trending_recommendations(top_n=5)

    for i, movie in enumerate(trending, 1):
        print(f"{i}. {movie['title']} ({movie['release_year']})")
        print(f"   Popularity: {movie['popularity']:.0f} | Rating: {movie['vote_average']}/10")
        print(f"   Genres: {', '.join(movie['genres'])}")
        print()

    db.close()


if __name__ == "__main__":
    main()
