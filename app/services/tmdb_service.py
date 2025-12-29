"""
TMDB Service - Fetch movie data from The Movie Database API
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import time

class TMDBService:
    """
    Service to interact with TMDB API
    Docs: https://developers.themoviedb.org/3
    """

    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"  # For poster images

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make a request to TMDB API with error handling

        Args:
            endpoint: API endpoint (e.g., '/movie/popular')
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        if params is None:
            params = {}

        # Add API key to all requests
        params['api_key'] = self.api_key

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching from TMDB: {e}")
            return None

    def fetch_popular_movies(self, pages: int = 5) -> pd.DataFrame:
        """
        Fetch popular movies from TMDB

        Args:
            pages: Number of pages to fetch (each page = 20 movies)

        Returns:
            DataFrame with movie data
        """
        print(f"[*] Fetching {pages} pages of popular movies from TMDB...")

        all_movies = []

        for page in range(1, pages + 1):
            print(f"  Fetching page {page}/{pages}...", end=" ")

            data = self._make_request('/movie/popular', {'page': page})

            if data and 'results' in data:
                all_movies.extend(data['results'])
                print(f"[OK] Got {len(data['results'])} movies")
            else:
                print("[FAILED]")

            # Be nice to the API - don't spam requests
            time.sleep(0.25)  # 250ms delay between requests

        print(f"[SUCCESS] Total movies fetched: {len(all_movies)}")

        # Convert to DataFrame
        df = pd.DataFrame(all_movies)

        # Process the data
        df = self._process_movie_data(df)

        return df

    def fetch_movie_details(self, movie_id: int) -> Dict:
        """
        Fetch detailed information for a specific movie
        Including genres, keywords, runtime, etc.
        """
        data = self._make_request(f'/movie/{movie_id}')
        return data

    def fetch_movies_by_genre(self, genre_id: int, pages: int = 3) -> pd.DataFrame:
        """
        Fetch movies by genre

        Genre IDs:
        - 28: Action
        - 12: Adventure
        - 35: Comedy
        - 18: Drama
        - 27: Horror
        - 878: Science Fiction
        - 53: Thriller
        - 10749: Romance
        """
        print(f"[*] Fetching movies for genre ID {genre_id}...")

        all_movies = []

        for page in range(1, pages + 1):
            data = self._make_request('/discover/movie', {
                'with_genres': genre_id,
                'page': page,
                'sort_by': 'popularity.desc'
            })

            if data and 'results' in data:
                all_movies.extend(data['results'])

            time.sleep(0.25)

        df = pd.DataFrame(all_movies)
        df = self._process_movie_data(df)

        return df

    def _process_movie_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and enhance movie data
        Add calculated fields like decade, full poster URL, etc.
        """
        if df.empty:
            return df

        # Parse release date and extract year/decade
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year
        df['decade'] = (df['release_year'] // 10) * 10

        # Convert genre IDs to readable names
        df['genre_names'] = df['genre_ids'].apply(self._get_genre_names)

        # Add full poster URL
        df['poster_url'] = df['poster_path'].apply(
            lambda x: f"{self.IMAGE_BASE_URL}{x}" if pd.notna(x) else None
        )

        # Add backdrop URL
        df['backdrop_url'] = df['backdrop_path'].apply(
            lambda x: f"{self.IMAGE_BASE_URL}{x}" if pd.notna(x) else None
        )

        # Rename columns to match our database schema
        df = df.rename(columns={
            'id': 'tmdb_id',
            'title': 'title',
            'overview': 'overview',
            'vote_average': 'vote_average',
            'vote_count': 'vote_count',
            'popularity': 'popularity',
            'original_language': 'original_language'
        })

        # Select relevant columns
        columns_to_keep = [
            'tmdb_id', 'title', 'overview', 'genre_ids', 'genre_names',
            'release_date', 'release_year', 'decade',
            'vote_average', 'vote_count', 'popularity',
            'poster_path', 'poster_url', 'backdrop_path', 'backdrop_url',
            'original_language', 'adult'
        ]

        # Only keep columns that exist
        columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        df = df[columns_to_keep]

        # Remove adult content
        if 'adult' in df.columns:
            df = df[df['adult'] == False]
            df = df.drop('adult', axis=1)

        # Remove duplicates
        df = df.drop_duplicates(subset=['tmdb_id'])

        # Sort by popularity
        df = df.sort_values('popularity', ascending=False)

        return df

    def _get_genre_names(self, genre_ids: List[int]) -> List[str]:
        """
        Convert genre IDs to names
        """
        genre_map = {
            28: 'Action',
            12: 'Adventure',
            16: 'Animation',
            35: 'Comedy',
            80: 'Crime',
            99: 'Documentary',
            18: 'Drama',
            10751: 'Family',
            14: 'Fantasy',
            36: 'History',
            27: 'Horror',
            10402: 'Music',
            9648: 'Mystery',
            10749: 'Romance',
            878: 'Science Fiction',
            10770: 'TV Movie',
            53: 'Thriller',
            10752: 'War',
            37: 'Western'
        }

        if not isinstance(genre_ids, list):
            return []

        return [genre_map.get(gid, f'Unknown({gid})') for gid in genre_ids]

    def get_genres(self) -> Dict:
        """
        Get all available genres from TMDB
        """
        data = self._make_request('/genre/movie/list')
        return data.get('genres', []) if data else []

    def search_movies(self, query: str, page: int = 1) -> pd.DataFrame:
        """
        Search for movies by title
        """
        data = self._make_request('/search/movie', {
            'query': query,
            'page': page
        })

        if data and 'results' in data:
            df = pd.DataFrame(data['results'])
            df = self._process_movie_data(df)
            return df

        return pd.DataFrame()


# Example usage / Test function
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        print("[ERROR] TMDB_API_KEY not found in .env file!")
    else:
        # Initialize service
        tmdb = TMDBService(api_key)

        # Test: Fetch popular movies
        print("\n" + "="*60)
        print("Testing TMDB Service")
        print("="*60 + "\n")

        movies_df = tmdb.fetch_popular_movies(pages=2)  # Get 40 movies

        print(f"\n[DATA] Preview:")
        print(f"Total movies: {len(movies_df)}")
        print(f"\nColumns: {list(movies_df.columns)}")
        print(f"\nFirst 3 movies:")
        print(movies_df[['title', 'release_year', 'vote_average', 'genre_names']].head(3))

        # Test: Get genres
        print("\n[GENRES] Available:")
        genres = tmdb.get_genres()
        for genre in genres[:5]:
            print(f"  - {genre['name']} (ID: {genre['id']})")
