"""
prepare_custom_dataset.py — Use Your Own Dataset
Converts your custom CSV/Excel dataset into the format needed for training.

Usage:
    python prepare_custom_dataset.py --input your_data.csv

Your CSV must have at least an email text column. Category and urgency columns
are optional — if missing, the script will guide you.

Supported formats: .csv, .xlsx, .xls
"""
import argparse
import csv
import os
import sys


VALID_CATEGORIES = [
    "Billing Issue", "Technical Support", "Account Access",
    "Complaint", "Feature Request", "General Inquiry"
]
VALID_URGENCIES = ["High", "Medium", "Low"]


def detect_columns(headers):
    """Try to auto-detect which columns map to email_text, category, urgency."""
    text_candidates = ["email_text", "text", "body", "content", "email", "message", "email_body", "email_content", "description"]
    cat_candidates = ["category", "label", "class", "type", "topic", "tag", "classification"]
    urg_candidates = ["urgency", "priority", "severity", "level", "urgent"]

    text_col = None
    cat_col = None
    urg_col = None

    headers_lower = [h.lower().strip() for h in headers]

    for candidate in text_candidates:
        if candidate in headers_lower:
            text_col = headers[headers_lower.index(candidate)]
            break

    for candidate in cat_candidates:
        if candidate in headers_lower:
            cat_col = headers[headers_lower.index(candidate)]
            break

    for candidate in urg_candidates:
        if candidate in headers_lower:
            urg_col = headers[headers_lower.index(candidate)]
            break

    return text_col, cat_col, urg_col


def load_csv(path):
    """Load CSV file and return headers + rows."""
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for row in reader:
            rows.append(row)
    return headers, rows


def load_excel(path):
    """Load Excel file (requires openpyxl or xlrd)."""
    try:
        import pandas as pd
        df = pd.read_excel(path)
        headers = df.columns.tolist()
        rows = df.to_dict("records")
        return headers, rows
    except ImportError:
        print("❌ To read Excel files, install pandas and openpyxl:")
        print("   pip install pandas openpyxl")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Prepare your custom dataset for training")
    parser.add_argument("--input", "-i", required=True, help="Path to your dataset (CSV or Excel)")
    parser.add_argument("--text-col", help="Name of the email text column (auto-detected if not specified)")
    parser.add_argument("--category-col", help="Name of the category column (optional)")
    parser.add_argument("--urgency-col", help="Name of the urgency column (optional)")
    parser.add_argument("--default-urgency", default="Medium", choices=VALID_URGENCIES,
                        help="Default urgency if no urgency column exists (default: Medium)")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    # Load file
    ext = os.path.splitext(input_path)[1].lower()
    if ext in (".xlsx", ".xls"):
        headers, rows = load_excel(input_path)
    elif ext == ".csv":
        headers, rows = load_csv(input_path)
    else:
        print(f"❌ Unsupported format: {ext}. Use .csv or .xlsx")
        sys.exit(1)

    print(f"📂 Loaded {len(rows)} rows from {input_path}")
    print(f"   Columns found: {headers}")

    # Detect or use specified columns
    text_col = args.text_col
    cat_col = args.category_col
    urg_col = args.urgency_col

    auto_text, auto_cat, auto_urg = detect_columns(headers)

    if not text_col:
        text_col = auto_text
    if not cat_col:
        cat_col = auto_cat
    if not urg_col:
        urg_col = auto_urg

    if not text_col:
        print(f"\n❌ Could not auto-detect the email text column.")
        print(f"   Available columns: {headers}")
        print(f"   Specify it with: --text-col 'column_name'")
        sys.exit(1)

    print(f"\n✅ Column mapping:")
    print(f"   Text column:     '{text_col}'")
    print(f"   Category column: '{cat_col}'" if cat_col else "   Category column: NOT FOUND (will need manual labels)")
    print(f"   Urgency column:  '{urg_col}'" if urg_col else f"   Urgency column:  NOT FOUND (using default: {args.default_urgency})")

    # Process rows
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "raw_emails.csv")

    processed = []
    skipped = 0

    for row in rows:
        text = str(row.get(text_col, "")).strip()
        if not text or len(text) < 10:
            skipped += 1
            continue

        category = str(row.get(cat_col, "General Inquiry")).strip() if cat_col else "General Inquiry"
        urgency = str(row.get(urg_col, args.default_urgency)).strip() if urg_col else args.default_urgency

        # Normalize category — fuzzy match to valid categories
        if category not in VALID_CATEGORIES:
            cat_lower = category.lower()
            matched = False
            for valid in VALID_CATEGORIES:
                if any(word in cat_lower for word in valid.lower().split()):
                    category = valid
                    matched = True
                    break
            if not matched:
                category = "General Inquiry"

        # Normalize urgency
        if urgency not in VALID_URGENCIES:
            urg_lower = urgency.lower()
            if "high" in urg_lower or "critical" in urg_lower or "urgent" in urg_lower:
                urgency = "High"
            elif "low" in urg_lower or "info" in urg_lower:
                urgency = "Low"
            else:
                urgency = "Medium"

        processed.append({
            "email_text": text,
            "category": category,
            "urgency": urgency,
        })

    # Save
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email_text", "category", "urgency"])
        writer.writeheader()
        writer.writerows(processed)

    print(f"\n✅ Processed {len(processed)} emails → {output_path}")
    if skipped:
        print(f"   ⚠ Skipped {skipped} rows (empty or too short)")

    # Distribution
    from collections import Counter
    cat_counts = Counter(e["category"] for e in processed)
    urg_counts = Counter(e["urgency"] for e in processed)
    print(f"\n📊 Category Distribution:")
    for c, n in sorted(cat_counts.items()):
        print(f"   {c}: {n}")
    print(f"\n📊 Urgency Distribution:")
    for u, n in sorted(urg_counts.items()):
        print(f"   {u}: {n}")

    print(f"\n🚀 Next steps:")
    print(f"   1. python preprocess.py")
    print(f"   2. python train_model.py")
    print(f"   3. streamlit run app.py")


if __name__ == "__main__":
    main()
