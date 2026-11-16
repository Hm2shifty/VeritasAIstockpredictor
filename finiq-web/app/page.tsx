'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import {
  TrendingUp,
  TrendingDown,
  Search,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Cpu,
  BarChart2,
  Clock,
  ShieldCheck,
  Zap,
} from 'lucide-react';

interface QuoteData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  marketCap?: number;
}

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  tickers: string[];
}

const DEFAULT_WATCHLIST: QuoteData[] = [
  { symbol: 'NVDA', name: 'NVIDIA Corp', price: 145.89, change: 4.82, changePercent: 3.42, volume: 54200000 },
  { symbol: 'AAPL', name: 'Apple Inc', price: 228.24, change: 1.15, changePercent: 0.51, volume: 48900000 },
  { symbol: 'MSFT', name: 'Microsoft Corp', price: 422.90, change: 3.65, changePercent: 0.87, volume: 22400000 },
  { symbol: 'TSLA', name: 'Tesla Inc', price: 342.10, change: -4.30, changePercent: -1.24, volume: 68100000 },
  { symbol: 'GOOGL', name: 'Alphabet Inc', price: 178.35, change: 2.10, changePercent: 1.19, volume: 28500000 },
];

const GAINERS: QuoteData[] = [
  { symbol: 'PLTR', name: 'Palantir Technologies', price: 62.40, change: 4.12, changePercent: 7.07, volume: 72100000 },
  { symbol: 'CRWD', name: 'CrowdStrike Holdings', price: 348.60, change: 18.20, changePercent: 5.51, volume: 6800000 },
  { symbol: 'ARM', name: 'Arm Holdings plc', price: 138.90, change: 6.40, changePercent: 4.83, volume: 14200000 },
  { symbol: 'NVDA', name: 'NVIDIA Corp', price: 145.89, change: 4.82, changePercent: 3.42, volume: 54200000 },
  { symbol: 'AMD', name: 'Advanced Micro Devices', price: 142.15, change: 4.35, changePercent: 3.16, volume: 38900000 },
];

const LOSERS: QuoteData[] = [
  { symbol: 'INTC', name: 'Intel Corporation', price: 23.40, change: -0.95, changePercent: -3.90, volume: 61200000 },
  { symbol: 'BA', name: 'Boeing Co', price: 146.50, change: -4.80, changePercent: -3.17, volume: 11400000 },
  { symbol: 'NKE', name: 'Nike Inc', price: 74.80, change: -1.90, changePercent: -2.48, volume: 15300000 },
  { symbol: 'TSLA', name: 'Tesla Inc', price: 342.10, change: -4.30, changePercent: -1.24, volume: 68100000 },
  { symbol: 'PFE', name: 'Pfizer Inc', price: 26.15, change: -0.32, changePercent: -1.21, volume: 24700000 },
];

