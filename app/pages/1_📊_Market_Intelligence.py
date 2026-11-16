"""
FINIQ - Market Intelligence & Macro Dashboard
Sector Performance Treemap, Fear & Greed Indicator, Macro Benchmarks, Breadth, and Economic Calendar
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
import pandas as pd
import numpy as np

# Import UI components and bridge functions
from app.ui_components import (
    inject_css,
    PLOTLY_LAYOUT,
    render_sidebar_branding,
    render_footer_disclaimer,
    safe_get_sector_performance,
    safe_get_data_status
)

st.set_page_config(
    page_title="FINIQ — Market Intelligence",
    page_icon="🌐",
    layout="wide"
)

inject_css()
render_sidebar_branding()

# Top Title & Header
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
    <div>
        <div style="font-size: 26px; font-weight: 800; letter-spacing: 0.04em; background: linear-gradient(90deg, #F3F6FC 0%, #3985F5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            MARKET INTELLIGENCE & MACRO
        </div>
        <div style="font-size: 13px; color: #8E9AAF;">
            Cross-asset regime analysis, sector capital flows, market breadth & sovereign yield dynamics
        </div>
    </div>
    <div style="text-align: right;">
        <span class="badge-bullish" style="font-size: 12px; padding: 4px 12px;">● Macro Regime: Expansionary</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# SECTION A & B: SECTOR HEATMAP & FEAR/GREED GAUGE (ROW 1)
# =====================================================================
col_treemap, col_gauge = st.columns([1.6, 1.0])

with col_treemap:
    st.markdown('<div class="section-title">🗺️ S&P 500 Sector Allocation & Performance</div>', unsafe_allow_html=True)
    
    sector_data = safe_get_sector_performance()
    
    # Prepare treemap data
    labels = ["US Market"] + [s["sector"] for s in sector_data]
    parents = [""] + ["US Market"] * len(sector_data)
    values = [sum([s.get("weight", 10.0) for s in sector_data])] + [s.get("weight", 10.0) for s in sector_data]
    changes = [0.0] + [s.get("change_pct", 0.0) for s in sector_data]
    descriptions = ["Benchmark"] + [s.get("description", "") for s in sector_data]
    
    # Treemap Figure
    treemap_fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        customdata=np.column_stack((changes, descriptions)),
        textinfo="label+value+text",
        texttemplate="<b>%{label}</b><br>%{customdata[0]:+.2f}%<br><span style='font-size:10px; color:#BAC7D5;'>%{value:.1f}% weight</span>",
        hovertemplate="<b>Sector: %{label}</b><br>1D Change: %{customdata[0]:+.2f}%<br>Weight: %{value:.1f}%<br>Drivers: %{customdata[1]}<extra></extra>",
        marker=dict(
            colors=changes,
            colorscale=[
                [0.0, '#F06470'],    # Severe decline
                [0.45, '#351c24'],
                [0.5, '#141E30'],    # Neutral border
                [0.55, '#14382c'],
                [1.0, '#20C997']     # Strong rally
            ],
            cmid=0.0,
            colorbar=dict(
                title=dict(text="1D Return %", font=dict(color="#F3F6FC", size=10)),
                tickfont=dict(color="#8E9AAF", size=10),
                thickness=12,
                len=0.8
            )
        )
    ))
    
    treemap_fig.update_layout(
        plot_bgcolor='#101827',
        paper_bgcolor='#141E30',
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        font=dict(family='Inter, sans-serif', color='#F3F6FC')
    )
    st.plotly_chart(treemap_fig, use_container_width=True, config={'displayModeBar': False})

with col_gauge:
    st.markdown('<div class="section-title">🧭 Market Sentiment: Fear & Greed</div>', unsafe_allow_html=True)
    
    # Current Fear & Greed index value
    current_fg = 67.0
    
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_fg,
        domain={'x': [0, 1], 'y': [0, 1]},
        delta={'reference': 62.0, 'increasing': {'color': '#20C997'}, 'suffix': ' vs Last Wk'},
        title={'text': "<b>MARKET GREED REGIME</b><br><span style='font-size:11px; color:#8E9AAF;'>Multi-Factor Composite Score</span>", 'font': {'color': '#F3F6FC', 'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#8E9AAF", 'tickfont': {'color': '#8E9AAF', 'size': 10}},
            'bar': {'color': "#3985F5", 'thickness': 0.28},
            'bgcolor': "#101827",
            'borderwidth': 1,
            'bordercolor': "#263449",
            'steps': [
                {'range': [0, 25], 'color': "rgba(240, 100, 112, 0.4)"},   # Extreme Fear
                {'range': [25, 45], 'color': "rgba(245, 130, 66, 0.35)"},  # Fear
                {'range': [45, 55], 'color': "rgba(245, 185, 66, 0.35)"},  # Neutral
                {'range': [55, 75], 'color': "rgba(130, 201, 103, 0.35)"}, # Greed
                {'range': [75, 100], 'color': "rgba(32, 201, 151, 0.4)"}   # Extreme Greed
            ],
            'threshold': {
                'line': {'color': "#F3F6FC", 'width': 3},
                'thickness': 0.75,
                'value': current_fg
            }
        }
    ))
    
    gauge_fig.update_layout(
        plot_bgcolor='#101827',
        paper_bgcolor='#141E30',
        font=dict(family='Inter, sans-serif', color='#F3F6FC'),
        height=260,
        margin=dict(l=20, r=20, t=30, b=10)
    )
    st.plotly_chart(gauge_fig, use_container_width=True, config={'displayModeBar': False})
    
    # Historical Sentiment Comparison Box
    st.markdown("""
    <div class="finiq-card" style="padding: 12px 16px; margin-bottom: 0;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center;">
            <div>
                <div style="font-size: 10px; color: #8E9AAF; text-transform: uppercase;">Prev Close</div>
                <div style="font-size: 15px; font-weight: 700; color: #20C997;">66 (Greed)</div>
            </div>
            <div>
                <div style="font-size: 10px; color: #8E9AAF; text-transform: uppercase;">1 Week Ago</div>
                <div style="font-size: 15px; font-weight: 700; color: #20C997;">62 (Greed)</div>
            </div>
            <div>
                <div style="font-size: 10px; color: #8E9AAF; text-transform: uppercase;">1 Month Ago</div>
                <div style="font-size: 15px; font-weight: 700; color: #F5B942;">54 (Neutral)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# SECTION C: MACRO INDICATORS TABLE & YIELD CURVE
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🏛️ Global Macro Benchmarks & Sovereign Yield Curve</div>', unsafe_allow_html=True)

