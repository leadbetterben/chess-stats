from chess_api.processor import get_opponent_country_stats


USERNAME = "benleggy23"

def main():
    opponents = get_opponent_country_stats(USERNAME)

    print(f"\nUnique opponents: {len(opponents)}")

    # 1. Find the maximum number of games
    max_games = max(info["games"] for info in opponents.values())

    # 2. Filter opponents who match that max
    top_opponents = {
        user: info
        for user, info in opponents.items()
        if info["games"] == max_games
    }

    # 3. Print them
    print(f"Most games against a single opponent: {max_games}\n")

    for user, info in top_opponents.items():
        print(f"{user}: {info['games']} games ({info['country']})")


if __name__ == "__main__":
    main()