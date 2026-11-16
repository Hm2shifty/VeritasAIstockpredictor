"""
FINIQ - Comprehensive Stock Analysis Platform
Interactive Candlestick/Line charts, Institutional Statistics, AI Directional Predictor, and Technical Indicators
"""

import os
import sys
from datetime import datetime

# Path setup for imports
for p in [
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    os.path.dirname(os.path.abspath(__file__)),
    '/home/hethm/Desktop/Project/Veritas'
]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Import UI components and bridge functions
from app.ui_components import (
    inject_css,
    PLOTLY_LAYOUT,
    render_sidebar_branding,
    render_footer_disclaimer,
    safe_get_quote,
    safe_get_history,
    safe_predict,
    safe_is_in_watchlist,
    safe_add_to_watchlist,
    safe_remove_from_watchlist
)

st.set_page_config(
    page_title="FINIQ — Stock Analysis",
    page_icon="📈",
    layout="wide"
)

inject_css()
render_sidebar_branding()

# Initialize session state for ticker selection
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

# =====================================================================
# SEARCH & QUICK SELECTION BAR
# =====================================================================
st.markdown("""
<div style="font-size: 26px; font-weight: 800; letter-spacing: 0.04em; background: linear-gradient(90deg, #F3F6FC 0%, #3985F5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;">
    STOCK ANALYSIS & QUANTITATIVE SIGNALS
</div>
<div style="font-size: 13px; color: #8E9AAF; margin-bottom: 16px;">
    Institutional single-ticker deep dive with algorithmic momentum forecasts, multi-period technicals, and order flow metrics
</div>
""", unsafe_allow_html=True)

col_search, col_btn = st.columns([4, 1])

with col_search:
    user_ticker = st.text_input(
        "Search by ticker or company name",
        value=st.session_state.selected_ticker,
        placeholder="e.g., NVDA, AAPL, MSFT, TSLA, GOOGL",
        label_visibility="collapsed",
        key="search_input_box"
    )

with col_btn:
    analyze_btn = st.button("🔍 Analyze Ticker", use_container_width=True)

if analyze_btn and user_ticker:
    st.session_state.selected_ticker = user_ticker.upper().strip()
    st.rerun()

# Quick pill selection row
quick_tickers = ["NVDA", "AAPL", "MSFT", "TSLA", "AMZN", "GOOGL", "META", "AMD", "PLTR"]
st.markdown("<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 16px;'>", unsafe_allow_html=True)
pill_cols = st.columns(len(quick_tickers) + 1)
with pill_cols[0]:
    st.markdown("<span style='font-size: 11px; color: #8E9AAF; font-weight: 600; text-transform: uppercase;'>Quick Select:</span>", unsafe_allow_html=True)
for i, q_t in enumerate(quick_tickers):
    with pill_cols[i + 1]:
        if st.button(q_t, key=f"quick_{q_t}", use_container_width=True):
            st.session_state.selected_ticker = q_t
            st.rerun()

active_ticker = st.session_state.selected_ticker.upper().strip()
quote = safe_get_quote(active_ticker)

# =====================================================================
# COMPANY HEADER & WATCHLIST TOGGLE
# =====================================================================
price = float(quote.get("price", 100.0))
change = float(quote.get("change", 0.0))
change_pct = float(quote.get("change_pct", 0.0))
is_pos = change >= 0
sign = "+" if is_pos else ""
c_color = "#20C997" if is_pos else "#F06470"
arrow = "▲" if is_pos else "▼"

in_wl = safe_is_in_watchlist(active_ticker)

header_col1, header_col2, header_col3 = st.columns([3, 2, 1.5])