const FALLBACK_NEWS: NewsItem[] = [
  {
    id: 'n1',
    title: 'NVIDIA AI Infrastructure Demand Hits Record Backlog for Blackwell Architectures',
    summary: 'Hyperscalers and sovereign AI clusters continue surging allocations into cutting-edge accelerator hardware, prompting upgrades across Wall Street.',
    source: 'Bloomberg Tech',
    publishedAt: '25m ago',
    sentiment: 'positive',
    tickers: ['NVDA', 'AMD', 'MSFT'],
  },
  {
    id: 'n2',
    title: 'Fed Minutes Reaffirm Balanced Rate Stance Amid Sticky Services Inflation',
    summary: 'FOMC participants observe resilient domestic labor metrics while noting caution regarding financial conditions easing too prematurely.',
    source: 'Reuters Macro',
    publishedAt: '1h ago',
    sentiment: 'neutral',
    tickers: ['SPY', 'QQQ'],
  },
  {
    id: 'n3',
    title: 'Palantir Secures Multi-Year Enterprise Defense Expansion for AI Decision Engines',
    summary: 'The defense intelligence contractor announced contract renewals exceeding initial scope projections, reinforcing commercial software momentum.',
    source: 'Financial Times',
    publishedAt: '2h ago',
    sentiment: 'positive',
    tickers: ['PLTR'],
  },
  {
    id: 'n4',
    title: 'Automotive EV Price War Compresses Q4 Margin Projections',
    summary: 'Increased competition across key global EV hubs drives margin compression warnings, though autonomous software monetization remains a long-term buffer.',
    source: 'Wall Street Journal',
    publishedAt: '3h ago',
    sentiment: 'negative',
    tickers: ['TSLA'],
  },
  {
    id: 'n5',
    title: 'Cloud Enterprise Spend Accelerates 22% YoY in Cloud Architecture Audits',
    summary: 'Enterprise migrations toward generative AI application layers drive renewed cloud capacity consumption for primary infrastructure providers.',
    source: 'CNBC Markets',
    publishedAt: '4h ago',
    sentiment: 'positive',
    tickers: ['MSFT', 'GOOGL', 'AMZN'],
  },
  {
    id: 'n6',
    title: 'Semiconductor Supply Chain Logistics Tighten Ahead of Next-Gen Node Ramps',
    summary: 'Foundry bottlenecks and advanced packaging substrates create near-term capacity constraints for high-performance computing chip designers.',
    source: 'Barron\'s',
    publishedAt: '5h ago',
    sentiment: 'neutral',
    tickers: ['INTC', 'TSM', 'NVDA'],
  },
];

