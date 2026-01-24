"""
Word Frequency Analysis for Power BI Word Cloud
Extracts words from reviews and creates word frequency dataset with sentiment scores
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


def extract_word_frequencies(input_csv: str, output_csv: str, min_word_length: int = 3, min_frequency: int = 5):
    """
    Extract word frequencies from reviews with sentiment information

    Args:
        input_csv: Path to input CSV file with reviews and sentiment
        output_csv: Path to output CSV file with word frequencies
        min_word_length: Minimum word length to include (default: 3)
        min_frequency: Minimum frequency for a word to be included (default: 5)
    """
    print(f"Reading reviews from: {input_csv}")
    df = pd.read_csv(input_csv, encoding='utf-8-sig')

    print(f"Total reviews: {len(df):,}")

    # Get English stopwords
    stop_words = set(stopwords.words('english'))

    # Add custom stop words for gaming context
    custom_stop_words = {
        'game', 'play', 'get', 'one', 'like', 'really', 'would',
        'could', 'time', 'make', 'even', 'much', 'also', 'good',
        'well', 'still', 'way', 'lot', 'thing', 'pretty', 'see'
    }
    stop_words.update(custom_stop_words)

    # Dictionary to store word statistics
    word_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'frequency': 0,
        'total_compound': 0.0,
        'positive_count': 0,
        'neutral_count': 0,
        'negative_count': 0,
        'appids': set()
    })

    print("\nExtracting words from reviews...")

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing reviews"):
        review_text = str(row['review'])
        sentiment_compound = row['sentiment_compound']
        sentiment_label = row['sentiment_label']
        appid = row['appid']

        # Tokenize and clean words
        words = word_tokenize(review_text.lower())

        for word in words:
            # Clean word: remove non-alphanumeric characters
            word = re.sub(r'[^a-z0-9]', '', word)

            # Skip if word is too short, is a stopword, or is numeric
            if (len(word) < min_word_length or
                word in stop_words or
                    word.isdigit()):
                continue

            # Update statistics
            word_stats[word]['frequency'] += 1
            word_stats[word]['total_compound'] += sentiment_compound
            word_stats[word]['appids'].add(appid)

            if sentiment_label == 'positive':
                word_stats[word]['positive_count'] += 1
            elif sentiment_label == 'neutral':
                word_stats[word]['neutral_count'] += 1
            else:
                word_stats[word]['negative_count'] += 1

    print(f"\nTotal unique words found: {len(word_stats):,}")

    # Convert to DataFrame
    word_data = []
    for word, stats in word_stats.items():
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
            'word': word,
            'frequency': freq,
            'avg_sentiment_compound': round(avg_compound, 4),
            'positive_count': stats['positive_count'],
            'neutral_count': stats['neutral_count'],
            'negative_count': stats['negative_count'],
            'dominant_sentiment': dominant_sentiment,
            'unique_games': len(stats['appids'])
        })

    # Create DataFrame and sort by frequency
    word_df = pd.DataFrame(word_data)
    word_df = word_df.sort_values('frequency', ascending=False)

    # Save to CSV
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    word_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n✓ Saved {len(word_df):,} words to {output_csv}")

    # Print summary
    print("\n" + "="*60)
    print("WORD FREQUENCY SUMMARY")
    print("="*60)
    print(f"Words after filtering: {len(word_df):,}")
    print(f"Minimum frequency threshold: {min_frequency}")
    print(f"Minimum word length: {min_word_length}")
    print(f"\nTop 10 most frequent words:")
    print(word_df[['word', 'frequency', 'avg_sentiment_compound',
          'dominant_sentiment']].head(10).to_string(index=False))
    print("="*60 + "\n")

    return word_df


def main():
    """Main execution function"""
    base_dir = Path(__file__).parent.parent

    # Input: reviews with sentiment
    input_csv = base_dir / "data" / "reviews" / \
        "PBI_review_ready" / "reviews_with_sentiment.csv"

    # Output: word frequencies
    output_csv = base_dir / "data" / "reviews" / \
        "PBI_review_ready" / "word_frequencies.csv"

    # Extract word frequencies
    extract_word_frequencies(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        min_word_length=3,
        min_frequency=5
    )

    print("✓ Word frequency analysis completed!")
    print(f"  Output: {output_csv}")
    print("\nYou can now import this CSV into Power BI and use it with the Word Cloud visual!")


if __name__ == "__main__":
    main()
