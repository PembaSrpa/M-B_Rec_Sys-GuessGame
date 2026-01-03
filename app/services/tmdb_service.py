import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import time

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        if params is None: params = {}
        params['api_key'] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] TMDB API error: {e}")
            return None

    def fetch_popular_movies(self, pages: int = 5) -> pd.DataFrame:
        all_movies = []
        for page in range(1, pages + 1):
            data = self._make_request('/movie/popular', {'page': page})
            if data and 'results' in data:
                all_movies.extend(data['results'])
            time.sleep(0.25)
        return self._process_movie_data(pd.DataFrame(all_movies))

    def fetch_1k_movies(self):
        all_movies = []
        years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018]
        for year in years:
            for page in range(1, 11):
                data = self._make_request('/discover/movie', {
                    'primary_release_year': year,
                    'sort_by': 'popularity.desc',
                    'page': page,
                    'vote_count.gte': 100
                })
                if data and 'results' in data:
                    all_movies.extend(data['results'])
                time.sleep(0.2)
        return self._process_movie_data(pd.DataFrame(all_movies))

    def _process_movie_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year
        df['decade'] = (df['release_year'] // 10) * 10
        df['genre_names'] = df['genre_ids'].apply(self._get_genre_names)
        df['poster_url'] = df['poster_path'].apply(lambda x: f"{self.IMAGE_BASE_URL}{x}" if pd.notna(x) else None)
        df = df.rename(columns={
            'id': 'tmdb_id', 'vote_average': 'vote_average',
            'vote_count': 'vote_count', 'popularity': 'popularity'
        })
        columns_to_keep = [
            'tmdb_id', 'title', 'overview', 'genre_ids', 'genre_names',
            'release_date', 'release_year', 'decade', 'vote_average',
            'vote_count', 'popularity', 'poster_url'
        ]
        df = df[[col for col in columns_to_keep if col in df.columns]]
        return df.drop_duplicates(subset=['tmdb_id']).sort_values('popularity', ascending=False)

    def _get_genre_names(self, genre_ids: List[int]) -> List[str]:
        genre_map = {
            28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
            99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History',
            27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance',
            878: 'Science Fiction', 10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western'
        }
        if not isinstance(genre_ids, list): return []
        return [genre_map.get(gid, f'Unknown({gid})') for gid in genre_ids]
