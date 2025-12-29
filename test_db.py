from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Attempting to connect to: {DATABASE_URL}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)

    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"PostgreSQL version: {version[0]}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
