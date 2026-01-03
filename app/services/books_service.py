import requests
import pandas as pd
from typing import List, Dict, Optional
import time

class GoogleBooksService:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: Optional[str] = None):
        # Filter out the string "optional" or empty values
        if api_key and str(api_key).lower() in ["optional", "none", ""]:
            self.api_key = None
        else:
            self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, params: Dict) -> Dict:
        # Only add the key parameter if we actually have a valid key
        if self.api_key:
            params['key'] = self.api_key

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)

            # Print specific error message if Google rejects the request
            if response.status_code != 200:
                print(f"Google API Error: {response.status_code} - {response.text}")
                return None

            return response.json()
        except Exception as e:
            print(f"Request Error: {e}")
            return None

    def fetch_books_by_genre(self, genre: str, max_results: int = 40) -> pd.DataFrame:
        all_books = []
        start_index = 0
        while len(all_books) < max_results:
            params = {
                'q': f'subject:{genre}',
                'maxResults': min(40, max_results - len(all_books)),
                'startIndex': start_index,
                'printType': 'books',
                'langRestrict': 'en'
            }
            data = self._make_request(params)

            if not data or 'items' not in data:
                break

            all_books.extend(data['items'])
            start_index += 40

            # Small delay to avoid hitting rate limits
            time.sleep(0.5)

        return self._process_book_data(all_books)

    def fetch_1k_books(self):
        keywords = ["fiction", "mystery", "thriller", "history", "science", "fantasy", "biography", "crime", "romance", "art"]
        all_dfs = []

        print(f"[*] Starting fetch for {len(keywords)} genres...")

        for kw in keywords:
            print(f"  > Fetching {kw}...")
            df = self.fetch_books_by_genre(kw, max_results=100)
            if not df.empty:
                all_dfs.append(df)

        if not all_dfs:
            return pd.DataFrame()

        return pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=['google_books_id'])

    def _process_book_data(self, books: List[Dict]) -> pd.DataFrame:
        processed = []
        for book in books:
            vol = book.get('volumeInfo', {})
            date = vol.get('publishedDate', '')

            # Extract year safely
            year = None
            if date and len(date) >= 4:
                year_str = date[:4]
                if year_str.isdigit():
                    year = int(year_str)

            processed.append({
                'google_books_id': book.get('id'),
                'title': vol.get('title', 'Unknown'),
                'authors': vol.get('authors', []),
                'description': vol.get('description', ''),
                'categories': vol.get('categories', []),
                'published_date': date,
                'year': year,
                'decade': (year // 10) * 10 if year else None,
                'page_count': vol.get('page_count', 0),
                'average_rating': vol.get('average_rating', 0),
                'ratings_count': vol.get('ratings_count', 0),
                'thumbnail': vol.get('imageLinks', {}).get('thumbnail', ''),
                'language': vol.get('language', 'en'),
                'publisher': vol.get('publisher', '')
            })
        return pd.DataFrame(processed)
