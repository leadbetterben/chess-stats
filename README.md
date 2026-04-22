# Chess Stats Analyzer

A Python script that analyzes chess games from Chess.com to provide statistics on opponents' countries.

## Overview

This tool fetches all your chess games from Chess.com, identifies your opponents, determines their countries, and aggregates statistics showing how many games you've played against players from each country.

## Features

- Fetches game archives from Chess.com API
- Tracks unique opponents and their countries
- Aggregates game counts by country
- Handles incremental updates (only processes new games)
- Parallel processing for efficient data fetching
- Stores processed data locally for quick re-runs

## Requirements

- Python 3.6+
- `requests` library

Install dependencies:

```bash
pip install requests
```

## Usage

1. Clone this repository
2. Edit `opponent_country.py` and change the `USERNAME` variable to your Chess.com username
3. Run the script:

```bash
python opponent_country.py
```

The script will:

- Fetch your game archives from Chess.com
- Process new games and identify opponents
- Look up countries for new opponents
- Display aggregated statistics by country

## Data Files

The script creates and maintains several data files in the `data/` directory:

- `archives.json`: List of processed game archive URLs
- `processed_games.json`: List of individual game URLs that have been processed
- `opponent_stats.json`: Statistics for each opponent (country and game count)

Note: The `data/` directory is gitignored to avoid committing personal game data.

## Output Example

```text
Unique opponents: 245

=== RESULTS ===

US: 89 (35.2%)
RU: 45 (17.8%)
DE: 23 (9.1%)
...
```

## API Rate Limits

The script respects Chess.com API rate limits and includes error handling for failed requests. It uses parallel processing with ThreadPoolExecutor to fetch data efficiently while staying within API limits.

## License

This project is open source. Feel free to modify and use as needed.
