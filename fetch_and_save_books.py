"""
Fetch books from Google Books API and save to database
"""
from app.services.books_service import GoogleBooksService
from app.database.db import SessionLocal
from app.database.crud import save_books_bulk, get_book_stats


def main():
    print("\n" + "="*60)
    print("FETCH AND SAVE BOOKS TO DATABASE")
    print("="*60 + "\n")

    # Initialize service (no API key needed)
    books_service = GoogleBooksService()

    # Fetch diverse collection
    print("[STEP 1] Fetching diverse book collection...\n")
    books_df = books_service.fetch_diverse_collection(books_per_genre=12)

    if books_df.empty:
        print("[ERROR] No books fetched!")
        return

    print(f"\n[INFO] Fetched {len(books_df)} unique books")
    print(f"[INFO] Year range: {books_df['year'].min():.0f} - {books_df['year'].max():.0f}")
    print(f"[INFO] Average rating: {books_df['average_rating'].mean():.2f}/5")

    # Save to database
    print(f"\n[STEP 2] Saving to database...\n")
    db = SessionLocal()

    try:
        saved_count = save_books_bulk(db, books_df)
        print(f"\n[SUCCESS] Saved {saved_count} books!")

        # Show stats
        print(f"\n[STEP 3] Database Statistics:\n")
        stats = get_book_stats(db)
        print(f"  Total books in DB: {stats['total_books']}")
        print(f"  Average rating: {stats['average_rating']}/5")

    except Exception as e:
        print(f"[ERROR] Failed to save books: {e}")
        db.rollback()
    finally:
        db.close()

    print("\n" + "="*60)
    print("[DONE] Process completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
