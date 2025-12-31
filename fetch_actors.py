"""
Fetch popular actors from TMDB API
"""
import os
from dotenv import load_dotenv
from app.services.tmdb_service import TMDBService
import json

load_dotenv()


def fetch_popular_actors(pages: int = 3):
    """
    Fetch popular actors from TMDB
    """
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("[ERROR] TMDB_API_KEY not found!")
        return

    tmdb = TMDBService(api_key)

    print("\n" + "="*60)
    print("FETCHING POPULAR ACTORS FROM TMDB")
    print("="*60 + "\n")

    all_actors = []

    for page in range(1, pages + 1):
        print(f"[*] Fetching page {page}/{pages}...")

        response = tmdb._make_request('/person/popular', {'page': page})

        if response and 'results' in response:
            all_actors.extend(response['results'])
            print(f"  Got {len(response['results'])} actors")

    print(f"\n[SUCCESS] Total actors fetched: {len(all_actors)}")

    # Process actors
    processed_actors = []

    for actor in all_actors:
        # Get known_for movies to determine genres
        known_for = actor.get('known_for', [])
        genres = set()

        for work in known_for[:3]:  # Top 3 works
            if 'genre_ids' in work:
                for genre_id in work['genre_ids']:
                    genre_name = tmdb._get_genre_names([genre_id])
                    genres.update(genre_name)

        processed_actors.append({
            'tmdb_id': actor.get('id'),
            'name': actor.get('name'),
            'popularity': actor.get('popularity'),
            'profile_path': actor.get('profile_path'),
            'known_for_department': actor.get('known_for_department'),
            'known_for': [work.get('title', work.get('name', '')) for work in known_for[:2]],
            'genres': list(genres)
        })

    # Sort by popularity
    processed_actors.sort(key=lambda x: x['popularity'], reverse=True)

    # Save to JSON
    output_file = 'data/actors_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_actors[:50], f, indent=2, ensure_ascii=False)  # Top 50

    print(f"\n[SUCCESS] Saved top 50 actors to {output_file}")

    # Show preview
    print(f"\n[PREVIEW] Top 10 actors:")
    for i, actor in enumerate(processed_actors[:10], 1):
        print(f"{i}. {actor['name']} (Popularity: {actor['popularity']:.0f})")
        print(f"   Known for: {', '.join(actor['known_for'][:2])}")
        print(f"   Genres: {', '.join(actor['genres'][:3])}")
        print()


if __name__ == "__main__":
    fetch_popular_actors(pages=3)
