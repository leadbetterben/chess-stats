# Chess Stats Analyzer

A modular Python package that analyzes chess games from Chess.com to provide statistics on opponents' countries.

## Overview

This tool fetches all your chess games from Chess.com, identifies your opponents, determines their countries, and aggregates statistics showing how many games you've played against players from each country.

## Features

- Fetches game archives from Chess.com API
- Tracks unique opponents and their countries
- Aggregates game counts by country
- Handles incremental updates (only processes new games)
- Parallel processing for efficient data fetching
- Stores processed data locally for quick re-runs
- Modular architecture with separate API client, caching, and processing components

## Project Structure

```text
chess-stats/
├── cli.py                     # Command-line argument parsing utilities
├── chess_api/                 # Core package
│   ├── __init__.py
│   ├── client.py              # Chess.com API client functions
│   ├── cache.py               # Data persistence utilities
│   └── processor.py           # Main game processing logic
├── report_country_stats.py        # Analyze games by opponent country
├── get_top_opponents.py       # Find most-played opponents
├── data/                      # Data storage (gitignored)
│   ├── archives.json
│   ├── processed_games.json
│   └── opponent_stats.json
└── README.md
```

## Requirements

- Python 3.6+
- `requests` library

Install dependencies:

```bash
pip install requests
```

## Available Scripts

### report_country_stats.py

Analyzes games by opponent country:

1. Fetches your game archives from Chess.com or stored data
2. Identifies all opponents and their countries
3. Displays aggregated statistics by country

Usage:

```bash
python report_country_stats.py <username>
```

Example:

```bash
python report_country_stats.py benleggy23
```

Output example:

```text
Unique opponents: 245

=== RESULTS ===

US: 89 (35.2%)
RU: 45 (17.8%)
DE: 23 (9.1%)
...
```

### get_top_opponents.py

Finds your most-played opponents:

1. Fetches your game archives from Chess.com or stored data
2. Identifies all opponents and games played against them
3. Displays top opponent(s) based on games played

Usage:

```bash
python get_top_opponents.py <username>
```

Example:

```bash
python get_top_opponents.py benleggy23
```

Output example:

```text
Unique opponents: 245
Most games against a single opponent: 12

Player123: 12 games (US)
Player456: 12 games (CA)
```

## Setup

1. Clone this repository
2. Edit any script and change the `USERNAME` variable to your Chess.com username
3. Run any of the scripts above

## Package Components

### chess_api.client

Contains functions for interacting with the Chess.com API:

- `fetch_archives(username)`: Get list of game archive URLs for a player
- `fetch_games(url)`: Fetch games from a specific archive URL
- `fetch_country(opponent)`: Get a player's country code

### chess_api.cache

Handles data persistence:

- `load_json(filename, default)`: Load JSON data from the data directory
- `save_json(filename, data)`: Save JSON data to the data directory

### chess_api.processor

Main processing logic:

- `get_report_country_stats_stats(username)`: Process all games and return opponent statistics
- `is_current_month(url)`: Check if an archive URL is for the current month

## Programmatic Usage

You can also import and use the package programmatically:

```python
from chess_api.processor import get_report_country_stats_stats
from collections import Counter

# Get opponent statistics
stats = get_report_country_stats_stats("your_username")

# Aggregate by country
country_counter = Counter()
for data in stats.values():
    country_counter[data["country"]] += data["games"]

# Print results
for country, count in country_counter.most_common():
    print(f"{country}: {count}")
```

## Data Files

The script creates and maintains several data files in the `data/` directory:

- `archives.json`: List of processed game archive URLs
- `processed_games.json`: List of individual game URLs that have been processed
- `opponent_stats.json`: Statistics for each opponent (country and game count)

Note: The `data/` directory is gitignored to avoid committing personal game data.

## API Rate Limits

The script respects Chess.com API rate limits and includes error handling for failed requests. It uses parallel processing with ThreadPoolExecutor to fetch data efficiently while staying within API limits.

## License

This project is open source. Feel free to modify and use as needed.
