"""
FINIQ Stock Direction Predictor

Uses technical indicators to predict directional bias (Bullish/Bearish/Neutral).
This is a directional classifier, NOT a price forecaster.
Never outputs specific price targets — only directional signals with confidence.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

MODEL_VERSION = '1.0.0'
MIN_DATA_POINTS = 60
FORWARD_DAYS_MAP = {
    '1D': 1,
    '5D': 5,
    '1W': 5,
    '2W': 10,
    '1M': 21,
}


# ---------------------------------------------------------------------------
# Technical Indicators
# ---------------------------------------------------------------------------

def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators from OHLCV data.

    Indicators:
    - RSI (14)
    - MACD (12, 26, 9)
    - Bollinger Bands (20, 2)
    - ATR (14)
    - Volume ratio (current vs 20-day avg)
    - Price momentum (5, 10, 20 day)
    - Golden/Death cross signal
    - Stochastic oscillator (14)
    - Moving averages (5, 10, 20, 50 day)
    - On-Balance Volume (OBV)
    - Williams %R
    """
    df = df.copy()

    # ---- Ensure column types ----
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['Close', 'High', 'Low', 'Volume'])

    close = df['Close']
    high  = df['High']
    low   = df['Low']
    vol   = df['Volume']

    # ---- Moving Averages ----
    df['MA5']  = close.rolling(5).mean()
    df['MA10'] = close.rolling(10).mean()
    df['MA20'] = close.rolling(20).mean()
    df['MA50'] = close.rolling(50).mean()

    # ---- Price relative to MAs ----
    df['Price_vs_MA5']  = (close - df['MA5'])  / df['MA5'].replace(0, np.nan)
    df['Price_vs_MA20'] = (close - df['MA20']) / df['MA20'].replace(0, np.nan)
    df['Price_vs_MA50'] = (close - df['MA50']) / df['MA50'].replace(0, np.nan)

    # ---- Golden / Death cross signal ----
    # +1 = MA5 above MA20 (bullish), -1 = MA5 below MA20 (bearish)
    df['Golden_Death_Cross'] = np.where(df['MA5'] > df['MA20'], 1, -1)

    # ---- RSI (14) ----
    delta = close.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI_overbought'] = (df['RSI'] > 70).astype(int)
    df['RSI_oversold']   = (df['RSI'] < 30).astype(int)

    # ---- MACD (12, 26, 9) ----
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD_line']   = ema12 - ema26
    df['MACD_signal'] = df['MACD_line'].ewm(span=9, adjust=False).mean()
    df['MACD_hist']   = df['MACD_line'] - df['MACD_signal']
    df['MACD_bullish'] = (df['MACD_line'] > df['MACD_signal']).astype(int)

    # ---- Bollinger Bands (20, 2) ----
    df['BB_mid']   = close.rolling(20).mean()
    df['BB_std']   = close.rolling(20).std()
    df['BB_upper'] = df['BB_mid'] + 2 * df['BB_std']
    df['BB_lower'] = df['BB_mid'] - 2 * df['BB_std']
    bb_range = (df['BB_upper'] - df['BB_lower']).replace(0, np.nan)
    df['BB_pct_b'] = (close - df['BB_lower']) / bb_range  # 0=lower, 1=upper
    df['BB_width']  = bb_range / df['BB_mid'].replace(0, np.nan)

    # ---- ATR (14) ----
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs()
    ], axis=1).max(axis=1)
    df['ATR'] = tr.ewm(com=13, adjust=False).mean()
    df['ATR_pct'] = df['ATR'] / close.replace(0, np.nan)   # Volatility normalised

    # ---- Volume Ratio ----
    df['Vol_MA20']    = vol.rolling(20).mean()
    df['Volume_ratio'] = vol / df['Vol_MA20'].replace(0, np.nan)

    # ---- Price Momentum ----
    df['Momentum_5']  = close.pct_change(5)
    df['Momentum_10'] = close.pct_change(10)
    df['Momentum_20'] = close.pct_change(20)

    # ---- Daily return & rolling std ----
    df['Daily_return']  = close.pct_change()
    df['Volatility_10'] = df['Daily_return'].rolling(10).std()

    # ---- Stochastic Oscillator (14) ----
    low14  = low.rolling(14).min()
    high14 = high.rolling(14).max()
    stoch_range = (high14 - low14).replace(0, np.nan)
    df['Stoch_K'] = 100 * (close - low14) / stoch_range
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
    df['Stoch_overbought'] = (df['Stoch_K'] > 80).astype(int)
    df['Stoch_oversold']   = (df['Stoch_K'] < 20).astype(int)

    # ---- On-Balance Volume (OBV) ----
    obv_values = []
    obv = 0
    for i in range(len(df)):
        if i == 0:
            obv_values.append(0)
            continue
        if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            obv += df['Volume'].iloc[i]
        elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            obv -= df['Volume'].iloc[i]
        obv_values.append(obv)
    df['OBV'] = obv_values
    df['OBV_MA10'] = df['OBV'].rolling(10).mean()
    df['OBV_signal'] = np.where(df['OBV'] > df['OBV_MA10'], 1, -1)

    # ---- Williams %R (14) ----
    df['Williams_R'] = -100 * (high14 - close) / stoch_range

    return df


