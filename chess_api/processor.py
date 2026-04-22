from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from chess_api.cache import load_json, save_json
from chess_api.client import fetch_archives, fetch_country, fetch_games

ARCHIVES_FILE = "archives.json"
GAMES_FILE = "processed_games.json"
STATS_FILE = "opponent_stats.json"

EXCLUDED_USERS = {"coach_levy"}

def get_opponent_country_stats(username):
    # Load existing data
    fetched_archives = load_json(ARCHIVES_FILE, [])
    processed_games = set(load_json(GAMES_FILE, []))
    opponent_stats = load_json(STATS_FILE, {})

    archives = fetch_archives(username)

     # Only process new archives (but always include current month)
    new_archives = [
        url for url in archives
        if url not in fetched_archives or is_current_month(url)
    ]

    # 🧩 Fetch games in parallel
    if new_archives:
        username = username.lower()
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_games, new_archives))
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

                        if opponent in EXCLUDED_USERS:
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
    
    # 🌍 Fetch missing countries
    opponents_to_fetch = [
        opp for opp, data in opponent_stats.items()
        if data["country"] == "Unknown" or data["games"] == 0
    ]

    if opponents_to_fetch:
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
        
    return opponent_stats


def is_current_month(url):
    parts = url.rstrip('/').split('/')
    year = int(parts[-2])
    month = int(parts[-1])
    now = datetime.now()
    return year == now.year and month == now.month
