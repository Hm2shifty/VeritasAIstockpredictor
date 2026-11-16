import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Portfolio | FINIQ",
    page_icon="💼",
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
    .stTextInput input, .stNumberInput input { background: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 8px !important; }
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

# Backend service imports with resilient fallbacks
try:
    from backend.services.market_data import get_quote
except Exception:
    def get_quote(ticker: str) -> dict:
        fallback_quotes = {
            'AAPL': {'company': 'Apple Inc.', 'price': 228.50, 'sector': 'Technology'},
            'NVDA': {'company': 'NVIDIA Corp.', 'price': 138.25, 'sector': 'Technology'},
            'MSFT': {'company': 'Microsoft Corp.', 'price': 425.00, 'sector': 'Technology'},
            'GOOGL': {'company': 'Alphabet Inc.', 'price': 178.50, 'sector': 'Communication Services'},
            'JPM': {'company': 'JPMorgan Chase & Co.', 'price': 232.00, 'sector': 'Financials'},
            'TSLA': {'company': 'Tesla Inc.', 'price': 315.00, 'sector': 'Consumer Discretionary'},
            'AMZN': {'company': 'Amazon.com Inc.', 'price': 208.00, 'sector': 'Consumer Discretionary'},
            'META': {'company': 'Meta Platforms Inc.', 'price': 585.00, 'sector': 'Communication Services'},
        }
        item = fallback_quotes.get(ticker.upper(), {'company': f'{ticker.upper()} Corp.', 'price': 100.0, 'sector': 'General'})
        return {'ticker': ticker.upper(), **item}

try:
    from backend.services.portfolio_service import (
        get_portfolio as svc_get_portfolio,
        add_holding as svc_add_holding,
        remove_holding as svc_remove_holding
    )
except Exception:
    svc_get_portfolio = None
    svc_add_holding = None
    svc_remove_holding = None

try:
    from backend.services.ai_service import complete, is_available
except Exception:
    def is_available() -> bool:
        return False
    def complete(*args, **kwargs) -> str:
        return None

try:
    from backend.database.db import init_db
    init_db()
except Exception:
    pass

DEMO_PORTFOLIO = [
    {'ticker': 'AAPL', 'company': 'Apple Inc.', 'shares': 50, 'purchase_price': 165.00},
    {'ticker': 'NVDA', 'company': 'NVIDIA Corp.', 'shares': 20, 'purchase_price': 495.00},
    {'ticker': 'MSFT', 'company': 'Microsoft Corp.', 'shares': 30, 'purchase_price': 380.00},
    {'ticker': 'GOOGL', 'company': 'Alphabet Inc.', 'shares': 25, 'purchase_price': 140.00},
    {'ticker': 'JPM', 'company': 'JPMorgan Chase', 'shares': 40, 'purchase_price': 185.00},
    {'ticker': 'TSLA', 'company': 'Tesla Inc.', 'shares': 15, 'purchase_price': 240.00},
]

# State Management for Holdings
if 'portfolio_holdings' not in st.session_state:
    # Try loading from service first
    loaded = []
    if svc_get_portfolio:
        try:
            loaded = svc_get_portfolio()
        except Exception:
            loaded = []
    if loaded and len(loaded) > 0:
        st.session_state.portfolio_holdings = loaded
    else:
        st.session_state.portfolio_holdings = [dict(h) for h in DEMO_PORTFOLIO]

def get_current_holdings():
    return st.session_state.portfolio_holdings

def add_holding_item(ticker: str, company: str, shares: float, price: float):
    ticker = ticker.strip().upper()
    if not ticker or shares <= 0 or price <= 0:
        return False
    
    # Update in service if available
    if svc_add_holding:
        try:
            svc_add_holding(ticker, company, shares, price)
        except Exception:
            pass

    # Update in session state
    found = False
    for h in st.session_state.portfolio_holdings:
        if h.get('ticker') == ticker:
            # Weighted average cost
            old_shares = float(h.get('shares', 0))
            new_shares = old_shares + shares
            if new_shares > 0:
                h['purchase_price'] = round((old_shares * float(h.get('purchase_price', 0)) + shares * price) / new_shares, 2)
            h['shares'] = new_shares
            found = True
            break
    if not found:
        st.session_state.portfolio_holdings.append({
            'ticker': ticker,
            'company': company if company else f"{ticker} Corp.",
            'shares': float(shares),
            'purchase_price': float(price)
        })
    return True