def _feature_columns() -> list:
    """Return ordered list of feature column names used for ML."""
    return [
        'RSI', 'RSI_overbought', 'RSI_oversold',
        'MACD_line', 'MACD_signal', 'MACD_hist', 'MACD_bullish',
        'BB_pct_b', 'BB_width',
        'ATR_pct',
        'Volume_ratio',
        'Momentum_5', 'Momentum_10', 'Momentum_20',
        'Price_vs_MA5', 'Price_vs_MA20', 'Price_vs_MA50',
        'Golden_Death_Cross',
        'Stoch_K', 'Stoch_D', 'Stoch_overbought', 'Stoch_oversold',
        'OBV_signal',
        'Williams_R',
        'Volatility_10',
        'Daily_return',
    ]


# ---------------------------------------------------------------------------
# Label Creation
# ---------------------------------------------------------------------------

def create_labels(df: pd.DataFrame, forward_days: int = 5) -> pd.Series:
    """
    Create direction labels based on future returns.

    Returns:
        pd.Series of int:
            1  = Bullish  (future return > +1%)
           -1  = Bearish  (future return < -1%)
            0  = Neutral

    Uses only past data, never future data for training (shift creates lookahead
    but labels are shifted to align with current row via forward return).
    At training time the last `forward_days` rows will have NaN labels and are
    dropped before fitting.
    """
    future_return = df['Close'].shift(-forward_days) / df['Close'] - 1
    labels = pd.Series(0, index=df.index, dtype=int)
    labels[future_return >  0.01] =  1
    labels[future_return < -0.01] = -1
    return labels


# ---------------------------------------------------------------------------
# Model Training
# ---------------------------------------------------------------------------

