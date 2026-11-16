"""
FINIQ - Financial News & Sentiment Intelligence
Real-time news processing, event classification, sentiment analytics, and topic clustering
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

# Import UI components and bridge functions
from app.ui_components import (
    inject_css,
    PLOTLY_LAYOUT,
    render_sidebar_branding,
    render_footer_disclaimer,
    safe_get_news
)

# Page Configuration
st.set_page_config(
    page_title="FINIQ — News Intelligence",
    page_icon="📰",
    layout="wide"
)

inject_css()
render_sidebar_branding()

# Top Header
st.markdown("""
<div style="font-size: 26px; font-weight: 800; letter-spacing: 0.04em; background: linear-gradient(90deg, #F3F6FC 0%, #3985F5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;">
    FINANCIAL NEWS & SENTIMENT INTELLIGENCE
</div>
<div style="font-size: 13px; color: #8E9AAF; margin-bottom: 20px;">
    Autonomous NLP news classification, institutional sentiment scoring, event tagging, and macroeconomic narratives
</div>
""", unsafe_allow_html=True)

# =====================================================================
# SEARCH & FILTER CONTROLS
# =====================================================================
col1, col2, col3 = st.columns([3, 1.2, 1.2])

with col1:
    search_query = st.text_input(
        "Search headlines, tickers, or themes",
        placeholder="e.g. AI chips, Federal Reserve, capex, antitrust, earnings",
        key="news_search_query"
    )

with col2:
    sentiment_filter = st.selectbox(
        "Sentiment Filter",
        options=["All", "Positive", "Negative", "Neutral"],
        index=0,
        key="news_sentiment_filter"
    )

with col3:
    event_filter = st.selectbox(
        "Event Type Filter",
        options=["All", "Earnings", "Macro", "Product", "Analyst Rating", "Regulatory", "M&A"],
        index=0,
        key="news_event_filter"
    )

# =====================================================================
# TRENDING TOPICS CHIPS
# =====================================================================
trending_topics = [
    "AI Hyperscaler Capex",
    "Fed Neutral Rate",
    "Semiconductor Tariffs",
    "Options Skew Imbalance",
    "Big Tech Antitrust",
    "Treasury Steepener"
]

st.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin: 12px 0 18px 0; flex-wrap: wrap;">
    <span style="font-size: 11px; font-weight: 700; color: #8E9AAF; text-transform: uppercase;">Trending Institutional Topics:</span>
""", unsafe_allow_html=True)

topic_cols = st.columns(len(trending_topics))
for idx, topic in enumerate(trending_topics):
    with topic_cols[idx]:
        if st.button(f"#{topic}", key=f"topic_btn_{idx}", use_container_width=True):
            st.session_state.news_search_query = topic
            st.rerun()

# Fetch news articles
all_articles = safe_get_news(query=search_query, limit=30)

# Filter articles based on controls
filtered_articles = []
for a in all_articles:
    sent_match = (sentiment_filter == "All") or (a.get("sentiment", "").lower() == sentiment_filter.lower())
    ev_type = a.get("event_type", "general").lower()
    ev_match = (event_filter == "All") or (ev_type == event_filter.lower())
    
    q_match = True
    if search_query:
        sq = search_query.lower()
        q_match = (sq in a.get("headline", "").lower()) or (sq in a.get("summary", "").lower())
        
    if sent_match and ev_match and q_match:
        filtered_articles.append(a)

if not filtered_articles:
    filtered_articles = all_articles  # fallback if over-filtered

# Calculate sentiment statistics
pos_count = sum(1 for a in filtered_articles if a.get("sentiment") == "positive")
neg_count = sum(1 for a in filtered_articles if a.get("sentiment") == "negative")
neu_count = sum(1 for a in filtered_articles if a.get("sentiment") == "neutral")
total_arts = len(filtered_articles)

# =====================================================================
# SENTIMENT OVERVIEW & EVENT TYPE DISTRIBUTION CHARTS
# =====================================================================
col_metrics_charts, col_event_pie = st.columns([1.5, 1.2])

