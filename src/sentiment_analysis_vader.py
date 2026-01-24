"""
VADER Sentiment Analysis for Steam Reviews
Analyzes sentiment of reviews from JSONL file and outputs results with sentiment scores
"""

import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from datetime import datetime
from typing import Optional

# Download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading VADER lexicon...")
    nltk.download('vader_lexicon')


def analyze_reviews(input_file: str, output_jsonl: Optional[str] = None, output_csv: Optional[str] = None):
    """
    Analyze sentiment of reviews using VADER

    Args:
        input_file: Path to input JSONL file with reviews
        output_jsonl: Path to output JSONL file with sentiment scores (optional)
        output_csv: Path to output CSV file with sentiment scores (optional)
    """
    # Initialize VADER sentiment analyzer
    sia = SentimentIntensityAnalyzer()

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    print(f"Reading reviews from: {input_file}")

    # Read and process reviews
    processed_reviews = []
    total_reviews = 0

    with open(input_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Processing reviews"):
            try:
                data = json.loads(line)
                appid = data.get('appid')
                reviews = data.get('reviews', [])

                for review in reviews:
                    review_text = review.get('review', '')

                    # Skip empty reviews
                    if not review_text.strip():
                        continue

                    # Perform sentiment analysis
                    sentiment_scores = sia.polarity_scores(review_text)

                    # Add sentiment scores to review
                    review['sentiment_scores'] = sentiment_scores
                    review['sentiment_compound'] = sentiment_scores['compound']
                    review['sentiment_label'] = get_sentiment_label(
                        sentiment_scores['compound'])

                    # Add appid for reference
                    review['appid'] = appid

                    processed_reviews.append(review)
                    total_reviews += 1

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue

    print(f"\nTotal reviews processed: {total_reviews}")

    # Print summary statistics
    print_sentiment_summary(processed_reviews)

    # Save to JSONL if specified
    if output_jsonl:
        save_to_jsonl(processed_reviews, output_jsonl)

    # Save to CSV if specified
    if output_csv:
        save_to_csv(processed_reviews, output_csv)

    return processed_reviews


def get_sentiment_label(compound_score: float) -> str:
    """
    Classify sentiment based on compound score

    Args:
        compound_score: VADER compound score (-1 to 1)

    Returns:
        Sentiment label: 'positive', 'neutral', or 'negative'
    """
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'


def print_sentiment_summary(reviews: list):
    """Print summary statistics of sentiment analysis"""
    if not reviews:
        print("No reviews to summarize")
        return

    positive = sum(1 for r in reviews if r['sentiment_label'] == 'positive')
    negative = sum(1 for r in reviews if r['sentiment_label'] == 'negative')
    neutral = sum(1 for r in reviews if r['sentiment_label'] == 'neutral')
    total = len(reviews)

    avg_compound = sum(r['sentiment_compound'] for r in reviews) / total

    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total reviews analyzed: {total:,}")
    print(f"\nSentiment Distribution:")
    print(f"  Positive: {positive:,} ({positive/total*100:.2f}%)")
    print(f"  Neutral:  {neutral:,} ({neutral/total*100:.2f}%)")
    print(f"  Negative: {negative:,} ({negative/total*100:.2f}%)")
    print(f"\nAverage Compound Score: {avg_compound:.4f}")
    print("="*60 + "\n")


def save_to_jsonl(reviews: list, output_file: str):
    """Save reviews with sentiment scores to JSONL file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving to JSONL: {output_file}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for review in reviews:
            f.write(json.dumps(review, ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(reviews):,} reviews to {output_file}")


def save_to_csv(reviews: list, output_file: str):
    """Save reviews with sentiment scores to CSV file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving to CSV: {output_file}")

    # Prepare data for CSV
    csv_data = []
    for review in reviews:
        row = {
            'appid': review.get('appid'),
            'recommendationid': review.get('recommendationid'),
            'review': review.get('review', ''),
            'voted_up': review.get('voted_up'),
            'language': review.get('language'),
            'timestamp_created': review.get('timestamp_created'),
            'sentiment_compound': review['sentiment_compound'],
            'sentiment_positive': review['sentiment_scores']['pos'],
            'sentiment_neutral': review['sentiment_scores']['neu'],
            'sentiment_negative': review['sentiment_scores']['neg'],
            'sentiment_label': review['sentiment_label'],
        }
        csv_data.append(row)

    # Create DataFrame and save
    df = pd.DataFrame(csv_data)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"✓ Saved {len(csv_data):,} reviews to {output_file}")


def main():
    """Main execution function"""
    # Define paths
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "data" / "reviews" / \
        "combined_reviews" / "all_reviews.jsonl"

    # Output paths
    timestamp = datetime.now().strftime("%Y%m%d")
    output_dir = base_dir / "data" / "reviews" / "PBI_review_ready"
    output_jsonl = output_dir / f"reviews_with_sentiment.jsonl"
    output_csv = output_dir / f"reviews_with_sentiment.csv"

    # Run analysis
    analyze_reviews(
        input_file=str(input_file),
        output_jsonl=str(output_jsonl),
        output_csv=str(output_csv)
    )

    print("\n✓ Sentiment analysis completed!")
    print(f"  - JSONL output: {output_jsonl}")
    print(f"  - CSV output: {output_csv}")


if __name__ == "__main__":
    main()