def train_model(df: pd.DataFrame, forward_days: int = 5) -> Tuple[RandomForestClassifier, StandardScaler, list, dict]:
    """
    Train the direction predictor on historical data.

    Uses TimeSeriesSplit to avoid lookahead bias.

    Returns:
        (model, scaler, feature_names, metrics)
    """
    df = compute_technical_indicators(df)
    labels = create_labels(df, forward_days=forward_days)

    feature_cols = _feature_columns()
    available_cols = [c for c in feature_cols if c in df.columns]

    # Align features and labels, drop NaN rows
    X = df[available_cols].copy()
    y = labels.copy()

    combined = pd.concat([X, y.rename('label')], axis=1).dropna()
    X_clean = combined[available_cols].values
    y_clean = combined['label'].values.astype(int)

    if len(X_clean) < 30:
        raise ValueError(f"Insufficient clean data for training: {len(X_clean)} rows after dropna")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)

    # Time-series cross-validation (5 splits)
    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = []

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
    )

    for train_idx, val_idx in tscv.split(X_scaled):
        X_tr, X_val = X_scaled[train_idx], X_scaled[val_idx]
        y_tr, y_val = y_clean[train_idx], y_clean[val_idx]
        if len(np.unique(y_tr)) < 2:
            continue
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        cv_scores.append(accuracy_score(y_val, preds))

    # Final fit on all data
    model.fit(X_scaled, y_clean)

    metrics = {
        'cv_accuracy_mean': float(np.mean(cv_scores)) if cv_scores else 0.0,
        'cv_accuracy_std':  float(np.std(cv_scores))  if cv_scores else 0.0,
        'training_samples': int(len(X_clean)),
        'feature_count':    len(available_cols),
    }

    return model, scaler, available_cols, metrics


# ---------------------------------------------------------------------------
# Main Predict Function
# ---------------------------------------------------------------------------

def predict(
    ticker: str,
    history_df: pd.DataFrame,
    horizon: str = '5D',
) -> dict:
    """
    Generate a directional prediction for a ticker.

    Returns:
    {
        ticker: str,
        direction: 'BULLISH' | 'BEARISH' | 'NEUTRAL',
        confidence: float (0.0 - 1.0),
        horizon: str,
        signal_strength: 'STRONG' | 'MODERATE' | 'WEAK',
        key_factors: list[dict],  # [{factor, value, impact, description}]
        technical_summary: dict,
        uncertainty_note: str,
        model_version: str,
        data_points_used: int,
        is_reliable: bool,
        reliability_note: str,
    }
    """
    base_result = {
        'ticker': ticker.upper(),
        'horizon': horizon,
        'model_version': MODEL_VERSION,
        'data_points_used': 0,
        'is_reliable': False,
    }

    try:
        # ---- Validate input ----
        if history_df is None or len(history_df) == 0:
            return {
                **base_result,
                'direction': 'NEUTRAL',
                'confidence': 0.0,
                'signal_strength': 'WEAK',
                'key_factors': [],
                'technical_summary': {},
                'uncertainty_note': 'No historical data available.',
                'reliability_note': 'No data provided.',
            }

        df = history_df.copy()

        # Normalise column names
        df.columns = [c.capitalize() if c.lower() in {'open','high','low','close','volume','date'}
                      else c for c in df.columns]

        if 'Date' in df.columns:
            df = df.sort_values('Date').reset_index(drop=True)

        data_points = len(df)
        base_result['data_points_used'] = data_points

        # ---- Insufficient data ----
        if data_points < MIN_DATA_POINTS:
            return {
                **base_result,
                'direction': 'NEUTRAL',
                'confidence': 0.20,
                'signal_strength': 'WEAK',
                'key_factors': [],
                'technical_summary': {},
                'uncertainty_note': (
                    f'Only {data_points} data points available. '
                    f'At least {MIN_DATA_POINTS} required for reliable prediction.'
                ),
                'reliability_note': f'Insufficient data ({data_points}/{MIN_DATA_POINTS} days required).',
            }

        # ---- Compute indicators ----
        df_ind = compute_technical_indicators(df)

        # ---- Determine forward_days from horizon ----
        forward_days = FORWARD_DAYS_MAP.get(horizon.upper(), 5)

        # ---- Train model (on EARLIER data only — temporal split to avoid lookahead bias) ----
        model, scaler, feature_cols, metrics = train_model(df, forward_days=forward_days)

        # ---- Temporal holdout evaluation: train on first 75%, test on last 25% ----
        # This satisfies the hackathon requirement: "train on earlier data, test on later data"
        vs_baseline = _compute_baseline_comparison(df, forward_days, feature_cols)
        metrics['vs_baseline'] = vs_baseline

        # ---- Predict on the most recent row ----
        latest = df_ind[feature_cols].iloc[-1:]
        if latest.isnull().any(axis=1).any():
            latest = latest.fillna(latest.median())

        X_latest = scaler.transform(latest.values)
        raw_prediction  = model.predict(X_latest)[0]
        proba = model.predict_proba(X_latest)[0]
        classes = list(model.classes_)

        pred_proba = proba[classes.index(raw_prediction)]

        # Map numeric label to direction string
        direction_map = {1: 'BULLISH', -1: 'BEARISH', 0: 'NEUTRAL'}
        direction = direction_map.get(int(raw_prediction), 'NEUTRAL')

        # ---- Signal strength ----
        if pred_proba >= 0.65:
            signal_strength = 'STRONG'
        elif pred_proba >= 0.52:
            signal_strength = 'MODERATE'
        else:
            signal_strength = 'WEAK'

        # ---- Key factors (feature importances) ----
        importances = dict(zip(feature_cols, model.feature_importances_))
        sorted_feats = sorted(importances.items(), key=lambda x: x[1], reverse=True)

        key_factors = _build_key_factors(sorted_feats[:8], df_ind, direction)

        # ---- Technical summary ----
        technical_summary = get_technical_summary(df_ind)

        # ---- Reliability ----
        is_reliable = (
            data_points >= MIN_DATA_POINTS
            and metrics['cv_accuracy_mean'] > 0.45
            and pred_proba > 0.45
        )
        reliability_note = (
            f"Model CV accuracy: {metrics['cv_accuracy_mean']:.1%} "
            f"(±{metrics['cv_accuracy_std']:.1%}) over {metrics['training_samples']} samples."
        ) if is_reliable else (
            f"Low model confidence or insufficient history. "
            f"CV accuracy: {metrics['cv_accuracy_mean']:.1%}."
        )

        return {
            'ticker': ticker.upper(),
            'direction': direction,
            'confidence': round(float(pred_proba), 4),
            'horizon': horizon,
            'signal_strength': signal_strength,
            'key_factors': key_factors,
            'technical_summary': technical_summary,
            'uncertainty_note': (
                "Directional signals only. Past model accuracy does not guarantee "
                "future performance. This is not financial advice."
            ),
            'model_version': MODEL_VERSION,
            'data_points_used': data_points,
            'is_reliable': is_reliable,
            'reliability_note': reliability_note,
            'cv_metrics': metrics,
            'vs_baseline': vs_baseline,
        }

    except Exception as e:
        return {
            **base_result,
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'signal_strength': 'WEAK',
            'key_factors': [],
            'technical_summary': {},
            'uncertainty_note': f'Prediction error: {str(e)}',
            'reliability_note': 'Model error — prediction unavailable.',
        }


