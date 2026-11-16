"""
FINIQ SQLite Database Layer

Persistent storage for: settings, watchlist, portfolio, and predictions.
Uses SQLite for zero-dependency deployment.

This project is a prototype and is not financial advice.
"""

import os
import sqlite3
import json
import threading
from datetime import datetime, timezone
from typing import Optional, Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_PATH = os.path.join(DB_DIR, "finiq.db")

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """Get a thread-local database connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(DB_DIR, exist_ok=True)
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_db():
    """Create all tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            ticker     TEXT PRIMARY KEY,
            company    TEXT,
            added_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS portfolio (
            ticker     TEXT PRIMARY KEY,
            company    TEXT,
            shares     REAL NOT NULL,
            avg_cost   REAL NOT NULL,
            added_at   TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id                   TEXT PRIMARY KEY,
            ticker               TEXT NOT NULL,
            predicted_direction  TEXT NOT NULL,
            confidence           REAL NOT NULL,
            horizon              TEXT NOT NULL,
            predicted_at         TEXT NOT NULL,
            actual_direction     TEXT,
            resolved_at          TEXT,
            features             TEXT,
            notes                TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_predictions_ticker ON predictions(ticker);
        CREATE INDEX IF NOT EXISTS idx_predictions_predicted_at ON predictions(predicted_at);
    """)
    conn.commit()
    _seed_default_data(conn)


def _seed_default_data(conn: sqlite3.Connection):
    """Add sample data if the database is brand new."""
    # Default watchlist
    defaults = [
        ("AAPL", "Apple Inc."),
        ("NVDA", "NVIDIA Corp."),
        ("MSFT", "Microsoft Corp."),
        ("TSLA", "Tesla Inc."),
    ]
    for ticker, company in defaults:
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (ticker, company) VALUES (?, ?)",
            (ticker, company)
        )

    # Default portfolio holdings
    portfolio_defaults = [
        ("AAPL", "Apple Inc.", 50.0, 145.00),
        ("MSFT", "Microsoft Corp.", 20.0, 285.00),
        ("NVDA", "NVIDIA Corp.", 15.0, 480.00),
        ("JPM",  "JPMorgan Chase", 30.0, 175.00),
    ]
    for ticker, company, shares, cost in portfolio_defaults:
        conn.execute(
            "INSERT OR IGNORE INTO portfolio (ticker, company, shares, avg_cost) VALUES (?, ?, ?, ?)",
            (ticker, company, shares, cost)
        )

    conn.commit()


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value by key."""
    conn = _get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default
    try:
        return json.loads(row["value"])
    except (json.JSONDecodeError, TypeError):
        return row["value"]


def set_setting(key: str, value: Any) -> bool:
    """Set a setting value."""
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))",
            (key, json.dumps(value))
        )
        conn.commit()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Watchlist
# ---------------------------------------------------------------------------

def get_watchlist() -> list:
    """Return all watchlist items."""
    conn = _get_conn()
    rows = conn.execute("SELECT ticker, company, added_at FROM watchlist ORDER BY added_at DESC").fetchall()
    return [dict(r) for r in rows]


def add_to_watchlist(ticker: str, company: str = "") -> bool:
    """Add a ticker to the watchlist."""
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (ticker, company) VALUES (?, ?)",
            (ticker.upper(), company)
        )
        conn.commit()
        return True
    except Exception:
        return False


def remove_from_watchlist(ticker: str) -> bool:
    """Remove a ticker from the watchlist."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker.upper(),))
        conn.commit()
        return True
    except Exception:
        return False


def is_in_watchlist(ticker: str) -> bool:
    """Check if a ticker is in the watchlist."""
    conn = _get_conn()
    row = conn.execute("SELECT 1 FROM watchlist WHERE ticker = ?", (ticker.upper(),)).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

def get_portfolio() -> list:
    """Return all portfolio holdings."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT ticker, company, shares, avg_cost, added_at FROM portfolio ORDER BY ticker"
    ).fetchall()
    return [dict(r) for r in rows]


def add_portfolio_holding(ticker: str, company: str, shares: float, avg_cost: float) -> bool:
    """Add or update a portfolio holding."""
    conn = _get_conn()
    try:
        conn.execute("""
            INSERT INTO portfolio (ticker, company, shares, avg_cost, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(ticker) DO UPDATE SET
                shares = excluded.shares,
                avg_cost = excluded.avg_cost,
                updated_at = datetime('now')
        """, (ticker.upper(), company, shares, avg_cost))
        conn.commit()
        return True
    except Exception:
        return False


def remove_portfolio_holding(ticker: str) -> bool:
    """Remove a holding from the portfolio."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker.upper(),))
        conn.commit()
        return True
    except Exception:
        return False


def update_portfolio_holding(ticker: str, shares: float = None, avg_cost: float = None) -> bool:
    """Partially update a portfolio holding."""
    conn = _get_conn()
    try:
        if shares is not None and avg_cost is not None:
            conn.execute(
                "UPDATE portfolio SET shares=?, avg_cost=?, updated_at=datetime('now') WHERE ticker=?",
                (shares, avg_cost, ticker.upper())
            )
        elif shares is not None:
            conn.execute(
                "UPDATE portfolio SET shares=?, updated_at=datetime('now') WHERE ticker=?",
                (shares, ticker.upper())
            )
        elif avg_cost is not None:
            conn.execute(
                "UPDATE portfolio SET avg_cost=?, updated_at=datetime('now') WHERE ticker=?",
                (avg_cost, ticker.upper())
            )
        conn.commit()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

def save_prediction(prediction: dict) -> bool:
    """Save a prediction record to the database."""
    conn = _get_conn()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO predictions
            (id, ticker, predicted_direction, confidence, horizon, predicted_at, features, notes)
            VALUES (:id, :ticker, :predicted_direction, :confidence, :horizon, :predicted_at, :features, :notes)
        """, {
            "id": prediction.get("id", f"{prediction['ticker']}_{prediction['predicted_at']}"),
            "ticker": prediction["ticker"],
            "predicted_direction": prediction["predicted_direction"],
            "confidence": prediction["confidence"],
            "horizon": prediction.get("horizon", "1M"),
            "predicted_at": prediction.get("predicted_at", datetime.now(timezone.utc).isoformat()),
            "features": json.dumps(prediction.get("features", {})),
            "notes": prediction.get("notes", ""),
        })
        conn.commit()
        return True
    except Exception:
        return False


def get_predictions(ticker: Optional[str] = None, limit: int = 100) -> list:
    """Return prediction history, optionally filtered by ticker."""
    conn = _get_conn()
    if ticker:
        rows = conn.execute(
            "SELECT * FROM predictions WHERE ticker = ? ORDER BY predicted_at DESC LIMIT ?",
            (ticker.upper(), limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY predicted_at DESC LIMIT ?",
            (limit,)
        ).fetchall()

    result = []
    for row in rows:
        d = dict(row)
        try:
            d["features"] = json.loads(d.get("features", "{}") or "{}")
        except Exception:
            d["features"] = {}
        result.append(d)
    return result


def resolve_prediction(prediction_id: str, actual_direction: str) -> bool:
    """Mark a prediction as resolved with the actual outcome."""
    conn = _get_conn()
    try:
        conn.execute("""
            UPDATE predictions
            SET actual_direction = ?, resolved_at = datetime('now')
            WHERE id = ?
        """, (actual_direction, prediction_id))
        conn.commit()
        return True
    except Exception:
        return False


# Initialize on import
init_db()
