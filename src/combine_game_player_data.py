"""
Combine Game Player Data with Timestamps
Combines multiple game_player_data_YYYYMMDD.json files into a single CSV file,
with each row representing a player count datapoint for a game.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def combine_game_player_data(data_dir: Path, output_file: Path):
    """
    Combine all timestamped game_player_data files into one CSV, grouped by appid.

    Args:
        data_dir: Directory containing the game_player_data_*.json files
        output_file: Path to the output combined CSV file
    """
    # Find all timestamped game player data files
    pattern = "game_player_data_*.json"
    json_files = sorted(data_dir.glob(pattern))

    # Filter out the main file (without timestamp)
    json_files = [f for f in json_files if f.name != "game_player_data.json"]

    if not json_files:
        print("No timestamped game_player_data files found!")
        return

    print(f"Found {len(json_files)} files to combine:")
    for file in json_files:
        print(f"  - {file.name}")

    # List to store all records
    all_records: List[Dict[str, Any]] = []

    # Process each file
    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"  Records: {len(data)}")

            # Add all records with human-readable date
            for record in data:
                record_with_date = {
                    'appid': record['appid'],
                    'player_no': record['player_no'],
                    'Date_collected': record['Date_collected'],
                    'Date_readable': datetime.fromtimestamp(record['Date_collected']).strftime('%Y-%m-%d %H:%M:%S')
                }
                all_records.append(record_with_date)

        except Exception as e:
            print(f"  Error processing {json_file.name}: {e}")
            continue

    # Convert to DataFrame
    df = pd.DataFrame(all_records)

    # Sort by appid and date
    df = df.sort_values(['appid', 'Date_collected'])

    # Save to CSV
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    # Print summary
    print("\n" + "="*60)
    print("COMBINED GAME PLAYER DATA SUMMARY")
    print("="*60)
    print(f"Total files processed: {len(json_files)}")
    print(f"Total records combined: {len(df):,}")
    print(f"Unique games (appids): {df['appid'].nunique():,}")
    print(f"Output file: {output_file}")

    return df


def main():
    """Main execution function"""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"

    # Output: combined game player data as CSV
    output_file = data_dir / "game_player_data_combined.csv"

    # Combine all timestamped files
    combine_game_player_data(data_dir, output_file)


if __name__ == "__main__":
    main()
