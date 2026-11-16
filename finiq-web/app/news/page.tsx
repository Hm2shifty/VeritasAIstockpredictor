'use client';

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import {
  Newspaper,
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Clock,
  Sparkles,
  ExternalLink,
  ShieldAlert,
  Tag,
  RefreshCw,
} from 'lucide-react';

interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  sentimentScore: number; // e.g. +0.82
  tickers: string[];
  url?: string;
}

const FALLBACK_NEWS: NewsArticle[] = [
  {
    id: 'art-1',
    title: 'Hyperscalers Escalate AI Capex Projections: Multi-Year Infrastructure Ramp Confirmed',
    summary: 'Cloud service providers announced expanded forward capital commitments targeting accelerated computing clusters and optical interconnects, exceeding consensus Wall Street estimates by 18%.',
    source: 'Bloomberg Technology',
    publishedAt: '25m ago',
    sentiment: 'positive',
    sentimentScore: 0.88,
    tickers: ['NVDA', 'MSFT', 'GOOGL', 'AMZN'],
  },
  {
    id: 'art-2',
    title: 'Federal Reserve Monetary Policy Minutes Signal Prolonged Caution on Rate Trajectory',
    summary: 'Policymakers emphasized strong employment metrics and steady core inflation as justification for a patient approach toward terminal rate adjustments in upcoming quarters.',
    source: 'Reuters Macro',
    publishedAt: '45m ago',
    sentiment: 'neutral',
    sentimentScore: 0.05,
    tickers: ['SPY', 'QQQ'],
  },
  {
    id: 'art-3',
    title: 'Automotive EV Margin Squeeze Persists Across European and Asian Manufacturing Hubs',
    summary: 'Price discounting across mass-market EV offerings continues compressing automotive gross margins, prompting revisions to full-year unit profitability targets.',
    source: 'Wall Street Journal',
    publishedAt: '1h ago',
    sentiment: 'negative',
    sentimentScore: -0.74,
    tickers: ['TSLA'],
  },
  {
    id: 'art-4',
    title: 'Palantir Secures Multi-Million Dollar Defense Intelligence Framework Expansion',
    summary: 'Government and enterprise contracts for automated decision-support platforms expanded under newly authorized procurement budgets, highlighting sovereign AI platform stickiness.',
    source: 'Defense One / FT',
    publishedAt: '2h ago',
    sentiment: 'positive',
    sentimentScore: 0.92,
    tickers: ['PLTR'],
  },
  {
    id: 'art-5',
    title: 'Semiconductor Wafer Packaging Bottlenecks Easing as New Foundries Ramp Output',
    summary: 'High-bandwidth memory integration and 2.5D packaging capacity improved 30% quarter-on-quarter, relieving production allocation ceilings for next-generation AI processors.',
    source: 'Nikkei Asian Review',
    publishedAt: '3h ago',
    sentiment: 'positive',
    sentimentScore: 0.79,
    tickers: ['NVDA', 'AMD', 'TSM'],
  },
  {
    id: 'art-6',
    title: 'Regulatory Scrutiny on Mobile Application Marketplace Commission Structures Deepens',
    summary: 'Antitrust regulators released preliminary findings recommending expanded third-party payment integration, creating modest revenue headwinds for digital service distribution.',
    source: 'CNBC Markets',
    publishedAt: '3h ago',
    sentiment: 'negative',
    sentimentScore: -0.65,
    tickers: ['AAPL', 'GOOGL'],
  },
  {
    id: 'art-7',
    title: 'Enterprise Software Spending Shows Resilient Cloud Migration Accelerations',
    summary: 'CIO sentiment surveys demonstrate software modernization budgets remain protected from discretionary spending cutbacks as businesses prioritize operational automation.',
    source: 'Barron\'s Tech',
    publishedAt: '4h ago',
    sentiment: 'positive',
    sentimentScore: 0.71,
    tickers: ['MSFT', 'CRWD', 'NOW'],
  },
  {
    id: 'art-8',
    title: 'Treasury Yield Curve Dynamics Reflect Steady Soft-Landing Macro Baseline',
    summary: 'Benchmark 10-year yields traded within a tight 8 bps band as institutional bond portfolios balanced robust retail sales against easing headline inflation prints.',
    source: 'MarketWatch Macro',
    publishedAt: '5h ago',
    sentiment: 'neutral',
    sentimentScore: 0.02,
    tickers: ['SPY', 'TLT'],
  },
];