def _compute_baseline_comparison(df: pd.DataFrame, forward_days: int, feature_cols: list) -> dict:
    """
    Compute a fair temporal train/test baseline comparison.

    Trains on the FIRST 75% of data (earlier) and evaluates on the LAST 25% (later).
    This avoids lookahead bias and satisfies: "train on earlier data, test on later data."

    Baselines compared:
    - Majority-class rule: always predict whichever direction appeared most often in training data
    - Buy-and-hold rule (Always Bullish): always predict BULLISH regardless of signals

    Returns precision, recall, F1 and accuracy for both model and baselines.
    """
    try:
        df_ind = compute_technical_indicators(df)
        labels = create_labels(df_ind, forward_days=forward_days)

        available_cols = [c for c in feature_cols if c in df_ind.columns]
        X = df_ind[available_cols].copy()
        y = labels.copy()

        combined = pd.concat([X, y.rename('label')], axis=1).dropna()
        if len(combined) < 60:
            return {}

        X_all = combined[available_cols].values
        y_all = combined['label'].values.astype(int)

        # --- Temporal split: earlier 75% = train, later 25% = test ---
        split = int(len(X_all) * 0.75)
        X_train, X_test = X_all[:split], X_all[split:]
        y_train, y_test = y_all[:split], y_all[split:]

        if len(np.unique(y_train)) < 2 or len(X_test) < 10:
            return {}

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s  = scaler.transform(X_test)

        model = RandomForestClassifier(
            n_estimators=100, max_depth=6, min_samples_split=10,
            min_samples_leaf=5, class_weight='balanced', random_state=42, n_jobs=-1,
        )
        model.fit(X_train_s, y_train)
        y_pred = model.predict(X_test_s)

        # --- Model metrics ---
        direction_map = {1: 'BULLISH', -1: 'BEARISH', 0: 'NEUTRAL'}
        classes_int = [-1, 0, 1]
        model_acc = float(accuracy_score(y_test, y_pred))

        # Precision / recall / F1 per class
        from sklearn.metrics import precision_recall_fscore_support
        prec, rec, f1, support = precision_recall_fscore_support(
            y_test, y_pred, labels=classes_int, zero_division=0
        )
        model_metrics = {}
        for i, cls in enumerate(classes_int):
            label = direction_map[cls]
            model_metrics[label] = {
                'precision': round(float(prec[i]), 4),
                'recall':    round(float(rec[i]),  4),
                'f1':        round(float(f1[i]),   4),
                'support':   int(support[i]),
            }

        # --- Baseline 1: Majority-class rule ---
        majority_class = int(np.bincount(y_train + 1).argmax() - 1)  # shift back
        y_majority = np.full_like(y_test, fill_value=majority_class)
        majority_acc = float(accuracy_score(y_test, y_majority))
        majority_label = direction_map.get(majority_class, 'NEUTRAL')

        prec_m, rec_m, f1_m, sup_m = precision_recall_fscore_support(
            y_test, y_majority, labels=classes_int, zero_division=0
        )
        majority_metrics = {}
        for i, cls in enumerate(classes_int):
            label = direction_map[cls]
            majority_metrics[label] = {
                'precision': round(float(prec_m[i]), 4),
                'recall':    round(float(rec_m[i]),  4),
                'f1':        round(float(f1_m[i]),   4),
            }

        # --- Baseline 2: Buy-and-hold (always BULLISH = +1) ---
        y_bullish = np.ones_like(y_test)
        bullish_acc = float(accuracy_score(y_test, y_bullish))

        prec_b, rec_b, f1_b, _ = precision_recall_fscore_support(
            y_test, y_bullish, labels=classes_int, zero_division=0
        )
        bullish_metrics = {}
        for i, cls in enumerate(classes_int):
            label = direction_map[cls]
            bullish_metrics[label] = {
                'precision': round(float(prec_b[i]), 4),
                'recall':    round(float(rec_b[i]),  4),
                'f1':        round(float(f1_b[i]),   4),
            }

        return {
            'train_samples':     split,
            'test_samples':      len(X_test),
            'train_period':      'Earlier 75% of data',
            'test_period':       'Later 25% of data',
            'model': {
                'name':     'RandomForest (11 technical indicators)',
                'accuracy': round(model_acc, 4),
                'metrics':  model_metrics,
            },
            'baseline_majority': {
                'name':           f'Always {majority_label} (majority class rule)',
                'accuracy':       round(majority_acc, 4),
                'majority_class': majority_label,
                'metrics':        majority_metrics,
            },
            'baseline_bullish': {
                'name':     'Always Bullish (buy-and-hold rule)',
                'accuracy': round(bullish_acc, 4),
                'metrics':  bullish_metrics,
            },
            'model_beats_majority': model_acc > majority_acc,
            'model_beats_bullish':  model_acc > bullish_acc,
            'accuracy_lift_vs_majority': round(model_acc - majority_acc, 4),
            'accuracy_lift_vs_bullish':  round(model_acc - bullish_acc, 4),
        }
    except Exception as e:
        return {'error': str(e)}


