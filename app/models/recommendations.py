"""
Movie/Book Recommendation Engine
Content-Based Filtering with Weighted Scoring
"""
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy.orm import Session
from app.database.models import Movie, Book
from app.database.crud import get_all_movies


class RecommendationEngine:
    """
    Content-based recommendation system
    Matches user preferences to content using weighted scoring
    """

    def __init__(self, db: Session):
        self.db = db

        # Mood to genre mapping
        self.mood_map = {
            'intense': ['Action', 'Thriller', 'Horror', 'War'],
            'light-hearted': ['Comedy', 'Animation', 'Family', 'Romance'],
            'thought-provoking': ['Drama', 'Mystery', 'Science Fiction', 'Documentary'],
            'emotional': ['Drama', 'Romance', 'Family'],
            'suspenseful': ['Thriller', 'Mystery', 'Horror', 'Crime']
        }

        # Setting to genre mapping
        self.setting_map = {
            'modern': ['Action', 'Thriller', 'Crime', 'Drama'],
            'historical': ['History', 'War', 'Drama'],
            'futuristic': ['Science Fiction', 'Fantasy'],
            'fantasy_world': ['Fantasy', 'Adventure', 'Animation']
        }

    def recommend_movies(
        self,
        genres: Optional[List[str]] = None,
        decade: Optional[str] = None,
        mood: Optional[str] = None,
        setting: Optional[str] = None,
        min_rating: Optional[float] = None,
        top_n: int = 5
    ) -> Dict:
        """
        Get movie recommendations based on user preferences

        Args:
            genres: List of preferred genres ['Action', 'Comedy']
            decade: Preferred decade '2010s', '2000s', etc.
            mood: User's mood 'intense', 'light-hearted', etc.
            setting: Preferred setting 'modern', 'futuristic', etc.
            min_rating: Minimum rating threshold (0-10)
            top_n: Number of recommendations to return

        Returns:
            {
                'recommendations': [...],
                'match_quality': 'high'/'medium'/'low',
                'total_candidates': 99
            }
        """
        print(f"[*] Getting recommendations with preferences:")
        print(f"    Genres: {genres}")
        print(f"    Decade: {decade}")
        print(f"    Mood: {mood}")
        print(f"    Setting: {setting}")

        # Get all movies
        all_movies = get_all_movies(self.db, limit=1000)

        if not all_movies:
            return {
                'recommendations': [],
                'match_quality': 'none',
                'total_candidates': 0
            }

        # Convert to DataFrame for easier manipulation
        movies_data = []
        for movie in all_movies:
            movies_data.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'genres': movie.genres,
                'release_year': movie.release_year,
                'decade': movie.decade,
                'vote_average': movie.vote_average,
                'vote_count': movie.vote_count,
                'popularity': movie.popularity,
                'poster_path': movie.poster_path,
                'backdrop_path': movie.backdrop_path
            })

        df = pd.DataFrame(movies_data)

        # Calculate match scores
        df['score'] = df.apply(
            lambda row: self._calculate_movie_score(
                row, genres, decade, mood, setting, min_rating
            ),
            axis=1
        )

        # Filter by minimum rating if specified
        if min_rating:
            df = df[df['vote_average'] >= min_rating]

        # Sort by score
        df = df.sort_values('score', ascending=False)

        # Determine match quality
        top_scores = df.head(top_n)['score'].values
        if len(top_scores) > 0:
            avg_score = top_scores.mean()
            if avg_score >= 7.0:
                match_quality = 'high'
            elif avg_score >= 4.0:
                match_quality = 'medium'
            else:
                match_quality = 'low'
        else:
            match_quality = 'none'

        # Get top N recommendations
        recommendations = df.head(top_n).to_dict('records')

        # Add match reasons
        for rec in recommendations:
            rec['match_reason'] = self._get_match_reason(
                rec, genres, decade, mood, setting
            )

        return {
            'recommendations': recommendations,
            'match_quality': match_quality,
            'total_candidates': len(all_movies)
        }

    def _calculate_movie_score(
        self,
        movie: pd.Series,
        genres: Optional[List[str]],
        decade: Optional[str],
        mood: Optional[str],
        setting: Optional[str],
        min_rating: Optional[float]
    ) -> float:
        """
        Calculate match score for a movie (0-10 scale)

        Weighting:
        - Genre match: 40%
        - Decade match: 15%
        - Mood match: 20%
        - Setting match: 10%
        - Quality (rating): 15%
        """
        score = 0.0
        movie_genres = movie['genres'] if isinstance(movie['genres'], list) else []

        # 1. Genre Match (40% weight) - most important
        if genres:
            genre_matches = sum(1 for g in genres if g in movie_genres)
            genre_score = (genre_matches / len(genres)) * 4.0
            score += genre_score
        else:
            score += 2.0  # Neutral score if no genre preference

        # 2. Decade Match (15% weight)
        if decade:
            decade_num = int(decade[:4]) if decade else None
            if decade_num and movie['decade'] == decade_num:
                score += 1.5  # Exact decade match
            elif decade_num and abs(movie['decade'] - decade_num) == 10:
                score += 0.75  # Adjacent decade (partial match)
        else:
            score += 0.75  # Neutral score

        # 3. Mood Match (20% weight)
        if mood and mood in self.mood_map:
            mood_genres = self.mood_map[mood]
            mood_matches = sum(1 for g in mood_genres if g in movie_genres)
            mood_score = (mood_matches / len(mood_genres)) * 2.0
            score += mood_score
        else:
            score += 1.0  # Neutral score

        # 4. Setting Match (10% weight)
        if setting and setting in self.setting_map:
            setting_genres = self.setting_map[setting]
            setting_matches = sum(1 for g in setting_genres if g in movie_genres)
            setting_score = (setting_matches / len(setting_genres)) * 1.0
            score += setting_score
        else:
            score += 0.5  # Neutral score

        # 5. Quality Score (15% weight) - based on rating
        if pd.notna(movie['vote_average']) and movie['vote_average'] > 0:
            rating = movie['vote_average']
            # Normalize rating to 0-1.5 scale
            quality_score = (rating / 10.0) * 1.5
            score += quality_score

        return round(score, 2)

    def _get_match_reason(
        self,
        movie: Dict,
        genres: Optional[List[str]],
        decade: Optional[str],
        mood: Optional[str],
        setting: Optional[str]
    ) -> str:
        """
        Generate human-readable reason for recommendation
        """
        reasons = []
        movie_genres = movie['genres'] if isinstance(movie['genres'], list) else []

        # Genre matches
        if genres:
            matched_genres = [g for g in genres if g in movie_genres]
            if matched_genres:
                reasons.append(f"Matches your genre preferences: {', '.join(matched_genres)}")

        # Decade match
        if decade:
            decade_num = int(decade[:4])
            if movie['decade'] == decade_num:
                reasons.append(f"From your preferred decade ({decade})")

        # Mood match
        if mood and mood in self.mood_map:
            mood_genres = self.mood_map[mood]
            matched_mood_genres = [g for g in mood_genres if g in movie_genres]
            if matched_mood_genres:
                reasons.append(f"Fits your {mood} mood")

        # High rating
        if movie['vote_average'] >= 7.5:
            reasons.append(f"Highly rated ({movie['vote_average']}/10)")

        # Popular
        if movie['popularity'] > 100:
            reasons.append("Very popular")

        return " | ".join(reasons) if reasons else "Recommended based on overall quality"

    def get_fallback_recommendations(self, top_n: int = 5) -> List[Dict]:
        """
        Get fallback recommendations when no preferences match
        Returns highly-rated popular movies
        """
        print("[*] Using fallback recommendations (popular + highly rated)")

        all_movies = get_all_movies(self.db, limit=100)

        movies_data = []
        for movie in all_movies:
            # Only include well-rated movies with enough votes
            if movie.vote_average >= 7.0 and movie.vote_count >= 100:
                movies_data.append({
                    'id': movie.id,
                    'tmdb_id': movie.tmdb_id,
                    'title': movie.title,
                    'overview': movie.overview,
                    'genres': movie.genres,
                    'release_year': movie.release_year,
                    'decade': movie.decade,
                    'vote_average': movie.vote_average,
                    'vote_count': movie.vote_count,
                    'popularity': movie.popularity,
                    'poster_path': movie.poster_path,
                    'backdrop_path': movie.backdrop_path,
                    'score': 0.0,
                    'match_reason': 'Popular and highly rated'
                })

        df = pd.DataFrame(movies_data)

        # Sort by combination of rating and popularity
        df['combined_score'] = (df['vote_average'] * 0.6) + (df['popularity'] / 100 * 0.4)
        df = df.sort_values('combined_score', ascending=False)

        return df.head(top_n).to_dict('records')

    def get_similar_movies(self, movie_id: int, top_n: int = 5) -> List[Dict]:
        """
        Find movies similar to a given movie
        Based on genre overlap, decade, and rating similarity

        Args:
            movie_id: Database ID of the reference movie
            top_n: Number of similar movies to return

        Returns:
            List of similar movies with similarity scores
        """
        # Get the reference movie
        reference_movie = self.db.query(Movie).filter(Movie.id == movie_id).first()

        if not reference_movie:
            return []

        print(f"[*] Finding movies similar to: {reference_movie.title}")

        # Get all other movies
        all_movies = self.db.query(Movie).filter(Movie.id != movie_id).all()

        similar_movies = []

        for movie in all_movies:
            similarity_score = self._calculate_similarity(reference_movie, movie)

            similar_movies.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'genres': movie.genres,
                'release_year': movie.release_year,
                'decade': movie.decade,
                'vote_average': movie.vote_average,
                'vote_count': movie.vote_count,
                'popularity': movie.popularity,
                'poster_path': movie.poster_path,
                'backdrop_path': movie.backdrop_path,
                'similarity_score': similarity_score,
                'match_reason': self._get_similarity_reason(reference_movie, movie)
            })

        # Sort by similarity score
        similar_movies.sort(key=lambda x: x['similarity_score'], reverse=True)

        return similar_movies[:top_n]

    def _calculate_similarity(self, movie1: Movie, movie2: Movie) -> float:
        """
        Calculate similarity score between two movies (0-10 scale)

        Factors:
        - Genre overlap: 50%
        - Decade proximity: 20%
        - Rating similarity: 20%
        - Popularity proximity: 10%
        """
        score = 0.0

        genres1 = set(movie1.genres) if movie1.genres else set()
        genres2 = set(movie2.genres) if movie2.genres else set()

        # 1. Genre overlap (50% weight) - Jaccard similarity
        if genres1 and genres2:
            intersection = len(genres1.intersection(genres2))
            union = len(genres1.union(genres2))
            genre_similarity = (intersection / union) * 5.0
            score += genre_similarity

        # 2. Decade proximity (20% weight)
        if movie1.decade and movie2.decade:
            decade_diff = abs(movie1.decade - movie2.decade)
            if decade_diff == 0:
                score += 2.0  # Same decade
            elif decade_diff == 10:
                score += 1.0  # Adjacent decade
            elif decade_diff == 20:
                score += 0.5  # Two decades apart

        # 3. Rating similarity (20% weight)
        if movie1.vote_average and movie2.vote_average:
            rating_diff = abs(movie1.vote_average - movie2.vote_average)
            rating_similarity = max(0, (10 - rating_diff) / 10) * 2.0
            score += rating_similarity

        # 4. Popularity proximity (10% weight)
        if movie1.popularity and movie2.popularity:
            pop_ratio = min(movie1.popularity, movie2.popularity) / max(movie1.popularity, movie2.popularity)
            score += pop_ratio * 1.0

        return round(score, 2)

    def _get_similarity_reason(self, movie1: Movie, movie2: Movie) -> str:
        """
        Generate reason for similarity
        """
        reasons = []

        genres1 = set(movie1.genres) if movie1.genres else set()
        genres2 = set(movie2.genres) if movie2.genres else set()

        # Shared genres
        shared_genres = genres1.intersection(genres2)
        if shared_genres:
            reasons.append(f"Shares genres: {', '.join(list(shared_genres)[:3])}")

        # Same decade
        if movie1.decade == movie2.decade:
            reasons.append(f"Both from {movie1.decade}s")

        # Similar ratings
        if movie1.vote_average and movie2.vote_average:
            rating_diff = abs(movie1.vote_average - movie2.vote_average)
            if rating_diff < 0.5:
                reasons.append(f"Similar ratings (~{movie2.vote_average:.1f}/10)")

        return " | ".join(reasons) if reasons else "General similarity"

    def get_trending_recommendations(self, top_n: int = 10) -> List[Dict]:
        """
        Get currently trending/popular movies
        Based on popularity and recent ratings
        """
        print("[*] Getting trending recommendations")

        # Get movies sorted by popularity
        trending_movies = self.db.query(Movie).filter(
            Movie.vote_count >= 100  # Must have significant votes
        ).order_by(
            Movie.popularity.desc()
        ).limit(top_n).all()

        result = []
        for movie in trending_movies:
            result.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'genres': movie.genres,
                'release_year': movie.release_year,
                'decade': movie.decade,
                'vote_average': movie.vote_average,
                'vote_count': movie.vote_count,
                'popularity': movie.popularity,
                'poster_path': movie.poster_path,
                'backdrop_path': movie.backdrop_path,
                'match_reason': 'Currently trending'
            })

        return result
