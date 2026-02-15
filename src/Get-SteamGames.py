import requests
import json
import time
from datetime import datetime
from pathlib import Path
from config import access_token
from combine_reviews_to_jsonl import combine_reviews_to_jsonl
from convert_jsonl_to_csv import convert_jsonl_to_csv
from combine_game_player_data import combine_game_player_data
from word_frequency_by_game import extract_word_frequencies_by_game

# Get the directory containing this script and set base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
REVIEWS_DIR = DATA_DIR / 'reviews'


def load_last_timestamps(filename=None):
    """Load last known timestamps for each appid"""
    if filename is None:
        filename = DATA_DIR / 'last_timestamps.json'
    if filename.exists():
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_last_timestamps(timestamps, filename=None):
    """Save last known timestamps for each appid"""
    if filename is None:
        filename = DATA_DIR / 'last_timestamps.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(timestamps, f, indent=2, ensure_ascii=False)


def fetch_and_save_steam_apps(token, output_file=None):
    if output_file is None:
        output_file = DATA_DIR / 'steam_app_list.json'

    url = f"https://api.steampowered.com/IStoreService/GetAppList/v1/?access_token={token}"
    r = requests.get(url)
    games = r.json()

    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)

    print(f"Data saved to: {output_file}")
    print(f"Full path: {output_file.absolute()}")

    return games


def check_current_players(appid, token):
    url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}&access_token={token}"
    r = requests.get(url)
    data = r.json()
    return data.get('response', {}).get('player_count', 0)


def get_game_reviews(appid, token, max_reviews=6000, last_timestamp=None):
    """
    Fetch game reviews from Steam API

    Args:
        appid: Steam app ID
        token: Steam API access token
        max_reviews: Maximum number of reviews to fetch (default: 6000)
        last_timestamp: Only fetch reviews newer than this timestamp (optional)

    Returns:
        tuple: (reviews list, max timestamp from fetched reviews)
    """
    all_reviews = []
    cursor = '*'  # Steam uses cursor for pagination
    max_timestamp = last_timestamp or 0

    while len(all_reviews) < max_reviews:
        url = f"https://store.steampowered.com/appreviews/{appid}?json=1&cursor={cursor}&num_per_page=100&access_token={token}&filter=recent"
        r = requests.get(url)
        data = r.json()

        if not data.get('success') or not data.get('reviews'):
            break

        reviews = data.get('reviews', [])

        # Filter reviews newer than last_timestamp
        if last_timestamp:
            reviews = [r for r in reviews if r['timestamp_created']
                       > last_timestamp]
            if not reviews:  # No new reviews, stop fetching
                break

        all_reviews.extend(reviews)

        # Update max_timestamp
        if reviews:
            current_max = max(review['timestamp_created']
                              for review in reviews)
            max_timestamp = max(max_timestamp, current_max)

        # Get cursor for next page
        cursor = data.get('cursor', '')
        if not cursor or cursor == '*':
            break

        print(f"Fetched {len(all_reviews)} reviews for AppID {appid}...")

    # Return reviews and max timestamp
    return all_reviews[:max_reviews], max_timestamp


# games = fetch_and_save_steam_apps(access_token)    # Uncomment to fetch and save the app list
with open(DATA_DIR / 'steam_app_list.json', 'r', encoding='utf-8') as f:
    games = json.load(f).get('response', {}).get('apps', [])
print(f"Total games loaded: {len(games)}")

# Load last known timestamps
last_timestamps = load_last_timestamps()
new_timestamps = {}

game_player_data = []
reviews_data = []
# Get current timestamp once for all games
date_collected_timestamp = int(time.time())

for game in games:
    game_appid = game.get('appid')
    player_no = check_current_players(game_appid, access_token)

    game_info = {
        'appid': game_appid,
        'player_no': player_no,
        'Date_collected': date_collected_timestamp
    }
    game_player_data.append(game_info)

    # Fetch reviews for the game (only newer than last timestamp)
    last_ts = last_timestamps.get(str(game_appid), None)
    reviews, max_timestamp = get_game_reviews(
        game_appid, access_token, max_reviews=6000, last_timestamp=last_ts)

    # Store the new max timestamp
    new_timestamps[str(game_appid)] = max_timestamp

    reviews_data.append({
        'appid': game_appid,
        'reviews': reviews
    })
timestamp = datetime.now().strftime('%Y%m%d')
# Save all collected data to JSON file
with open(DATA_DIR / f'game_player_data_{timestamp}.json', 'w', encoding='utf-8') as f:
    json.dump(game_player_data, f, indent=2, ensure_ascii=False)


with open(REVIEWS_DIR / f'reviews_recent_data_{timestamp}.json', 'w', encoding='utf-8') as f:
    json.dump(reviews_data, f, indent=2, ensure_ascii=False)

# Save new timestamps for next run
save_last_timestamps(new_timestamps)

print(f"\nCollected data for {len(game_player_data)} games")
print(f"Collected reviews for {len(reviews_data)} games")
print(f"Timestamps saved to {DATA_DIR / 'last_timestamps.json'}")

# Combine reviews to JSONL
print("\n" + "="*50)
print("Combining reviews to JSONL...")
print("="*50)
combine_reviews_to_jsonl()

# Convert JSONL to CSV
print("\n" + "="*50)
print("Converting JSONL to CSV for Power BI...")
print("="*50)
convert_jsonl_to_csv()

# Combine game player data
print("\n" + "="*50)
print("Combining game player data...")
print("="*50)
combine_game_player_data(DATA_DIR, DATA_DIR / "game_player_data_combined.csv")

# Analyze word frequencies by game
print("\n" + "="*50)
print("Analyzing word frequencies by game...")
print("="*50)
input_csv = DATA_DIR / "reviews" / "PBI_review_ready" / "reviews_with_sentiment.csv"
output_csv = DATA_DIR / "reviews" / "PBI_review_ready" / "word_frequencies_by_game.csv"
extract_word_frequencies_by_game(str(input_csv), str(output_csv))
