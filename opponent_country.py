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

BASE_URL = "https://api.chess.com/pub"

OPPONENTS_FILE = "data/opponents.json"
COUNTRIES_FILE = "data/countries.json"
ARCHIVES_FILE = "data/archives.json"

def is_current_month(url):
    parts = url.rstrip('/').split('/')
    year = int(parts[-2])
    month = int(parts[-1])
    now = datetime.datetime.now()
    return year == now.year and month == now.month

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
    archives = get_archives()
    fetched_archives = []
    if os.path.exists(ARCHIVES_FILE):
        with open(ARCHIVES_FILE, 'r') as f:
            fetched_archives = json.load(f)
    
    new_archives = [url for url in archives if url not in fetched_archives]
    
    opponents = set()
    if os.path.exists(OPPONENTS_FILE):
        with open(OPPONENTS_FILE, 'r') as f:
            opponents = set(json.load(f))
    
    if new_archives:
        new_opponents = extract_opponents(new_archives)
        opponents.update(new_opponents)
        fetched_archives.extend([url for url in new_archives if not is_current_month(url)])
        
        os.makedirs(os.path.dirname(OPPONENTS_FILE), exist_ok=True)
        with open(OPPONENTS_FILE, 'w') as f:
            json.dump(list(opponents), f)
        with open(ARCHIVES_FILE, 'w') as f:
            json.dump(fetched_archives, f)

    print(f"\nUnique opponents: {len(opponents)}")

    countries = {}
    if os.path.exists(COUNTRIES_FILE):
        with open(COUNTRIES_FILE, 'r') as f:
            countries = json.load(f)

    # Find opponents without country
    opponents_to_fetch = [opp for opp in opponents if opp not in countries]
    
    if opponents_to_fetch:
        print(f"Fetching countries for {len(opponents_to_fetch)} new opponents")
        # 🔥 Parallel requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_country, opp): opp for opp in opponents_to_fetch}

            for future in as_completed(futures):
                opp = futures[future]
                country = future.result()
                countries[opp] = country

        with open(COUNTRIES_FILE, 'w') as f:
            json.dump(countries, f)

    country_counter = Counter(countries.values())

    print("\n=== RESULTS ===\n")
    for country, count in country_counter.most_common():
        print(f"{country}: {count}")

if __name__ == "__main__":
    main()
