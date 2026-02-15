# Steam Games Analysis

Comprehensive Steam game data collection and sentiment analysis pipeline for Power BI visualization.

## Overview

This project fetches Steam game data (player counts and reviews), performs sentiment analysis on reviews, and prepares the data for visualization in Power BI. It includes automated data processing, word frequency analysis, and incremental data collection with timestamp tracking.

## Features

- **Automated Data Collection**: Fetches current player counts and reviews from Steam API
- **Incremental Updates**: Only fetches new reviews since last run using timestamp tracking
- **Sentiment Analysis**: Analyzes review sentiment using VADER
- **Word Frequency Analysis**: Extracts word frequencies by game for word cloud visualization
- **Data Pipeline**: Automatic data processing and consolidation
- **Power BI Ready**: Outputs CSV files optimized for Power BI

## Project Structure

```
Steam_Games_analysis/
├── data/
│   ├── steam_app_list.json                    # Complete Steam app catalog
│   ├── last_timestamps.json                   # Timestamp tracking for incremental updates
│   ├── game_player_data_YYYYMMDD.json        # Daily player count snapshots
│   ├── game_player_data_combined.csv         # Combined historical player data
│   └── reviews/
│       ├── reviews_recent_data_YYYYMMDD.json # Daily review snapshots
│       ├── combined_reviews/
│       │   └── all_reviews.jsonl             # All reviews in JSONL format
│       └── PBI_review_ready/
│           ├── all_reviews.csv               # Reviews for Power BI
│           ├── reviews_with_sentiment.csv    # Reviews with sentiment scores
│           └── word_frequencies_by_game.csv  # Word frequencies for word cloud
├── src/
│   ├── Get-SteamGames.py                     # Main orchestration script
│   ├── config.py                             # API configuration
│   ├── combine_game_player_data.py           # Consolidate player data
│   ├── combine_reviews_to_jsonl.py           # Combine reviews to JSONL
│   ├── convert_jsonl_to_csv.py               # Convert JSONL to CSV
│   ├── sentiment_analysis_vader.py           # VADER sentiment analysis
│   ├── word_frequency_analysis.py            # Overall word frequency
│   └── word_frequency_by_game.py             # Per-game word frequency
└── README.md
```

## Installation

1. **Clone the repository**
   ```bash
   cd Steam_Games_analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install requests pandas nltk tqdm vaderSentiment
   ```

5. **Download NLTK data**
   The script will automatically download required NLTK data on first run.

## Configuration

1. Create `src/config.py` with your Steam API access token:
   ```python
   access_token = "your_steam_api_token_here"
   ```

2. 
    - Get your Steam API key from: https://steamcommunity.com/dev/apikey
    - Generate your Steam API access token from: https://steamapi.xpaw.me

## Usage

Run the complete data pipeline:
```bash
python src/Get-SteamGames.py
```

This script will:
1. Load the Steam app list
2. Fetch current player counts for all games
3. Fetch new reviews (only since last run)
4. Save timestamped data files
5. Combine all reviews into JSONL format
6. Convert to CSV for Power BI
7. Perform sentiment analysis
8. Analyze word frequencies by game
9. Combine all player count data

### Individual Scripts

You can also run individual processing scripts:

```bash
# Combine player data
python src/combine_game_player_data.py

# Combine reviews
python src/combine_reviews_to_jsonl.py

# Convert to CSV
python src/convert_jsonl_to_csv.py

# Run sentiment analysis
python src/sentiment_analysis_vader.py

# Analyze word frequencies
python src/word_frequency_by_game.py
```

## Output Files

### For Power BI Import

- `data/game_player_data_combined.csv` - Historical player counts with timestamps
- `data/reviews/PBI_review_ready/reviews_with_sentiment.csv` - Reviews with sentiment analysis
- `data/reviews/PBI_review_ready/word_frequencies_by_game.csv` - Word frequencies for word cloud

### Data Format

**game_player_data_combined.csv**:
- `appid`: Steam App ID
- `player_no`: Current player count
- `Date_collected`: Unix timestamp
- `Date_readable`: Human-readable date

**reviews_with_sentiment.csv**:
- `appid`: Steam App ID
- `review`: Review text
- `sentiment_compound`: VADER compound score (-1 to 1)
- `sentiment_positive`, `sentiment_neutral`, `sentiment_negative`: Individual scores
- `sentiment_label`: Overall sentiment (positive/neutral/negative)

**word_frequencies_by_game.csv**:
- `appid`: Steam App ID
- `word`: Extracted word
- `frequency`: Number of occurrences
- `avg_sentiment_compound`: Average sentiment for reviews containing this word
- `dominant_sentiment`: Most common sentiment for this word

## Features Details

### Incremental Data Collection

The system tracks the last review timestamp for each game in `last_timestamps.json`. On subsequent runs, only new reviews are fetched, making the process efficient.

### Sentiment Analysis

Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) for sentiment analysis, which is optimized for social media text and short reviews.

### Word Frequency Analysis

- Filters out stop words (common English words + gaming-specific terms)
- Minimum word length: 3 characters
- Minimum frequency: 3 occurrences per game
- Tracks sentiment association with each word

## Dependencies

- `requests` - API calls
- `pandas` - Data processing
- `nltk` - Natural language processing
- `tqdm` - Progress bars
- `vaderSentiment` - Sentiment analysis

## Notes

- The script fetches up to 6,000 reviews per game
- Data files are timestamped by date (YYYYMMDD format)
- All CSV files use UTF-8-BOM encoding for Excel compatibility
- The pipeline can take considerable time depending on the number of games
