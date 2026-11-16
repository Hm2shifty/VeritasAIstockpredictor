"""
FINIQ - Institutional AI Financial Intelligence Platform
Main Entry Point & Market Overview Dashboard
"""

import os
import sys
from datetime import datetime

# Path setup for imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Import design system & UI components
from app.ui_components import (
    inject_css,
    PLOTLY_LAYOUT,
    render_sidebar_branding,
    render_footer_disclaimer,
    get_market_hours_status,
    safe_init_db,
    safe_get_market_indices,
    safe_get_top_movers,
    safe_get_market_summary,
    safe_get_quote,
    safe_get_data_status,
    safe_get_market_news,
    safe_get_watchlist,
    safe_add_to_watchlist,
    safe_remove_from_watchlist,
    safe_is_in_watchlist
)

# 1. Page Configuration
st.set_page_config(
    page_title="FINIQ — Institutional Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Design System CSS
inject_css()

# 3. Sidebar Branding & System Info
render_sidebar_branding()

with st.sidebar:
    st.markdown("""
    <div style="font-size: 11px; color: #8E9AAF; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">
        Quick Ticker Jump
    </div>
    """, unsafe_allow_html=True)
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("NVDA", key="sb_nvda", use_container_width=True):
            st.session_state.selected_ticker = "NVDA"
            st.switch_page("pages/2_📈_Stock_Analysis.py")
        if st.button("MSFT", key="sb_msft", use_container_width=True):
            st.session_state.selected_ticker = "MSFT"
            st.switch_page("pages/2_📈_Stock_Analysis.py")
    with col_sb2:
        if st.button("AAPL", key="sb_aapl", use_container_width=True):
            st.session_state.selected_ticker = "AAPL"
            st.switch_page("pages/2_📈_Stock_Analysis.py")
        if st.button("TSLA", key="sb_tsla", use_container_width=True):
            st.session_state.selected_ticker = "TSLA"
            st.switch_page("pages/2_📈_Stock_Analysis.py")

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 11px; color: #8E9AAF; line-height: 1.5;">
        <span style="color: #F3F6FC; font-weight: 600;">Platform Engine:</span><br>
        • Multi-Agent AI Debate Arena<br>
        • Quantitative Trend Predictor<br>
        • Sentiment & News Intelligence<br>
        • Simulated Portfolio Analytics
    </div>
    """, unsafe_allow_html=True)

# 4. Initialize Database
safe_init_db()

# =====================================================================
# SECTION A: TOP STATUS BAR
# =====================================================================
market_status, status_color, current_dt_str = get_market_hours_status()
data_status = safe_get_data_status()

col_logo, col_time, col_mkt, col_feed = st.columns([3, 2.2, 1.8, 2])

with col_logo:
    st.markdown("""
    <div style="display: flex; flex-direction: column;">
        <div style="font-size: 26px; font-weight: 800; letter-spacing: 0.04em; background: linear-gradient(90deg, #F3F6FC 0%, #3985F5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            FINIQ OVERVIEW
        </div>
        <div style="font-size: 12px; color: #8E9AAF; font-weight: 500;">
            Institutional Multi-Agent Financial Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_time:
    st.markdown(f"""
    <div class="metric-card" style="padding: 10px 14px; margin-bottom: 0;">
        <div class="metric-label" style="margin-bottom: 2px;">Market Time (Eastern)</div>
        <div style="font-size: 14px; font-weight: 600; color: #F3F6FC;">
            📅 {current_dt_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_mkt:
    st.markdown(f"""
    <div class="metric-card" style="padding: 10px 14px; margin-bottom: 0;">
        <div class="metric-label" style="margin-bottom: 2px;">US Exchanges</div>
        <div style="font-size: 14px; font-weight: 700; color: {status_color};">
            ● {market_status}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_feed:
    st.markdown(f"""
    <div class="metric-card" style="padding: 10px 14px; margin-bottom: 0;">
        <div class="metric-label" style="margin-bottom: 2px;">Data Engine Feed</div>
        <div style="font-size: 14px; font-weight: 600; color: #F5B942;">
            ⚡ {data_status}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# Demo Mode Notification Banner
st.markdown("""
<div class="demo-banner">
    <div>
        <strong>⚡ INSTITUTIONAL SANDBOX ACTIVE</strong> — Running multi-source simulated market feeds with full autonomous AI reasoning pipelines.
    </div>
    <div style="font-size: 11px; opacity: 0.85;">
        Live API connectors available in Settings
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# SECTION B: MARKET OVERVIEW — 5 INDEX CARDS IN A ROW
# =====================================================================
st.markdown('<div class="section-title">📊 Key Benchmark Indices</div>', unsafe_allow_html=True)

indices = safe_get_market_indices()
index_cols = st.columns(len(indices))

def create_sparkline_fig(sparkline_data: list[float], is_positive: bool):
    """Generates an ultra-compact mini sparkline for metric cards."""
    line_color = "#20C997" if is_positive else "#F06470"
    fill_color = "rgba(32, 201, 151, 0.12)" if is_positive else "rgba(240, 100, 112, 0.12)"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=sparkline_data,
        mode='lines',
        line=dict(color=line_color, width=2),
        fill='tozeroy',
        fillcolor=fill_color,
        hoverinfo='skip'
    ))
    fig.update_layout(
        plot_bgcolor='transparent',
        paper_bgcolor='transparent',
        margin=dict(l=0, r=0, t=0, b=0),
        height=45,
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(visible=False, showgrid=False),
        showlegend=False
    )
    return fig

for idx, item in enumerate(indices):
    with index_cols[idx]:
        is_pos = item.get("change", 0) >= 0
        sign = "+" if is_pos else ""
        change_class = "metric-change-positive" if is_pos else "metric-change-negative"
        arrow = "▲" if is_pos else "▼"
        val_str = f"{item['value']:,.2f}" if isinstance(item['value'], (int, float)) else str(item['value'])
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 4px;">
            <div class="metric-label">{item['name']}</div>
            <div class="metric-value">{val_str}</div>
            <div class="{change_class}">
                {arrow} {sign}{item.get('change', 0):.2f} ({sign}{item.get('change_pct', 0):.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Plot sparkline below card
        spark_data = item.get("sparkline", [100, 101, 100.5, 102])
        spark_fig = create_sparkline_fig(spark_data, is_pos)
        st.plotly_chart(spark_fig, use_container_width=True, config={'displayModeBar': False})

# =====================================================================
# SECTION C: MARKET SENTIMENT CARD & TOP MOVERS (2-COLUMN SPLIT)
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

col_sentiment, col_movers = st.columns([1.1, 1.4])

with col_sentiment:
    st.markdown('<div class="section-title">🧠 AI Market Sentiment Pulse</div>', unsafe_allow_html=True)
    summary_data = safe_get_market_summary()
    
    sentiment_label = summary_data.get("sentiment", "BULLISH").upper()
    bull_pct = int(summary_data.get("bullish_pct", 60))
    neutral_pct = int(summary_data.get("neutral_pct", 25))
    bear_pct = int(summary_data.get("bearish_pct", 15))
    
    badge_type = "badge-bullish" if "BULL" in sentiment_label else ("badge-bearish" if "BEAR" in sentiment_label else "badge-neutral")
    
    st.markdown(f"""
    <div class="finiq-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <span style="font-size: 13px; font-weight: 600; color: #8E9AAF;">AGGREGATE BIAS</span>
            <span class="{badge_type}" style="font-size: 13px; padding: 4px 14px;">● {sentiment_label} REGIME</span>
        </div>
        
        <!-- Multi-segment visual progress bar -->
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
                <span style="color: #20C997; font-weight: 600;">Bullish: {bull_pct}%</span>
                <span style="color: #8E9AAF; font-weight: 600;">Neutral: {neutral_pct}%</span>
                <span style="color: #F06470; font-weight: 600;">Bearish: {bear_pct}%</span>
            </div>
            <div style="height: 10px; width: 100%; border-radius: 6px; overflow: hidden; display: flex; background: #101827; border: 1px solid #263449;">
                <div style="width: {bull_pct}%; background: #20C997; transition: width 0.3s ease;"></div>
                <div style="width: {neutral_pct}%; background: #8E9AAF; transition: width 0.3s ease;"></div>
                <div style="width: {bear_pct}%; background: #F06470; transition: width 0.3s ease;"></div>
            </div>
        </div>
        
        <div style="font-size: 13px; line-height: 1.6; color: #BAC7D5; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(38,52,73,0.6);">
            {summary_data.get('summary_text', '')}
        </div>
        
        <div style="margin-top: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #8E9AAF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                Key Market Drivers
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #BAC7D5; line-height: 1.6;">
                {''.join([f"<li>{ev}</li>" for ev in summary_data.get('key_events', [])])}
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_movers:
    st.markdown('<div class="section-title">🔥 Daily Market Movers</div>', unsafe_allow_html=True)
    movers = safe_get_top_movers(limit=5)
    
    tab_gainers, tab_losers = st.tabs(["🟢 Top Gainers", "🔴 Top Losers"])
    
    with tab_gainers:
        gainers_html = """
        <table class="finiq-table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Price</th>
                    <th>Change</th>
                    <th>Volume</th>
                    <th>Sentiment</th>
                </tr>
            </thead>
            <tbody>
        """
        for g in movers.get("gainers", []):
            pct_val = g.get('change_pct', 0)
            sign = "+" if pct_val >= 0 else ""
            gainers_html += f"""
                <tr>
                    <td><strong style="color: #3985F5;">{g.get('ticker')}</strong></td>
                    <td style="color: #BAC7D5;">{g.get('company')}</td>
                    <td style="font-weight: 600;">${g.get('price', 0):.2f}</td>
                    <td style="color: #20C997; font-weight: 600;">{sign}{pct_val:.2f}%</td>
                    <td style="color: #8E9AAF;">{g.get('volume', '-')}</td>
                    <td><span class="badge-positive">{g.get('sentiment', 'Bullish')}</span></td>
                </tr>
            """
        gainers_html += "</tbody></table>"
        st.markdown(gainers_html, unsafe_allow_html=True)
        
    with tab_losers:
        losers_html = """
        <table class="finiq-table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Price</th>
                    <th>Change</th>
                    <th>Volume</th>
                    <th>Sentiment</th>
                </tr>
            </thead>
            <tbody>
        """
        for l in movers.get("losers", []):
            pct_val = l.get('change_pct', 0)
            sign = "+" if pct_val >= 0 else ""
            losers_html += f"""
                <tr>
                    <td><strong style="color: #3985F5;">{l.get('ticker')}</strong></td>
                    <td style="color: #BAC7D5;">{l.get('company')}</td>
                    <td style="font-weight: 600;">${l.get('price', 0):.2f}</td>
                    <td style="color: #F06470; font-weight: 600;">{sign}{pct_val:.2f}%</td>
                    <td style="color: #8E9AAF;">{l.get('volume', '-')}</td>
                    <td><span class="badge-negative">{l.get('sentiment', 'Bearish')}</span></td>
                </tr>
            """
        losers_html += "</tbody></table>"
        st.markdown(losers_html, unsafe_allow_html=True)

# =====================================================================
# SECTION D: WATCHLIST MANAGEMENT
# =====================================================================
st.markdown('<div class="section-title">⭐ Institutional Watchlist</div>', unsafe_allow_html=True)

watchlist_items = safe_get_watchlist()

# Add ticker input row
wl_input_col, wl_btn_col, wl_spacer = st.columns([3, 1.2, 4])
with wl_input_col:
    new_ticker_input = st.text_input(
        "Add Ticker to Watchlist",
        placeholder="Enter symbol (e.g., AMD, META, TSLA)",
        label_visibility="collapsed",
        key="main_wl_input"
    )
with wl_btn_col:
    if st.button("➕ Add Ticker", key="main_wl_add_btn", use_container_width=True):
        if new_ticker_input:
            safe_add_to_watchlist(new_ticker_input)
            st.success(f"Added {new_ticker_input.upper()} to Watchlist!")
            st.rerun()

# Display Watchlist items as interactive grid cards
if watchlist_items:
    wl_cols = st.columns(min(4, len(watchlist_items)))
    for idx, item in enumerate(watchlist_items):
        t = item.get("ticker", "")
        quote = safe_get_quote(t)
        p = quote.get("price", 100.0)
        c = quote.get("change", 0.0)
        pct = quote.get("change_pct", 0.0)
        is_pos = c >= 0
        sign = "+" if is_pos else ""
        c_class = "metric-change-positive" if is_pos else "metric-change-negative"
        col_target = wl_cols[idx % len(wl_cols)]
        
        with col_target:
            st.markdown(f"""
            <div class="metric-card" style="position: relative;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 17px; font-weight: 700; color: #3985F5;">{t}</div>
                        <div style="font-size: 11px; color: #8E9AAF; margin-bottom: 8px;">{quote.get('company', '')[:22]}</div>
                    </div>
                    <span class="badge-neutral" style="font-size: 10px;">{quote.get('sector', 'Tech')[:10]}</span>
                </div>
                <div class="metric-value" style="font-size: 20px;">${p:,.2f}</div>
                <div class="{c_class}">
                    {sign}{c:.2f} ({sign}{pct:.2f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            btn_act_col1, btn_act_col2 = st.columns([1, 1])
            with btn_act_col1:
                if st.button(f"Analyze", key=f"wl_ana_{t}_{idx}", use_container_width=True):
                    st.session_state.selected_ticker = t
                    st.switch_page("pages/2_📈_Stock_Analysis.py")
            with btn_act_col2:
                if st.button(f"Remove", key=f"wl_del_{t}_{idx}", use_container_width=True):
                    safe_remove_from_watchlist(t)
                    st.rerun()
else:
    st.info("Your watchlist is currently empty. Add tickers above to track price momentum and signals.")

# =====================================================================
# SECTION E: MARKET NEWS STREAM (2-COLUMN GRID)
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">📰 Real-Time Financial News Intelligence</div>', unsafe_allow_html=True)

news_articles = safe_get_market_news(limit=6)

news_col1, news_col2 = st.columns(2)

for i, art in enumerate(news_articles):
    target_col = news_col1 if i % 2 == 0 else news_col2
    sent = art.get("sentiment", "neutral").lower()
    badge_class = "badge-positive" if sent == "positive" else ("badge-negative" if sent == "negative" else "badge-neutral")
    event_type = art.get("event_type", "general").upper()
    
    with target_col:
        st.markdown(f"""
        <div class="news-card">
            <div>
                <div class="news-meta">
                    <span style="font-weight: 600; color: #F3F6FC;">{art.get('source', 'FINIQ Wire')}</span>
                    <span>•</span>
                    <span>{art.get('published_at', 'Recently')}</span>
                    <span>•</span>
                    <span class="{badge_class}">{sent.capitalize()}</span>
                </div>
                <div class="news-headline">{art.get('headline', '')}</div>
                <div class="news-summary">{art.get('summary', '')}</div>
            </div>
            <div class="news-tags">
                <span class="badge-purple" style="font-size: 10px;">🏷️ {event_type}</span>
                <span style="font-size: 11px; color: #8E9AAF;">Relevance: {int(art.get('relevance_score', 0.85)*100)}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer Disclaimer
render_footer_disclaimer()