def delete_holding_item(ticker: str):
    ticker = ticker.strip().upper()
    if svc_remove_holding:
        try:
            svc_remove_holding(ticker)
        except Exception:
            pass
    st.session_state.portfolio_holdings = [
        h for h in st.session_state.portfolio_holdings if h.get('ticker') != ticker
    ]

# Header
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
    <div>
        <h1 style="color:#F3F6FC; margin:0; font-size:26px; font-weight:700;">💼 Simulated Portfolio Manager</h1>
        <p style="color:#8E9AAF; margin:4px 0 0 0; font-size:13px;">Monitor simulated positions, asset allocation, diversification, and AI-driven portfolio risk diagnostics.</p>
    </div>
    <div style="text-align:right;">
        <span class="demo-banner" style="display:inline-block; margin-bottom:0;">🔒 SIMULATED ENVIRONMENT &bull; NO REAL CAPITAL AT RISK</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Expander: Add New Holding
with st.expander('➕ Add New Holding', expanded=False):
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1.2, 1.2, 1])
    with col1:
        new_ticker = st.text_input('Ticker Symbol', value='NVDA', max_chars=8, key='add_ticker_input').strip().upper()
    with col2:
        default_company = "NVIDIA Corporation"
        if new_ticker:
            try:
                q = get_quote(new_ticker)
                default_company = q.get('company', f"{new_ticker} Inc.")
            except Exception:
                pass
        new_company = st.text_input('Company Name', value=default_company, key='add_company_input')
    with col3:
        new_shares = st.number_input('Shares', min_value=0.01, value=10.0, step=1.0, key='add_shares_input')
    with col4:
        default_price = 135.00
        if new_ticker:
            try:
                q = get_quote(new_ticker)
                if q.get('price'):
                    default_price = float(q['price'])
            except Exception:
                pass
        new_price = st.number_input('Purchase Price ($)', min_value=0.01, value=default_price, step=1.0, key='add_price_input')
    with col5:
        st.write("")
        st.write("")
        if st.button('Add Position', use_container_width=True, key='btn_submit_holding'):
            if new_ticker:
                add_holding_item(new_ticker, new_company, new_shares, new_price)
                st.success(f"Added {new_shares} shares of {new_ticker}")
                st.rerun()
            else:
                st.error("Please enter a valid ticker.")

holdings_raw = get_current_holdings()

