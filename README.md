# FINIQ — AI-Powered Financial Intelligence

**Track:** Finance  
**Team:** Rikin Maddi, Ahaan Sah, Heth Maheswari  
**Live demo:** https://veritas-stockspred.vercel.app/

> This project is a prototype and is not financial advice.

FINIQ is an interactive AI-powered financial intelligence platform built for the AI + Finance hackathon track. It works fully in demo mode without any API keys.

## The problem

Many first-time investors, like a high school student with summer-job savings, get stock tips from apps that never explain why, or how often they're wrong. A confident signal with no reasoning and no track record can lead to bad money decisions. FINIQ is built for that moment, just before someone buys their first stock.

## What we built

FINIQ is a web dashboard with these main pages:

- **Market Intelligence:** indices, sector moves and market breadth, so the user sees the big picture first.
- **Stock Analysis:** a prediction for each stock, with a confidence level and the factors behind it.
- **News Intelligence:** each headline is scored positive, neutral or negative and linked to the stocks it affects.
- **AI Analyst Debate:** four AI analysts argue it out: a bull analyst, a bear analyst, a risk analyst who sets limits, and a chief investment officer who weighs all three into a verdict with a confidence level.
- **Prediction Performance:** shows how our model compares with simple baselines, including per-class precision, recall and F1.
- **Also included:** Portfolio, Risk Analysis, AI Assistant and Settings pages.

## What we added

We started from the suggested news-and-stock project. We added three things of our own:

- **Our own user:** a first-time investor who needs reasons, not just a signal.
- **Explainable debates:** every signal comes with arguments for and against.
- **A public report card:** baselines, results and misses are shown inside the product.

## Hackathon requirements

| Requirement | Status | Location |
| --- | --- | --- |
| Beats a simple baseline | ✅ | Page 7: Prediction Performance |
| Precision and recall reported | ✅ | Page 7, then "Run Live Baseline Comparison" |
| Train on earlier data, test on later data | ✅ | Temporal 75/25 split in `predictor.py`, `_compute_baseline_comparison()` |
| Prototype disclaimer | ✅ | Throughout the app |

## How it works

**Data:** Prices come through a Yahoo Finance gateway. In demo mode, the prices, headlines and debate text are sample content. We evaluated the model on 50 out-of-sample predictions. TODO: name the training dataset.

**Model:** A Random Forest classifier with 11 technical indicators predicts direction (bullish, bearish or neutral). We split the data by date, training on the earlier 75% and testing on the later 25%, with no random shuffling, so the model can't learn from the future. TODO: confirm that the embargo gap and the t-1 feature lag described on the website's Validation page are implemented in `predictor.py`.

**Debates:** The four debate agents are AI-written. In demo mode they are curated sample text, and live debates use GPT-4o when an `OPENAI_API_KEY` is set.

**Baselines:**

1. **Majority class:** always predicts whichever direction was most common in the training data.
2. **Buy and hold:** always predicts bullish.

Accuracy alone can be misleading for imbalanced stock-direction data, so we report precision, recall and F1 for each class. Bearish recall matters most for protecting users from downside risk.

## Results

| Method | Accuracy |
| --- | --- |
| Majority class (baseline) | 52.1% |
| Buy and hold (baseline) | 54.3% |
| FINIQ Random Forest | about 65% (50 out-of-sample predictions, NVIDIA) |

| Class | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Bullish | 68.2% | 71.4% | 0.697 |
| Bearish | 61.5% | 57.1% | 0.592 |
| Neutral | 62.5% | 66.7% | 0.645 |

TODO: confirm these numbers match the output of "Run Live Baseline Comparison" in the app. If they are sample values, say so here.

This is a small sample, so we don't claim the result will hold up in the future.

**Where it fails:** On August 19, 2026, the model predicted a rise with 86% confidence, and the stock fell. Across the 50 predictions it missed 18, and 8 of those misses were "neutral" calls where the stock actually moved. Our best explanation, which we have not yet tested: the model only sees price-based indicators from before each prediction, so it cannot react to news that arrives afterward, and near-flat "neutral" days are easy to misjudge in either direction.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add OPENAI_API_KEY
streamlit run app/main.py
```

The app opens at http://localhost:8501 and works fully in demo mode without API keys.

## Architecture

```
app/
  main.py                      # Home dashboard
  ui_components.py             # Shared styles and safe import wrappers
  pages/
    1_Market_Intelligence.py
    2_Stock_Analysis.py
    3_AI_Analyst_Debate.py     # Bull / Bear / Risk / Chief 4-agent debate
    4_News_Intelligence.py
    5_Portfolio.py
    6_Risk_Analysis.py
    7_Prediction_Performance.py  # P/R/F1 and baseline comparison
    8_AI_Assistant.py
    9_Settings.py
backend/
  agents/                      # bull, bear, risk, chief analysts
  models/                      # predictor.py (Random Forest + baseline comparison), evaluation.py
  services/                    # market_data, news_data, ai_service, portfolio_service
  database/                    # db.py (SQLite: watchlist, portfolio, predictions, settings)
```

## What we'd do next

1. Test more stocks and longer time periods, to see if the result holds up.
2. Add a plain-language beginner mode, and try it with real first-time investors.

## Sources

- [Yahoo Finance](https://finance.yahoo.com/) (prices)
- [OpenAI GPT-4o](https://openai.com/) (live debates)
- TODO: news dataset and sentiment model, with links
- Claude (Anthropic): helped plan features and draft our demo script and write-up
- ChatGPT Codex (OpenAI): used as a coding assistant while building the project

*This project is a prototype and is not financial advice.*