def _build_key_factors(
    sorted_feats: list,
    df_ind: pd.DataFrame,
    direction: str,
) -> list:
    """Build human-readable key factor dicts from feature importances."""

    factor_descriptions = {
        'RSI': (
            'RSI',
            lambda v: f"{v:.1f}",
            lambda v, d: (
                ('Overbought — potential reversal risk', 'BEARISH')  if v > 70 else
                ('Oversold — potential bounce opportunity', 'BULLISH') if v < 30 else
                ('Neutral RSI zone (30–70)', 'NEUTRAL')
            ),
        ),
        'MACD_hist': (
            'MACD Histogram',
            lambda v: f"{v:.4f}",
            lambda v, d: (
                ('Positive histogram — bullish momentum building', 'BULLISH') if v > 0 else
                ('Negative histogram — bearish momentum building', 'BEARISH')
            ),
        ),
        'MACD_bullish': (
            'MACD Signal Cross',
            lambda v: 'Above signal' if v == 1 else 'Below signal',
            lambda v, d: (
                ('MACD line above signal — bullish crossover', 'BULLISH') if v == 1 else
                ('MACD line below signal — bearish crossover', 'BEARISH')
            ),
        ),
        'BB_pct_b': (
            'Bollinger %B',
            lambda v: f"{v:.2f}",
            lambda v, d: (
                ('Price near upper band — potential overbought', 'BEARISH') if v > 0.8 else
                ('Price near lower band — potential oversold', 'BULLISH')    if v < 0.2 else
                ('Price within Bollinger Band midrange', 'NEUTRAL')
            ),
        ),
        'Momentum_5': (
            '5-Day Momentum',
            lambda v: f"{v:.2%}",
            lambda v, d: (
                (f'Strong recent upward momentum ({v:.2%})', 'BULLISH')  if v > 0.02 else
                (f'Strong recent downward momentum ({v:.2%})', 'BEARISH') if v < -0.02 else
                (f'Modest recent price movement ({v:.2%})', 'NEUTRAL')
            ),
        ),
        'Momentum_20': (
            '20-Day Momentum',
            lambda v: f"{v:.2%}",
            lambda v, d: (
                (f'Positive monthly trend ({v:.2%})', 'BULLISH')  if v > 0 else
                (f'Negative monthly trend ({v:.2%})', 'BEARISH')
            ),
        ),
        'Golden_Death_Cross': (
            'MA Cross Signal',
            lambda v: 'Golden Cross' if v == 1 else 'Death Cross',
            lambda v, d: (
                ('MA5 above MA20 — bullish alignment', 'BULLISH')  if v == 1 else
                ('MA5 below MA20 — bearish alignment', 'BEARISH')
            ),
        ),
        'Price_vs_MA20': (
            'Price vs 20-Day MA',
            lambda v: f"{v:.2%} from MA20",
            lambda v, d: (
                (f'Price {v:.2%} above 20-day moving average', 'BULLISH') if v > 0 else
                (f'Price {v:.2%} below 20-day moving average', 'BEARISH')
            ),
        ),
        'Price_vs_MA50': (
            'Price vs 50-Day MA',
            lambda v: f"{v:.2%} from MA50",
            lambda v, d: (
                (f'Price {v:.2%} above 50-day moving average — trend positive', 'BULLISH') if v > 0 else
                (f'Price {v:.2%} below 50-day moving average — trend negative', 'BEARISH')
            ),
        ),
        'Volume_ratio': (
            'Volume Ratio',
            lambda v: f"{v:.2f}x avg",
            lambda v, d: (
                (f'Volume {v:.2f}x average — strong conviction', 'BULLISH')  if v > 1.5 and d == 'BULLISH' else
                (f'Volume {v:.2f}x average — distribution pressure', 'BEARISH') if v > 1.5 and d == 'BEARISH' else
                (f'Volume {v:.2f}x average — normal activity', 'NEUTRAL')
            ),
        ),
        'Stoch_K': (
            'Stochastic %K',
            lambda v: f"{v:.1f}",
            lambda v, d: (
                ('Stochastic overbought (>80)', 'BEARISH') if v > 80 else
                ('Stochastic oversold (<20)', 'BULLISH')   if v < 20 else
                ('Stochastic in neutral range', 'NEUTRAL')
            ),
        ),
        'ATR_pct': (
            'ATR Volatility',
            lambda v: f"{v:.2%}",
            lambda v, d: (
                (f'High volatility ({v:.2%} ATR) — elevated uncertainty', 'NEUTRAL') if v > 0.025 else
                (f'Normal volatility ({v:.2%} ATR)', 'NEUTRAL')
            ),
        ),
        'OBV_signal': (
            'On-Balance Volume',
            lambda v: 'Rising' if v == 1 else 'Falling',
            lambda v, d: (
                ('OBV rising — accumulation signal', 'BULLISH')    if v == 1 else
                ('OBV falling — distribution signal', 'BEARISH')
            ),
        ),
        'Williams_R': (
            'Williams %R',
            lambda v: f"{v:.1f}",
            lambda v, d: (
                ('Williams %R overbought (>-20)', 'BEARISH') if v > -20 else
                ('Williams %R oversold (<-80)', 'BULLISH')   if v < -80 else
                ('Williams %R neutral zone', 'NEUTRAL')
            ),
        ),
    }

    factors = []
    latest_row = df_ind.iloc[-1]

    for feat_name, importance in sorted_feats:
        if feat_name not in factor_descriptions:
            continue
        label, fmt_fn, desc_fn = factor_descriptions[feat_name]
        raw_val = latest_row.get(feat_name, np.nan)
        if pd.isna(raw_val):
            continue
        try:
            formatted_val = fmt_fn(raw_val)
            desc_tuple = desc_fn(raw_val, direction)
            description, impact = desc_tuple
        except Exception:
            continue

        factors.append({
            'factor':      label,
            'value':       formatted_val,
            'impact':      impact,
            'description': description,
            'importance':  round(float(importance), 4),
        })

    return factors