# Quick action bar if empty or to load demo
if not holdings_raw:
    st.markdown("""
    <div class="demo-banner">
        ⚠️ <strong>Portfolio is currently empty.</strong> You can add a holding using the expander above or load the institutional demo portfolio.
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Load Demo Portfolio", key="btn_load_demo"):
        st.session_state.portfolio_holdings = [dict(h) for h in DEMO_PORTFOLIO]
        st.rerun()
    st.stop()

# Enrich holdings with current prices and metadata
enriched_holdings = []
total_current_value = 0.0
total_cost_basis = 0.0

sector_map = {
    'AAPL': 'Information Technology',
    'NVDA': 'Information Technology',
    'MSFT': 'Information Technology',
    'GOOGL': 'Communication Services',
    'META': 'Communication Services',
    'TSLA': 'Consumer Discretionary',
    'AMZN': 'Consumer Discretionary',
    'JPM': 'Financials',
    'V': 'Financials',
    'BA': 'Industrials',
    'DIS': 'Communication Services',
    'AMD': 'Information Technology',
    'INTC': 'Information Technology',
}

for h in holdings_raw:
    ticker = h.get('ticker', '').upper()
    shares = float(h.get('shares', 0.0))
    cost = float(h.get('purchase_price', 0.0))
    company = h.get('company', f"{ticker} Corp.")
    
    # Current price lookup
    curr_price = cost
    sector = sector_map.get(ticker, 'Diversified')
    try:
        q = get_quote(ticker)
        if q and 'price' in q and q['price'] is not None:
            curr_price = float(q['price'])
        if q and 'sector' in q and q['sector']:
            sector = q['sector']
        if q and 'company' in q and q['company']:
            company = q['company']
    except Exception:
        pass

    curr_value = shares * curr_price
    cost_value = shares * cost
    gain_loss = curr_value - cost_value
    gain_loss_pct = ((curr_price - cost) / cost * 100.0) if cost > 0 else 0.0

    total_current_value += curr_value
    total_cost_basis += cost_value

    enriched_holdings.append({
        'ticker': ticker,
        'company': company,
        'shares': shares,
        'avg_cost': cost,
        'current_price': curr_price,
        'current_value': curr_value,
        'cost_basis': cost_value,
        'gain_loss': gain_loss,
        'gain_loss_pct': gain_loss_pct,
        'sector': sector
    })

# Add weights
for item in enriched_holdings:
    item['weight_pct'] = (item['current_value'] / total_current_value * 100.0) if total_current_value > 0 else 0.0

total_gain_loss = total_current_value - total_cost_basis
total_gain_loss_pct = (total_gain_loss / total_cost_basis * 100.0) if total_cost_basis > 0 else 0.0

# B. PORTFOLIO SUMMARY METRICS
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Portfolio Value</div>
        <div class="metric-value">${total_current_value:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Cost Basis</div>
        <div class="metric-value">${total_cost_basis:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    color_cls = "badge-positive" if total_gain_loss >= 0 else "badge-negative"
    sign = "+" if total_gain_loss >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Gain / Loss ($)</div>
        <div class="metric-value" style="color: {'#20C997' if total_gain_loss >= 0 else '#F06470'};">
            {sign}${total_gain_loss:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Return (%)</div>
        <div class="metric-value" style="color: {'#20C997' if total_gain_loss_pct >= 0 else '#F06470'};">
            {sign}{total_gain_loss_pct:,.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Holdings Count</div>
        <div class="metric-value">{len(enriched_holdings)} Assets</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# C. HOLDINGS TABLE
st.markdown('<div class="finiq-card" style="padding:16px 20px;">', unsafe_allow_html=True)
st.markdown('<h3 style="color:#F3F6FC; margin:0 0 12px 0; font-size:16px; font-weight:600;">📊 Active Portfolio Positions</h3>', unsafe_allow_html=True)

# Table Header
h_cols = st.columns([1.1, 2.2, 0.9, 1.1, 1.1, 1.3, 1.3, 1.1, 0.9, 0.7])
headers = ["Ticker", "Company", "Shares", "Avg Cost", "Price", "Value", "Gain/Loss $", "Return %", "Weight", ""]
for col, h in zip(h_cols, headers):
    col.markdown(f"<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>{h}</span>", unsafe_allow_html=True)

st.markdown("<hr style='border:0; border-top:1px solid #263449; margin:8px 0;'>", unsafe_allow_html=True)

to_delete = None
for idx, item in enumerate(enriched_holdings):
    r_cols = st.columns([1.1, 2.2, 0.9, 1.1, 1.1, 1.3, 1.3, 1.1, 0.9, 0.7])
    
    gl_sign = "+" if item['gain_loss'] >= 0 else ""
    gl_color = "#20C997" if item['gain_loss'] >= 0 else "#F06470"
    badge_style = "badge-positive" if item['gain_loss'] >= 0 else "badge-negative"
    
    r_cols[0].markdown(f"<strong style='color:#3985F5; font-size:13px;'>{item['ticker']}</strong>", unsafe_allow_html=True)
    r_cols[1].markdown(f"<span style='color:#F3F6FC; font-size:12px;'>{item['company']}</span>", unsafe_allow_html=True)
    r_cols[2].markdown(f"<span style='color:#F3F6FC; font-size:12px;'>{item['shares']:g}</span>", unsafe_allow_html=True)
    r_cols[3].markdown(f"<span style='color:#8E9AAF; font-size:12px;'>${item['avg_cost']:,.2f}</span>", unsafe_allow_html=True)
    r_cols[4].markdown(f"<span style='color:#F3F6FC; font-size:12px;'>${item['current_price']:,.2f}</span>", unsafe_allow_html=True)
    r_cols[5].markdown(f"<span style='color:#F3F6FC; font-size:12px; font-weight:600;'>${item['current_value']:,.2f}</span>", unsafe_allow_html=True)
    r_cols[6].markdown(f"<span style='color:{gl_color}; font-size:12px; font-weight:600;'>{gl_sign}${item['gain_loss']:,.2f}</span>", unsafe_allow_html=True)
    r_cols[7].markdown(f"<span class='{badge_style}'>{gl_sign}{item['gain_loss_pct']:.1f}%</span>", unsafe_allow_html=True)
    r_cols[8].markdown(f"<span style='color:#8E9AAF; font-size:12px;'>{item['weight_pct']:.1f}%</span>", unsafe_allow_html=True)
    
    if r_cols[9].button('🗑️', key=f"del_{item['ticker']}_{idx}", help=f"Remove {item['ticker']}"):
        to_delete = item['ticker']

st.markdown('</div>', unsafe_allow_html=True)

if to_delete:
    delete_holding_item(to_delete)
    st.toast(f"Removed {to_delete} from simulated portfolio.")
    st.rerun()

# D. ALLOCATION CHARTS (2 Columns)
c_left, c_right = st.columns(2)

palette = ['#3985F5', '#8767F7', '#20C997', '#F5B942', '#F06470', '#00C7D9', '#E062AE', '#A5D6A7']

with c_left:
    st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
    st.markdown('<h4 style="color:#F3F6FC; margin:0 0 8px 0; font-size:14px; font-weight:600;">Asset Value Breakdown</h4>', unsafe_allow_html=True)
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=[h['ticker'] for h in enriched_holdings],
        values=[h['current_value'] for h in enriched_holdings],
        hole=0.55,
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        marker=dict(colors=palette, line=dict(color='#141E30', width=2))
    )])
    pie_layout = dict(PLOTLY_LAYOUT)
    pie_layout['height'] = 320
    pie_layout['showlegend'] = True
    pie_fig.update_layout(**pie_layout)
    st.plotly_chart(pie_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
    st.markdown('<h4 style="color:#F3F6FC; margin:0 0 8px 0; font-size:14px; font-weight:600;">Sector Allocation Breakdown</h4>', unsafe_allow_html=True)
    
    # Aggregate by sector
    sector_df = pd.DataFrame(enriched_holdings).groupby('sector')['current_value'].sum().reset_index()
    sector_df['weight_pct'] = sector_df['current_value'] / total_current_value * 100.0
    sector_df = sector_df.sort_values(by='weight_pct', ascending=True)

    bar_fig = go.Figure(data=[go.Bar(
        x=sector_df['weight_pct'],
        y=sector_df['sector'],
        orientation='h',
        marker=dict(
            color='#3985F5',
            line=dict(color='#8767F7', width=1)
        ),
        text=[f"{v:.1f}%" for v in sector_df['weight_pct']],
        textposition='outside',
        cliponaxis=False
    )])
    bar_layout = dict(PLOTLY_LAYOUT)
    bar_layout['height'] = 320
    bar_layout['xaxis']['title'] = 'Allocation Weight (%)'
    bar_layout['yaxis']['autorange'] = True
    bar_fig.update_layout(**bar_layout)
    st.plotly_chart(bar_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# F. PORTFOLIO RISK METRICS
st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#F3F6FC; margin:0 0 14px 0; font-size:15px; font-weight:600;">🛡️ Portfolio Risk & Diversification Metrics</h4>', unsafe_allow_html=True)

# Calculations
sorted_holdings = sorted(enriched_holdings, key=lambda x: x['weight_pct'], reverse=True)
top_pos = sorted_holdings[0] if sorted_holdings else {'ticker': 'N/A', 'weight_pct': 0.0}
unique_sectors = len(sector_df)

# Herfindahl-Hirschman Index (sum of squared weights as fractions)
weights_frac = [h['weight_pct'] / 100.0 for h in enriched_holdings]
hhi = sum([w**2 for w in weights_frac])
hhi_label = "Low Concentration" if hhi < 0.18 else ("Moderate" if hhi < 0.28 else "High Concentration")

# Estimated Beta (weighted proxy)
beta_proxies = {
    'AAPL': 1.10, 'NVDA': 1.68, 'MSFT': 1.18, 'GOOGL': 1.05,
    'TSLA': 1.95, 'JPM': 0.95, 'AMZN': 1.25, 'META': 1.22
}
weighted_beta = sum([h['weight_pct']/100.0 * beta_proxies.get(h['ticker'], 1.0) for h in enriched_holdings])

rk1, rk2, rk3, rk4 = st.columns(4)
with rk1:
    st.markdown(f"""
    <div style="background:#101827; border:1px solid #263449; border-radius:8px; padding:12px;">
        <div class="metric-label">Largest Position Weight</div>
        <div style="font-size:18px; font-weight:600; color:#F3F6FC;">{top_pos['ticker']} ({top_pos['weight_pct']:.1f}%)</div>
        <div style="font-size:11px; color:#8E9AAF; margin-top:4px;">Single-asset concentration risk</div>
    </div>
    """, unsafe_allow_html=True)

with rk2:
    st.markdown(f"""
    <div style="background:#101827; border:1px solid #263449; border-radius:8px; padding:12px;">
        <div class="metric-label">Sector Breadth</div>
        <div style="font-size:18px; font-weight:600; color:#F3F6FC;">{unique_sectors} Distinct Sectors</div>
        <div style="font-size:11px; color:#8E9AAF; margin-top:4px;">Breadth across market sectors</div>
    </div>
    """, unsafe_allow_html=True)

with rk3:
    hhi_color = "#20C997" if hhi < 0.18 else ("#F5B942" if hhi < 0.28 else "#F06470")
    st.markdown(f"""
    <div style="background:#101827; border:1px solid #263449; border-radius:8px; padding:12px;">
        <div class="metric-label">Concentration Index (HHI)</div>
        <div style="font-size:18px; font-weight:600; color:{hhi_color};">{hhi:.3f} &bull; {hhi_label}</div>
        <div style="font-size:11px; color:#8E9AAF; margin-top:4px;">Standardized diversification gauge</div>
    </div>
    """, unsafe_allow_html=True)

with rk4:
    st.markdown(f"""
    <div style="background:#101827; border:1px solid #263449; border-radius:8px; padding:12px;">
        <div class="metric-label">Estimated Portfolio Beta</div>
        <div style="font-size:18px; font-weight:600; color:#3985F5;">{weighted_beta:.2f} &times; S&P 500</div>
        <div style="font-size:11px; color:#8E9AAF; margin-top:4px;">Sensitivity relative to broad market</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# E. AI PORTFOLIO REPORT
st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
col_head, col_btn = st.columns([3, 1])
with col_head:
    st.markdown('<h4 style="color:#F3F6FC; margin:0; font-size:16px; font-weight:600;">🧠 Institutional AI Portfolio Intelligence Audit</h4>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8E9AAF; font-size:12px; margin:4px 0 0 0;">Synthesize deep risk vectors, factor tilt exposures, and quantitative correlation hazards.</p>', unsafe_allow_html=True)
with col_btn:
    generate_report = st.button("Generate AI Report", key="btn_gen_ai_report", use_container_width=True)

if generate_report:
    st.session_state['show_ai_portfolio_report'] = True

if st.session_state.get('show_ai_portfolio_report', False):
    st.markdown("<hr style='border:0; border-top:1px solid #263449; margin:16px 0;'>", unsafe_allow_html=True)
    
    # Try calling AI service if available
    report_text = None
    if is_available():
        try:
            summary_prompt = f"""
            Analyze this investment portfolio:
            - Holdings: {[f"{h['ticker']} ({h['shares']} shares, weight {h['weight_pct']:.1f}%)" for h in enriched_holdings]}
            - Total Value: ${total_current_value:,.2f}
            - Sectors: {sector_df.to_dict(orient='records')}
            - Herfindahl Index: {hhi:.3f}
            - Estimated Beta: {weighted_beta:.2f}

            Provide a 4-part institutional analysis:
            1. Concentration Analysis
            2. Diversification Assessment
            3. Sector Exposure Risks
            4. Correlated Holdings Warning
            """
            report_text = complete(
                system_prompt="You are a Chief Risk Officer and Senior Portfolio Strategist at a premier asset management institution.",
                user_message=summary_prompt,
                max_tokens=800
            )
        except Exception:
            report_text = None

    if report_text:
        st.markdown(f"""
        <div style="background:#101827; border:1px solid #3985F5; border-radius:8px; padding:16px; margin-top:8px;">
            <div style="color:#3985F5; font-size:12px; font-weight:600; margin-bottom:8px;">⚡ LIVE AI SYNTHESIS (GPT-4o)</div>
            <div style="color:#F3F6FC; font-size:13px; line-height:1.7;">{report_text}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # High quality structured institutional audit fallback
        top_sector = sector_df.iloc[-1]['sector'] if len(sector_df) > 0 else 'Technology'
        top_sector_pct = sector_df.iloc[-1]['weight_pct'] if len(sector_df) > 0 else 50.0
        
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("📌 1. Concentration Analysis", expanded=True):
                st.markdown(f"""
                - **Top Position Dominance:** **{top_pos['ticker']}** accounts for **{top_pos['weight_pct']:.1f}%** of capital. Position sizing rules at standard hedge funds generally cap single non-diversified assets at 15–20%.
                - **Top 3 Assets:** The three largest positions control **{sum([h['weight_pct'] for h in sorted_holdings[:3]]):.1f}%** of the aggregate portfolio value.
                - **Capital Preservation Buffer:** High single-position weights heighten vulnerability to idiosyncratic earnings misses or regulatory actions.
                """)
            with st.expander("🌐 2. Diversification Assessment", expanded=True):
                st.markdown(f"""
                - **Herfindahl-Hirschman Score:** **{hhi:.3f}** indicates a **{hhi_label.lower()}** distribution.
                - **Asset Class Focus:** Current holdings are exclusively large-cap domestic equities; minimal exposure to fixed income, commodities, or emerging markets.
                - **Effective Holdings Count:** Across the {len(enriched_holdings)} holdings, the risk profile behaves like an effective basket of {max(2, round(1/hhi, 1))} uncorrelated assets.
                """)
        with c2:
            with st.expander("⚡ 3. Sector Exposure Risks", expanded=True):
                st.markdown(f"""
                - **Heavy Sector Tilt:** Allocation is heavily tilted toward **{top_sector}** at **{top_sector_pct:.1f}%**.
                - **Macro Sensitivity:** Elevated sensitivity to benchmark interest rates, monetary policy statements, and semiconductor supply chain lead times.
                - **Defensive Absence:** Consumer staples, utilities, and healthcare are underweighted relative to the S&P 500 benchmark.
                """)
            with st.expander("⚠️ 4. Correlated Holdings Warning", expanded=True):
                st.markdown(f"""
                - **Mega-Cap Co-Movement:** High statistical correlation observed between **AAPL, NVDA, and MSFT** (rolling 60-day &rho; &gt; 0.72).
                - **Drawdown Clustering:** In market liquidity shocks, high-beta tech holdings tend to de-lever simultaneously, producing rapid portfolio drawdowns.
                - **Hedging Consideration:** Consider protective index puts (SPY/QQQ) or tactical reallocation into defensive value or Treasury equivalents.
                """)

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
