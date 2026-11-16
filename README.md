# FINIQ — AI-Powered Financial Intelligence Platform

> **This project is a prototype and is not financial advice.**

A sophisticated, interactive AI-powered financial intelligence platform built for the **AI + Finance** hackathon track.

---

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add OPENAI_API_KEY
streamlit run app/main.py
```
App opens at **http://localhost:8501** — works fully in demo mode without API keys.

---

## Hackathon Requirements

| Requirement | Status | Location |
|---|---|---|
| Beats a simple baseline | ✅ | Page 7 — Prediction Performance |
| Precision & Recall reported | ✅ | Page 7 → Run Live Baseline Comparison |
| Train on earlier / test on later data | ✅ Temporal 75/25 split | predictor.py → `_compute_baseline_comparison()` |
| Prototype disclaimer | ✅ | Throughout the app |

### Baseline Comparison

The ML model (RandomForest + 11 technical indicators) is compared against:
- **Baseline 1 — Majority Class**: always predicts whichever direction dominated in training data
- **Baseline 2 — Buy & Hold**: always predicts BULLISH

Precision, Recall, and F1 are reported **per class** (BULLISH/BEARISH/NEUTRAL). Accuracy alone is misleading for imbalanced stock direction data.

### Why Not Just Accuracy?

Stock directions are often imbalanced. BEARISH recall matters most for protecting users from downside risk. FINIQ reports per-class P/R/F1 for all three classes.

---

## Architecture

```
app/
  main.py                        # Home dashboard
  ui_components.py               # Shared styles + safe import wrappers
  pages/
    1_Market_Intelligence.py
    2_Stock_Analysis.py
    3_AI_Analyst_Debate.py       # Bull / Bear / Risk / Chief 4-agent debate
    4_News_Intelligence.py
    5_Portfolio.py
    6_Risk_Analysis.py
    7_Prediction_Performance.py  # <-- hackathon metrics: P/R/F1 + baseline comparison
    8_AI_Assistant.py
    9_Settings.py
backend/
  agents/   bull, bear, risk, chief analysts
  models/   predictor.py (RandomForest + baseline comparison), evaluation.py
  services/ market_data, news_data, ai_service, portfolio_service
  database/ db.py (SQLite: watchlist, portfolio, predictions, settings)
```

---

> **This project is a prototype and is not financial advice.**
