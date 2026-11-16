"""
FINIQ Portfolio Service

Manages user portfolio holdings, tracks P&L, and provides analytics.
Stores data in SQLite via the database module.

This project is a prototype and is not financial advice.
"""

import os
import sys

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.database.db import (
    get_portfolio as _db_get_portfolio,
    add_portfolio_holding,
    remove_portfolio_holding,
    update_portfolio_holding,
    init_db,
)
from backend.services.market_data import get_quote

# Ensure DB is initialized
init_db()


def get_portfolio() -> list:
    """
    Return the current portfolio holdings with live price enrichment.
    Each holding dict has: ticker, company, shares, avg_cost, current_price,
    market_value, unrealized_pnl, unrealized_pnl_pct, weight
    """
    holdings = _db_get_portfolio()
    if not holdings:
        return []

    total_value = 0.0
    enriched = []

    for h in holdings:
        ticker = h.get("ticker", "")
        shares = float(h.get("shares", 0))
        avg_cost = float(h.get("avg_cost", 0))

        quote = get_quote(ticker)
        price = quote.get("price", avg_cost)
        market_value = price * shares
        cost_basis = avg_cost * shares
        unrealized_pnl = market_value - cost_basis
        unrealized_pnl_pct = ((price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0

        total_value += market_value

        enriched.append({
            "ticker": ticker,
            "company": quote.get("company", ticker),
            "sector": quote.get("sector", "N/A"),
            "shares": shares,
            "avg_cost": round(avg_cost, 2),
            "current_price": round(price, 2),
            "market_value": round(market_value, 2),
            "cost_basis": round(cost_basis, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
            "day_change": quote.get("change", 0),
            "day_change_pct": quote.get("change_pct", 0),
            "weight": 0.0,  # will be computed below
        })

    # Compute weights
    for h in enriched:
        h["weight"] = round(h["market_value"] / total_value * 100, 1) if total_value > 0 else 0

    # Sort by market value descending
    enriched.sort(key=lambda x: x["market_value"], reverse=True)
    return enriched


def add_holding(ticker: str, shares: float, avg_cost: float, company: str = "") -> bool:
    """Add or update a portfolio holding."""
    ticker = ticker.strip().upper()
    if not company:
        try:
            q = get_quote(ticker)
            company = q.get("company", ticker)
        except Exception:
            company = ticker
    return add_portfolio_holding(ticker, company, shares, avg_cost)


def remove_holding(ticker: str) -> bool:
    """Remove a holding from the portfolio."""
    return remove_portfolio_holding(ticker.strip().upper())


def get_portfolio_summary() -> dict:
    """
    Return aggregate portfolio metrics.
    """
    holdings = get_portfolio()
    if not holdings:
        return {
            "total_value": 0.0,
            "total_cost": 0.0,
            "total_pnl": 0.0,
            "total_pnl_pct": 0.0,
            "num_holdings": 0,
            "day_pnl": 0.0,
        }

    total_value = sum(h["market_value"] for h in holdings)
    total_cost = sum(h["cost_basis"] for h in holdings)
    total_pnl = total_value - total_cost
    total_pnl_pct = ((total_pnl / total_cost) * 100) if total_cost > 0 else 0
    day_pnl = sum(h["day_change"] * h["shares"] for h in holdings)

    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "num_holdings": len(holdings),
        "day_pnl": round(day_pnl, 2),
    }
