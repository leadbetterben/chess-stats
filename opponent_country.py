import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import datetime

USERNAME = "benleggy23"

HEADERS = {
    "User-Agent": "chess-country-stats/1.0"
}
session = requests.Session()
session.headers.update(HEADERS)

BASE_URL = "https://api.chess.com/pub"

DATA_DIR = "data"
ARCHIVES_FILE = f"{DATA_DIR}/archives.json"
GAMES_FILE = f"{DATA_DIR}/processed_games.json"
STATS_FILE = f"{DATA_DIR}/opponent_stats.json"

def fetch_games(url):
    print(f"Fetching games: {url}")
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("games", [])
    except Exception as e:
        print(f"Error: exception fetching games from {url}: {e}")
        return []
    print(f"Error: failed to fetch games from {url}")
    return []


def fetch_country(opponent):
    try:
        r = session.get(f"{BASE_URL}/player/{opponent}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            country_url = data.get("country")
            if country_url:
                return country_url.split("/")[-1]
    except Exception as e:
        print(f"Error: exception fetching country for {opponent}: {e}")
    print(f"Error: failed to fetch country for {opponent}")
    return "Unknown"


def is_current_month(url):
    parts = url.rstrip('/').split('/')
    year = int(parts[-2])
    month = int(parts[-1])
    now = datetime.datetime.now()
    return year == now.year and month == now.month


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    # Load existing data
    fetched_archives = load_json(ARCHIVES_FILE, [])
    processed_games = set(load_json(GAMES_FILE, []))
    opponent_stats = load_json(STATS_FILE, {})

    # Fetch archive list
    r = session.get(f"{BASE_URL}/player/{USERNAME}/games/archives")
    archives = r.json().get("archives", [])

    # Only process new archives (but always include current month)
    new_archives = [
        url for url in archives
        if url not in fetched_archives or is_current_month(url)
    ]

    # 🧩 Fetch games in parallel
    if new_archives:
        print(f"Processing {len(new_archives)} archives...\n")

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_games, new_archives))

        username = USERNAME.lower()
        for archive_games in results:
            for game in archive_games:
                for side in ("white", "black"):
                    player = game.get(side)
                    if not player:
                        continue

                    opponent = player.get("username")
                    if not opponent:
                        continue

                    opponent = opponent.lower()
                    if opponent == username:
                        continue

                    if opponent not in opponent_stats:
                        opponent_stats[opponent] = {
                            "country": "Unknown",
                            "games": 0
                        }

                    game_id = game.get("url")

                    if game_id in processed_games:
                        continue

                    processed_games.add(game_id)

                    opponent_stats[opponent]["games"] += 1

        # Save processed archives (exclude current month)
        fetched_archives.extend([
            url for url in new_archives if not is_current_month(url)
        ])

        save_json(ARCHIVES_FILE, fetched_archives)
        save_json(GAMES_FILE, list(processed_games))
        save_json(STATS_FILE, opponent_stats)

    print(f"\nUnique opponents: {len(opponent_stats)}")

    # 🌍 Fetch missing countries
    opponents_to_fetch = [
        opp for opp, data in opponent_stats.items()
        if data["country"] == "Unknown"
    ]

    if opponents_to_fetch:
        print(f"Fetching countries for {len(opponents_to_fetch)} opponents...\n")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(fetch_country, opp): opp
                for opp in opponents_to_fetch
            }

            for future in as_completed(futures):
                opp = futures[future]
                country = future.result()
                opponent_stats[opp]["country"] = country

        save_json(STATS_FILE, opponent_stats)

    # 📊 Aggregate results
    country_counter = Counter()

    for data in opponent_stats.values():
        country_counter[data["country"]] += data["games"]

    total_games = sum(country_counter.values())

    print("\n=== RESULTS ===\n")
    for country, count in country_counter.most_common():
        pct = (count / total_games) * 100 if total_games else 0
        print(f"{country}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
