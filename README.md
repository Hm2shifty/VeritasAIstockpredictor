FINIQ — AI-Powered Financial Intelligence Platform
This project is a prototype and is not financial advice.


A sophisticated, interactive AI-powered financial intelligence platform built for the AI + Finance hackathon track.


Quick Start
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add OPENAI_API_KEY
streamlit run app/main.py
App opens at http://localhost:8501 — works fully in demo mode without API keys.


Hackathon Requirements
Requirement	Status	Location
Beats a simple baseline	✅	Page 7 — Prediction Performance
Precision & Recall reported	✅	Page 7 → Run Live Baseline Comparison
Train on earlier / test on later data	✅ Temporal 75/25 split	predictor.py → _compute_baseline_comparison()
Prototype disclaimer	✅	Throughout the app
Baseline Comparison
The ML model (RandomForest + 11 technical indicators) is compared against:


Baseline 1 — Majority Class: always predicts whichever direction dominated in training data
Baseline 2 — Buy & Hold: always predicts BULLISH
Precision, Recall, and F1 are reported per class (BULLISH/BEARISH/NEUTRAL). Accuracy alone is misleading for imbalanced stock direction data.


Why Not Just Accuracy?
Stock directions are often imbalanced. BEARISH recall matters most for protecting users from downside risk. FINIQ reports per-class P/R/F1 for all three classes.


Architecture
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

To add on,
# FINIQ


**Track:** Finance  
**Team:** TODO: team member names


> This project is a prototype and is not financial advice.


## The problem


Many first-time investors, like a high school student with summer-job savings, get stock tips from apps that never explain why, or how often they're wrong. A confident signal with no reasoning and no track record can lead to bad money decisions. FINIQ is built for that moment, just before someone buys their first stock.


## What we built


FINIQ is a web dashboard:


- **Market page:** indices, sector moves and market breadth, so the user sees the big picture first.
- **News page:** each headline is scored positive, neutral or negative and linked to the stocks it affects.
- **AI Debate:** four AI analysts argue it out: a bull analyst, a bear analyst, a risk analyst who sets limits, and a chief investment officer who weighs all three into a verdict with a confidence level.
- **Validation page:** shows how our model compares with simple baselines, including its misses.


## What we added


We started from the suggested news-and-stock project. We added three things of our own:


- **Our own user:** a first-time investor who needs reasons, not just a signal.
- **Explainable debates:** every signal comes with arguments for and against.
- **A public report card:** baselines, results and misses are shown inside the product.


## How it works


**Data:** Prices come through a Yahoo Finance gateway. In demo mode, the prices, headlines and debate text are sample content. TODO: name the dataset and the number of examples used to train and test the model.


**Model:** Our ML ensemble predicts direction (bullish, bearish or neutral). We test it with walk-forward validation: no random shuffling, a gap between training and test periods, and indicators computed only from data before the prediction date. The debates are written by AI agents. In demo mode they are curated, and live debates use GPT-4o.


## Results


| Method | Accuracy |
| --- | --- |
| Always guess the most common outcome (baseline) | 52.1% |
| Buy-and-hold (baseline) | 54.3% |
| FINIQ ML ensemble | about 65% (50 out-of-sample predictions, NVIDIA) |


This is a small sample, so we don't claim the result will hold up in the future.


**Where it fails:** On August 19, 2026, the model predicted a rise with 86% confidence, and the stock fell. Across the 50 predictions it missed 18, often when it called a move "neutral" and the stock actually moved. TODO: add why you think this happens.


## What we'd do next


1. Test more stocks and longer time periods, to see if the result holds up.
2. Add a plain-language beginner mode, and try it with real first-time investors.


## Sources


- Yahoo Finance (prices): TODO: link
- OpenAI GPT-4o (debates): TODO: link
- TODO: news dataset and sentiment model, with links
- AI tools used for coding, writing or script help: TODO: list them, with links


*This project is a prototype and is not financial advice.*