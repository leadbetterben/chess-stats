from collections import Counter

from cli import get_username
from chess_api.processor import get_opponent_country_stats


def main(username):
    opponent_stats = get_opponent_country_stats(username)

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
    username = get_username()
    main(username)
