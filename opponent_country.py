from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from chess_api.cache import save_json
from chess_api.client import fetch_country, fetch_games
from chess_api.processor import get_opponent_country_stats

USERNAME = "benleggy23"

def main():
    opponent_stats = get_opponent_country_stats(USERNAME)

    print(f"\nUnique opponents: {len(opponent_stats)}")

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