export default function Dashboard() {
  const router = useRouter();
  const [searchInput, setSearchInput] = useState('');
  const [watchlist, setWatchlist] = useState<QuoteData[]>(DEFAULT_WATCHLIST);
  const [news, setNews] = useState<NewsItem[]>(FALLBACK_NEWS);
  const [moverTab, setMoverTab] = useState<'gainers' | 'losers'>('gainers');
  const [loadingQuotes, setLoadingQuotes] = useState(false);

  // Fetch watchlist quotes from /api/quote/[ticker]
  useEffect(() => {
    async function loadWatchlistQuotes() {
      try {
        setLoadingQuotes(true);
        const tickers = ['AAPL', 'NVDA', 'MSFT', 'TSLA', 'GOOGL'];
        const results = await Promise.allSettled(
          tickers.map((t) => fetch(`/api/quote/${t}`).then((r) => (r.ok ? r.json() : null)))
        );

        const updated = DEFAULT_WATCHLIST.map((item, idx) => {
          const res = results[idx];
          if (res.status === 'fulfilled' && res.value) {
            const val = res.value;
            return {
              symbol: val.symbol || item.symbol,
              name: val.name || item.name,
              price: val.price ?? item.price,
              change: val.change ?? item.change,
              changePercent: val.changePercent ?? item.changePercent,
              volume: val.volume ?? item.volume,
            };
          }
          return item;
        });
        setWatchlist(updated);
      } catch {
        // Fallback quotes maintained
      } finally {
        setLoadingQuotes(false);
      }
    }

    async function loadNews() {
      try {
        const res = await fetch('/api/news');
        if (res.ok) {
          const data = await res.json();
          const items = Array.isArray(data) ? data : data.news || data.articles;
          if (Array.isArray(items) && items.length > 0) {
            setNews(items.slice(0, 6));
          }
        }
      } catch {
        // Keep fallback news
      }
    }

    loadWatchlistQuotes();
    loadNews();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = searchInput.trim().toUpperCase();
    if (clean) {
      router.push(`/stock/${clean}`);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar title="Institutional Intelligence Dashboard" subtitle="Real-time multi-agent financial analytics & predictions" />

        <main className="page-container">
          {/* Quick Search & Hero Banner */}
          <div
            className="card card-accent"
            style={{
              marginBottom: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge badge-purple" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    <Zap size={11} /> AI Decision Engine
                  </span>
                  <span className="badge badge-blue">Temporal ML Walk-Forward</span>
                </div>
                <h2 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-0)', margin: 0 }}>
                  Institutional Market Intelligence & Algorithmic Consensus
                </h2>
                <p style={{ fontSize: '13px', color: 'var(--text-2)', marginTop: '4px' }}>
                  Analyze equity dynamics with 4-agent adversarial debates, zero-lookahead ML predictions, and real-time sentiment extraction.
                </p>
              </div>

              {/* Quick Jump Buttons */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <Link href="/debate/NVDA" className="btn btn-primary btn-sm">
                  <Cpu size={14} /> NVDA Debate
                </Link>
                <Link href="/performance" className="btn btn-secondary btn-sm">
                  <BarChart2 size={14} /> ML vs Baseline
                </Link>
              </div>
            </div>

            {/* Big Ticker Search Bar */}
            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '10px' }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <Search
                  size={16}
                  style={{
                    position: 'absolute',
                    left: '14px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-2)',
                  }}
                />
                <input
                  type="text"
                  className="finiq-input"
                  placeholder="Enter any stock ticker (e.g. NVDA, AAPL, MSFT, TSLA, AMZN, PLTR)..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  style={{
                    paddingLeft: '40px',
                    paddingTop: '11px',
                    paddingBottom: '11px',
                    fontSize: '14px',
                    textTransform: 'uppercase',
                    background: 'var(--bg-0)',
                  }}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ padding: '0 24px' }}>
                Analyze Stock
              </button>
            </form>

            {/* Quick Chips */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-3)', fontWeight: 600 }}>POPULAR:</span>
              {['NVDA', 'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'PLTR', 'AMD', 'AMZN'].map((t) => (
                <Link
                  key={t}
                  href={`/stock/${t}`}
                  className="ticker-tag"
                  style={{ textDecoration: 'none', cursor: 'pointer' }}
                >
                  {t}
                </Link>
              ))}
            </div>
          </div>

          {/* Hero Section: 4 Metric Cards */}
          <section style={{ marginBottom: '28px' }}>
            <div className="section-title">
              <BarChart2 size={15} color="var(--accent)" />
              <span>Macro Regime & Benchmark Indicators</span>
            </div>
            <div className="metric-grid metric-grid-4">
              {/* S&P 500 */}
              <div className="metric-card">
                <div className="metric-label">S&P 500 Index (^GSPC)</div>
                <div className="metric-value">5,983.25</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
                  <span className="badge badge-green">
                    <TrendingUp size={11} /> +32.18 (+0.54%)
                  </span>
                  <span className="metric-sub" style={{ margin: 0 }}>All-time Range</span>
                </div>
              </div>

              {/* NASDAQ 100 */}
              <div className="metric-card">
                <div className="metric-label">NASDAQ Composite (^IXIC)</div>
                <div className="metric-value">19,281.40</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
                  <span className="badge badge-green">
                    <TrendingUp size={11} /> +145.22 (+0.76%)
                  </span>
                  <span className="metric-sub" style={{ margin: 0 }}>Tech Momentum</span>
                </div>
              </div>

              {/* VIX Volatility */}
              <div className="metric-card">
                <div className="metric-label">CBOE Volatility (^VIX)</div>
                <div className="metric-value">14.85</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
                  <span className="badge badge-green">
                    <TrendingDown size={11} /> -0.62 (-4.01%)
                  </span>
                  <span className="badge badge-blue" style={{ fontSize: '10px' }}>
                    Low Risk Regime
                  </span>
                </div>
              </div>

              {/* Bitcoin / Alternative Benchmark */}
              <div className="metric-card">
                <div className="metric-label">Bitcoin / Gold Asset Proxy</div>
                <div className="metric-value">$91,420</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
                  <span className="badge badge-green">
                    <TrendingUp size={11} /> +2.15%
                  </span>
                  <span className="metric-sub" style={{ margin: 0 }}>Gold: $2,684 (+0.4%)</span>
                </div>
              </div>
            </div>
          </section>

          {/* Mini Watchlist Section */}
          <section style={{ marginBottom: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div className="section-title" style={{ margin: 0 }}>
                <TrendingUp size={15} color="var(--positive)" />
                <span>Core Watchlist Intelligence</span>
              </div>
              <span style={{ fontSize: '11px', color: 'var(--text-3)' }}>
                Live quote feeds with instant ML drill-down
              </span>
            </div>

            <div className="grid-auto">
              {watchlist.map((item) => {
                const isUp = item.change >= 0;
                return (
                  <Link
                    key={item.symbol}
                    href={`/stock/${item.symbol}`}
                    className="card card-sm"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      textDecoration: 'none',
                      transition: 'all 0.2s ease',
                      border: '1px solid var(--border)',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <div>
                          <span className="ticker-tag" style={{ fontSize: '13px' }}>
                            {item.symbol}
                          </span>
                          <div
                            style={{
                              fontSize: '11px',
                              color: 'var(--text-2)',
                              marginTop: '4px',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              maxWidth: '140px',
                            }}
                          >
                            {item.name}
                          </div>
                        </div>
                        <span className={`badge ${isUp ? 'badge-green' : 'badge-red'}`}>
                          {isUp ? '+' : ''}
                          {item.changePercent.toFixed(2)}%
                        </span>
                      </div>

                      <div style={{ fontFamily: 'var(--mono)', fontSize: '20px', fontWeight: 800, color: 'var(--text-0)', margin: '8px 0 4px' }}>
                        ${item.price.toFixed(2)}
                      </div>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontSize: '11px',
                        color: 'var(--text-3)',
                        borderTop: '1px solid rgba(26,39,64,0.6)',
                        paddingTop: '8px',
                        marginTop: '8px',
                      }}
                    >
                      <span>Vol: {( (item.volume || 10000000) / 1e6).toFixed(1)}M</span>
                      <span style={{ color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '2px', fontWeight: 600 }}>
                        Details <ArrowUpRight size={12} />
                      </span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </section>

          {/* Two Column Grid: Market Movers & Recent News */}
          <div className="grid-2" style={{ marginBottom: '28px' }}>
            {/* Market Movers Table */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div className="section-title" style={{ margin: 0 }}>
                  <Zap size={15} color="var(--warning)" />
                  <span>Market Movers (High Volume)</span>
                </div>
                {/* Tabs */}
                <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-1)', padding: '2px', borderRadius: '6px' }}>
                  <button
                    onClick={() => setMoverTab('gainers')}
                    style={{
                      border: 'none',
                      background: moverTab === 'gainers' ? 'var(--positive-dim)' : 'transparent',
                      color: moverTab === 'gainers' ? 'var(--positive)' : 'var(--text-2)',
                      fontSize: '11px',
                      fontWeight: 700,
                      padding: '4px 10px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Gainers
                  </button>
                  <button
                    onClick={() => setMoverTab('losers')}
                    style={{
                      border: 'none',
                      background: moverTab === 'losers' ? 'var(--negative-dim)' : 'transparent',
                      color: moverTab === 'losers' ? 'var(--negative)' : 'var(--text-2)',
                      fontSize: '11px',
                      fontWeight: 700,
                      padding: '4px 10px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Losers
                  </button>
                </div>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table className="finiq-table">
                  <thead>
                    <tr>
                      <th>Ticker</th>
                      <th>Price</th>
                      <th>Change</th>
                      <th>Volume</th>
                      <th style={{ textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(moverTab === 'gainers' ? GAINERS : LOSERS).map((mover) => {
                      const isUp = mover.change >= 0;
                      return (
                        <tr key={mover.symbol}>
                          <td>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                              <span style={{ fontWeight: 700, color: 'var(--text-0)', fontFamily: 'var(--mono)' }}>
                                {mover.symbol}
                              </span>
                              <span style={{ fontSize: '11px', color: 'var(--text-3)' }}>{mover.name}</span>
                            </div>
                          </td>
                          <td className="mono">${mover.price.toFixed(2)}</td>
                          <td>
                            <span className={`badge ${isUp ? 'badge-green' : 'badge-red'}`}>
                              {isUp ? '+' : ''}
                              {mover.changePercent.toFixed(2)}%
                            </span>
                          </td>
                          <td className="mono" style={{ color: 'var(--text-2)', fontSize: '12px' }}>
                            {((mover.volume || 0) / 1e6).toFixed(1)}M
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            <Link href={`/stock/${mover.symbol}`} className="btn btn-secondary btn-sm" style={{ padding: '3px 8px', fontSize: '11px' }}>
                              Inspect
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Quick Agent Debate Spotlight */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div className="section-title">
                  <Cpu size={15} color="var(--purple)" />
                  <span>Adversarial Debate Spotlight</span>
                </div>
                <div
                  style={{
                    background: 'var(--bg-1)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    padding: '16px',
                    marginBottom: '16px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="ticker-tag">NVDA</span>
                      <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-0)' }}>NVIDIA Corporation</span>
                    </div>
                    <span className="badge badge-green">BULLISH CONSENSUS</span>
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.5, margin: 0 }}>
                    &ldquo;Chief Analyst synthesis indicates sustained generative AI Capex momentum outweighs consumer chip cycle deceleration. Recommended risk-hedged target: $165.00.&rdquo;
                  </p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div style={{ background: 'rgba(14,203,129,0.06)', border: '1px solid rgba(14,203,129,0.2)', padding: '12px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--positive)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Bull Thesis
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-1)', lineHeight: 1.4 }}>
                      Blackwell architecture ramp and hyperscaler software margins drive 48% FCF expansion.
                    </div>
                  </div>
                  <div style={{ background: 'rgba(246,70,93,0.06)', border: '1px solid rgba(246,70,93,0.2)', padding: '12px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--negative)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Bear Thesis
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-1)', lineHeight: 1.4 }}>
                      Customer custom silicon buildout (TPU, Trainium) poses medium-term pricing compression risk.
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-3)' }}>4-agent multi-perspective consensus</span>
                <Link href="/debate/NVDA" className="btn btn-primary btn-sm">
                  Launch Full Debate <ArrowUpRight size={13} />
                </Link>
              </div>
            </div>
          </div>

          {/* Recent Financial News Grid (6 cards) */}
          <section style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div className="section-title" style={{ margin: 0 }}>
                <Clock size={15} color="var(--accent)" />
                <span>Real-Time Market & Sentiment Intelligence</span>
              </div>
              <Link href="/news" className="btn btn-secondary btn-sm" style={{ fontSize: '11px' }}>
                View All Intelligence News
              </Link>
            </div>

            <div className="grid-3">
              {news.slice(0, 6).map((item) => {
                const sentimentBadge =
                  item.sentiment === 'positive'
                    ? 'badge-green'
                    : item.sentiment === 'negative'
                    ? 'badge-red'
                    : 'badge-blue';

                return (
                  <div key={item.id} className="news-card">
                    <div className="news-meta">
                      <span>{item.source}</span>
                      <span>•</span>
                      <span>{item.publishedAt}</span>
                      <span className={`badge ${sentimentBadge}`} style={{ marginLeft: 'auto', textTransform: 'capitalize' }}>
                        {item.sentiment}
                      </span>
                    </div>

                    <h4 className="news-headline">{item.title}</h4>
                    <p className="news-summary">{item.summary}</p>

                    <div style={{ display: 'flex', gap: '6px', marginTop: '12px', flexWrap: 'wrap' }}>
                      {item.tickers.map((t) => (
                        <Link key={t} href={`/stock/${t}`} className="ticker-tag" style={{ fontSize: '10px', textDecoration: 'none' }}>
                          ${t}
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Institutional Disclaimer Footer */}
          <footer
            style={{
              marginTop: '40px',
              padding: '24px 0',
              borderTop: '1px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '8px',
              color: 'var(--text-3)',
              fontSize: '12px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldCheck size={14} color="var(--warning)" />
              <span style={{ color: 'var(--text-2)', fontWeight: 600 }}>FINIQ Research & Analytics Platform</span>
            </div>
            <p style={{ margin: 0, maxWidth: '720px' }}>
              This project is a prototype and is not financial advice. All algorithmic signals, multi-agent debates, and baseline accuracy metrics are generated for demonstration and research purposes only.
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
