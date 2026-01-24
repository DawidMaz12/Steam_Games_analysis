"""
Word Frequency Analysis by Game for Power BI Word Cloud
Extracts words from reviews with game-level tracking for filtering in Power BI
"""

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
import re
from typing import Dict, Set, Any

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading punkt_tab tokenizer...")
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading stopwords...")
    nltk.download('stopwords')


def extract_word_frequencies_by_game(input_csv: str, output_csv: str, min_word_length: int = 3, min_frequency: int = 3):
    """
    Extract word frequencies from reviews, tracked per game for Power BI filtering

    Args:
        input_csv: Path to input CSV file with reviews and sentiment
        output_csv: Path to output CSV file with word frequencies by game
        min_word_length: Minimum word length to include (default: 3)
        min_frequency: Minimum frequency for a word-game combination (default: 3)
    """
    print(f"Reading reviews from: {input_csv}")
    df = pd.read_csv(input_csv, encoding='utf-8-sig')

    print(f"Total reviews: {len(df):,}")
    print(f"Unique games: {df['appid'].nunique():,}")

    # Get English stopwords
    stop_words = set(stopwords.words('english'))

    # Add custom stop words for gaming context
    custom_stop_words = {
        'game', 'play', 'get', 'one', 'like', 'really', 'would',
        'could', 'time', 'make', 'even', 'much', 'also', 'good',
        'well', 'still', 'way', 'lot', 'thing', 'pretty', 'see',
        'games', 'playing', 'played', 'player', 'players'
    }
    stop_words.update(custom_stop_words)

    # Dictionary to store word statistics per game
    # Structure: {(word, appid): {stats}}
    word_game_stats: Dict[tuple, Dict[str, Any]] = defaultdict(lambda: {
        'frequency': 0,
        'total_compound': 0.0,
        'positive_count': 0,
        'neutral_count': 0,
        'negative_count': 0
    })

    print("\nExtracting words from reviews...")

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing reviews"):
        review_text = str(row['review'])
        sentiment_compound = row['sentiment_compound']
        sentiment_label = row['sentiment_label']
        appid = row['appid']

        # Tokenize and clean words
        words = word_tokenize(review_text.lower())

        # Track unique words per review to avoid counting duplicates within same review
        unique_words = set()

        for word in words:
            # Clean word: remove non-alphanumeric characters
            word = re.sub(r'[^a-z0-9]', '', word)

            # Skip if word is too short, is a stopword, or is numeric
            if (len(word) < min_word_length or
                word in stop_words or
                    word.isdigit()):
                continue

            unique_words.add(word)

        # Update statistics for each unique word in this review
        for word in unique_words:
            key = (word, appid)
            word_game_stats[key]['frequency'] += 1
            word_game_stats[key]['total_compound'] += sentiment_compound

            if sentiment_label == 'positive':
                word_game_stats[key]['positive_count'] += 1
            elif sentiment_label == 'neutral':
                word_game_stats[key]['neutral_count'] += 1
            else:
                word_game_stats[key]['negative_count'] += 1

    print(f"\nTotal unique word-game combinations: {len(word_game_stats):,}")

    # Convert to DataFrame
    word_data = []
    for (word, appid), stats in tqdm(word_game_stats.items(), desc="Building dataset"):
        freq = stats['frequency']

        # Filter by minimum frequency
        if freq < min_frequency:
            continue

        avg_compound = stats['total_compound'] / freq

        # Determine dominant sentiment
        sentiment_counts = {
            'positive': stats['positive_count'],
            'neutral': stats['neutral_count'],
            'negative': stats['negative_count']
        }
        dominant_sentiment = max(
            sentiment_counts.keys(), key=lambda x: sentiment_counts[x])

        word_data.append({
            'appid': appid,
            'word': word,
            'frequency': freq,
            'avg_sentiment_compound': round(avg_compound, 4),
            'positive_count': stats['positive_count'],
            'neutral_count': stats['neutral_count'],
            'negative_count': stats['negative_count'],
            'dominant_sentiment': dominant_sentiment
        })

    # Create DataFrame and sort
    word_df = pd.DataFrame(word_data)
    word_df = word_df.sort_values(
        ['appid', 'frequency'], ascending=[True, False])

    # Save to CSV
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    word_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n✓ Saved {len(word_df):,} word-game combinations to {output_csv}")

    # Print summary
    print("\n" + "="*60)
    print("WORD FREQUENCY BY GAME SUMMARY")
    print("="*60)
    print(f"Total word-game combinations: {len(word_df):,}")
    print(f"Unique words: {word_df['word'].nunique():,}")
    print(f"Games covered: {word_df['appid'].nunique():,}")
    print(f"Minimum frequency threshold: {min_frequency}")
    print(f"Minimum word length: {min_word_length}")
    print(f"\nTop 10 most frequent words (across all games):")
    top_words = word_df.groupby('word')['frequency'].sum(
    ).sort_values(ascending=False).head(10)
    for word, freq in top_words.items():
        print(f"  {word}: {freq:,}")
    print("="*60 + "\n")

    return word_df


def main():
    """Main execution function"""
    base_dir = Path(__file__).parent.parent

    # Input: reviews with sentiment
    input_csv = base_dir / "data" / "reviews" / \
        "PBI_review_ready" / "reviews_with_sentiment.csv"

    # Output: word frequencies by game
    output_csv = base_dir / "data" / "reviews" / \
        "PBI_review_ready" / "word_frequencies_by_game.csv"

    # Extract word frequencies by game
    extract_word_frequencies_by_game(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        min_word_length=3,
        min_frequency=3
    )

    print("✓ Word frequency by game analysis completed!")
    print(f"  Output: {output_csv}")
    print("\nPower BI Usage:")
    print("  1. Import word_frequencies_by_game.csv")
    print("  2. Create relationship with game data using 'appid'")
    print("  3. Add Word Cloud visual")
    print("  4. Category: word")
    print("  5. Values: frequency")
    print("  6. Add game name slicer to filter by specific game")
    print("  7. Word cloud will dynamically update based on game selection!")


if __name__ == "__main__":
    main()
