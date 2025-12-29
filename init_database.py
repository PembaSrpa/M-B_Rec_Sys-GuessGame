from app.database.db import init_db, engine
from sqlalchemy import text

if __name__ == "__main__":
    print("🚀 Initializing database...")

    # Test connection first
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        exit(1)

    # Create tables
    init_db()

    print("\n📊 Database schema created successfully!")
    print("\nTables created:")
    print("  - movies")
    print("  - books")
    print("  - characters")
    print("  - game_sessions")
