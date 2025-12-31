"""
Google Books Service - Fetch book data from Google Books API
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import time


class GoogleBooksService:
    """
    Service to interact with Google Books API
    Docs: https://developers.google.com/books/docs/v1/using
    """

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: Optional[str] = None):
        """
        API key is optional for Google Books
        But having one increases rate limits
        """
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, params: Dict) -> Dict:
        """
        Make request to Google Books API
        """
        if self.api_key:
            params['key'] = self.api_key

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Google Books API error: {e}")
            return None

    def fetch_books_by_genre(self, genre: str, max_results: int = 40) -> pd.DataFrame:
        """
        Fetch books by genre/subject

        Popular genres:
        - Fiction
        - Science Fiction
        - Fantasy
        - Mystery
        - Romance
        - Thriller
        - Biography
        - History
        """
        print(f"[*] Fetching books for genre: {genre}")

        all_books = []
        start_index = 0

        while len(all_books) < max_results:
            params = {
                'q': f'subject:{genre}',
                'maxResults': min(40, max_results - len(all_books)),
                'startIndex': start_index,
                'orderBy': 'relevance',
                'printType': 'books',
                'langRestrict': 'en'
            }

            data = self._make_request(params)

            if not data or 'items' not in data:
                break

            all_books.extend(data['items'])
            print(f"  Fetched {len(all_books)}/{max_results} books")

            if len(data['items']) < 40:
                break

            start_index += 40
            time.sleep(0.3)  # Rate limiting

        print(f"[SUCCESS] Total books fetched: {len(all_books)}")

        # Process and return DataFrame
        return self._process_book_data(all_books)

    def fetch_bestsellers(self, category: str = 'fiction', max_results: int = 40) -> pd.DataFrame:
        """
        Fetch bestselling books
        """
        print(f"[*] Fetching bestsellers in {category}")

        params = {
            'q': f'{category}+bestseller',
            'maxResults': max_results,
            'orderBy': 'relevance',
            'printType': 'books',
            'langRestrict': 'en'
        }

        data = self._make_request(params)

        if not data or 'items' not in data:
            return pd.DataFrame()

        return self._process_book_data(data['items'])

    def search_books(self, query: str, max_results: int = 20) -> pd.DataFrame:
        """
        Search books by title or author
        """
        print(f"[*] Searching books: {query}")

        params = {
            'q': query,
            'maxResults': max_results,
            'orderBy': 'relevance',
            'printType': 'books',
            'langRestrict': 'en'
        }

        data = self._make_request(params)

        if not data or 'items' not in data:
            return pd.DataFrame()

        return self._process_book_data(data['items'])

    def _process_book_data(self, books: List[Dict]) -> pd.DataFrame:
        """
        Process raw book data into clean DataFrame
        """
        processed_books = []

        for book in books:
            volume_info = book.get('volumeInfo', {})

            # Extract data
            google_books_id = book.get('id')
            title = volume_info.get('title', 'Unknown')
            authors = volume_info.get('authors', [])
            description = volume_info.get('description', '')
            categories = volume_info.get('categories', [])
            published_date = volume_info.get('publishedDate', '')
            page_count = volume_info.get('pageCount', 0)
            average_rating = volume_info.get('averageRating', 0)
            ratings_count = volume_info.get('ratingsCount', 0)
            language = volume_info.get('language', 'en')
            publisher = volume_info.get('publisher', '')

            # Get thumbnail
            image_links = volume_info.get('imageLinks', {})
            thumbnail = image_links.get('thumbnail', image_links.get('smallThumbnail', ''))

            # Parse publication year and decade
            try:
                if len(published_date) >= 4:
                    year = int(published_date[:4])
                    decade = (year // 10) * 10
                else:
                    year = None
                    decade = None
            except:
                year = None
                decade = None

            processed_books.append({
                'google_books_id': google_books_id,
                'title': title,
                'authors': authors,
                'description': description,
                'categories': categories,
                'published_date': published_date,
                'year': year,
                'decade': decade,
                'page_count': page_count,
                'average_rating': average_rating,
                'ratings_count': ratings_count,
                'thumbnail': thumbnail,
                'language': language,
                'publisher': publisher
            })

        df = pd.DataFrame(processed_books)

        # Remove duplicates
        if not df.empty:
            df = df.drop_duplicates(subset=['google_books_id'])

            # Filter out books with no rating (too obscure)
            df = df[df['ratings_count'] > 0]

            # Sort by rating and ratings count
            df['quality_score'] = df['average_rating'] * (df['ratings_count'] ** 0.3)
            df = df.sort_values('quality_score', ascending=False)

        return df

    def fetch_diverse_collection(self, books_per_genre: int = 15) -> pd.DataFrame:
        """
        Fetch a diverse collection across multiple genres
        """
        print("[*] Fetching diverse book collection...")

        genres = [
            'fiction',
            'science fiction',
            'fantasy',
            'mystery',
            'thriller',
            'romance',
            'biography',
            'history'
        ]

        all_books = []

        for genre in genres:
            print(f"\n[*] Genre: {genre}")
            books = self.fetch_books_by_genre(genre, max_results=books_per_genre)

            if not books.empty:
                all_books.append(books)

            time.sleep(0.5)  # Be nice to API

        if all_books:
            combined = pd.concat(all_books, ignore_index=True)

            # Remove duplicates
            combined = combined.drop_duplicates(subset=['google_books_id'])

            print(f"\n[SUCCESS] Total unique books: {len(combined)}")
            return combined

        return pd.DataFrame()


# Test function
if __name__ == "__main__":
    service = GoogleBooksService()

    print("\n" + "="*60)
    print("Testing Google Books Service")
    print("="*60 + "\n")

    # Test: Fetch fiction books
    books = service.fetch_books_by_genre('fiction', max_results=20)

    print(f"\n[DATA] Preview:")
    print(f"Total books: {len(books)}")

    if not books.empty:
        print(f"\nFirst 3 books:")
        print(books[['title', 'authors', 'year', 'average_rating', 'categories']].head(3))
