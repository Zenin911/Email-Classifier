"""
classifier.py — Model Loader & Prediction Helper
Loads trained .pkl models and provides a predict() function.
"""
import os
import re
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure NLTK data is available
for resource in ["stopwords", "wordnet", "punkt_tab"]:
    nltk.download(resource, quiet=True)

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def clean_text(text: str) -> str:
    """Clean input text with same pipeline used in training."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = text.lower()
    tokens = text.split()
    tokens = [
        LEMMATIZER.lemmatize(word)
        for word in tokens
        if word not in STOP_WORDS and len(word) > 2
    ]
    return " ".join(tokens)


class EmailClassifier:
    """Loads models and classifies emails."""

    def __init__(self):
        self.tfidf = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
        self.cat_model = joblib.load(os.path.join(MODEL_DIR, "category_model.pkl"))
        self.urg_model = joblib.load(os.path.join(MODEL_DIR, "urgency_model.pkl"))
        self.cat_encoder = joblib.load(os.path.join(MODEL_DIR, "category_encoder.pkl"))
        self.urg_encoder = joblib.load(os.path.join(MODEL_DIR, "urgency_encoder.pkl"))

    def predict(self, email_text: str) -> dict:
        """Classify a single email and return category, urgency, confidence."""
        cleaned = clean_text(email_text)
        features = self.tfidf.transform([cleaned])

        # Category prediction
        cat_idx = self.cat_model.predict(features)[0]
        category = self.cat_encoder.inverse_transform([cat_idx])[0]

        # Category confidence
        if hasattr(self.cat_model, "predict_proba"):
            cat_proba = self.cat_model.predict_proba(features)[0]
            cat_confidence = float(max(cat_proba))
        else:
            cat_confidence = 0.85  # Fallback

        # Urgency prediction
        urg_idx = self.urg_model.predict(features)[0]
        urgency = self.urg_encoder.inverse_transform([urg_idx])[0]

        # Urgency confidence
        if hasattr(self.urg_model, "predict_proba"):
            urg_proba = self.urg_model.predict_proba(features)[0]
            urg_confidence = float(max(urg_proba))
        else:
            urg_confidence = 0.85

        # Overall confidence = average of both
        confidence = round((cat_confidence + urg_confidence) / 2, 4)

        return {
            "category": category,
            "urgency": urgency,
            "confidence": confidence,
            "cat_confidence": round(cat_confidence, 4),
            "urg_confidence": round(urg_confidence, 4),
        }


# ─── Auto-routing Map ───────────────────────────────────────────────────────
ROUTING_MAP = {
    "complaint": {"team": "⚡ Escalation Team", "color": "#FF6B6B"},
    "feedback":  {"team": "💬 Feedback Team", "color": "#4ECDC4"},
    "other":     {"team": "📋 General Support", "color": "#34D399"},
    "spam":      {"team": "🚫 Spam Filter", "color": "#6C757D"},
    "support":   {"team": "🔧 Technical Team", "color": "#45B7D1"},
}


# ─── Smart Reply Templates ──────────────────────────────────────────────────
REPLY_TEMPLATES = {
    "complaint": """Dear Customer,

We sincerely apologize for the experience you've described. Your feedback is extremely valuable to us.

Your complaint has been escalated to our management team for immediate review. A senior representative will contact you within 24 hours to discuss a resolution.

We are committed to making this right.

Best regards,
Customer Relations Team""",

    "feedback": """Dear Customer,

Thank you so much for your thoughtful feedback! We're delighted to hear about your experience.

Your comments have been shared with our team and will help us continue improving our products and services.

We truly appreciate you taking the time to let us know.

Best regards,
Customer Experience Team""",

    "other": """Dear Customer,

Thank you for reaching out to us! We've received your message.

Our team will review it and get back to you with a response within 24 hours. In the meantime, you may find helpful information in our FAQ section.

Best regards,
Customer Support Team""",

    "spam": """[Auto-filtered]

This message has been automatically flagged as spam/phishing by our AI system. No action is required.

If you believe this was flagged incorrectly, please contact support.""",

    "support": """Dear Customer,

Thank you for reporting this issue. We're sorry for the inconvenience.

Our Technical Team has been notified and is investigating. Here are some initial steps you can try:
1. Clear your browser cache and cookies
2. Restart the application or device
3. Check your internet connection

We'll get back to you with a detailed solution shortly.

Best regards,
Technical Support Team""",
}