macro_col_metrics, macro_col_chart = st.columns([1.3, 1.3])

macro_data = [
    {"name": "10-Year Treasury Yield", "ticker": "US10Y", "value": "4.42%", "change": "+0.03%", "pos": True, "impact": "Neutral / Anchored"},
    {"name": "2-Year Treasury Yield", "ticker": "US02Y", "value": "4.28%", "change": "-0.01%", "pos": False, "impact": "Pricing Fed Easing"},
    {"name": "Yield Curve Spread (10Y - 2Y)", "ticker": "SPREAD", "value": "+14 bps", "change": "+4 bps", "pos": True, "impact": "Positive Slope (Uninverted)"},
    {"name": "US Dollar Index", "ticker": "DXY", "value": "104.15", "change": "-0.22%", "pos": False, "impact": "Supportive for Equities"},
    {"name": "Gold Spot Bullion", "ticker": "XAU/USD", "value": "$2,684.50", "change": "+0.85%", "pos": True, "impact": "Geopolitical Hedge Bid"},
    {"name": "WTI Light Sweet Crude", "ticker": "CL", "value": "$71.20", "change": "-1.15%", "pos": False, "impact": "Disinflationary Impulse"},
    {"name": "Bitcoin Benchmark", "ticker": "BTC/USD", "value": "$91,450", "change": "+2.40%", "pos": True, "impact": "High-Beta Liquidity Proxy"}
]

with macro_col_metrics:
    macro_html = """
    <table class="finiq-table">
        <thead>
            <tr>
                <th>Macro Asset</th>
                <th>Ticker</th>
                <th>Price / Yield</th>
                <th>Change</th>
                <th>Macro Implication</th>
            </tr>
        </thead>
        <tbody>
    """
    for m in macro_data:
        c_class = "color: #20C997;" if m["pos"] else "color: #F06470;"
        arrow = "▲" if m["pos"] else "▼"
        macro_html += f"""
            <tr>
                <td style="font-weight: 600;">{m['name']}</td>
                <td style="color: #3985F5; font-size: 11px; font-weight: 600;">{m['ticker']}</td>
                <td style="font-weight: 700;">{m['value']}</td>
                <td style="{c_class} font-weight: 600;">{arrow} {m['change']}</td>
                <td style="color: #BAC7D5; font-size: 12px;">{m['impact']}</td>
            </tr>
        """
    macro_html += "</tbody></table>"
    st.markdown(macro_html, unsafe_allow_html=True)

