from collections import Counter
from pandas import DataFrame
from plotly.express import choropleth
import pycountry

from cli import get_username
from chess_api.processor import get_opponent_country_stats

def to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

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

    # 🌍 MAP VISUALISATION
    df = DataFrame(
        country_counter.items(),
        columns=["country_code", "games"]
    )
    df["country_code"] = df["country_code"].apply(to_iso3)
    df = df.dropna()

    fig = choropleth(
        df,
        locations="country_code",
        color="games",
        color_continuous_scale="Blues",
        title="Games Played by Country",
    )

    fig.show()

if __name__ == "__main__":
    username = get_username()
    main(username)
