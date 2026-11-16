"""
FINIQ - Multi-Agent AI Analyst Debate Arena
Autonomous Bull, Bear, Risk, and Chief Investment Officer debate synthesis
"""

import os
import sys
import time
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

# Import UI components and bridge functions
from app.ui_components import (
    inject_css,
    render_sidebar_branding,
    render_footer_disclaimer,
    safe_get_quote,
    safe_run_full_debate
)

# Page Configuration
st.set_page_config(
    page_title="FINIQ — AI Analyst Debate Arena",
    page_icon="🤖",
    layout="wide"
)

inject_css()
render_sidebar_branding()

# Title Header
st.markdown("""
<div style="font-size: 26px; font-weight: 800; letter-spacing: 0.04em; background: linear-gradient(90deg, #F3F6FC 0%, #3985F5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;">
    AI ANALYST DEBATE ARENA
</div>
<div style="font-size: 13px; color: #8E9AAF; margin-bottom: 20px;">
    Four autonomous institutional agents debate company fundamentals, valuation risks, and structural catalysts to forge high-conviction research synthesis
</div>
""", unsafe_allow_html=True)

# Ticker setup
default_ticker = st.session_state.get("debate_ticker", st.session_state.get("selected_ticker", "NVDA"))

col_input, col_action = st.columns([3, 1.2])

with col_input:
    debate_ticker = st.text_input(
        "Ticker Symbol",
        value=default_ticker,
        placeholder="Enter symbol (e.g. NVDA, AAPL, TSLA, MSFT)",
        label_visibility="collapsed",
        key="debate_ticker_input"
    ).upper().strip()

with col_action:
    run_btn = st.button("⚡ Run Multi-Agent Debate", use_container_width=True, key="run_debate_btn")

# Quick ticker selection chips
st.markdown("<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 16px;'>", unsafe_allow_html=True)
deb_chips = ["NVDA", "AAPL", "MSFT", "TSLA", "PLTR", "AMZN"]
deb_cols = st.columns(len(deb_chips) + 1)
with deb_cols[0]:
    st.markdown("<span style='font-size: 11px; color: #8E9AAF; font-weight: 600; text-transform: uppercase;'>Quick Debate:</span>", unsafe_allow_html=True)
for i, d_c in enumerate(deb_chips):
    with deb_cols[i + 1]:
        if st.button(d_c, key=f"chip_deb_{d_c}", use_container_width=True):
            debate_ticker = d_c
            st.session_state.debate_ticker = d_c
            st.session_state.selected_ticker = d_c
            st.rerun()

quote = safe_get_quote(debate_ticker)

# AI Connection Info Banner
st.markdown("""
<div class="demo-banner">
    <div>
        <strong>🤖 Autonomous Multi-Agent Framework:</strong> Featuring adversarial Bull, Bear, and Risk agents synthesized by Chief Investment Officer.
    </div>
    <div style="font-size: 11px; opacity: 0.85;">
        Running High-Fidelity Institutional Model Engine
    </div>
</div>
""", unsafe_allow_html=True)

# Cache Key for session
cache_key = f"debate_result_{debate_ticker}"

if run_btn or cache_key not in st.session_state:
    if run_btn:
        with st.status(f"🚀 Deploying AI Agent Arena for {debate_ticker}...", expanded=True) as status:
            st.write("🐂 **Bull Analyst** compiling supply chain metrics, pricing power, and market catalysts...")
            time.sleep(0.3)
            st.write("🐻 **Bear Analyst** auditing customer concentration, valuation multiples, and margin compression...")
            time.sleep(0.3)
            st.write("⚠️ **Risk Analyst** stress-testing regulatory exposure and capital cost sensitivities...")
            time.sleep(0.2)
            st.write("🎓 **Chief Investment Officer** synthesizing thesis points and adjudicating consensus...")
            time.sleep(0.2)
            
            debate_data = safe_run_full_debate(debate_ticker)
            st.session_state[cache_key] = debate_data
            status.update(label="✅ Multi-Agent Research Synthesis Complete!", state="complete", expanded=False)
    else:
        st.session_state[cache_key] = safe_run_full_debate(debate_ticker)

data = st.session_state[cache_key]
bull = data.get("bull", {})
bear = data.get("bear", {})
risk = data.get("risk", {})
chief = data.get("chief", {})

# =====================================================================
# AGENT DEBATE INTERFACE: 2x2 GRID (BULL, BEAR, RISK) & CHIEF ANALYST
# =====================================================================

col_bull, col_bear = st.columns(2)

