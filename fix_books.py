import os
from dotenv import load_dotenv
from app.services.books_service import GoogleBooksService
from app.database.db import SessionLocal
from app.database.crud import save_books_bulk

load_dotenv()

def fix_books():
    db = SessionLocal()
    # If you don't have a key, leave GOOGLE_BOOKS_API_KEY blank in .env
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")

    print("[*] Initializing Books Service...")
    books_service = GoogleBooksService(api_key)

    print("[*] Fetching 1000 books (this may take a minute)...")
    books_df = books_service.fetch_1k_books()

    if not books_df.empty:
        save_books_bulk(db, books_df)
        print(f"[SUCCESS] Uploaded {len(books_df)} books to Supabase.")
    else:
        print("[ERROR] No books were fetched. Check API limits or connection.")

    db.close()

if __name__ == "__main__":
    fix_books()
