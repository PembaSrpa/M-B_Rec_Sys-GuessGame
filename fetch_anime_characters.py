import requests
import json
import time

def fetch_top_anime_characters(limit: int = 1000):
    print("\n" + "="*60)
    print(f"FETCHING {limit} ANIME CHARACTERS FROM JIKAN API")
    print("="*60 + "\n")

    base_url = "https://api.jikan.moe/v4/characters"
    all_characters = []
    page = 1

    while len(all_characters) < limit:
        print(f"[*] Fetching page {page}...")
        try:
            response = requests.get(
                base_url,
                params={
                    'page': page,
                    'order_by': 'favorites',
                    'sort': 'desc',
                    'limit': 25
                },
                timeout=15
            )

            if response.status_code == 429:
                print("[!] Rate limited. Sleeping for 5 seconds...")
                time.sleep(5)
                continue

            if response.status_code != 200:
                print(f"[ERROR] API returned status {response.status_code}")
                break

            data = response.json()
            if 'data' not in data or not data['data']:
                break

            all_characters.extend(data['data'])
            print(f"  Got {len(data['data'])} characters (Total: {len(all_characters)})")

            page += 1
            time.sleep(1.5)

        except Exception as e:
            print(f"[ERROR] Failed to fetch: {e}")
            break

    processed_characters = []
    for char in all_characters[:limit]:
        anime_list = char.get('anime', [])
        anime_name = anime_list[0]['anime']['title'] if anime_list else 'Unknown'

        processed_characters.append({
            'mal_id': char.get('mal_id'),
            'name': char.get('name'),
            'name_kanji': char.get('name_kanji'),
            'favorites': char.get('favorites', 0),
            'image_url': char.get('images', {}).get('jpg', {}).get('image_url'),
            'anime': anime_name,
            'url': char.get('url')
        })

    output_file = 'data/anime_characters_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_characters, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Saved {len(processed_characters)} characters to {output_file}")

if __name__ == "__main__":
    fetch_top_anime_characters(limit=1000)