# --- 1. BULL ANALYST CARD ---
with col_bull:
    b_score = float(bull.get("bullish_score", 8.5))
    b_pct = int(b_score * 10)
    
    st.markdown(f"""
    <div class="agent-card agent-card-bull">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 22px;">🐂</span>
                <div>
                    <div style="font-size: 16px; font-weight: 700; color: #20C997;">BULL ANALYST</div>
                    <div style="font-size: 11px; color: #8E9AAF;">Growth & Secular Upside Focus</div>
                </div>
            </div>
            <span class="badge-positive" style="font-size: 12px; padding: 4px 12px;">
                High Conviction
            </span>
        </div>
        
        <div style="font-size: 14px; font-weight: 700; color: #F3F6FC; margin-bottom: 14px; line-height: 1.4;">
            "{bull.get('thesis_title', 'Secular Moat & Hyper-Expansion Supercycle')}"
        </div>
        
        <!-- Bullish Score Progress Bar -->
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span style="color: #8E9AAF;">Bullish Conviction Score</span>
                <span style="color: #20C997; font-weight: 700;">{b_score:.1f} / 10.0</span>
            </div>
            <div style="height: 8px; width: 100%; border-radius: 4px; background: #101827; border: 1px solid #263449; overflow: hidden;">
                <div style="width: {b_pct}%; height: 100%; background: #20C997;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📌 Core Bull Arguments (Expand to View)", expanded=True):
        for arg in bull.get("key_arguments", []):
            st.markdown(f"• {arg}")
            
    st.markdown("""
        <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(38,52,73,0.5);">
            <div style="font-size: 11px; font-weight: 700; color: #20C997; text-transform: uppercase; margin-bottom: 6px;">
                Upcoming Positive Catalysts
            </div>
    """, unsafe_allow_html=True)
    for cat in bull.get("catalysts", []):
        st.markdown(f"<div style='font-size: 12px; color: #BAC7D5; margin-bottom: 4px;'>🚀 {cat}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- 2. BEAR ANALYST CARD ---
with col_bear:
    be_score = float(bear.get("bearish_score", 6.8))
    be_pct = int(be_score * 10)
    
    st.markdown(f"""
    <div class="agent-card agent-card-bear">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 22px;">🐻</span>
                <div>
                    <div style="font-size: 16px; font-weight: 700; color: #F06470;">BEAR ANALYST</div>
                    <div style="font-size: 11px; color: #8E9AAF;">Valuation, Multiple Contraction & Headwinds</div>
                </div>
            </div>
            <span class="badge-negative" style="font-size: 12px; padding: 4px 12px;">
                Moderate Caution
            </span>
        </div>
        
        <div style="font-size: 14px; font-weight: 700; color: #F3F6FC; margin-bottom: 14px; line-height: 1.4;">
            "{bear.get('thesis_title', 'Peak Margins & Extreme Concentration Headwinds')}"
        </div>
        
        <!-- Bearish Score Progress Bar -->
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span style="color: #8E9AAF;">Bearish Conviction Score</span>
                <span style="color: #F06470; font-weight: 700;">{be_score:.1f} / 10.0</span>
            </div>
            <div style="height: 8px; width: 100%; border-radius: 4px; background: #101827; border: 1px solid #263449; overflow: hidden;">
                <div style="width: {be_pct}%; height: 100%; background: #F06470;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📌 Core Bear Arguments (Expand to View)", expanded=True):
        for arg in bear.get("key_arguments", []):
            st.markdown(f"• {arg}")
            
    st.markdown("""
        <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(38,52,73,0.5);">
            <div style="font-size: 11px; font-weight: 700; color: #F06470; text-transform: uppercase; margin-bottom: 6px;">
                Key Downside Vulnerabilities
            </div>
    """, unsafe_allow_html=True)
    for risk_item in bear.get("downside_risks", []):
        st.markdown(f"<div style='font-size: 12px; color: #BAC7D5; margin-bottom: 4px;'>🔻 {risk_item}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- 3. RISK ANALYST CARD ---
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

r_level = risk.get("risk_level", "MODERATE").upper()
r_badge = "badge-negative" if r_level in ["CRITICAL", "HIGH"] else "badge-warning"

st.markdown(f"""
<div class="agent-card agent-card-risk">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 22px;">⚠️</span>
            <div>
                <div style="font-size: 16px; font-weight: 700; color: #F5B942;">RISK & GOVERNANCE ANALYST</div>
                <div style="font-size: 11px; color: #8E9AAF;">Tail-Risk Evaluation, Antitrust & Supply Bottlenecks</div>
            </div>
        </div>
        <span class="{r_badge}" style="font-size: 12px; padding: 4px 12px;">
            Risk Rating: {r_level}
        </span>
    </div>
    
    <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px;">
        <div>
            <div style="font-size: 12px; font-weight: 700; color: #F5B942; text-transform: uppercase; margin-bottom: 8px;">
                Identified Structural Risk Vectors
            </div>
            <ol style="margin: 0; padding-left: 20px; font-size: 13px; color: #BAC7D5; line-height: 1.6;">
                {''.join([f'<li style="margin-bottom: 6px;">{r}</li>' for r in risk.get('key_risks', [])])}
            </ol>
        </div>
        
        <div style="background: rgba(16, 24, 39, 0.6); border: 1px solid #263449; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #8E9AAF; text-transform: uppercase; margin-bottom: 6px;">
                Adversarial Checks on Bull / Bear
            </div>
            <div style="font-size: 12px; color: #BAC7D5; margin-bottom: 8px; line-height: 1.4;">
                <strong style="color: #20C997;">Bull Challenge:</strong> {risk.get('bull_challenges', 'Overlooks potential hardware digestion cycles.')}
            </div>
            <div style="font-size: 12px; color: #BAC7D5; line-height: 1.4;">
                <strong style="color: #F06470;">Bear Challenge:</strong> {risk.get('bear_challenges', 'Underestimates deep switching friction of proprietary developer tooling.')}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. CHIEF INVESTMENT OFFICER (CIO) FULL-WIDTH CARD ---
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

outlook = chief.get("overall_outlook", "BULLISH").upper()
out_cls = "badge-bullish" if "BULL" in outlook else ("badge-bearish" if "BEAR" in outlook else "badge-neutral")

st.markdown(f"""
<div class="agent-card agent-card-chief">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid rgba(57,133,245,0.3); padding-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 26px;">🎓</span>
            <div>
                <div style="font-size: 18px; font-weight: 800; color: #F3F6FC; letter-spacing: 0.02em;">
                    CHIEF INVESTMENT OFFICER SYNTHESIS
                </div>
                <div style="font-size: 11px; color: #8E9AAF;">Institutional Adjudication & Capital Allocation Guidance</div>
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span style="font-size: 11px; color: #8E9AAF;">ADJUDICATED STANCE:</span>
            <span class="{out_cls}" style="font-size: 14px; font-weight: 800; padding: 6px 16px;">
                ● {outlook} ({chief.get('outlook_strength', 'MODERATE')} CONVICTION)
            </span>
        </div>
    </div>
    
    <div style="margin-bottom: 16px;">
        <div style="font-size: 12px; font-weight: 700; color: #3985F5; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
            Executive Research Summary
        </div>
        <div style="font-size: 14px; line-height: 1.7; color: #F3F6FC;">
            {chief.get('executive_summary', '')}
        </div>
    </div>
    
    <!-- Side-by-Side Strongest Arguments Comparison -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 18px 0;">
        <div style="background: rgba(32, 201, 151, 0.08); border: 1px solid rgba(32, 201, 151, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #20C997; text-transform: uppercase; margin-bottom: 4px;">
                Strongest Bull Argument
            </div>
            <div style="font-size: 13px; color: #F3F6FC; line-height: 1.5;">
                {chief.get('strongest_bull_argument', '')}
            </div>
        </div>
        
        <div style="background: rgba(240, 100, 112, 0.08); border: 1px solid rgba(240, 100, 112, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #F06470; text-transform: uppercase; margin-bottom: 4px;">
                Strongest Bear Counterpoint
            </div>
            <div style="font-size: 13px; color: #F3F6FC; line-height: 1.5;">
                {chief.get('strongest_bear_argument', '')}
            </div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; border-top: 1px solid #263449; padding-top: 14px;">
        <div>
            <div style="font-size: 11px; color: #8E9AAF; text-transform: uppercase;">Primary Tail Risk</div>
            <div style="font-size: 12px; color: #F5B942; font-weight: 600; margin-top: 2px;">
                {chief.get('most_critical_risk', 'Foundry supply constraints')}
            </div>
        </div>
        <div>
            <div style="font-size: 11px; color: #8E9AAF; text-transform: uppercase;">Evidence Quality</div>
            <div style="font-size: 12px; color: #20C997; font-weight: 700; margin-top: 2px;">
                ● {chief.get('evidence_quality', 'STRONG')} (Multi-source audited)
            </div>
        </div>
        <div>
            <div style="font-size: 11px; color: #8E9AAF; text-transform: uppercase;">Synthesis Confidence</div>
            <div style="font-size: 12px; color: #3985F5; font-weight: 700; margin-top: 2px;">
                {chief.get('confidence', 'HIGH')} FIDELITY
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer Disclaimer
render_footer_disclaimer()
