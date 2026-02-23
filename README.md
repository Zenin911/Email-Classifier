# 🧠 AI-Powered Email Classifier

An intelligent email classification system that automatically categorizes emails by **category** and **urgency** using machine learning, with a beautiful Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54-FF4B4B?logo=streamlit)
![XGBoost](https://img.shields.io/badge/XGBoost-3.2-green)
![Accuracy](https://img.shields.io/badge/Accuracy-98.19%25-brightgreen)

---

## ✨ Features

- **AI Classification** — Categorizes emails into 5 classes: `complaint`, `feedback`, `support`, `spam`, `other`
- **Urgency Detection** — Assigns `High`, `Medium`, or `Low` priority
- **Confidence Scores** — Shows prediction confidence for both category and urgency
- **Smart Routing** — Auto-suggests which team should handle each email
- **Reply Templates** — Generates suggested replies based on category
- **Interactive Dashboard** — KPI cards, Plotly charts, filters, search, and CSV export
- **Custom Training** — Train on your own dataset with `prepare_custom_dataset.py`

## 🎯 Model Performance

Trained on **204,907 real emails** from a custom dataset:

| Metric | Category | Urgency |
|--------|----------|---------|
| Accuracy | **96.65%** | **99.73%** |
| Precision | 96.74% | 99.73% |
| Recall | 96.65% | 99.73% |
| **Overall** | **98.19%** | |

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/<your-username>/EmailClassifier.git
cd EmailClassifier
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501)

> **Note:** Pre-trained models are included in `models/` — no training needed to get started!

### 3. Train on Your Own Data (Optional)

```bash
# Prepare your dataset (CSV with 'text' and 'label' columns)
python prepare_custom_dataset.py --input your_data.csv --text-col text --category-col label

# Preprocess & train
python preprocess.py
python train_model.py
```

## 📁 Project Structure

```
EmailClassifier/
├── app.py                     # Streamlit app (Analyze + Dashboard)
├── classifier.py              # Model loader & prediction engine
├── train_model.py             # TF-IDF + XGBoost/LogReg training
├── preprocess.py              # Text cleaning pipeline (NLTK)
├── generate_dataset.py        # Synthetic dataset generator
├── prepare_custom_dataset.py  # Custom dataset adapter
├── requirements.txt           # Python dependencies
├── models/                    # Trained model files (.pkl)
│   ├── tfidf_vectorizer.pkl
│   ├── category_model.pkl
│   ├── urgency_model.pkl
│   ├── category_encoder.pkl
│   └── urgency_encoder.pkl
└── data/                      # Training data (gitignored)
```

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| ML Models | XGBoost (category) + Logistic Regression (urgency) |
| Feature Extraction | TF-IDF Vectorization (5,000 features) |
| Text Processing | NLTK (stopwords, lemmatization) |
| Frontend | Streamlit with custom CSS |
| Visualization | Plotly |

## 📸 Screenshots

| Analyze Email | Dashboard |
|---------------|-----------|
| Paste email → AI classifies with confidence scores | KPIs, charts, filters, and email table |

## 📄 License

MIT License — feel free to use, modify, and distribute.