export default function NewsIntelligencePage() {
  const [news, setNews] = useState<NewsArticle[]>(FALLBACK_NEWS);
  const [loading, setLoading] = useState(false);
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'negative' | 'neutral'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchNews = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/news');
      if (res.ok) {
        const data = await res.json();
        const items = Array.isArray(data) ? data : data.news || data.articles;
        if (Array.isArray(items) && items.length > 0) {
          setNews(items);
        }
      }
    } catch {
      // Use fallback news items silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  const filteredNews = useMemo(() => {
    return news.filter((item) => {
      // Sentiment filter
      if (sentimentFilter !== 'all' && item.sentiment !== sentimentFilter) {
        return false;
      }
      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = item.title.toLowerCase().includes(q);
        const matchSummary = item.summary.toLowerCase().includes(q);
        const matchTicker = item.tickers.some((t) => t.toLowerCase().includes(q));
        const matchSource = item.source.toLowerCase().includes(q);
        if (!matchTitle && !matchSummary && !matchTicker && !matchSource) {
          return false;
        }
      }
      return true;
    });
  }, [news, sentimentFilter, searchQuery]);

  // Sentiment counts
  const counts = useMemo(() => {
    return {
      all: news.length,
      positive: news.filter((n) => n.sentiment === 'positive').length,
      negative: news.filter((n) => n.sentiment === 'negative').length,
      neutral: news.filter((n) => n.sentiment === 'neutral').length,
    };
  }, [news]);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar
          title="Financial News & Sentiment Intelligence"
          subtitle="Real-time Natural Language Sentiment Classification"
        />

        <main className="page-container">
          {/* Header Banner */}
          <div
            className="card card-accent"
            style={{
              marginBottom: '24px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '16px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span className="badge badge-purple">
                  <Sparkles size={12} /> NLP Sentiment Engine
                </span>
                <span className="badge badge-blue">Continuous Ingestion</span>
              </div>
              <h2 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-0)', margin: '4px 0' }}>
                Market Narrative & Entity-Level Sentiment Tracking
              </h2>
              <p style={{ fontSize: '13px', color: 'var(--text-2)', margin: 0 }}>
                Algorithmic natural language parsing of global financial dispatches with ticker association and polarity scoring.
              </p>
            </div>

            <button
              onClick={fetchNews}
              disabled={loading}
              className="btn btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={14} className={loading ? 'spinner' : ''} />
              <span>{loading ? 'Refreshing...' : 'Refresh Feed'}</span>
            </button>
          </div>

          {/* Filter Bar: Sentiment Tabs + Search Input */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '24px',
              flexWrap: 'wrap',
              gap: '16px',
            }}
          >
            {/* Sentiment Tabs */}
            <div className="tab-bar" style={{ margin: 0 }}>
              <button
                onClick={() => setSentimentFilter('all')}
                className={`tab-btn ${sentimentFilter === 'all' ? 'active' : ''}`}
              >
                All News ({counts.all})
              </button>
              <button
                onClick={() => setSentimentFilter('positive')}
                className={`tab-btn ${sentimentFilter === 'positive' ? 'active' : ''}`}
              >
                <span className="text-green">●</span> Positive ({counts.positive})
              </button>
              <button
                onClick={() => setSentimentFilter('negative')}
                className={`tab-btn ${sentimentFilter === 'negative' ? 'active' : ''}`}
              >
                <span className="text-red">●</span> Negative ({counts.negative})
              </button>
              <button
                onClick={() => setSentimentFilter('neutral')}
                className={`tab-btn ${sentimentFilter === 'neutral' ? 'active' : ''}`}
              >
                <span className="text-blue">●</span> Neutral ({counts.neutral})
              </button>
            </div>

            {/* Keyword / Ticker Search Input */}
            <div style={{ position: 'relative', width: '280px' }}>
              <Search
                size={14}
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-3)',
                }}
              />
              <input
                type="text"
                className="finiq-input"
                placeholder="Filter by ticker or keyword..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  paddingLeft: '34px',
                  fontSize: '12px',
                }}
              />
            </div>
          </div>

          {/* 2-Column Grid of News Cards */}
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
              <div className="spinner" style={{ width: '32px', height: '32px', borderWidth: '3px' }} />
            </div>
          ) : filteredNews.length === 0 ? (
            <div
              className="card"
              style={{
                textAlign: 'center',
                padding: '48px 24px',
                color: 'var(--text-2)',
              }}
            >
              No financial intelligence news matching the active filter criteria.
            </div>
          ) : (
            <div className="grid-2" style={{ marginBottom: '32px' }}>
              {filteredNews.map((article) => {
                const sentimentBadge =
                  article.sentiment === 'positive'
                    ? 'badge-green'
                    : article.sentiment === 'negative'
                    ? 'badge-red'
                    : 'badge-blue';

                const scoreFormatted =
                  article.sentimentScore !== undefined
                    ? `${article.sentimentScore > 0 ? '+' : ''}${(article.sentimentScore * 100).toFixed(0)}%`
                    : null;

                return (
                  <div key={article.id} className="news-card">
                    {/* Header: Source, Time, Sentiment */}
                    <div className="news-meta">
                      <span style={{ fontWeight: 600, color: 'var(--text-1)' }}>{article.source}</span>
                      <span>•</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                        <Clock size={11} /> {article.publishedAt}
                      </span>

                      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        {scoreFormatted && (
                          <span
                            className="text-mono"
                            style={{
                              fontSize: '10px',
                              color:
                                article.sentiment === 'positive'
                                  ? 'var(--positive)'
                                  : article.sentiment === 'negative'
                                  ? 'var(--negative)'
                                  : 'var(--text-2)',
                            }}
                          >
                            Score: {scoreFormatted}
                          </span>
                        )}
                        <span className={`badge ${sentimentBadge}`} style={{ textTransform: 'capitalize' }}>
                          {article.sentiment === 'positive' && <TrendingUp size={11} />}
                          {article.sentiment === 'negative' && <TrendingDown size={11} />}
                          <span>{article.sentiment}</span>
                        </span>
                      </div>
                    </div>

                    {/* Headline */}
                    <h3 className="news-headline">{article.title}</h3>

                    {/* Summary */}
                    <p className="news-summary">{article.summary}</p>

                    {/* Associated Tickers */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginTop: '14px',
                        paddingTop: '10px',
                        borderTop: '1px solid rgba(26,39,64,0.6)',
                        flexWrap: 'wrap',
                        gap: '8px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                        <Tag size={12} color="var(--text-3)" />
                        {article.tickers.map((t) => (
                          <Link
                            key={t}
                            href={`/stock/${t}`}
                            className="ticker-tag"
                            style={{ fontSize: '11px', textDecoration: 'none' }}
                            title={`Inspect ${t} Equity Analysis`}
                          >
                            ${t}
                          </Link>
                        ))}
                      </div>

                      <div style={{ display: 'flex', gap: '8px' }}>
                        {article.tickers.length > 0 && (
                          <Link
                            href={`/debate/${article.tickers[0]}`}
                            className="btn btn-secondary btn-sm"
                            style={{ fontSize: '11px', padding: '3px 8px' }}
                          >
                            Debate ${article.tickers[0]}
                          </Link>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Institutional Disclaimer */}
          <footer
            style={{
              padding: '24px 0',
              borderTop: '1px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '6px',
              color: 'var(--text-3)',
              fontSize: '12px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldAlert size={14} color="var(--warning)" />
              <span style={{ color: 'var(--text-2)', fontWeight: 600 }}>FINIQ Intelligence Feed</span>
            </div>
            <p style={{ margin: 0, maxWidth: '700px' }}>
              This project is a prototype and is not financial advice. Sentiment classifications are generated via automated machine learning parsing and are provided for research demonstration only.
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
