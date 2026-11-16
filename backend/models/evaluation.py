"""
FINIQ Prediction Performance Evaluator

Tracks and evaluates the accuracy of FINIQ's directional predictions.
Distinguishes between backtested and live forward-tested results.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
import math
from datetime import datetime, timedelta, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Performance Summary
# ---------------------------------------------------------------------------

def get_performance_summary(predictions: list) -> dict:
    """
    Calculate performance metrics from prediction history.

    Returns:
    {
        total_predictions: int,
        resolved_predictions: int,
        directional_accuracy: float,
        precision: dict,
        recall: dict,
        f1_score: dict,
        avg_confidence: float,
        confidence_calibration: float,
        by_ticker: dict,
        by_horizon: dict,
        backtest_accuracy: float,
        live_accuracy: float,
        vs_baseline: dict,
    }
    """
    if not predictions:
        return _empty_performance()

    total = len(predictions)
    resolved = [p for p in predictions if p.get('actual_direction') is not None]
    n_resolved = len(resolved)

    if n_resolved == 0:
        return {
            **_empty_performance(),
            'total_predictions': total,
            'avg_confidence': _safe_mean([p.get('confidence', 0) for p in predictions]),
        }

    # ---- Overall accuracy ----
    correct = [p for p in resolved if p.get('predicted_direction') == p.get('actual_direction')]
    directional_accuracy = len(correct) / n_resolved

    # ---- Per-class precision / recall / F1 ----
    classes = ['BULLISH', 'BEARISH', 'NEUTRAL']
    precision, recall, f1 = {}, {}, {}

    for cls in classes:
        tp = sum(1 for p in resolved
                 if p.get('predicted_direction') == cls and p.get('actual_direction') == cls)
        fp = sum(1 for p in resolved
                 if p.get('predicted_direction') == cls and p.get('actual_direction') != cls)
        fn = sum(1 for p in resolved
                 if p.get('predicted_direction') != cls and p.get('actual_direction') == cls)

        prec   = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_val = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

        precision[cls] = round(prec,   4)
        recall[cls]    = round(rec,    4)
        f1[cls]        = round(f1_val, 4)

    # ---- Avg confidence ----
    avg_confidence = _safe_mean([p.get('confidence', 0) for p in resolved])

    # ---- Confidence calibration (Brier score style — lower is better) ----
    # We express it as 1 - brier_scaled so higher is better (like accuracy)
    brier_scores = []
    for p in resolved:
        conf  = p.get('confidence', 0.5)
        is_ok = 1.0 if p.get('predicted_direction') == p.get('actual_direction') else 0.0
        brier_scores.append((conf - is_ok) ** 2)
    confidence_calibration = round(1.0 - _safe_mean(brier_scores), 4)

    # ---- By ticker ----
    by_ticker: dict = {}
    ticker_groups: dict = {}
    for p in resolved:
        t = p.get('ticker', 'UNKNOWN')
        ticker_groups.setdefault(t, []).append(p)
    for t, group in ticker_groups.items():
        t_correct = sum(1 for p in group if p.get('predicted_direction') == p.get('actual_direction'))
        by_ticker[t] = {
            'total':    len(group),
            'correct':  t_correct,
            'accuracy': round(t_correct / len(group), 4),
        }

    # ---- By horizon ----
    by_horizon: dict = {}
    horizon_groups: dict = {}
    for p in resolved:
        h = p.get('horizon', 'UNKNOWN')
        horizon_groups.setdefault(h, []).append(p)
    for h, group in horizon_groups.items():
        h_correct = sum(1 for p in group if p.get('predicted_direction') == p.get('actual_direction'))
        by_horizon[h] = {
            'total':    len(group),
            'correct':  h_correct,
            'accuracy': round(h_correct / len(group), 4),
        }

    # ---- Backtest vs live accuracy ----
    backtest_preds = [p for p in resolved if p.get('is_backtest', False)]
    live_preds     = [p for p in resolved if not p.get('is_backtest', False)]

    backtest_accuracy = (
        sum(1 for p in backtest_preds if p.get('predicted_direction') == p.get('actual_direction')) / len(backtest_preds)
        if backtest_preds else None
    )
    live_accuracy = (
        sum(1 for p in live_preds if p.get('predicted_direction') == p.get('actual_direction')) / len(live_preds)
        if live_preds else None
    )

    # ---- vs Baseline ----
    # Baseline 1: always predict NEUTRAL
    neutral_correct = sum(1 for p in resolved if p.get('actual_direction') == 'NEUTRAL')
    neutral_baseline_acc = neutral_correct / n_resolved

    # Baseline 2: majority class baseline
    actual_dirs = [p.get('actual_direction') for p in resolved]
    majority = max(set(actual_dirs), key=actual_dirs.count) if actual_dirs else 'NEUTRAL'
    majority_count = actual_dirs.count(majority) if actual_dirs else 0
    majority_baseline_acc = majority_count / n_resolved if n_resolved else 0

    vs_baseline = {
        'vs_always_neutral': round(directional_accuracy - neutral_baseline_acc, 4),
        'vs_majority_class': round(directional_accuracy - majority_baseline_acc, 4),
        'majority_class':    majority,
        'neutral_baseline_accuracy': round(neutral_baseline_acc, 4),
        'majority_baseline_accuracy': round(majority_baseline_acc, 4),
    }

    return {
        'total_predictions':    total,
        'resolved_predictions': n_resolved,
        'directional_accuracy': round(directional_accuracy, 4),
        'precision':            precision,
        'recall':               recall,
        'f1_score':             f1,
        'avg_confidence':       round(avg_confidence, 4),
        'confidence_calibration': confidence_calibration,
        'by_ticker':            by_ticker,
        'by_horizon':           by_horizon,
        'backtest_accuracy':    round(backtest_accuracy, 4) if backtest_accuracy is not None else None,
        'live_accuracy':        round(live_accuracy,     4) if live_accuracy     is not None else None,
        'vs_baseline':          vs_baseline,
    }


def _empty_performance() -> dict:
    return {
        'total_predictions':    0,
        'resolved_predictions': 0,
        'directional_accuracy': 0.0,
        'precision':            {'BULLISH': 0.0, 'BEARISH': 0.0, 'NEUTRAL': 0.0},
        'recall':               {'BULLISH': 0.0, 'BEARISH': 0.0, 'NEUTRAL': 0.0},
        'f1_score':             {'BULLISH': 0.0, 'BEARISH': 0.0, 'NEUTRAL': 0.0},
        'avg_confidence':       0.0,
        'confidence_calibration': 0.0,
        'by_ticker':            {},
        'by_horizon':           {},
        'backtest_accuracy':    None,
        'live_accuracy':        None,
        'vs_baseline':          {},
    }


def _safe_mean(values: list) -> float:
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else 0.0


# ---------------------------------------------------------------------------
# Demo Prediction History
# ---------------------------------------------------------------------------

def generate_demo_prediction_history() -> list:
    """
    Generate realistic demo prediction history for display purposes.

    Returns 50 predictions with:
    - Various tickers
    - Mix of BULLISH/BEARISH/NEUTRAL
    - Mix of correct/incorrect outcomes
    - Realistic confidence values (0.45–0.80)
    - Timestamps spread over past 90 days

    Directional accuracy ~58-65% (realistic for ML models).
    """
    rng = random.Random(42)  # fixed seed for reproducibility

    tickers  = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA', 'META', 'JPM', 'BAC', 'AMD']
    horizons = ['1D', '5D', '1W', '2W', '1M']
    directions_pool = ['BULLISH', 'BEARISH', 'NEUTRAL']

    # We want ~60% accuracy, so for each prediction we decide if it's correct
    # and derive actual_direction accordingly
    predictions = []
    now = datetime.now(timezone.utc)

    for i in range(50):
        ticker    = rng.choice(tickers)
        horizon   = rng.choice(horizons)
        predicted = rng.choices(directions_pool, weights=[0.45, 0.35, 0.20], k=1)[0]

        # 60% chance correct
        is_correct = rng.random() < 0.60
        if is_correct:
            actual = predicted
        else:
            others = [d for d in directions_pool if d != predicted]
            actual = rng.choice(others)

        # Confidence: higher when model was correct (realistic bias)
        base_conf = rng.uniform(0.48, 0.72)
        confidence = min(0.88, base_conf + (0.06 if is_correct else -0.03))
        confidence = max(0.40, confidence)

        # Timestamp: spread over last 90 days, resolved if >horizon days ago
        days_ago = rng.randint(1, 90)
        created_at = now - timedelta(days=days_ago)

        # Only mark as resolved if enough time has passed for the horizon
        horizon_days = {'1D': 1, '5D': 5, '1W': 7, '2W': 14, '1M': 30}
        h_days = horizon_days.get(horizon, 5)
        is_resolved = days_ago >= h_days

        is_backtest = days_ago > 30

        pred = {
            'id':                   i + 1,
            'ticker':               ticker,
            'horizon':              horizon,
            'predicted_direction':  predicted,
            'actual_direction':     actual if is_resolved else None,
            'confidence':           round(confidence, 4),
            'is_correct':           is_correct if is_resolved else None,
            'created_at':           created_at.isoformat(),
            'resolved_at':          (created_at + timedelta(days=h_days)).isoformat() if is_resolved else None,
            'is_backtest':          is_backtest,
            'model_version':        '1.0.0',
        }
        predictions.append(pred)

    # Sort newest first
    predictions.sort(key=lambda p: p['created_at'], reverse=True)
    return predictions


# ---------------------------------------------------------------------------
# Chart Data
# ---------------------------------------------------------------------------

def get_performance_charts_data(predictions: list) -> dict:
    """
    Prepare data for performance visualization charts.
    Returns chart-ready data for Plotly.
    """
    if not predictions:
        return {}

    resolved = [p for p in predictions if p.get('actual_direction') is not None]
    if not resolved:
        return {}

    # ---- 1. Rolling accuracy (time series) ----
    resolved_sorted = sorted(resolved, key=lambda p: p.get('created_at', ''))
    rolling_window = 10
    rolling_accuracy = []
    for i in range(len(resolved_sorted)):
        window = resolved_sorted[max(0, i - rolling_window + 1): i + 1]
        correct = sum(1 for p in window if p.get('predicted_direction') == p.get('actual_direction'))
        rolling_accuracy.append({
            'date':     resolved_sorted[i].get('created_at', ''),
            'accuracy': round(correct / len(window), 4),
        })

    # ---- 2. Accuracy by confidence bucket ----
    buckets = [
        ('0.40–0.49', 0.40, 0.50),
        ('0.50–0.59', 0.50, 0.60),
        ('0.60–0.69', 0.60, 0.70),
        ('0.70–0.79', 0.70, 0.80),
        ('0.80+',     0.80, 1.01),
    ]
    confidence_calibration = []
    for label, lo, hi in buckets:
        bucket_preds = [p for p in resolved if lo <= p.get('confidence', 0) < hi]
        if bucket_preds:
            correct = sum(1 for p in bucket_preds if p.get('predicted_direction') == p.get('actual_direction'))
            acc = correct / len(bucket_preds)
        else:
            acc = 0.0
        confidence_calibration.append({
            'bucket':   label,
            'accuracy': round(acc, 4),
            'count':    len(bucket_preds),
        })

    # ---- 3. Direction distribution ----
    pred_dirs   = [p.get('predicted_direction') for p in resolved]
    actual_dirs = [p.get('actual_direction')    for p in resolved]
    direction_distribution = {
        'predicted': {
            'BULLISH': pred_dirs.count('BULLISH'),
            'BEARISH': pred_dirs.count('BEARISH'),
            'NEUTRAL': pred_dirs.count('NEUTRAL'),
        },
        'actual': {
            'BULLISH': actual_dirs.count('BULLISH'),
            'BEARISH': actual_dirs.count('BEARISH'),
            'NEUTRAL': actual_dirs.count('NEUTRAL'),
        },
    }

    # ---- 4. Accuracy by ticker ----
    ticker_perf: dict = {}
    for p in resolved:
        t = p.get('ticker', 'UNKNOWN')
        ticker_perf.setdefault(t, {'correct': 0, 'total': 0})
        ticker_perf[t]['total'] += 1
        if p.get('predicted_direction') == p.get('actual_direction'):
            ticker_perf[t]['correct'] += 1
    accuracy_by_ticker = [
        {'ticker': t, 'accuracy': round(v['correct'] / v['total'], 4), 'count': v['total']}
        for t, v in ticker_perf.items()
    ]
    accuracy_by_ticker.sort(key=lambda x: x['accuracy'], reverse=True)

    return {
        'rolling_accuracy':          rolling_accuracy,
        'confidence_calibration':    confidence_calibration,
        'direction_distribution':    direction_distribution,
        'accuracy_by_ticker':        accuracy_by_ticker,
    }


# ---------------------------------------------------------------------------
# Confusion Matrix
# ---------------------------------------------------------------------------

def get_confusion_matrix_data(predictions: list) -> dict:
    """
    Calculate confusion matrix for resolved predictions.

    Returns:
    {
        matrix: list[list[int]],     # 3x3 [actual][predicted]
        labels: ['BULLISH', 'BEARISH', 'NEUTRAL'],
        normalized: list[list[float]],
        total: int,
    }
    """
    resolved = [p for p in predictions if p.get('actual_direction') is not None]
    classes  = ['BULLISH', 'BEARISH', 'NEUTRAL']
    n = len(classes)
    matrix = [[0] * n for _ in range(n)]

    for p in resolved:
        actual    = p.get('actual_direction')
        predicted = p.get('predicted_direction')
        if actual in classes and predicted in classes:
            i = classes.index(actual)
            j = classes.index(predicted)
            matrix[i][j] += 1

    # Row-normalized matrix (recall view)
    normalized = []
    for row in matrix:
        total_row = sum(row)
        if total_row > 0:
            normalized.append([round(v / total_row, 4) for v in row])
        else:
            normalized.append([0.0] * n)

    return {
        'matrix':     matrix,
        'labels':     classes,
        'normalized': normalized,
        'total':      len(resolved),
    }