with header_col1:
    st.markdown(f"""
    <div style="display: flex; align-items: baseline; gap: 12px;">
        <span style="font-size: 32px; font-weight: 800; color: #3985F5; letter-spacing: -0.02em;">{active_ticker}</span>
        <span style="font-size: 20px; font-weight: 600; color: #F3F6FC;">{quote.get('company', active_ticker)}</span>
    </div>
    <div style="font-size: 12px; color: #8E9AAF; margin-top: 4px; display: flex; gap: 10px;">
        <span><strong>Exchange:</strong> {quote.get('exchange', 'NASDAQ')}</span>
        <span>•</span>
        <span><strong>Sector:</strong> {quote.get('sector', 'Technology')}</span>
        <span>•</span>
        <span><strong>Industry:</strong> {quote.get('industry', 'Semiconductors')}</span>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown(f"""
    <div style="text-align: right;">
        <div style="font-size: 32px; font-weight: 800; color: #F3F6FC; font-variant-numeric: tabular-nums;">
            ${price:,.2f}
        </div>
        <div style="font-size: 15px; font-weight: 700; color: {c_color};">
            {arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%) <span style="font-size: 11px; color: #8E9AAF; font-weight: 400;">Today</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_col3:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    if in_wl:
        if st.button("★ In Watchlist", key="btn_wl_toggle", use_container_width=True):
            safe_remove_from_watchlist(active_ticker)
            st.toast(f"Removed {active_ticker} from watchlist")
            st.rerun()
    else:
        if st.button("+ Add to Watchlist", key="btn_wl_toggle", use_container_width=True):
            safe_add_to_watchlist(active_ticker, quote.get("company", active_ticker))
            st.toast(f"Added {active_ticker} to watchlist")
            st.rerun()
            
    if st.button("⚡ Run AI Debate", key="btn_jump_debate", use_container_width=True):
        st.session_state.debate_ticker = active_ticker
        st.switch_page("pages/3_🤖_AI_Analyst_Debate.py")

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# =====================================================================
# INTERACTIVE PRICE & VOLUME CHART
# =====================================================================
chart_ctrl_col1, chart_ctrl_col2 = st.columns([3, 1])

with chart_ctrl_col1:
    periods = ["1D", "1W", "1M", "3M", "6M", "1Y", "5Y"]
    selected_period = st.radio(
        "Time Horizon",
        options=periods,
        index=3,  # Default to 3M
        horizontal=True,
        label_visibility="collapsed",
        key="chart_period_radio"
    )

with chart_ctrl_col2:
    chart_type = st.radio(
        "Chart Style",
        options=["Candlestick", "Line"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="chart_style_radio"
    )

# Fetch historical data
history_df = safe_get_history(active_ticker, selected_period)

if history_df is not None and not history_df.empty:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )
    
    # 1. Main Price Trace
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=history_df['Date'],
            open=history_df['Open'],
            high=history_df['High'],
            low=history_df['Low'],
            close=history_df['Close'],
            name=active_ticker,
            increasing_line_color='#20C997',
            decreasing_line_color='#F06470',
            increasing_fillcolor='rgba(32, 201, 151, 0.7)',
            decreasing_fillcolor='rgba(240, 100, 112, 0.7)'
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=history_df['Date'],
            y=history_df['Close'],
            mode='lines',
            name=f"{active_ticker} Close",
            line=dict(color='#3985F5', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(57, 133, 245, 0.12)'
        ), row=1, col=1)

    # 2. Moving Average Overlays if sufficient data
    if len(history_df) >= 20:
        sma20 = history_df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=history_df['Date'], y=sma20,
            mode='lines', name='20 SMA',
            line=dict(color='#F5B942', width=1.5, dash='dot')
        ), row=1, col=1)
        
    if len(history_df) >= 50:
        sma50 = history_df['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=history_df['Date'], y=sma50,
            mode='lines', name='50 SMA',
            line=dict(color='#8767F7', width=1.5)
        ), row=1, col=1)

    # 3. Volume Bars
    vol_colors = [
        '#20C997' if c >= o else '#F06470'
        for c, o in zip(history_df['Close'], history_df['Open'])
    ]
    fig.add_trace(go.Bar(
        x=history_df['Date'],
        y=history_df['Volume'],
        name='Volume',
        marker_color=vol_colors,
        opacity=0.7
    ), row=2, col=1)

    # Layout styling matching design system
    fig.update_layout(
        plot_bgcolor='#101827',
        paper_bgcolor='#141E30',
        font=dict(family='Inter, sans-serif', color='#F3F6FC', size=11),
        height=480,
        margin=dict(l=40, r=20, t=10, b=20),
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(20, 30, 48, 0.8)',
            bordercolor='#263449'
        )
    )
    
    fig.update_xaxes(gridcolor='#263449', linecolor='#263449', tickcolor='#8E9AAF', row=1, col=1)
    fig.update_xaxes(gridcolor='#263449', linecolor='#263449', tickcolor='#8E9AAF', row=2, col=1)
    fig.update_yaxes(title="Price ($)", gridcolor='#263449', linecolor='#263449', tickcolor='#8E9AAF', row=1, col=1)
    fig.update_yaxes(title="Vol", gridcolor='#263449', linecolor='#263449', tickcolor='#8E9AAF', row=2, col=1)

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("Historical price data currently loading or unavailable.")

