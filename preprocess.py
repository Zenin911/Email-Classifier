"""
preprocess.py — Text Cleaning Pipeline
Cleans raw emails: removes HTML, lowercases, removes stopwords, lemmatizes.
"""
import csv
import os
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data (safe to call multiple times)
for resource in ["stopwords", "wordnet", "punkt_tab"]:
    nltk.download(resource, quiet=True)

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """Full cleaning pipeline for a single email text."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    # Remove special characters and digits (keep letters and spaces)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Lowercase
    text = text.lower()
    # Tokenize
    tokens = text.split()
    # Remove stopwords and lemmatize
    tokens = [
        LEMMATIZER.lemmatize(word)
        for word in tokens
        if word not in STOP_WORDS and len(word) > 2
    ]
    return " ".join(tokens)


def main():
    input_path = os.path.join("data", "raw_emails.csv")
    output_path = os.path.join("data", "cleaned_emails.csv")

    if not os.path.exists(input_path):
        print(f"❌ {input_path} not found. Run generate_dataset.py first.")
        return

    cleaned = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned_text = clean_text(row["email_text"])
            if cleaned_text.strip():  # Skip empty results
                cleaned.append({
                    "email_text": cleaned_text,
                    "category": row["category"],
                    "urgency": row["urgency"],
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email_text", "category", "urgency"])
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"✅ Cleaned {len(cleaned)} emails → {output_path}")
    # Show sample
    print("\n📝 Sample cleaned text:")
    for item in cleaned[:3]:
        print(f"   [{item['category']} | {item['urgency']}] {item['email_text'][:80]}...")


if __name__ == "__main__":
    main()
