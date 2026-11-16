"""
FINIQ News Intelligence Service

Provides curated financial news with sentiment analysis.
Operates in demo mode when live APIs are unavailable.

This project is a prototype and is not financial advice.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Demo news corpus — realistic financial news articles
# ---------------------------------------------------------------------------

DEMO_NEWS = [
    {
        "headline": "Federal Reserve Signals Gradual Rate Cuts Amid Cooling Inflation",
        "summary": "Fed Chair indicated the central bank is prepared to ease monetary policy as inflation continues to trend toward the 2% target, boosting risk assets across markets.",
        "source": "Financial Times",
        "tickers": ["SPY", "QQQ", "JPM", "V", "MA"],
        "sentiment": "positive",
        "event_type": "macro",
        "relevance_score": 0.95,
    },
    {
        "headline": "NVIDIA Posts Record Quarter; AI Chip Demand Surpasses All Forecasts",
        "summary": "NVIDIA reported $22.1B in quarterly revenue, exceeding analyst estimates by 18%. Data center segment grew 427% year-over-year as hyperscalers accelerate AI infrastructure buildout.",
        "source": "Wall Street Journal",
        "tickers": ["NVDA", "AMD", "INTC", "MSFT", "GOOGL"],
        "sentiment": "positive",
        "event_type": "earnings",
        "relevance_score": 0.98,
    },
    {
        "headline": "Apple Unveils Next-Generation AI Features Across Product Line",
        "summary": "Apple announced a sweeping integration of on-device AI across iPhone, Mac, and iPad. The company emphasized privacy-first design with no cloud data exposure.",
        "source": "Reuters",
        "tickers": ["AAPL", "MSFT", "GOOGL", "META"],
        "sentiment": "positive",
        "event_type": "product",
        "relevance_score": 0.92,
    },
    {
        "headline": "Rising Treasury Yields Put Pressure on Tech Valuations",
        "summary": "10-year Treasury yields climbed to 4.52%, their highest level in three months, triggering a rotation out of growth stocks and into value-oriented sectors.",
        "source": "Bloomberg",
        "tickers": ["QQQ", "NVDA", "TSLA", "NFLX", "CRM"],
        "sentiment": "negative",
        "event_type": "macro",
        "relevance_score": 0.89,
    },
    {
        "headline": "Amazon Web Services Wins $10B Government Cloud Contract",
        "summary": "AWS secured a multi-year contract with the Department of Defense, expanding its already dominant cloud infrastructure position and validating its enterprise AI capabilities.",
        "source": "CNBC",
        "tickers": ["AMZN", "MSFT", "GOOGL"],
        "sentiment": "positive",
        "event_type": "corporate",
        "relevance_score": 0.94,
    },
    {
        "headline": "Tesla Faces Delivery Shortfall as EV Demand Softens in Key Markets",
        "summary": "Tesla reported Q3 deliveries 8% below consensus estimates as competition from Chinese manufacturers intensifies and consumer EV adoption slows in Europe.",
        "source": "Reuters",
        "tickers": ["TSLA"],
        "sentiment": "negative",
        "event_type": "earnings",
        "relevance_score": 0.96,
    },
    {
        "headline": "JPMorgan Raises S&P 500 Year-End Target to 5,800",
        "summary": "JPMorgan's equity strategy team raised their S&P 500 year-end target, citing stronger-than-expected corporate earnings, resilient consumer spending, and AI productivity gains.",
        "source": "Financial Times",
        "tickers": ["SPY", "QQQ", "JPM"],
        "sentiment": "positive",
        "event_type": "analyst_upgrade",
        "relevance_score": 0.88,
    },
    {
        "headline": "Meta Platforms Ad Revenue Growth Accelerates; AI Tools Drive Engagement",
        "summary": "Meta's advertising revenue grew 24% year-over-year as AI-powered ad targeting improvements lifted conversion rates across Facebook, Instagram, and WhatsApp.",
        "source": "Wall Street Journal",
        "tickers": ["META", "GOOGL", "AMZN"],
        "sentiment": "positive",
        "event_type": "earnings",
        "relevance_score": 0.93,
    },
    {
        "headline": "Intel Restructures Operations; Plans 15% Workforce Reduction",
        "summary": "Intel announced sweeping restructuring plans including significant job cuts and a refocus on its core semiconductor manufacturing business as it battles market share losses.",
        "source": "Reuters",
        "tickers": ["INTC", "AMD", "NVDA"],
        "sentiment": "negative",
        "event_type": "corporate",
        "relevance_score": 0.91,
    },
    {
        "headline": "Healthcare Sector Outperforms as Defensive Rotation Gains Momentum",
        "summary": "Healthcare stocks hit 52-week highs as investors rotated into defensive sectors amid uncertainty over global growth outlook and elevated geopolitical risk.",
        "source": "Bloomberg",
        "tickers": ["JNJ", "UNH", "PG"],
        "sentiment": "positive",
        "event_type": "sector",
        "relevance_score": 0.84,
    },
    {
        "headline": "PayPal Launches AI-Powered Fraud Detection System",
        "summary": "PayPal unveiled a next-generation fraud detection platform powered by large language models, claiming a 40% reduction in false positives and $500M in annual fraud prevention.",
        "source": "TechCrunch",
        "tickers": ["PYPL", "V", "MA"],
        "sentiment": "positive",
        "event_type": "product",
        "relevance_score": 0.87,
    },
    {
        "headline": "Disney+ Subscriber Growth Beats Estimates; Streaming Unit Turns Profitable",
        "summary": "Disney+ added 7.4M new subscribers in Q3, beating estimates by 2.1M. The streaming division reported its first quarterly profit, validating the company's direct-to-consumer strategy.",
        "source": "CNBC",
        "tickers": ["DIS", "NFLX"],
        "sentiment": "positive",
        "event_type": "earnings",
        "relevance_score": 0.90,
    },
    {
        "headline": "Salesforce Acquires AI Startup for $2.1B to Bolster Enterprise Automation",
        "summary": "Salesforce completed its acquisition of an AI workflow automation startup, integrating advanced LLM capabilities into its Einstein platform for enterprise customers.",
        "source": "Financial Times",
        "tickers": ["CRM", "MSFT"],
        "sentiment": "positive",
        "event_type": "merger",
        "relevance_score": 0.86,
    },
    {
        "headline": "Oil Prices Fall 3% on Unexpected Inventory Build",
        "summary": "Crude oil prices dropped sharply after the EIA reported a larger-than-expected weekly inventory build, raising concerns about softening global demand.",
        "source": "Reuters",
        "tickers": ["SPY"],
        "sentiment": "negative",
        "event_type": "commodity",
        "relevance_score": 0.80,
    },
    {
        "headline": "Visa and Mastercard Report Strong Cross-Border Transaction Growth",
        "summary": "Both payment networks reported double-digit international transaction growth, driven by sustained travel recovery and expanding digital payment adoption in emerging markets.",
        "source": "Bloomberg",
        "tickers": ["V", "MA", "PYPL"],
        "sentiment": "positive",
        "event_type": "earnings",
        "relevance_score": 0.89,
    },
]

SOURCES = [
    "Financial Times", "Bloomberg", "Reuters", "Wall Street Journal",
    "CNBC", "Barron's", "The Economist", "MarketWatch", "Seeking Alpha",
]

SENTIMENT_OPTIONS = ["positive", "negative", "neutral"]


def _time_ago(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m ago"
    h = minutes // 60
    if h < 24:
        return f"{h}h ago"
    return f"{h // 24}d ago"


def get_market_news(limit: int = 10) -> list:
    """
    Return a list of recent market news articles.
    Articles are sorted by relevance and freshness.
    """
    rng = random.Random(42)
    news = []
    for i, article in enumerate(DEMO_NEWS[:limit]):
        time_offset = rng.randint(5, 240) + i * 15
        article_copy = dict(article)
        article_copy["published_at"] = _time_ago(time_offset)
        article_copy["id"] = f"news_{i:04d}"
        news.append(article_copy)
    return news[:limit]


def get_news(query: Optional[str] = None, ticker: Optional[str] = None, limit: int = 20) -> list:
    """
    Return filtered news. Can filter by ticker or free-text query.
    """
    all_news = get_market_news(limit=len(DEMO_NEWS))

    if ticker:
        ticker = ticker.upper()
        filtered = [n for n in all_news if ticker in n.get("tickers", [])]
        if not filtered:
            # Return generic market news for unknown tickers
            filtered = all_news[:5]
        all_news = filtered

    if query:
        q = query.lower()
        all_news = [n for n in all_news if q in n["headline"].lower() or q in n["summary"].lower()]

    return all_news[:limit]


def analyze_sentiment(text: str) -> dict:
    """
    Simple rule-based sentiment analyzer for financial text.
    Returns sentiment label and confidence score.
    """
    positive_words = {
        "beat", "exceed", "record", "growth", "profit", "win", "strong",
        "rally", "surge", "gain", "positive", "bullish", "upgrade", "outperform",
        "rise", "higher", "increase", "expand", "momentum", "opportunity",
    }
    negative_words = {
        "miss", "fall", "decline", "loss", "weak", "concern", "risk",
        "drop", "cut", "reduce", "downgrade", "underperform", "sell-off",
        "lower", "decrease", "contract", "pressure", "shortfall", "layoff",
    }

    words = set(text.lower().split())
    pos_count = len(words & positive_words)
    neg_count = len(words & negative_words)
    total = pos_count + neg_count

    if total == 0:
        return {"sentiment": "neutral", "confidence": 0.5, "positive_signals": 0, "negative_signals": 0}

    pos_ratio = pos_count / total
    if pos_ratio > 0.6:
        sentiment = "positive"
        confidence = min(0.5 + (pos_ratio - 0.5) * 1.5, 0.95)
    elif pos_ratio < 0.4:
        sentiment = "negative"
        confidence = min(0.5 + (0.5 - pos_ratio) * 1.5, 0.95)
    else:
        sentiment = "neutral"
        confidence = 0.55

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_signals": pos_count,
        "negative_signals": neg_count,
    }