with macro_col_chart:
    # US Treasury Yield Curve Chart
    maturities = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
    current_yields = [4.65, 4.58, 4.49, 4.35, 4.28, 4.25, 4.30, 4.36, 4.42, 4.68, 4.60]
    one_month_ago = [4.85, 4.80, 4.72, 4.55, 4.45, 4.38, 4.40, 4.45, 4.48, 4.75, 4.68]
    one_year_ago = [5.45, 5.42, 5.38, 5.15, 4.85, 4.60, 4.48, 4.52, 4.55, 4.88, 4.72]
    
    yc_fig = go.Figure()
    
    yc_fig.add_trace(go.Scatter(
        x=maturities, y=current_yields,
        mode='lines+markers',
        name='Current Curve',
        line=dict(color='#3985F5', width=3),
        marker=dict(size=7, color='#3985F5')
    ))
    
    yc_fig.add_trace(go.Scatter(
        x=maturities, y=one_month_ago,
        mode='lines+markers',
        name='1 Month Ago',
        line=dict(color='#8767F7', width=2, dash='dot'),
        marker=dict(size=5, color='#8767F7')
    ))
    
    yc_fig.add_trace(go.Scatter(
        x=maturities, y=one_year_ago,
        mode='lines+markers',
        name='1 Year Ago (Peak Inversion)',
        line=dict(color='#8E9AAF', width=1.5, dash='dash'),
        marker=dict(size=4, color='#8E9AAF')
    ))
    
    yc_fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="<b>US Sovereign Treasury Term Structure</b>", font=dict(color="#F3F6FC", size=13)),
        height=320,
        xaxis=dict(gridcolor='#263449', tickfont=dict(color='#8E9AAF', size=11)),
        yaxis=dict(title="Yield %", gridcolor='#263449', tickfont=dict(color='#8E9AAF', size=11), range=[3.8, 5.8]),
        margin=dict(l=35, r=15, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(yc_fig, use_container_width=True, config={'displayModeBar': False})

# =====================================================================
# SECTION D & E: MARKET BREADTH & ECONOMIC CALENDAR
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

col_breadth, col_calendar = st.columns([1.1, 1.4])

with col_breadth:
    st.markdown('<div class="section-title">📊 NYSE & NASDAQ Market Breadth</div>', unsafe_allow_html=True)
    
    # Breadth visual breakdown bar chart
    breadth_categories = ['Advancing Issues', 'Declining Issues', 'Unchanged', '52W New Highs', '52W New Lows']
    breadth_counts = [1842, 1120, 148, 284, 42]
    breadth_colors = ['#20C997', '#F06470', '#8E9AAF', '#3985F5', '#F5B942']
    
    breadth_fig = go.Figure(go.Bar(
        x=breadth_counts,
        y=breadth_categories,
        orientation='h',
        marker=dict(color=breadth_colors, line=dict(color='#263449', width=1)),
        text=breadth_counts,
        textposition='outside',
        textfont=dict(color='#F3F6FC', size=11)
    ))
    
    breadth_fig.update_layout(
        **PLOTLY_LAYOUT,
        height=260,
        margin=dict(l=40, r=40, t=10, b=20),
        xaxis=dict(showgrid=True, gridcolor='#263449', tickfont=dict(color='#8E9AAF')),
        yaxis=dict(autorange="reversed", tickfont=dict(color='#F3F6FC', size=11))
    )
    st.plotly_chart(breadth_fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("""
    <div class="finiq-card" style="padding: 10px 16px; margin-top: -6px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px;">
            <span style="color: #8E9AAF;">Stocks Above 50-Day SMA:</span>
            <span style="color: #20C997; font-weight: 700;">68.4% (Bullish Breadth)</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
            <span style="color: #8E9AAF;">Stocks Above 200-Day SMA:</span>
            <span style="color: #20C997; font-weight: 700;">71.2% (Healthy Expansion)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_calendar:
    st.markdown('<div class="section-title">📅 High-Impact Macro & Economic Calendar</div>', unsafe_allow_html=True)
    
    calendar_events = [
        {"date": "Wed, Nov 20", "time": "14:00 ET", "event": "FOMC Meeting Minutes Release", "impact": "HIGH", "consensus": "Dovish Bias", "prev": "25 bps cut"},
        {"date": "Thu, Nov 21", "time": "08:30 ET", "event": "Initial Jobless Claims", "impact": "MEDIUM", "consensus": "218K", "prev": "217K"},
        {"date": "Thu, Nov 21", "time": "09:45 ET", "event": "S&P Flash US Manufacturing PMI", "impact": "HIGH", "consensus": "50.5", "prev": "48.5"},
        {"date": "Tue, Nov 26", "time": "10:00 ET", "event": "Consumer Confidence Index (CB)", "impact": "MEDIUM", "consensus": "108.0", "prev": "108.7"},
        {"date": "Wed, Nov 27", "time": "08:30 ET", "event": "Core PCE Inflation Index (YoY)", "impact": "CRITICAL", "consensus": "2.7%", "prev": "2.7%"}
    ]
    
    cal_html = """
    <table class="finiq-table">
        <thead>
            <tr>
                <th>Date / Time</th>
                <th>Economic Release</th>
                <th>Impact</th>
                <th>Consensus</th>
                <th>Previous</th>
            </tr>
        </thead>
        <tbody>
    """
    for ev in calendar_events:
        imp_badge = "badge-negative" if ev["impact"] == "CRITICAL" else ("badge-warning" if ev["impact"] == "HIGH" else "badge-bullish")
        cal_html += f"""
            <tr>
                <td style="color: #8E9AAF; font-size: 12px; font-weight: 500;">
                    {ev['date']}<br><span style="font-size: 11px; color: #BAC7D5;">{ev['time']}</span>
                </td>
                <td style="font-weight: 600; color: #F3F6FC;">{ev['event']}</td>
                <td><span class="{imp_badge}">{ev['impact']}</span></td>
                <td style="font-weight: 600; color: #3985F5;">{ev['consensus']}</td>
                <td style="color: #8E9AAF;">{ev['prev']}</td>
            </tr>
        """
    cal_html += "</tbody></table>"
    st.markdown(cal_html, unsafe_allow_html=True)

# Footer Disclaimer
render_footer_disclaimer()
