"""
FINIQ Market Data Service

Provides real market data via yfinance with intelligent demo/fallback mode.
When yfinance is unavailable or rate-limited, synthesizes realistic demo data
seeded from actual stock characteristics so the app always works.

This project is a prototype and is not financial advice.
"""

import os
import sys
import random
import math
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Demo stock universe — realistic ticker profiles
# ---------------------------------------------------------------------------

DEMO_STOCKS = {
    "AAPL": {"company": "Apple Inc.", "sector": "Technology", "base_price": 189.50, "volatility": 0.018, "trend": 0.0003},
    "MSFT": {"company": "Microsoft Corp.", "sector": "Technology", "base_price": 415.00, "volatility": 0.016, "trend": 0.0004},
    "GOOGL": {"company": "Alphabet Inc.", "sector": "Technology", "base_price": 175.30, "volatility": 0.019, "trend": 0.0003},
    "AMZN": {"company": "Amazon.com Inc.", "sector": "Consumer Disc.", "base_price": 195.80, "volatility": 0.021, "trend": 0.0003},
    "NVDA": {"company": "NVIDIA Corp.", "sector": "Technology", "base_price": 875.00, "volatility": 0.035, "trend": 0.0007},
    "META": {"company": "Meta Platforms Inc.", "sector": "Communication", "base_price": 530.00, "volatility": 0.024, "trend": 0.0005},
    "TSLA": {"company": "Tesla Inc.", "sector": "Consumer Disc.", "base_price": 248.00, "volatility": 0.045, "trend": 0.0001},
    "JPM":  {"company": "JPMorgan Chase", "sector": "Financials", "base_price": 215.00, "volatility": 0.014, "trend": 0.0002},
    "V":    {"company": "Visa Inc.", "sector": "Financials", "base_price": 285.00, "volatility": 0.012, "trend": 0.0002},
    "JNJ":  {"company": "Johnson & Johnson", "sector": "Healthcare", "base_price": 158.00, "volatility": 0.011, "trend": 0.0001},
    "UNH":  {"company": "UnitedHealth Group", "sector": "Healthcare", "base_price": 525.00, "volatility": 0.016, "trend": 0.0003},
    "HD":   {"company": "Home Depot Inc.", "sector": "Consumer Disc.", "base_price": 365.00, "volatility": 0.014, "trend": 0.0002},
    "PG":   {"company": "Procter & Gamble", "sector": "Consumer Staples", "base_price": 165.00, "volatility": 0.009, "trend": 0.0001},
    "MA":   {"company": "Mastercard Inc.", "sector": "Financials", "base_price": 480.00, "volatility": 0.013, "trend": 0.0003},
    "DIS":  {"company": "Walt Disney Co.", "sector": "Communication", "base_price": 115.00, "volatility": 0.022, "trend": 0.0001},
    "NFLX": {"company": "Netflix Inc.", "sector": "Communication", "base_price": 625.00, "volatility": 0.028, "trend": 0.0004},
    "AMD":  {"company": "Advanced Micro Devices", "sector": "Technology", "base_price": 165.00, "volatility": 0.038, "trend": 0.0005},
    "INTC": {"company": "Intel Corp.", "sector": "Technology", "base_price": 42.00, "volatility": 0.025, "trend": -0.0001},
    "CRM":  {"company": "Salesforce Inc.", "sector": "Technology", "base_price": 295.00, "volatility": 0.022, "trend": 0.0003},
    "PYPL": {"company": "PayPal Holdings", "sector": "Financials", "base_price": 68.00, "volatility": 0.028, "trend": -0.0001},
    "SPY":  {"company": "SPDR S&P 500 ETF", "sector": "ETF", "base_price": 510.00, "volatility": 0.010, "trend": 0.0003},
    "QQQ":  {"company": "Invesco QQQ Trust", "sector": "ETF", "base_price": 440.00, "volatility": 0.012, "trend": 0.0004},
    "GLD":  {"company": "SPDR Gold Shares", "sector": "Commodities", "base_price": 215.00, "volatility": 0.008, "trend": 0.0002},
    "BRK.B": {"company": "Berkshire Hathaway B", "sector": "Financials", "base_price": 365.00, "volatility": 0.012, "trend": 0.0002},
    "WMT":  {"company": "Walmart Inc.", "sector": "Consumer Staples", "base_price": 68.00, "volatility": 0.011, "trend": 0.0002},
}

