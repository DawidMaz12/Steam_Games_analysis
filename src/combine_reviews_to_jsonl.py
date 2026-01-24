import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def combine_reviews_to_jsonl():
    """Extend all_reviews.jsonl with only today's review data, consolidating by appid."""

    # Define paths
    reviews_folder = Path(__file__).parent.parent / 'data' / 'reviews'
    output_file = reviews_folder / 'combined_reviews' / 'all_reviews.jsonl'

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Get today's date in the format used by the review files
    today = datetime.now().strftime('%Y%m%d')
    today_file = reviews_folder / f'reviews_recent_data_{today}.json'

    # Check if today's file exists
    if not today_file.exists():
        print(f"❌ No review file found for today ({today})")
        print(f"   Expected: {today_file}")
        return

    print(f"Found today's review file: {today_file.name}")

    # Dictionary to store consolidated reviews by appid
    consolidated_data = defaultdict(lambda: {'appid': None, 'reviews': []})

    # Load existing data if the output file exists
    if output_file.exists():
        print(f"\nLoading existing data from {output_file.name}...")
        with open(output_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                game_data = json.loads(line.strip())
                appid = game_data['appid']
                consolidated_data[appid] = game_data

        print(f"  Loaded {len(consolidated_data)} existing appids")
        existing_review_count = sum(
            len(data['reviews']) for data in consolidated_data.values())
        print(f"  Existing reviews: {existing_review_count}")
    else:
        print("\nNo existing data file found. Creating new one...")

    # Process today's review file
    print(f"\nProcessing {today_file.name}...")
    new_reviews_added = 0

    # Load the JSON file
    with open(today_file, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    # Consolidate reviews by appid
    for game_data in data:
        appid = game_data['appid']

        # Initialize appid if not set
        if consolidated_data[appid]['appid'] is None:
            consolidated_data[appid]['appid'] = appid

        # Add all reviews from today's entry
        if 'reviews' in game_data:
            consolidated_data[appid]['reviews'].extend(game_data['reviews'])
            new_reviews_added += len(game_data['reviews'])

    print(f"  Processed {len(data)} game entries")
    print(f"  Added {new_reviews_added} new reviews")

    print(f"\nConsolidating {len(consolidated_data)} unique appids...")

    # Write consolidated data to JSONL file
    total_reviews = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for appid in sorted(consolidated_data.keys()):
            game_data = consolidated_data[appid]
            num_reviews = len(game_data['reviews'])
            total_reviews += num_reviews

            # Write as single JSON line
            json.dump(game_data, outfile, ensure_ascii=False)
            outfile.write('\n')

    print(f"\n✓ Successfully created {output_file}")
    print(f"  Unique appids: {len(consolidated_data)}")
    print(f"  Total reviews: {total_reviews}")
    print(f"  File size: {output_file.stat().st_size / (1024*1024):.2f} MB")

    # Show sample statistics
    review_counts = [len(data['reviews'])
                     for data in consolidated_data.values()]
    print(f"\nReview statistics:")
    print(f"  Min reviews per game: {min(review_counts)}")
    print(f"  Max reviews per game: {max(review_counts)}")
    print(
        f"  Avg reviews per game: {sum(review_counts) / len(review_counts):.1f}")


if __name__ == "__main__":
    combine_reviews_to_jsonl()
