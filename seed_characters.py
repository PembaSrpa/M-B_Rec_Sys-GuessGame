import json
from app.database.db import SessionLocal
from app.database.models import Character
from datetime import datetime


def seed_characters():
    print("[*] Loading characters from JSON...")

    with open('data/characters_seed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    characters = data['characters']
    print(f"[*] Found {len(characters)} characters to seed")

    db = SessionLocal()

    try:
        added = 0
        updated = 0

        for char_data in characters:
            # Check if character already exists
            existing = db.query(Character).filter(
                Character.name == char_data['name']
            ).first()

            if existing:
                # Update existing
                existing.type = char_data['type']
                existing.alignment = char_data.get('alignment')
                existing.traits = char_data.get('traits', [])
                existing.genres = char_data.get('genres', [])
                existing.popularity_score = char_data.get('popularity_score')
                existing.source = char_data.get('source')
                existing.additional_info = {
                    'gender': char_data.get('gender')
                }
                updated += 1
            else:
                # Create new
                character = Character(
                    name=char_data['name'],
                    type=char_data['type'],
                    alignment=char_data.get('alignment'),
                    traits=char_data.get('traits', []),
                    genres=char_data.get('genres', []),
                    popularity_score=char_data.get('popularity_score'),
                    source=char_data.get('source'),
                    additional_info={
                        'gender': char_data.get('gender')
                    }
                )
                db.add(character)
                added += 1

        db.commit()

        print(f"[SUCCESS] Added: {added}, Updated: {updated}")
        print(f"[SUCCESS] Total characters in database: {added + updated}")

    except Exception as e:
        print(f"[ERROR] Failed to seed characters: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_characters()