MARKET_INDICES = [
    {"name": "S&P 500",   "ticker": "^GSPC", "base": 5200, "volatility": 0.009},
    {"name": "NASDAQ",    "ticker": "^IXIC", "base": 16400, "volatility": 0.012},
    {"name": "DOW JONES", "ticker": "^DJI",  "base": 39200, "volatility": 0.008},
    {"name": "VIX",       "ticker": "^VIX",  "base": 16.5,  "volatility": 0.04},
]

# ---------------------------------------------------------------------------
# Data synthesis helpers
# ---------------------------------------------------------------------------

def _seed_for(ticker: str, date: Optional[datetime] = None) -> int:
    """Deterministic seed so prices are stable across page reloads."""
    base = sum(ord(c) for c in ticker) * 37
    if date:
        base += date.year * 365 + date.timetuple().tm_yday
    return base % (2 ** 31)


def _make_ohlcv_series(ticker: str, days: int = 365) -> pd.DataFrame:
    """
    Synthesize a realistic OHLCV time series for the given ticker.
    Uses geometric Brownian motion with the ticker's volatility profile.
    """
    profile = DEMO_STOCKS.get(ticker.upper(), {
        "base_price": 100.0, "volatility": 0.02, "trend": 0.0002
    })
    rng = np.random.default_rng(_seed_for(ticker))

    base = profile["base_price"]
    vol = profile["volatility"]
    drift = profile["trend"]

    # Generate log-returns
    daily_returns = rng.normal(drift, vol, days)
    # Add occasional jumps (earnings, news events)
    jump_days = rng.choice(days, size=max(1, days // 30), replace=False)
    daily_returns[jump_days] += rng.normal(0, vol * 3, len(jump_days))

    prices = base * np.exp(np.cumsum(daily_returns))

    # Build OHLCV
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days + 1)
    dates = pd.bdate_range(start=start_date, end=end_date)[-days:]

    highs = prices * (1 + rng.uniform(0.001, vol, days))
    lows = prices * (1 - rng.uniform(0.001, vol, days))
    opens = np.roll(prices, 1)
    opens[0] = prices[0] * (1 - rng.uniform(0, 0.005))
    vol_base = base * 1_000_000
    volumes = rng.lognormal(np.log(vol_base), 0.5, days).astype(int)

    df = pd.DataFrame({
        "Date": dates,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": prices,
        "Volume": volumes,
    })
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    return df


def _get_latest_price(ticker: str) -> dict:
    """Get the most recent synthesized price for a ticker."""
    profile = DEMO_STOCKS.get(ticker.upper())
    if not profile:
        return _unknown_quote(ticker)

    df = _make_ohlcv_series(ticker, 5)
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    price = float(latest["Close"])
    prev_price = float(prev["Close"])
    change = price - prev_price
    change_pct = (change / prev_price) * 100

    return {
        "ticker": ticker.upper(),
        "company": profile["company"],
        "sector": profile["sector"],
        "price": round(price, 2),
        "prev_close": round(prev_price, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "open": round(float(latest["Open"]), 2),
        "high": round(float(latest["High"]), 2),
        "low": round(float(latest["Low"]), 2),
        "volume": int(latest["Volume"]),
        "avg_volume": int(df["Volume"].mean()),
        "market_cap": f"{price * random.randint(5, 500) / 1000:.1f}T" if price > 100 else f"{price * random.randint(1, 50):.0f}B",
        "pe_ratio": round(random.uniform(15, 45), 1),
        "52w_high": round(df["High"].max(), 2),
        "52w_low": round(df["Low"].min(), 2),
        "beta": round(profile["volatility"] / 0.012, 2),
        "data_source": "DEMO",
    }


def _unknown_quote(ticker: str) -> dict:
    """Fallback for unknown tickers."""
    rng = random.Random(_seed_for(ticker))
    price = rng.uniform(20, 400)
    change_pct = rng.uniform(-3, 3)
    change = price * change_pct / 100
    return {
        "ticker": ticker.upper(),
        "company": f"{ticker.upper()} Corp.",
        "sector": "Unknown",
        "price": round(price, 2),
        "prev_close": round(price - change, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "open": round(price * 0.998, 2),
        "high": round(price * 1.015, 2),
        "low": round(price * 0.985, 2),
        "volume": rng.randint(500_000, 10_000_000),
        "avg_volume": rng.randint(1_000_000, 20_000_000),
        "market_cap": "N/A",
        "pe_ratio": round(rng.uniform(10, 50), 1),
        "52w_high": round(price * 1.35, 2),
        "52w_low": round(price * 0.65, 2),
        "beta": round(rng.uniform(0.5, 2.0), 2),
        "data_source": "DEMO",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_quote(ticker: str) -> dict:
    """
    Get current quote for a ticker.
    Attempts live yfinance data first, falls back to synthesized demo data.
    """
    ticker = ticker.strip().upper()
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="2d", auto_adjust=True)
        if hist.empty or len(hist) < 2:
            raise ValueError("No data")
        price = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2])
        change = price - prev_close
        change_pct = (change / prev_close) * 100
        profile = DEMO_STOCKS.get(ticker, {})
        return {
            "ticker": ticker,
            "company": getattr(info, "long_name", None) or profile.get("company", ticker),
            "sector": profile.get("sector", "N/A"),
            "price": round(price, 2),
            "prev_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "open": round(float(hist["Open"].iloc[-1]), 2),
            "high": round(float(hist["High"].iloc[-1]), 2),
            "low": round(float(hist["Low"].iloc[-1]), 2),
            "volume": int(hist["Volume"].iloc[-1]) if "Volume" in hist else 0,
            "avg_volume": int(hist["Volume"].mean()) if "Volume" in hist else 0,
            "market_cap": getattr(info, "market_cap", "N/A"),
            "pe_ratio": getattr(info, "pe_ratio", None) or 0,
            "52w_high": getattr(info, "fifty_two_week_high", round(price * 1.3, 2)),
            "52w_low": getattr(info, "fifty_two_week_low", round(price * 0.7, 2)),
            "beta": getattr(info, "beta", 1.0) or 1.0,
            "data_source": "LIVE",
        }
    except Exception:
        return _get_latest_price(ticker)


def get_history(ticker: str, period: str = "1M") -> pd.DataFrame:
    """
    Get OHLCV history for a ticker.
    
    period: '1D', '5D', '1M', '3M', '6M', '1Y', '2Y', '5Y'
    Returns DataFrame with columns: Open, High, Low, Close, Volume
    If dates are present, train on earlier data and test on later data.
    """
    ticker = ticker.strip().upper()
    period_map = {
        "1D": 1, "5D": 5, "1W": 7, "1M": 30, "3M": 90,
        "6M": 180, "1Y": 365, "2Y": 730, "5Y": 1825, "MAX": 2000,
    }
    yf_period_map = {
        "1D": "5d", "5D": "1mo", "1W": "1mo", "1M": "3mo", "3M": "6mo",
        "6M": "1y", "1Y": "2y", "2Y": "5y", "5Y": "max", "MAX": "max",
    }
    days = period_map.get(period.upper(), 30)

    try:
        import yfinance as yf
        yf_period = yf_period_map.get(period.upper(), "3mo")
        df = yf.Ticker(ticker).history(period=yf_period, auto_adjust=True)
        if df.empty or len(df) < 10:
            raise ValueError("Insufficient data")
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.index.name = "Date"
        return df.sort_index()
    except Exception:
        return _make_ohlcv_series(ticker, max(days, 60))


def get_market_indices() -> list:
    """Get current values for major market indices."""
    results = []
    for idx in MARKET_INDICES:
        try:
            import yfinance as yf
            df = yf.Ticker(idx["ticker"]).history(period="2d", auto_adjust=True)
            if not df.empty and len(df) >= 2:
                price = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                change = price - prev
                change_pct = (change / prev) * 100
                results.append({
                    "name": idx["name"],
                    "ticker": idx["ticker"],
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "data_source": "LIVE",
                })
                continue
        except Exception:
            pass
        # Demo fallback
        rng = random.Random(_seed_for(idx["ticker"]))
        base = idx["base"]
        change_pct = rng.uniform(-1.5, 1.5)
        change = base * change_pct / 100
        results.append({
            "name": idx["name"],
            "ticker": idx["ticker"],
            "price": round(base + change, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "data_source": "DEMO",
        })
    return results


def get_top_movers(limit: int = 5) -> dict:
    """Return top gainers and losers from the demo stock universe."""
    quotes = []
    for ticker in list(DEMO_STOCKS.keys())[:20]:
        q = _get_latest_price(ticker)
        quotes.append(q)

    quotes.sort(key=lambda x: x["change_pct"])
    losers = quotes[:limit]
    gainers = sorted(quotes, key=lambda x: x["change_pct"], reverse=True)[:limit]

    for g in gainers:
        g["volume"] = f"{g['volume'] / 1_000_000:.1f}M"
        g["sentiment"] = "Bullish" if g["change_pct"] > 1 else "Positive"
    for l in losers:
        l["volume"] = f"{l['volume'] / 1_000_000:.1f}M"
        l["sentiment"] = "Bearish" if l["change_pct"] < -1 else "Negative"

    return {"gainers": gainers, "losers": losers}


def get_market_summary() -> dict:
    """Return a brief market summary dictionary."""
    indices = get_market_indices()
    sp500 = next((i for i in indices if "S&P" in i["name"]), indices[0])
    nasdaq = next((i for i in indices if "NASDAQ" in i["name"]), indices[1])
    vix = next((i for i in indices if "VIX" in i["name"]), {"price": 16.5})

    # Determine overall sentiment
    if sp500["change_pct"] > 0.5:
        overall = "Risk-On"
        sentiment_color = "#20C997"
    elif sp500["change_pct"] < -0.5:
        overall = "Risk-Off"
        sentiment_color = "#F06470"
    else:
        overall = "Neutral"
        sentiment_color = "#F5B942"

    adv = random.randint(1800, 2800)
    dec = 4000 - adv

    return {
        "overall_sentiment": overall,
        "sentiment_color": sentiment_color,
        "sp500_change_pct": sp500["change_pct"],
        "nasdaq_change_pct": nasdaq["change_pct"],
        "vix": vix.get("price", 16.5),
        "advancing_stocks": adv,
        "declining_stocks": dec,
        "volume_ratio": round(random.uniform(0.75, 1.35), 2),
        "key_events": [
            "Fed maintains rates; next FOMC in 6 weeks",
            "Tech sector earnings beat consensus by 4.2%",
            "Oil down 1.8% on demand concerns",
            "10Y Treasury yield at 4.32%, stable",
        ],
    }


def get_data_status() -> dict:
    """Return status of data sources."""
    live = False
    try:
        import yfinance as yf
        t = yf.Ticker("AAPL")
        h = t.history(period="1d")
        live = not h.empty
    except Exception:
        pass
    return {
        "live_data_available": live,
        "demo_mode": not live,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "coverage": f"{len(DEMO_STOCKS)} tickers in demo universe",
    }
