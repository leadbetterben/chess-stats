import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os

USERNAME = "benleggy23"

HEADERS = {
    "User-Agent": "chess-country-stats/1.0"
}

BASE_URL = "https://api.chess.com/pub"

OPPONENTS_FILE = "data/opponents.json"
COUNTRIES_FILE = "data/countries.json"

def get_archives():
    r = requests.get(f"{BASE_URL}/player/{USERNAME}/games/archives", headers=HEADERS)
    return r.json().get("archives", [])

def get_games(url):
    r = requests.get(url, headers=HEADERS)
    return r.json().get("games", [])

def extract_opponents(archives):
    opponents = set()

    for archive_url in archives:
        print(f"Fetching games: {archive_url}")
        games = get_games(archive_url)

        for game in games:
            for side in ["white", "black"]:
                player = game.get(side)
                if player:
                    username = player.get("username")
                    if username and username.lower() != USERNAME.lower():
                        opponents.add(username)

    return opponents

def fetch_country(opponent):
    try:
        r = requests.get(f"{BASE_URL}/player/{opponent}", headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return "Unknown"

        data = r.json()
        country_url = data.get("country")

        if country_url:
            return country_url.split("/")[-1]

    except:
        return "Unknown"

    return "Unknown"

def main():
    if os.path.exists(OPPONENTS_FILE):
        with open(OPPONENTS_FILE, 'r') as f:
            opponents = set(json.load(f))
    else:
        archives = get_archives()
        opponents = extract_opponents(archives)
        with open(OPPONENTS_FILE, 'w') as f:
            json.dump(list(opponents), f)

    print(f"\nUnique opponents: {len(opponents)}")

    if os.path.exists(COUNTRIES_FILE):
        with open(COUNTRIES_FILE, 'r') as f:
            country_data = json.load(f)
        country_counter = Counter(country_data)
    else:
        country_counter = Counter()
        # 🔥 Parallel requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_country, opp): opp for opp in opponents}

            for future in as_completed(futures):
                country = future.result()
                country_counter[country] += 1

        with open(COUNTRIES_FILE, 'w') as f:
            json.dump(dict(country_counter), f)

    print("\n=== RESULTS ===\n")
    for country, count in country_counter.most_common():
        print(f"{country}: {count}")

if __name__ == "__main__":
    main()
