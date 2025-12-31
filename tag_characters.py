"""
Interactive tool to tag characters with game attributes
"""
import json
import os


def load_raw_data():
    """Load raw actor and anime character data"""
    actors = []
    anime_chars = []

    if os.path.exists('data/actors_raw.json'):
        with open('data/actors_raw.json', 'r', encoding='utf-8') as f:
            actors = json.load(f)

    if os.path.exists('data/anime_characters_raw.json'):
        with open('data/anime_characters_raw.json', 'r', encoding='utf-8') as f:
            anime_chars = json.load(f)

    return actors, anime_chars


def tag_character_interactive(character, char_type):
    """
    Interactively tag a single character
    """
    print("\n" + "="*60)
    if char_type == 'actor':
        print(f"TAGGING: {character['name']}")
        print(f"Known for: {', '.join(character.get('known_for', []))}")
        print(f"Genres: {', '.join(character.get('genres', []))}")
    else:
        print(f"TAGGING: {character['name']}")
        print(f"From: {character.get('anime', 'Unknown')}")
    print("="*60)

    # Gender
    print("\nGender?")
    print("1. male")
    print("2. female")
    gender = input("Choice (1/2): ").strip()
    gender = 'male' if gender == '1' else 'female'

    # Traits (for anime) or actor traits
    print("\nSelect traits (comma-separated numbers):")
    trait_options = [
        'funny', 'serious', 'determined', 'intelligent',
        'mysterious', 'strong', 'charismatic', 'witty',
        'skilled', 'intense', 'pure_hearted', 'loyal'
    ]
    for i, trait in enumerate(trait_options, 1):
        print(f"{i}. {trait}")

    trait_input = input("Traits: ").strip()
    trait_indices = [int(x.strip()) - 1 for x in trait_input.split(',') if x.strip().isdigit()]
    traits = [trait_options[i] for i in trait_indices if 0 <= i < len(trait_options)]

    # Alignment (for anime only)
    alignment = None
    if char_type == 'anime':
        print("\nAlignment?")
        print("1. hero")
        print("2. villain")
        print("3. anti-hero")
        align_choice = input("Choice (1/2/3): ").strip()
        alignment = {'1': 'hero', '2': 'villain', '3': 'anti-hero'}.get(align_choice, 'hero')

    # Popularity score
    if char_type == 'actor':
        # Use TMDB popularity, normalize to 0-100
        raw_pop = character.get('popularity', 50)
        popularity_score = min(100, int((raw_pop / 300) * 100))
    else:
        # Use MAL favorites, normalize to 0-100
        raw_fav = character.get('favorites', 1000)
        popularity_score = min(100, int((raw_fav / 150000) * 100))

    print(f"\nAuto-calculated popularity: {popularity_score}")
    manual_pop = input("Override? (press Enter to keep, or enter 0-100): ").strip()
    if manual_pop.isdigit():
        popularity_score = int(manual_pop)

    # Build tagged character
    tagged = {
        'name': character['name'],
        'type': char_type,
        'alignment': alignment,
        'traits': traits,
        'genres': character.get('genres', [])[:3],  # Max 3 genres
        'popularity_score': popularity_score,
        'gender': gender
    }

    if char_type == 'actor':
        tagged['source'] = ', '.join(character.get('known_for', [])[:2])
        tagged['image_url'] = f"https://image.tmdb.org/t/p/w185{character.get('profile_path')}" if character.get('profile_path') else None
    else:
        tagged['source'] = character.get('anime', 'Unknown')
        tagged['image_url'] = character.get('image_url')

    return tagged


def quick_tag_mode():
    """
    Quick tagging with presets for common characters
    """
    actors, anime_chars = load_raw_data()

    print("\n" + "="*60)
    print("QUICK TAG MODE - Top 30 Characters")
    print("="*60)
    print("\nI'll show you characters. Tag the ones you recognize.")
    print("Type 'skip' to skip a character")
    print("Type 'done' to finish\n")

    tagged_characters = []

    # Mix actors and anime (top 15 each)
    characters_to_tag = []

    for actor in actors[:15]:
        characters_to_tag.append(('actor', actor))

    for char in anime_chars[:15]:
        characters_to_tag.append(('anime', char))

    for char_type, character in characters_to_tag:
        print(f"\n[{len(tagged_characters) + 1}/30] {character['name']}")

        if char_type == 'actor':
            print(f"  Known for: {', '.join(character.get('known_for', []))}")
        else:
            print(f"  From: {character.get('anime', 'Unknown')}")

        action = input("Tag this character? (y/skip/done): ").strip().lower()

        if action == 'done':
            break
        elif action == 'skip' or action == 'n':
            continue

        # Tag this character
        tagged = tag_character_interactive(character, char_type)
        tagged_characters.append(tagged)

        print(f"\n[SUCCESS] Tagged! Total: {len(tagged_characters)}")

    # Save tagged characters
    output_file = 'data/characters_tagged.json'

    # Load existing if any
    existing = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing = data.get('characters', [])

    # Merge (avoid duplicates)
    existing_names = {char['name'] for char in existing}
    for tagged in tagged_characters:
        if tagged['name'] not in existing_names:
            existing.append(tagged)

    # Assign IDs
    for i, char in enumerate(existing, 1):
        char['id'] = i

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'characters': existing}, f, indent=2, ensure_ascii=False)

    print("\n" + "="*60)
    print(f"[SUCCESS] Saved {len(existing)} total characters to {output_file}")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("CHARACTER TAGGING TOOL")
    print("="*60)
    print("\nThis tool helps you tag characters with game attributes.")
    print("We'll go through the top actors and anime characters.\n")

    input("Press Enter to start...")

    quick_tag_mode()