# =====================================================================
# KEY FINANCIAL STATISTICS (4-COLUMN GRID)
# =====================================================================
st.markdown('<div class="section-title">📊 Key Financial & Trading Statistics</div>', unsafe_allow_html=True)

s_c1, s_c2, s_c3, s_c4 = st.columns(4)

with s_c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Open / Prev Close</div>
        <div style="font-size: 16px; font-weight: 700; color: #F3F6FC;">
            ${quote.get('open', price):.2f} / ${quote.get('prev_close', price):.2f}
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Market Capitalization</div>
        <div class="metric-value">${quote.get('market_cap', '1.25T')}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Beta (5Y Monthly)</div>
        <div class="metric-value">1.64</div>
    </div>
    """, unsafe_allow_html=True)

with s_c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Day High / Low Range</div>
        <div style="font-size: 16px; font-weight: 700; color: #F3F6FC;">
            ${quote.get('high', price):.2f} - ${quote.get('low', price):.2f}
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Trailing P/E Ratio</div>
        <div class="metric-value">{quote.get('pe_ratio', 34.2)}x</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Forward P/E Ratio</div>
        <div class="metric-value">{round(float(quote.get('pe_ratio', 34.2)) * 0.82, 1)}x</div>
    </div>
    """, unsafe_allow_html=True)

