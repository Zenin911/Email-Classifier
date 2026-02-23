"""
train_model.py — Model Training & Evaluation
TF-IDF + XGBoost (category) + Logistic Regression (urgency)
"""
import os
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("⚠ XGBoost not installed, falling back to Logistic Regression for category model.")


def load_data(path):
    """Load cleaned CSV without pandas dependency."""
    import csv
    texts, categories, urgencies = [], [], []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["email_text"])
            categories.append(row["category"])
            urgencies.append(row["urgency"])
    return texts, categories, urgencies


def print_metrics(name, y_true, y_pred, labels):
    """Print evaluation metrics."""
    print(f"\n{'='*60}")
    print(f"📊 {name} — Evaluation Results")
    print(f"{'='*60}")
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    print(f"  Accuracy:  {acc:.4f}  {'✅' if acc > 0.85 else '⚠'}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1 Score:  {f1:.4f}")

    print(f"\n📋 Classification Report:")
    print(classification_report(y_true, y_pred, target_names=labels))

    print(f"🔢 Confusion Matrix:")
    cm = confusion_matrix(y_true, y_pred)
    # Pretty print
    max_label_len = max(len(l) for l in labels)
    header = " " * (max_label_len + 2) + "  ".join(f"{l[:6]:>6}" for l in labels)
    print(header)
    for i, row in enumerate(cm):
        row_str = "  ".join(f"{v:>6}" for v in row)
        print(f"  {labels[i]:<{max_label_len}} {row_str}")

    return acc


def main():
    input_path = os.path.join("data", "cleaned_emails.csv")
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"❌ {input_path} not found. Run preprocess.py first.")
        return

    # Load data
    texts, categories, urgencies = load_data(input_path)
    print(f"📂 Loaded {len(texts)} samples")

    # ─── TF-IDF Vectorization ───────────────────────────────────────────
    print("\n🔧 Fitting TF-IDF vectorizer (max_features=5000)...")
    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True)
    X = tfidf.fit_transform(texts)
    print(f"   Feature matrix shape: {X.shape}")

    # ─── Encode Labels ──────────────────────────────────────────────────
    cat_encoder = LabelEncoder()
    urg_encoder = LabelEncoder()
    y_cat = cat_encoder.fit_transform(categories)
    y_urg = urg_encoder.fit_transform(urgencies)

    # ─── Split Data ─────────────────────────────────────────────────────
    X_train, X_test, yc_train, yc_test, yu_train, yu_test = train_test_split(
        X, y_cat, y_urg, test_size=0.2, random_state=42, stratify=y_cat
    )
    print(f"   Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

    # ─── Train Category Model ───────────────────────────────────────────
    print("\n🚀 Training Category Classifier...")
    if HAS_XGBOOST:
        cat_model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
            verbosity=0,
        )
    else:
        cat_model = LogisticRegression(max_iter=1000, random_state=42, C=10)

    cat_model.fit(X_train, yc_train)
    yc_pred = cat_model.predict(X_test)
    cat_acc = print_metrics(
        "Category Classifier",
        yc_test, yc_pred,
        cat_encoder.classes_.tolist()
    )

    # ─── Train Urgency Model ────────────────────────────────────────────
    print("\n🚀 Training Urgency Classifier...")
    urg_model = LogisticRegression(max_iter=1000, random_state=42, C=10)
    urg_model.fit(X_train, yu_train)
    yu_pred = urg_model.predict(X_test)
    urg_acc = print_metrics(
        "Urgency Classifier",
        yu_test, yu_pred,
        urg_encoder.classes_.tolist()
    )

    # ─── Save Models ────────────────────────────────────────────────────
    joblib.dump(tfidf, os.path.join(model_dir, "tfidf_vectorizer.pkl"))
    joblib.dump(cat_model, os.path.join(model_dir, "category_model.pkl"))
    joblib.dump(urg_model, os.path.join(model_dir, "urgency_model.pkl"))
    joblib.dump(cat_encoder, os.path.join(model_dir, "category_encoder.pkl"))
    joblib.dump(urg_encoder, os.path.join(model_dir, "urgency_encoder.pkl"))

    print(f"\n{'='*60}")
    print(f"✅ All models saved to '{model_dir}/'")
    print(f"   - tfidf_vectorizer.pkl")
    print(f"   - category_model.pkl  (accuracy: {cat_acc:.2%})")
    print(f"   - urgency_model.pkl   (accuracy: {urg_acc:.2%})")
    print(f"   - category_encoder.pkl")
    print(f"   - urgency_encoder.pkl")
    print(f"{'='*60}")

    overall = (cat_acc + urg_acc) / 2
    if overall > 0.85:
        print(f"\n🎯 Overall accuracy: {overall:.2%} — TARGET MET ✅")
    else:
        print(f"\n⚠ Overall accuracy: {overall:.2%} — below 85% target")


if __name__ == "__main__":
    main()