with col_metrics_charts:
    st.markdown('<div class="section-title">📊 News Sentiment Distribution</div>', unsafe_allow_html=True)
    
    # 3 Metrics at top
    m_c1, m_c2, m_c3 = st.columns(3)
    with m_c1:
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 8px;">
            <div class="metric-label">Positive Articles</div>
            <div class="metric-value" style="color: #20C997;">{pos_count} <span style="font-size: 13px; font-weight: 500;">({int(pos_count/max(1, total_arts)*100)}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m_c2:
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 8px;">
            <div class="metric-label">Neutral Articles</div>
            <div class="metric-value" style="color: #8E9AAF;">{neu_count} <span style="font-size: 13px; font-weight: 500;">({int(neu_count/max(1, total_arts)*100)}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m_c3:
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 8px;">
            <div class="metric-label">Negative Articles</div>
            <div class="metric-value" style="color: #F06470;">{neg_count} <span style="font-size: 13px; font-weight: 500;">({int(neg_count/max(1, total_arts)*100)}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    # Horizontal Sentiment Bar Chart
    sent_bar_fig = go.Figure()
    sent_bar_fig.add_trace(go.Bar(
        y=['Sentiment Flow'],
        x=[pos_count],
        name='Positive',
        orientation='h',
        marker=dict(color='#20C997')
    ))
    sent_bar_fig.add_trace(go.Bar(
        y=['Sentiment Flow'],
        x=[neu_count],
        name='Neutral',
        orientation='h',
        marker=dict(color='#8E9AAF')
    ))
    sent_bar_fig.add_trace(go.Bar(
        y=['Sentiment Flow'],
        x=[neg_count],
        name='Negative',
        orientation='h',
        marker=dict(color='#F06470')
    ))
    
    sent_bar_fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode='stack',
        height=130,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(visible=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(sent_bar_fig, use_container_width=True, config={'displayModeBar': False})

with col_event_pie:
    st.markdown('<div class="section-title">🏷️ Event Type Distribution</div>', unsafe_allow_html=True)
    
    # Event breakdown
    event_counts = {}
    for a in filtered_articles:
        ev = a.get("event_type", "general").capitalize()
        event_counts[ev] = event_counts.get(ev, 0) + 1
        
    pie_fig = go.Figure(go.Pie(
        labels=list(event_counts.keys()),
        values=list(event_counts.values()),
        hole=0.55,
        marker=dict(
            colors=['#3985F5', '#8767F7', '#20C997', '#F5B942', '#F06470', '#8E9AAF'],
            line=dict(color='#141E30', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(color='#F3F6FC', size=11),
        hoverinfo='label+value+percent'
    ))
    
    pie_fig.update_layout(
        plot_bgcolor='#101827',
        paper_bgcolor='#141E30',
        font=dict(family='Inter, sans-serif', color='#F3F6FC'),
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False
    )
    st.plotly_chart(pie_fig, use_container_width=True, config={'displayModeBar': False})

# =====================================================================
# NEWS ARTICLES 3-COLUMN GRID
# =====================================================================
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
st.markdown(f'<div class="section-title">📰 Filtered Institutional News Stream ({len(filtered_articles)} Articles)</div>', unsafe_allow_html=True)

grid_cols = st.columns(3)

for idx, article in enumerate(filtered_articles):
    target_col = grid_cols[idx % 3]
    
    sent = article.get("sentiment", "neutral").lower()
    badge_cls = "badge-positive" if sent == "positive" else ("badge-negative" if sent == "negative" else "badge-neutral")
    ev_tag = article.get("event_type", "macro").upper()
    relevance = int(article.get("relevance_score", 0.88) * 100)
    
    with target_col:
        st.markdown(f"""
        <div class="news-card finiq-card" style="margin-bottom: 16px;">
            <div>
                <div class="news-meta">
                    <span style="font-weight: 700; color: #F3F6FC;">{article.get('source', 'FINIQ Wire')}</span>
                    <span>•</span>
                    <span>{article.get('published_at', '15m ago')}</span>
                    <span>•</span>
                    <span class="{badge_cls}">{sent.capitalize()}</span>
                </div>
                <div class="news-headline" style="font-size: 14px; margin-bottom: 8px;">
                    {article.get('headline')}
                </div>
                <div class="news-summary" style="font-size: 12px; line-height: 1.5; color: #BAC7D5; margin-bottom: 12px;">
                    {article.get('summary')}
                </div>
            </div>
            
            <div style="border-top: 1px solid rgba(38,52,73,0.5); padding-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                <span class="badge-purple" style="font-size: 10px;">🏷️ {ev_tag}</span>
                <span style="font-size: 11px; color: #8E9AAF;">Relevance: {relevance}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer Disclaimer
render_footer_disclaimer()
