import requests

HEADERS = {
    "User-Agent": "chess-country-stats/1.0"
}
session = requests.Session()
session.headers.update(HEADERS)

BASE_URL = "https://api.chess.com/pub"

def fetch_archives(username):
    r = session.get(f"{BASE_URL}/player/{username}/games/archives")
    return r.json().get("archives", [])


def fetch_games(url):
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("games", [])
    except:
        return []
    return []


def fetch_country(opponent):
    try:
        r = session.get(f"{BASE_URL}/player/{opponent}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            country_url = data.get("country")
            if country_url:
                return country_url.split("/")[-1]
    except:
        return "Unknown"
    return "Unknown"