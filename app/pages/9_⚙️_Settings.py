import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests

st.set_page_config(
    page_title="Settings | FINIQ",
    page_icon="⚙️",
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
    .stTextInput input, .stSelectbox select { background: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 8px !important; }
    .demo-banner { background: rgba(245,185,66,0.1); border: 1px solid rgba(245,185,66,0.3); border-radius: 8px; padding: 8px 16px; color: #F5B942; font-size: 12px; margin-bottom: 16px; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# Backend imports with resilient fallbacks
try:
    from backend.services.ai_service import is_available, get_client
except Exception:
    def is_available():
        return bool(os.environ.get('OPENAI_API_KEY'))
    def get_client():
        return None

try:
    from backend.services.market_data import get_data_status
except Exception:
    def get_data_status():
        if os.environ.get('ALPHA_VANTAGE_API_KEY') or os.environ.get('FINNHUB_API_KEY'):
            return 'LIVE'
        return 'DEMO'

try:
    from backend.database.db import get_setting, set_setting
except Exception:
    def get_setting(key, default=None):
        return os.environ.get(key, default)
    def set_setting(key, value):
        os.environ[key] = str(value)
        return True

# Helper functions for key management
def get_key_val(key_name: str) -> str:
    # Check session state first, then env, then db
    if key_name in st.session_state and st.session_state[key_name]:
        return st.session_state[key_name]
    if os.environ.get(key_name):
        return os.environ[key_name]
    try:
        val = get_setting(key_name)
        if val:
            return val
    except Exception:
        pass
    return ""

def mask_key(raw_key: str) -> str:
    if not raw_key:
        return ""
    if len(raw_key) <= 6:
        return "••••••"
    return "••••••••••••" + raw_key[-4:]

def save_key(key_name: str, new_val: str):
    if new_val:
        st.session_state[key_name] = new_val
        os.environ[key_name] = new_val
        try:
            set_setting(key_name, new_val)
        except Exception:
            pass

# A. PAGE HEADER
st.markdown("""
<div style="margin-bottom:20px;">
    <h1 style="color:#F3F6FC; margin:0; font-size:26px; font-weight:700;">⚙️ Settings & API Configuration</h1>
    <p style="color:#8E9AAF; margin:4px 0 0 0; font-size:13px;">Manage market data connectors, news feeds, OpenAI credentials, cache parameters, and system preferences.</p>
</div>
""", unsafe_allow_html=True)

# B. API STATUS OVERVIEW
av_key = get_key_val('ALPHA_VANTAGE_API_KEY')
fh_key = get_key_val('FINNHUB_API_KEY')
poly_key = get_key_val('POLYGON_API_KEY')
td_key = get_key_val('TWELVEDATA_API_KEY')
mkt_key = get_key_val('MARKETAUX_API_KEY')
news_key = get_key_val('NEWSAPI_KEY')
ai_key = get_key_val('OPENAI_API_KEY')

s1, s2, s3 = st.columns(3)

with s1:
    market_badge = '<span class="badge-positive">LIVE CONNECTED</span>' if (av_key or fh_key or poly_key or td_key) else '<span class="badge-warning">DEMO MODE / YFINANCE</span>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Market Data Provider</div>
        <div style="margin-top:6px;">{market_badge}</div>
        <div style="color:#8E9AAF; font-size:11px; margin-top:8px;">
            Alpha Vantage: {'✅' if av_key else '❌'} &bull; Finnhub: {'✅' if fh_key else '❌'} &bull; yfinance: ✅
        </div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    news_badge = '<span class="badge-positive">LIVE CONNECTED</span>' if (fh_key or mkt_key or news_key) else '<span class="badge-warning">DEMO FEED ACTIVE</span>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">News Intelligence Feed</div>
        <div style="margin-top:6px;">{news_badge}</div>
        <div style="color:#8E9AAF; font-size:11px; margin-top:8px;">
            Finnhub News: {'✅' if fh_key else '❌'} &bull; Marketaux: {'✅' if mkt_key else '❌'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    ai_badge = '<span class="badge-positive">OPENAI CONNECTED</span>' if ai_key else '<span class="badge-negative">DISCONNECTED</span>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">AI Engine (GPT-4o)</div>
        <div style="margin-top:6px;">{ai_badge}</div>
        <div style="color:#8E9AAF; font-size:11px; margin-top:8px;">
            Debate, Assistant & AI Reports {'Enabled' if ai_key else 'in Demo Fallback'}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# C. MARKET DATA PROVIDERS SECTION
st.markdown('<h3 style="color:#F3F6FC; font-size:17px; font-weight:600; margin-bottom:12px;">📊 Market Data Providers</h3>', unsafe_allow_html=True)

# 1. Alpha Vantage
av_status_badge = "✅ Connected" if av_key else "⚠️ Disconnected"
with st.expander(f"Alpha Vantage — {av_status_badge}", expanded=False):
    st.markdown("**Features:** Real-time equity quotes, intraday & daily historical timeseries, fundamentals, company earnings.")
    c_in, c_b1, c_b2 = st.columns([3, 1, 1])
    with c_in:
        av_input = st.text_input("Alpha Vantage API Key", value=av_key, type="password", key="inp_av_key", placeholder="Enter key...")
    with c_b1:
        st.write("")
        st.write("")
        if st.button("Save Key", key="save_av_btn", use_container_width=True):
            save_key('ALPHA_VANTAGE_API_KEY', av_input)
            st.success("Alpha Vantage API key saved!")
            st.rerun()
    with c_b2:
        st.write("")
        st.write("")
        if st.button("Test API", key="test_av_btn", use_container_width=True):
            test_key = av_input or av_key
            if not test_key:
                st.warning("Please enter a key to test.")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        r = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey={test_key}", timeout=6)
                        data = r.json()
                        if "Global Quote" in data or "Note" in data:
                            st.success("✅ Alpha Vantage connection verified successfully!")
                        elif "Error Message" in data:
                            st.error(f"❌ Alpha Vantage API returned error: {data['Error Message']}")
                        else:
                            st.info(f"Response received (status {r.status_code})")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

# 2. Finnhub
fh_status_badge = "✅ Connected" if fh_key else "⚠️ Disconnected"
with st.expander(f"Finnhub Stock API — {fh_status_badge}", expanded=False):
    st.markdown("**Features:** Real-time price quotes, market news, sentiment scores, insider transactions, SEC filings.")
    c_in, c_b1, c_b2 = st.columns([3, 1, 1])
    with c_in:
        fh_input = st.text_input("Finnhub API Key / Token", value=fh_key, type="password", key="inp_fh_key", placeholder="Enter token...")
    with c_b1:
        st.write("")
        st.write("")
        if st.button("Save Key", key="save_fh_btn", use_container_width=True):
            save_key('FINNHUB_API_KEY', fh_input)
            st.success("Finnhub token saved!")
            st.rerun()
    with c_b2:
        st.write("")
        st.write("")
        if st.button("Test API", key="test_fh_btn", use_container_width=True):
            test_key = fh_input or fh_key
            if not test_key:
                st.warning("Please enter a token to test.")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        r = requests.get(f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={test_key}", timeout=6)
                        if r.status_code == 200 and 'c' in r.json():
                            st.success("✅ Finnhub connection verified successfully!")
                        else:
                            st.error(f"❌ Finnhub test failed: HTTP {r.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

# 3. Polygon.io
poly_status_badge = "✅ Connected" if poly_key else "⚠️ Disconnected"
with st.expander(f"Polygon.io — {poly_status_badge}", expanded=False):
    st.markdown("**Features:** High-speed streaming ticks, aggregate bars, options, reference data.")
    c_in, c_b1, c_b2 = st.columns([3, 1, 1])
    with c_in:
        poly_input = st.text_input("Polygon.io API Key", value=poly_key, type="password", key="inp_poly_key", placeholder="Enter key...")
    with c_b1:
        st.write("")
        st.write("")
        if st.button("Save Key", key="save_poly_btn", use_container_width=True):
            save_key('POLYGON_API_KEY', poly_input)
            st.success("Polygon.io key saved!")
            st.rerun()
    with c_b2:
        st.write("")
        st.write("")
        if st.button("Test API", key="test_poly_btn", use_container_width=True):
            test_key = poly_input or poly_key
            if not test_key:
                st.warning("Please enter a key to test.")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        r = requests.get(f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={test_key}", timeout=6)
                        if r.status_code == 200:
                            st.success("✅ Polygon.io connection verified!")
                        else:
                            st.error(f"❌ Polygon.io returned HTTP {r.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

# 4. Twelve Data
td_status_badge = "✅ Connected" if td_key else "⚠️ Disconnected"
with st.expander(f"Twelve Data — {td_status_badge}", expanded=False):
    st.markdown("**Features:** Global equities, forex, cryptocurrencies, technical indicators API.")
    c_in, c_b1, c_b2 = st.columns([3, 1, 1])
    with c_in:
        td_input = st.text_input("Twelve Data API Key", value=td_key, type="password", key="inp_td_key", placeholder="Enter key...")
    with c_b1:
        st.write("")
        st.write("")
        if st.button("Save Key", key="save_td_btn", use_container_width=True):
            save_key('TWELVEDATA_API_KEY', td_input)
            st.success("Twelve Data key saved!")
            st.rerun()
    with c_b2:
        st.write("")
        st.write("")
        if st.button("Test API", key="test_td_btn", use_container_width=True):
            test_key = td_input or td_key
            if not test_key:
                st.warning("Please enter a key to test.")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        r = requests.get(f"https://api.twelvedata.com/price?symbol=AAPL&apikey={test_key}", timeout=6)
                        if r.status_code == 200 and 'price' in r.json():
                            st.success("✅ Twelve Data connection verified!")
                        else:
                            st.error(f"❌ Twelve Data returned error: {r.text[:80]}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

st.write("")

# D. NEWS PROVIDERS SECTION
st.markdown('<h3 style="color:#F3F6FC; font-size:17px; font-weight:600; margin-bottom:12px;">📰 News Intelligence Providers</h3>', unsafe_allow_html=True)

# 1. Marketaux
mkt_status_badge = "✅ Connected" if mkt_key else "⚠️ Disconnected"
with st.expander(f"Marketaux News API — {mkt_status_badge}", expanded=False):
    st.markdown("**Features:** AI-classified financial news, entity sentiment, ticker tagging, macro events.")
    c_in, c_b1, c_b2 = st.columns([3, 1, 1])
    with c_in:
        mkt_input = st.text_input("Marketaux API Token", value=mkt_key, type="password", key="inp_mkt_key", placeholder="Enter token...")
    with c_b1:
        st.write("")
        st.write("")
        if st.button("Save Key", key="save_mkt_btn", use_container_width=True):
            save_key('MARKETAUX_API_KEY', mkt_input)
            st.success("Marketaux key saved!")
            st.rerun()
    with c_b2:
        st.write("")
        st.write("")
        if st.button("Test API", key="test_mkt_btn", use_container_width=True):
            test_key = mkt_input or mkt_key
            if not test_key:
                st.warning("Please enter a token to test.")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        r = requests.get(f"https://api.marketaux.com/v1/news/all?symbols=AAPL&api_token={test_key}", timeout=6)
                        if r.status_code == 200:
                            st.success("✅ Marketaux news feed verified!")
                        else:
                            st.error(f"❌ Marketaux returned HTTP {r.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

# 2. NewsAPI
news_status_badge = "✅ Connected" if news_key else "⚠️ Disconnected"
with st.expander(f"NewsAPI.org — {news_status_badge}", expanded=False):
    st.markdown("**Features:** Global general business headlines, wire services, international coverage.")
    c_in, c_b1, c_b2 = st.columns([3, 1, 1])
    with c_in:
        news_input = st.text_input("NewsAPI Key", value=news_key, type="password", key="inp_news_key", placeholder="Enter key...")
    with c_b1:
        st.write("")
        st.write("")
        if st.button("Save Key", key="save_news_btn", use_container_width=True):
            save_key('NEWSAPI_KEY', news_input)
            st.success("NewsAPI key saved!")
            st.rerun()
    with c_b2:
        st.write("")
        st.write("")
        if st.button("Test API", key="test_news_btn", use_container_width=True):
            test_key = news_input or news_key
            if not test_key:
                st.warning("Please enter a key to test.")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        r = requests.get(f"https://newsapi.org/v2/top-headlines?category=business&apiKey={test_key}", timeout=6)
                        if r.status_code == 200:
                            st.success("✅ NewsAPI connection verified!")
                        else:
                            st.error(f"❌ NewsAPI returned HTTP {r.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

st.write("")

# E. AI PROVIDERS SECTION
st.markdown('<h3 style="color:#F3F6FC; font-size:17px; font-weight:600; margin-bottom:12px;">🧠 AI Reasoning Engine (OpenAI)</h3>', unsafe_allow_html=True)

ai_status_badge = "✅ Connected" if ai_key else "⚠️ Disconnected"
with st.expander(f"OpenAI GPT-4o API — {ai_status_badge}", expanded=True):
    st.markdown("**Features:** Powers the Multi-Agent Analyst Debate (Bull, Bear, Risk, Chief), Conversational AI Assistant, and Automated Portfolio Audits.")
    
    col_ai_k, col_ai_m = st.columns([2.5, 1.5])
    with col_ai_k:
        openai_input = st.text_input("OpenAI API Key", value=ai_key, type="password", key="inp_openai_key", placeholder="sk-proj-...")
    with col_ai_m:
        current_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        selected_model = st.selectbox("Model Selection", options=['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo'], index=0)
    
    col_ab1, col_ab2 = st.columns(2)
    with col_ab1:
        if st.button("Save OpenAI Configuration", key="save_openai_btn", use_container_width=True):
            save_key('OPENAI_API_KEY', openai_input)
            os.environ['OPENAI_MODEL'] = selected_model
            try:
                set_setting('OPENAI_MODEL', selected_model)
            except Exception:
                pass
            st.success("OpenAI configuration saved!")
            st.rerun()
    with col_ab2:
        if st.button("Test OpenAI Connection", key="test_openai_btn", use_container_width=True):
            test_key = openai_input or ai_key
            if not test_key:
                st.warning("Please provide an OpenAI API key.")
            else:
                with st.spinner("Testing OpenAI authentication..."):
                    try:
                        r = requests.get(
                            "https://api.openai.com/v1/models",
                            headers={"Authorization": f"Bearer {test_key}"},
                            timeout=7
                        )
                        if r.status_code == 200:
                            st.success(f"✅ OpenAI API connection successful! Ready with model '{selected_model}'.")
                        else:
                            st.error(f"❌ OpenAI authentication failed: HTTP {r.status_code} ({r.text[:80]})")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

    st.markdown("""
    <div style="background:#101827; border:1px solid #263449; border-radius:8px; padding:12px; margin-top:12px;">
        <span style="color:#3985F5; font-size:11px; font-weight:600; text-transform:uppercase;">Capabilities Unlocked with OpenAI:</span>
        <ul style="color:#8E9AAF; font-size:12px; margin:6px 0 0 16px; padding:0; line-height:1.6;">
            <li><strong>Multi-Agent Debate:</strong> Bull vs. Bear adversarial thesis exchange synthesized by Chief Investment Officer.</li>
            <li><strong>Interactive AI Assistant:</strong> Context-grounded educational financial research queries.</li>
            <li><strong>AI Portfolio Health Audit:</strong> Automated concentration, factor tilt, and correlation warning generation.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# F. FEATURES DEPENDENCY TABLE
st.markdown('<div class="finiq-card" style="padding:16px 20px;">', unsafe_allow_html=True)
st.markdown('<h3 style="color:#F3F6FC; font-size:16px; font-weight:600; margin:0 0 12px 0;">📋 Feature & API Dependency Matrix</h3>', unsafe_allow_html=True)

dep_cols = st.columns([2, 2.5, 1.5])
dep_cols[0].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Feature</span>", unsafe_allow_html=True)
dep_cols[1].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Required Connector</span>", unsafe_allow_html=True)
dep_cols[2].markdown("<span style='color:#8E9AAF; font-size:11px; font-weight:600; text-transform:uppercase;'>Current Status</span>", unsafe_allow_html=True)
st.markdown("<hr style='border:0; border-top:1px solid #263449; margin:8px 0;'>", unsafe_allow_html=True)

features_data = [
    ("Live Market Data", "Alpha Vantage or Finnhub", "✅ Live Connected" if (av_key or fh_key) else "⚠️ Demo Mode", "badge-positive" if (av_key or fh_key) else "badge-warning"),
    ("Real-Time News Feeds", "Finnhub News or Marketaux", "✅ Live Connected" if (fh_key or mkt_key) else "⚠️ Demo Mode", "badge-positive" if (fh_key or mkt_key) else "badge-warning"),
    ("AI Analyst Debate", "OpenAI API", "✅ Ready" if ai_key else "⚠️ Demo Fallback", "badge-positive" if ai_key else "badge-neutral"),
    ("Conversational AI Assistant", "OpenAI API", "✅ Ready" if ai_key else "⚠️ Demo Fallback", "badge-positive" if ai_key else "badge-neutral"),
    ("AI Portfolio Health Report", "OpenAI API", "✅ Ready" if ai_key else "⚠️ Demo Fallback", "badge-positive" if ai_key else "badge-neutral"),
    ("Historical Timeseries Charts", "yfinance (Free)", "✅ Always Available", "badge-positive"),
]

for feat, req, stat, badge_cls in features_data:
    r_cols = st.columns([2, 2.5, 1.5])
    r_cols[0].markdown(f"<strong style='color:#F3F6FC; font-size:13px;'>{feat}</strong>", unsafe_allow_html=True)
    r_cols[1].markdown(f"<span style='color:#8E9AAF; font-size:12px;'>{req}</span>", unsafe_allow_html=True)
    r_cols[2].markdown(f"<span class='{badge_cls}'>{stat}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# G. GENERAL SETTINGS
st.markdown('<div class="finiq-card">', unsafe_allow_html=True)
st.markdown('<h3 style="color:#F3F6FC; font-size:16px; font-weight:600; margin:0 0 14px 0;">⚙️ Application Execution & Cache Preferences</h3>', unsafe_allow_html=True)

gcol1, gcol2, gcol3 = st.columns(3)

with gcol1:
    refresh_int = st.select_slider(
        "Auto-Refresh Frequency",
        options=["30s", "60s", "5min", "15min", "Manual"],
        value="5min"
    )

with gcol2:
    cache_ttl = st.selectbox(
        "Cache Duration (TTL)",
        options=["60 seconds", "300 seconds (5 min)", "600 seconds (10 min)", "3600 seconds (1 hr)"],
        index=1
    )

with gcol3:
    demo_toggle = st.toggle("Enforce Demo Mode Only", value=False, help="When enabled, suppresses live API queries even if keys are provided.")

if st.button("Save General Preferences", key="save_gen_pref"):
    st.session_state['refresh_interval'] = refresh_int
    st.session_state['cache_ttl'] = cache_ttl
    st.session_state['force_demo_mode'] = demo_toggle
    st.toast("Application preferences updated successfully.")

st.markdown('</div>', unsafe_allow_html=True)

# H. ABOUT SECTION
st.markdown("""
<div class="finiq-card" style="border: 1px solid #263449;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h4 style="color:#F3F6FC; margin:0; font-size:15px; font-weight:600;">FINIQ Financial Intelligence Platform</h4>
            <p style="color:#8E9AAF; font-size:12px; margin:4px 0 0 0;">Version 1.0.0 &bull; Build 2026.11-Enterprise &bull; Streamlit + Python Modular Backend</p>
        </div>
        <div>
            <span class="badge-bullish">HACKATHON EDITION</span>
        </div>
    </div>
    <hr style="border:0; border-top:1px solid #263449; margin:12px 0;">
    <p style="color:#8E9AAF; font-size:11px; margin:0; line-height:1.6;">
        Designed for institutional-grade market intelligence, multi-agent adversarial synthesis, and quantitative portfolio risk oversight. 
        Developed with privacy-first boundaries where third-party data is sanitized against prompt injection prior to LLM reasoning.
    </p>
</div>
""", unsafe_allow_html=True)

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
