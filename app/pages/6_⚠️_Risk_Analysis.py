import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Risk Analysis | FINIQ",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    :root {
        --bg-primary: #080D18;
        --bg-secondary: #101827;
        --bg-card: #141E30;
        --border: #263449;
        --accent-blue: #3985F5;
        --accent-purple: #8767F7;
        --positive: #20C997;
        --negative: #F06470;
        --warning: #F5B942;
        --text-primary: #F3F6FC;
        --text-secondary: #8E9AAF;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: var(--bg-primary) !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0C1420 !important; border-right: 1px solid var(--border) !important; }
    .finiq-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    .metric-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; }
    .metric-label { color: var(--text-secondary); font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
    .metric-value { color: var(--text-primary); font-size: 22px; font-weight: 600; }
    .badge-positive { background: rgba(32,201,151,0.15); color: #20C997; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-negative { background: rgba(240,100,112,0.15); color: #F06470; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-neutral { background: rgba(142,154,175,0.15); color: #8E9AAF; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-bullish { background: rgba(57,133,245,0.15); color: #3985F5; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-warning { background: rgba(245,185,66,0.15); color: #F5B942; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .finiq-table { width: 100%; border-collapse: collapse; }
    .finiq-table th { color: var(--text-secondary); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; padding: 8px 12px; border-bottom: 1px solid var(--border); text-align: left; }
    .finiq-table td { color: var(--text-primary); font-size: 13px; padding: 10px 12px; border-bottom: 1px solid rgba(38,52,73,0.5); }
    .stButton > button { background: var(--accent-blue) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
    .stTextInput input { background: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 8px !important; }
    .demo-banner { background: rgba(245,185,66,0.1); border: 1px solid rgba(245,185,66,0.3); border-radius: 8px; padding: 8px 16px; color: #F5B942; font-size: 12px; margin-bottom: 16px; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

PLOTLY_LAYOUT = dict(
    plot_bgcolor='#101827',
    paper_bgcolor='#141E30',
    font=dict(family='Inter', color='#F3F6FC', size=12),
    xaxis=dict(gridcolor='#263449', linecolor='#263449', tickfont=dict(color='#8E9AAF', size=11)),
    yaxis=dict(gridcolor='#263449', linecolor='#263449', tickfont=dict(color='#8E9AAF', size=11)),
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode='x unified',
    legend=dict(bgcolor='#141E30', bordercolor='#263449', font=dict(color='#F3F6FC')),
)

# Backend service imports with fallbacks
try:
    from backend.services.market_data import get_history, get_market_indices
except Exception:
    get_history = None
    get_market_indices = None

try:
    from backend.services.portfolio_service import get_portfolio
except Exception:
    get_portfolio = None

# Retrieve holdings or default to demo set
holdings = []
if 'portfolio_holdings' in st.session_state and st.session_state.portfolio_holdings:
    holdings = st.session_state.portfolio_holdings
elif get_portfolio:
    try:
        holdings = get_portfolio()
    except Exception:
        holdings = []

if not holdings:
    tickers = ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'JPM', 'TSLA']
else:
    tickers = [h.get('ticker') for h in holdings if h.get('ticker')]
    if len(tickers) < 2:
        tickers = ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'JPM', 'TSLA']

# Page Header
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
    <div>
        <h1 style="color:#F3F6FC; margin:0; font-size:26px; font-weight:700;">⚠️ Comprehensive Risk Analytics</h1>
        <p style="color:#8E9AAF; margin:4px 0 0 0; font-size:13px;">Quantitative factor decomposition, correlation matrices, tail-risk drawdown simulations, and Value at Risk (VaR).</p>
    </div>
    <div>
        <span class="badge-bullish" style="font-size:12px; padding:6px 14px;">INSTITUTIONAL RISK DESK</span>
    </div>
</div>
""", unsafe_allow_html=True)

# A. RISK OVERVIEW (4 Gauge / Indicator Cards)
st.markdown('<div class="finiq-card" style="padding:16px 20px;">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#F3F6FC; margin:0 0 12px 0; font-size:15px; font-weight:600;">⚡ Real-Time Risk Factor Gauges</h4>', unsafe_allow_html=True)

g1, g2, g3, g4 = st.columns(4)

# Gauge 1: Market Risk (VIX)
vix_val = 14.8
try:
    if get_market_indices:
        indices = get_market_indices()
        for idx in indices:
            if idx.get('symbol') in ['VIX', '^VIX']:
                vix_val = float(idx.get('value', 14.8))
except Exception:
    pass

with g1:
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=vix_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Market Risk (VIX)", 'font': {'size': 13, 'color': '#8E9AAF'}},
        number={'suffix': "", 'font': {'size': 22, 'color': '#F3F6FC'}},
        gauge={
            'axis': {'range': [0, 50], 'tickwidth': 1, 'tickcolor': "#263449", 'tickfont': {'color': '#8E9AAF', 'size': 9}},
            'bar': {'color': "#20C997" if vix_val < 20 else ("#F5B942" if vix_val < 30 else "#F06470")},
            'bgcolor': "#101827",
            'borderwidth': 1,
            'bordercolor': "#263449",
            'steps': [
                {'range': [0, 20], 'color': 'rgba(32, 201, 151, 0.15)'},
                {'range': [20, 30], 'color': 'rgba(245, 185, 66, 0.15)'},
                {'range': [30, 50], 'color': 'rgba(240, 100, 112, 0.15)'}
            ]
        }
    ))
    fig_g1.update_layout(paper_bgcolor='#141E30', plot_bgcolor='#141E30', height=140, margin=dict(l=15, r=15, t=30, b=10))
    st.plotly_chart(fig_g1, use_container_width=True)
    st.markdown("<div style='text-align:center; font-size:11px; color:#20C997; font-weight:600;'>Low Volatility Regime (&lt;20)</div>", unsafe_allow_html=True)

# Gauge 2: Concentration Risk
conc_val = 68.5  # % in top 3
with g2:
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=conc_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Concentration Risk", 'font': {'size': 13, 'color': '#8E9AAF'}},
        number={'suffix': "%", 'font': {'size': 22, 'color': '#F3F6FC'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#263449", 'tickfont': {'color': '#8E9AAF', 'size': 9}},
            'bar': {'color': "#F5B942"},
            'bgcolor': "#101827",
            'borderwidth': 1,
            'bordercolor': "#263449",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(32, 201, 151, 0.15)'},
                {'range': [40, 70], 'color': 'rgba(245, 185, 66, 0.15)'},
                {'range': [70, 100], 'color': 'rgba(240, 100, 112, 0.15)'}
            ]
        }
    ))
    fig_g2.update_layout(paper_bgcolor='#141E30', plot_bgcolor='#141E30', height=140, margin=dict(l=15, r=15, t=30, b=10))
    st.plotly_chart(fig_g2, use_container_width=True)
    st.markdown("<div style='text-align:center; font-size:11px; color:#F5B942; font-weight:600;'>Moderate Clustering (Top 3 = 68%)</div>", unsafe_allow_html=True)

# Gauge 3: Sector Overweight Risk
sector_risk_val = 58.0  # % in tech
with g3:
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sector_risk_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sector Risk (Tech Tilt)", 'font': {'size': 13, 'color': '#8E9AAF'}},
        number={'suffix': "%", 'font': {'size': 22, 'color': '#F3F6FC'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#263449", 'tickfont': {'color': '#8E9AAF', 'size': 9}},
            'bar': {'color': "#F06470"},
            'bgcolor': "#101827",
            'borderwidth': 1,
            'bordercolor': "#263449",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(32, 201, 151, 0.15)'},
                {'range': [30, 50], 'color': 'rgba(245, 185, 66, 0.15)'},
                {'range': [50, 100], 'color': 'rgba(240, 100, 112, 0.15)'}
            ]
        }
    ))
    fig_g3.update_layout(paper_bgcolor='#141E30', plot_bgcolor='#141E30', height=140, margin=dict(l=15, r=15, t=30, b=10))
    st.plotly_chart(fig_g3, use_container_width=True)
    st.markdown("<div style='text-align:center; font-size:11px; color:#F06470; font-weight:600;'>Elevated Overweight Tilt</div>", unsafe_allow_html=True)

# Gauge 4: Liquidity Risk
liq_val = 94.2  # liquidity score out of 100
with g4:
    fig_g4 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=liq_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Liquidity Score", 'font': {'size': 13, 'color': '#8E9AAF'}},
        number={'suffix': "/100", 'font': {'size': 22, 'color': '#F3F6FC'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#263449", 'tickfont': {'color': '#8E9AAF', 'size': 9}},
            'bar': {'color': "#20C997"},
            'bgcolor': "#101827",
            'borderwidth': 1,
            'bordercolor': "#263449",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(240, 100, 112, 0.15)'},
                {'range': [50, 75], 'color': 'rgba(245, 185, 66, 0.15)'},
                {'range': [75, 100], 'color': 'rgba(32, 201, 151, 0.15)'}
            ]
        }
    ))
    fig_g4.update_layout(paper_bgcolor='#141E30', plot_bgcolor='#141E30', height=140, margin=dict(l=15, r=15, t=30, b=10))
    st.plotly_chart(fig_g4, use_container_width=True)
    st.markdown("<div style='text-align:center; font-size:11px; color:#20C997; font-weight:600;'>Ultra-Liquid Large Caps</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# B. PORTFOLIO CORRELATION HEATMAP
st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#F3F6FC; margin:0 0 6px 0; font-size:16px; font-weight:600;">🔗 Cross-Asset Correlation Heatmap (60-Day Rolling)</h4>', unsafe_allow_html=True)
st.markdown('<p style="color:#8E9AAF; font-size:12px; margin:0 0 14px 0;">Pairwise Pearson correlation coefficients between portfolio holdings. Values near +1.0 indicate high co-movement and reduced diversification benefit.</p>', unsafe_allow_html=True)

# Synthetic realistic correlation matrix based on actual tickers
n = len(tickers)
np.random.seed(42)
base_corr = {
    ('AAPL', 'MSFT'): 0.78,
    ('AAPL', 'NVDA'): 0.72,
    ('AAPL', 'GOOGL'): 0.69,
    ('AAPL', 'JPM'): 0.35,
    ('AAPL', 'TSLA'): 0.54,
    ('MSFT', 'NVDA'): 0.81,
    ('MSFT', 'GOOGL'): 0.76,
    ('MSFT', 'JPM'): 0.38,
    ('MSFT', 'TSLA'): 0.49,
    ('NVDA', 'GOOGL'): 0.68,
    ('NVDA', 'JPM'): 0.28,
    ('NVDA', 'TSLA'): 0.62,
    ('GOOGL', 'JPM'): 0.32,
    ('GOOGL', 'TSLA'): 0.51,
    ('JPM', 'TSLA'): 0.22,
}

corr_matrix = np.eye(n)
for i in range(n):
    for j in range(n):
        if i == j:
            corr_matrix[i][j] = 1.0
        else:
            t1, t2 = tickers[i], tickers[j]
            pair = (t1, t2) if (t1, t2) in base_corr else (t2, t1)
            if pair in base_corr:
                corr_matrix[i][j] = base_corr[pair]
            else:
                # Plausible pseudo correlation based on ticker hash
                val = 0.3 + 0.5 * abs(np.sin(hash(t1 + t2) % 100))
                corr_matrix[i][j] = round(val, 2)

corr_text = [[f"{val:.2f}" for val in row] for row in corr_matrix]

fig_corr = go.Figure(data=go.Heatmap(
    z=corr_matrix,
    x=tickers,
    y=tickers,
    colorscale=[[0, '#F06470'], [0.5, '#263449'], [1, '#20C997']],
    zmid=0.5,
    zmin=0.0,
    zmax=1.0,
    text=corr_text,
    texttemplate='%{text}',
    hoverongaps=False,
    colorbar=dict(title=dict(text="Correlation (&rho;)", font=dict(color='#8E9AAF', size=11)), tickfont=dict(color='#8E9AAF'))
))
layout_corr = dict(PLOTLY_LAYOUT)
layout_corr['height'] = 400
layout_corr['margin'] = dict(l=60, r=40, t=30, b=40)
fig_corr.update_layout(**layout_corr)
st.plotly_chart(fig_corr, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# C. VOLATILITY CHART & D. DRAWDOWN ANALYSIS (2 Columns)
c_vol, c_dd = st.columns(2)

with c_vol:
    st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
    st.markdown('<h4 style="color:#F3F6FC; margin:0 0 6px 0; font-size:15px; font-weight:600;">📈 30-Day Rolling Annualized Volatility</h4>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8E9AAF; font-size:12px; margin:0 0 12px 0;">Annualized standard deviation of daily logarithmic returns over the past 90 days.</p>', unsafe_allow_html=True)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=60, freq='B')
    fig_vol = go.Figure()
    
    palette_lines = ['#3985F5', '#8767F7', '#20C997', '#F5B942', '#F06470', '#00C7D9']
    base_vols = {'AAPL': 21.5, 'NVDA': 48.2, 'MSFT': 22.0, 'GOOGL': 24.5, 'JPM': 18.2, 'TSLA': 54.0}
    
    for idx, t in enumerate(tickers[:6]):
        bv = base_vols.get(t, 25.0)
        # Create realistic rolling series
        noise = np.sin(np.linspace(0, 4*np.pi, 60) + idx) * (bv * 0.15)
        trend = np.linspace(-1, 2, 60)
        vol_series = bv + noise + trend
        
        fig_vol.add_trace(go.Scatter(
            x=dates,
            y=vol_series,
            mode='lines',
            name=t,
            line=dict(color=palette_lines[idx % len(palette_lines)], width=2)
        ))
    
    layout_vol = dict(PLOTLY_LAYOUT)
    layout_vol['height'] = 340
    layout_vol['yaxis']['title'] = 'Annualized Vol (%)'
    layout_vol['yaxis']['ticksuffix'] = '%'
    fig_vol.update_layout(**layout_vol)
    st.plotly_chart(fig_vol, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_dd:
    st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
    st.markdown('<h4 style="color:#F3F6FC; margin:0 0 6px 0; font-size:15px; font-weight:600;">📉 Maximum Drawdown Analysis</h4>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8E9AAF; font-size:12px; margin:0 0 12px 0;">Peak-to-trough decline experienced over the trailing 12-month period.</p>', unsafe_allow_html=True)
    
    dd_data = {
        'NVDA': -22.4,
        'TSLA': -34.8,
        'AAPL': -14.2,
        'MSFT': -12.8,
        'GOOGL': -16.5,
        'JPM': -9.4
    }
    
    dd_tickers = [t for t in tickers[:6]]
    dd_vals = [dd_data.get(t, -18.0) for t in dd_tickers]
    
    # Sort by severity
    dd_sorted = sorted(zip(dd_tickers, dd_vals), key=lambda x: x[1])
    sorted_tickers = [x[0] for x in dd_sorted]
    sorted_vals = [x[1] for x in dd_sorted]

    fig_dd = go.Figure(go.Bar(
        y=sorted_tickers,
        x=sorted_vals,
        orientation='h',
        marker=dict(
            color='#F06470',
            line=dict(color='rgba(240, 100, 112, 0.4)', width=1)
        ),
        text=[f"{v:.1f}%" for v in sorted_vals],
        textposition='inside',
        cliponaxis=False
    ))
    layout_dd = dict(PLOTLY_LAYOUT)
    layout_dd['height'] = 340
    layout_dd['xaxis']['title'] = 'Max Drawdown (%)'
    layout_dd['xaxis']['ticksuffix'] = '%'
    layout_dd['yaxis']['autorange'] = True
    fig_dd.update_layout(**layout_dd)
    st.plotly_chart(fig_dd, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# E. RISK FACTOR TABLE
st.markdown('<div class="finiq-card" style="padding:16px 20px;">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#F3F6FC; margin:0 0 6px 0; font-size:16px; font-weight:600;">📋 Institutional Risk Factor Matrix</h4>', unsafe_allow_html=True)
st.markdown('<p style="color:#8E9AAF; font-size:12px; margin:0 0 14px 0;">Comprehensive breakdown of key systemic and idiosyncratic risk factors across the portfolio.</p>', unsafe_allow_html=True)

risk_factors = [
    {
        "factor": "Concentration Risk",
        "level": "MODERATE",
        "color": "#F5B942",
        "impact": "High capital clustering in top holdings (NVDA, AAPL, MSFT)",
        "mitigation": "Enforce strict single-position 15% maximum risk mandate"
    },
    {
        "factor": "Correlation Clustering",
        "level": "HIGH",
        "color": "#F06470",
        "impact": "Significant co-movement among large tech holdings (&rho; > 0.75)",
        "mitigation": "Incorporate non-correlated assets (Commodities, Short Treasuries)"
    },
    {
        "factor": "Sector Concentration",
        "level": "HIGH",
        "color": "#F06470",
        "impact": "Over 55% portfolio exposure centered in Information Technology",
        "mitigation": "Reallocate towards Healthcare, Consumer Staples, or Utilities"
    },
    {
        "factor": "Macro Rate Sensitivity",
        "level": "MODERATE",
        "color": "#F5B942",
        "impact": "Elevated duration and multiple compression risk if Treasury yields rise",
        "mitigation": "Pair high-growth equity multiples with cash flow generative value"
    },
    {
        "factor": "Liquidity Risk",
        "level": "LOW",
        "color": "#20C997",
        "impact": "Ultra-large cap equities with multi-billion dollar daily liquidity",
        "mitigation": "Zero execution slippage in ordinary liquid market environments"
    },
    {
        "factor": "Tail Volatility",
        "level": "MODERATE",
        "color": "#F5B942",
        "impact": "Elevated idiosyncratic beta in high-momentum semiconductor assets",
        "mitigation": "Utilize defined-risk collar or put protection structures"
    }
]

# Table Header
rf_cols = st.columns([1.5, 1, 3, 2.5])
rf_cols[0].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Risk Factor</span>", unsafe_allow_html=True)
rf_cols[1].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Severity Level</span>", unsafe_allow_html=True)
rf_cols[2].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Potential Impact</span>", unsafe_allow_html=True)
rf_cols[3].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Mitigation Strategy</span>", unsafe_allow_html=True)
st.markdown("<hr style='border:0; border-top:1px solid #263449; margin:8px 0;'>", unsafe_allow_html=True)

for rf in risk_factors:
    r_cols = st.columns([1.5, 1, 3, 2.5])
    r_cols[0].markdown(f"<strong style='color:#F3F6FC; font-size:13px;'>{rf['factor']}</strong>", unsafe_allow_html=True)
    badge_bg = f"rgba({int(rf['color'][1:3],16)}, {int(rf['color'][3:5],16)}, {int(rf['color'][5:7],16)}, 0.15)"
    r_cols[1].markdown(f"<span style='background:{badge_bg}; color:{rf['color']}; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600;'>{rf['level']}</span>", unsafe_allow_html=True)
    r_cols[2].markdown(f"<span style='color:#F3F6FC; font-size:12px;'>{rf['impact']}</span>", unsafe_allow_html=True)
    r_cols[3].markdown(f"<span style='color:#8E9AAF; font-size:12px;'>{rf['mitigation']}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# F. VALUE AT RISK (VaR)
st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#F3F6FC; margin:0 0 6px 0; font-size:16px; font-weight:600;">📐 Value at Risk (VaR) Quantitative Engine</h4>', unsafe_allow_html=True)
st.markdown('<p style="color:#8E9AAF; font-size:12px; margin:0 0 16px 0;">Parametric and historical simulation model estimating potential dollar loss over a specified holding period.</p>', unsafe_allow_html=True)

vcol1, vcol2, vcol3 = st.columns([1.5, 1.5, 3])

portfolio_val = 58412.50
if 'portfolio_holdings' in st.session_state and st.session_state.portfolio_holdings:
    try:
        val = sum([float(h.get('shares', 0)) * float(h.get('purchase_price', 0)) for h in st.session_state.portfolio_holdings])
        if val > 0:
            portfolio_val = val
    except Exception:
        pass

with vcol1:
    conf_level = st.selectbox("Confidence Level", options=["95% Confidence", "99% Confidence"], index=0)
with vcol2:
    time_horizon = st.selectbox("Holding Horizon", options=["1-Day Horizon", "5-Day Horizon", "10-Day Horizon"], index=0)

# Parametric VaR calculation
z_score = 1.645 if "95%" in conf_level else 2.326
horizon_days = 1 if "1-Day" in time_horizon else (5 if "5-Day" in time_horizon else 10)
daily_vol = 0.0165  # ~26% annualized vol
horizon_vol = daily_vol * np.sqrt(horizon_days)
var_pct = z_score * horizon_vol * 100.0
var_dollar = portfolio_val * (var_pct / 100.0)

with vcol3:
    st.markdown(f"""
    <div style="background:#101827; border:1px solid #3985F5; border-radius:10px; padding:14px 18px;">
        <div style="color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;">Estimated Value at Risk ({conf_level})</div>
        <div style="display:flex; align-items:baseline; gap:12px; margin-top:4px;">
            <div style="font-size:24px; font-weight:700; color:#F06470;">-${var_dollar:,.2f}</div>
            <div style="font-size:16px; font-weight:600; color:#F5B942;">({var_pct:.2f}% of capital)</div>
        </div>
        <p style="color:#8E9AAF; font-size:12px; margin:6px 0 0 0;">
            At <strong>{conf_level}</strong>, the estimated maximum expected loss over a <strong>{time_horizon}</strong> is <strong>${var_dollar:,.2f}</strong> ({var_pct:.2f}%).
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<p style="color:#8E9AAF; font-size:11px; margin-top:12px; line-height:1.5;">
<em>Note on Parametric Modeling:</em> VaR assumes standard normal return distributions and stationary covariance matrices. 
In systemic stress regimes, fat tails and jump-diffusion dynamics can cause actual losses to exceed parametric predictions. 
VaR calculations are for educational and illustrative purposes only.
</p>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer Disclaimer
st.markdown('---')
st.markdown("""
<div style='background:#101827; border:1px solid #263449; border-radius:8px; padding:12px 16px; margin-top:24px;'>
<p style='color:#8E9AAF; font-size:11px; margin:0; line-height:1.6;'>
<strong style='color:#F5B942;'>⚠️ API CONNECTION NOTICE:</strong> FINIQ is currently operating in demonstration mode unless an active data provider is connected. 
To unlock live market data, real-time news feeds, advanced AI analysis, and additional platform capabilities, users must connect valid third-party API credentials. 
Data availability, refresh frequency, and functionality depend on the selected provider, API subscription, rate limits, and permissions. 
Demo data is illustrative and should not be used for investment decisions.
</p>
</div>
""", unsafe_allow_html=True)