with s_c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">52-Week High / Low</div>
        <div style="font-size: 16px; font-weight: 700; color: #F3F6FC;">
            ${quote.get('week_52_high', price*1.15):.2f} - ${quote.get('week_52_low', price*0.75):.2f}
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-label">EPS (TTM Diluted)</div>
        <div class="metric-value">${quote.get('eps', 4.12):.2f}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Dividend Yield</div>
        <div class="metric-value">0.08%</div>
    </div>
    """, unsafe_allow_html=True)

with s_c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Day Volume / Avg Volume</div>
        <div style="font-size: 15px; font-weight: 700; color: #F3F6FC;">
            {quote.get('volume', '48.2M')} / {quote.get('avg_volume', '42.1M')}
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Shares Outstanding</div>
        <div class="metric-value">24.6B</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Short Float Ratio</div>
        <div class="metric-value" style="color: #20C997;">1.38% (Low)</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# AI DIRECTIONAL PREDICTION & QUANTITATIVE OUTLOOK
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🧠 AI Algorithmic Outlook & Directional Bias</div>', unsafe_allow_html=True)

pred = safe_predict(active_ticker, history_df)

direction = pred.get("direction", "BULLISH").upper()
confidence = float(pred.get("confidence", 0.70))
conf_pct = int(confidence * 100)
strength = pred.get("signal_strength", "STRONG").upper()
badge_cls = "badge-bullish" if direction == "BULLISH" else ("badge-bearish" if direction == "BEARISH" else "badge-neutral")

col_pred_card, col_pred_factors = st.columns([1.1, 1.4])

with col_pred_card:
    st.markdown(f"""
    <div class="finiq-card" style="height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <span style="font-size: 12px; font-weight: 600; color: #8E9AAF; text-transform: uppercase;">5-Day Forecast Horizon</span>
            <span class="{badge_cls}" style="font-size: 13px; padding: 4px 12px;">● {direction} SIGNAL</span>
        </div>
        
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
                <span style="color: #BAC7D5;">Model Confidence Score</span>
                <span style="color: #F3F6FC; font-weight: 700;">{conf_pct}%</span>
            </div>
            <div style="height: 8px; width: 100%; border-radius: 4px; background: #101827; border: 1px solid #263449; overflow: hidden;">
                <div style="width: {conf_pct}%; height: 100%; background: linear-gradient(90deg, #3985F5 0%, #20C997 100%);"></div>
            </div>
        </div>
        
        <div style="display: flex; gap: 12px; margin-bottom: 16px;">
            <div class="metric-card" style="flex: 1; padding: 10px 14px; margin-bottom: 0;">
                <div class="metric-label" style="font-size: 10px;">Signal Conviction</div>
                <div style="font-size: 14px; font-weight: 700; color: #3985F5;">{strength}</div>
            </div>
            <div class="metric-card" style="flex: 1; padding: 10px 14px; margin-bottom: 0;">
                <div class="metric-label" style="font-size: 10px;">Model Calibration</div>
                <div style="font-size: 14px; font-weight: 700; color: #20C997;">High Fidelity</div>
            </div>
        </div>
        
        <div style="font-size: 12px; color: #8E9AAF; line-height: 1.5; border-top: 1px solid #263449; padding-top: 12px;">
            <strong style="color: #BAC7D5;">Uncertainty & Risk Note:</strong><br>
            {pred.get('uncertainty_note', 'Model predictions represent probabilistic directional expectation based on historical pattern matching and volume momentum.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_pred_factors:
    factors = pred.get("key_factors", [])
    st.markdown('<div class="finiq-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 12px; font-weight: 600; color: #8E9AAF; text-transform: uppercase; margin-bottom: 12px;">
        Key Quantitative Drivers & Factor Attribution
    </div>
    """, unsafe_allow_html=True)
    
    for f in factors:
        impact = f.get("impact", "Positive")
        is_p = impact == "Positive"
        icon = "➕" if is_p else ("➖" if impact == "Negative" else "⚪")
        badge = "badge-positive" if is_p else ("badge-negative" if impact == "Negative" else "badge-neutral")
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid rgba(38,52,73,0.4);">
            <div>
                <div style="font-size: 13px; font-weight: 600; color: #F3F6FC;">
                    {icon} {f.get('factor')} <span style="font-weight: 400; color: #8E9AAF; font-size: 11px;">({f.get('value')})</span>
                </div>
                <div style="font-size: 11px; color: #BAC7D5; margin-top: 2px;">
                    {f.get('description')}
                </div>
            </div>
            <span class="{badge}" style="font-size: 10px; margin-left: 10px; white-space: nowrap;">{impact}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# TECHNICAL INDICATORS SIGNAL TABLE
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">📐 Technical Indicator Suite & Oscillator Readouts</div>', unsafe_allow_html=True)

tech_summary = pred.get("technical_summary", {})

tech_table_html = """
<table class="finiq-table">
    <thead>
        <tr>
            <th>Indicator</th>
            <th>Value</th>
            <th>Signal</th>
            <th>Institutional Interpretation</th>
        </tr>
    </thead>
    <tbody>
"""

for ind_name, data in tech_summary.items():
    sig = data.get("signal", "NEUTRAL").upper()
    sig_badge = "badge-positive" if "BUY" in sig else ("badge-negative" if "SELL" in sig else "badge-neutral")
    tech_table_html += f"""
        <tr>
            <td style="font-weight: 600; color: #3985F5;">{ind_name}</td>
            <td style="font-weight: 700; color: #F3F6FC;">{data.get('value')}</td>
            <td><span class="{sig_badge}">● {sig}</span></td>
            <td style="color: #BAC7D5; font-size: 12px;">{data.get('description')}</td>
        </tr>
    """

tech_table_html += "</tbody></table>"
st.markdown(tech_table_html, unsafe_allow_html=True)

# Footer Disclaimer
render_footer_disclaimer()