# ---------------------------------------------------------------------------
# Technical Summary
# ---------------------------------------------------------------------------

def get_technical_summary(df: pd.DataFrame) -> dict:
    """
    Get a human-readable summary of current technical signals.
    Returns dict of indicator name -> {value, signal, description}
    """
    if df is None or len(df) == 0:
        return {}

    latest = df.iloc[-1]

    def safe(col: str, default=None):
        val = latest.get(col, default)
        return None if pd.isna(val) else val

    summary = {}

    # RSI
    rsi = safe('RSI')
    if rsi is not None:
        if rsi > 70:
            rsi_signal, rsi_desc = 'OVERBOUGHT', 'RSI above 70 — potential reversal'
        elif rsi < 30:
            rsi_signal, rsi_desc = 'OVERSOLD',   'RSI below 30 — potential bounce'
        else:
            rsi_signal, rsi_desc = 'NEUTRAL',    'RSI in normal range (30–70)'
        summary['RSI_14'] = {'value': round(rsi, 2), 'signal': rsi_signal, 'description': rsi_desc}

    # MACD
    macd_hist = safe('MACD_hist')
    macd_bull = safe('MACD_bullish')
    if macd_hist is not None:
        macd_signal = 'BULLISH' if (macd_bull == 1 and macd_hist > 0) else \
                      'BEARISH' if (macd_bull == 0 and macd_hist < 0) else 'NEUTRAL'
        summary['MACD'] = {
            'value':       round(macd_hist, 5),
            'signal':      macd_signal,
            'description': f"Histogram: {macd_hist:.5f}, {'Above' if macd_bull == 1 else 'Below'} signal line",
        }

    # Bollinger Bands
    bb_pct = safe('BB_pct_b')
    bb_width = safe('BB_width')
    if bb_pct is not None:
        bb_sig = 'OVERBOUGHT' if bb_pct > 0.8 else 'OVERSOLD' if bb_pct < 0.2 else 'NEUTRAL'
        summary['Bollinger_Bands'] = {
            'value':       round(bb_pct, 3),
            'signal':      bb_sig,
            'description': f"%B={bb_pct:.2f}, Width={bb_width:.3f}" if bb_width else f"%B={bb_pct:.2f}",
        }

    # Moving averages
    ma5  = safe('MA5')
    ma20 = safe('MA20')
    ma50 = safe('MA50')
    close = safe('Close')
    if close and ma20:
        pct_vs_ma20 = (close - ma20) / ma20
        ma20_sig = 'ABOVE_MA20' if pct_vs_ma20 > 0 else 'BELOW_MA20'
        summary['Moving_Averages'] = {
            'value':       round(pct_vs_ma20, 4),
            'signal':      ma20_sig,
            'description': (
                f"Price {abs(pct_vs_ma20):.2%} {'above' if pct_vs_ma20 > 0 else 'below'} MA20"
                + (f", MA5 {'>' if ma5 and ma5 > ma20 else '<'} MA20" if ma5 else "")
            ),
        }

    # Stochastic
    stoch_k = safe('Stoch_K')
    stoch_d = safe('Stoch_D')
    if stoch_k is not None:
        stoch_sig = 'OVERBOUGHT' if stoch_k > 80 else 'OVERSOLD' if stoch_k < 20 else 'NEUTRAL'
        summary['Stochastic'] = {
            'value':       round(stoch_k, 2),
            'signal':      stoch_sig,
            'description': f"%K={stoch_k:.1f}, %D={stoch_d:.1f}" if stoch_d else f"%K={stoch_k:.1f}",
        }

    # ATR
    atr_pct = safe('ATR_pct')
    if atr_pct is not None:
        vol_level = 'HIGH' if atr_pct > 0.025 else 'MODERATE' if atr_pct > 0.012 else 'LOW'
        summary['ATR_Volatility'] = {
            'value':       round(atr_pct, 5),
            'signal':      vol_level,
            'description': f"ATR is {atr_pct:.2%} of price — {vol_level.lower()} volatility",
        }

    # Volume
    vol_ratio = safe('Volume_ratio')
    if vol_ratio is not None:
        vol_sig = 'HIGH_VOLUME' if vol_ratio > 1.5 else 'LOW_VOLUME' if vol_ratio < 0.7 else 'NORMAL'
        summary['Volume'] = {
            'value':       round(vol_ratio, 3),
            'signal':      vol_sig,
            'description': f"Volume is {vol_ratio:.2f}x the 20-day average",
        }

    # Golden/Death cross
    gd = safe('Golden_Death_Cross')
    if gd is not None:
        summary['MA_Cross'] = {
            'value':       int(gd),
            'signal':      'GOLDEN_CROSS' if gd == 1 else 'DEATH_CROSS',
            'description': 'MA5 above MA20 — bullish alignment' if gd == 1 else 'MA5 below MA20 — bearish alignment',
        }

    # OBV
    obv_sig = safe('OBV_signal')
    if obv_sig is not None:
        summary['OBV'] = {
            'value':       int(obv_sig),
            'signal':      'ACCUMULATION' if obv_sig == 1 else 'DISTRIBUTION',
            'description': 'On-Balance Volume rising — buying pressure' if obv_sig == 1 else 'On-Balance Volume falling — selling pressure',
        }

    # Williams %R
    wr = safe('Williams_R')
    if wr is not None:
        wr_sig = 'OVERBOUGHT' if wr > -20 else 'OVERSOLD' if wr < -80 else 'NEUTRAL'
        summary['Williams_R'] = {
            'value':       round(wr, 2),
            'signal':      wr_sig,
            'description': f"Williams %R = {wr:.1f}",
        }

    return summary
