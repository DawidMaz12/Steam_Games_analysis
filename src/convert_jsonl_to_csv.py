import json
import csv
from pathlib import Path


def convert_jsonl_to_csv():
    """Convert the consolidated JSONL reviews file to a flattened CSV format."""

    # Define paths
    reviews_folder = Path(__file__).parent.parent / 'data' / 'reviews'
    input_file = reviews_folder / 'combined_reviews' / 'all_reviews.jsonl'
    output_file = reviews_folder / 'PBI_review_ready' / 'all_reviews.csv'

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return

    print(f"Reading from: {input_file}")

    # Define CSV columns
    fieldnames = [
        'appid',
        'recommendation_id',
        'author_steamid',
        'author_num_games_owned',
        'author_num_reviews',
        'author_playtime_forever',
        'author_playtime_last_two_weeks',
        'author_playtime_at_review',
        'author_last_played',
        'language',
        'review',
        'timestamp_created',
        'timestamp_updated',
        'voted_up',
        'votes_up',
        'votes_funny',
        'weighted_vote_score',
        'comment_count',
        'steam_purchase',
        'received_for_free',
        'written_during_early_access',
        'primarily_steam_deck'
    ]

    # Open output CSV file
    total_rows = 0
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Read each line from JSONL file
        with open(input_file, 'r', encoding='utf-8') as jsonfile:
            for line in jsonfile:
                game_data = json.loads(line.strip())
                appid = game_data['appid']

                # Flatten each review into a CSV row
                if 'reviews' in game_data:
                    for review in game_data['reviews']:
                        row = {
                            'appid': appid,
                            'recommendation_id': review.get('recommendationid', ''),
                            'author_steamid': review.get('author', {}).get('steamid', ''),
                            'author_num_games_owned': review.get('author', {}).get('num_games_owned', ''),
                            'author_num_reviews': review.get('author', {}).get('num_reviews', ''),
                            'author_playtime_forever': review.get('author', {}).get('playtime_forever', ''),
                            'author_playtime_last_two_weeks': review.get('author', {}).get('playtime_last_two_weeks', ''),
                            'author_playtime_at_review': review.get('author', {}).get('playtime_at_review', ''),
                            'author_last_played': review.get('author', {}).get('last_played', ''),
                            'language': review.get('language', ''),
                            'review': review.get('review', ''),
                            'timestamp_created': review.get('timestamp_created', ''),
                            'timestamp_updated': review.get('timestamp_updated', ''),
                            'voted_up': review.get('voted_up', ''),
                            'votes_up': review.get('votes_up', ''),
                            'votes_funny': review.get('votes_funny', ''),
                            'weighted_vote_score': review.get('weighted_vote_score', ''),
                            'comment_count': review.get('comment_count', ''),
                            'steam_purchase': review.get('steam_purchase', ''),
                            'received_for_free': review.get('received_for_free', ''),
                            'written_during_early_access': review.get('written_during_early_access', ''),
                            'primarily_steam_deck': review.get('primarily_steam_deck', '')
                        }
                        writer.writerow(row)
                        total_rows += 1

    print(f"\n✓ Successfully created {output_file}")
    print(f"  Total rows: {total_rows:,}")
    print(f"  File size: {output_file.stat().st_size / (1024*1024):.2f} MB")


if __name__ == "__main__":
    convert_jsonl_to_csv()
