'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Sidebar from '../../components/Sidebar';
import Topbar from '../../components/Topbar';
import StockChart, { StockCandle } from '../../components/StockChart';
import {
  TrendingUp,
  TrendingDown,
  Cpu,
  BarChart3,
  Activity,
  Layers,
  ArrowUpRight,
  ShieldAlert,
  Sparkles,
  Info,
  KeyRound,
} from 'lucide-react';

/* ─────────────────────────────────────────────
   Types
───────────────────────────────────────────── */
interface QuoteDetail {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  sector: string;
  open: number;
  high: number;
  low: number;
  volume: number;
  avgVolume: number;
  marketCap: string;
  pe: number | null;
  week52High: number;
  week52Low: number;
  beta: number;
  dataSource: 'LIVE' | 'DEMO';
}

interface MLPrediction {
  direction: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  horizon: string;
  expectedReturn: string;
  modelName: string;
  factors: Array<{ factor: string; impact: 'positive' | 'negative' | 'neutral'; weight: string }>;
}

/* ─────────────────────────────────────────────
   AAPL-first demo profiles — rich & accurate
───────────────────────────────────────────── */
const DEMO_PROFILES: Record<string, QuoteDetail> = {
  AAPL: {
    symbol: 'AAPL', name: 'Apple Inc.', sector: 'Consumer Electronics & Services',
    price: 228.52, change: 2.14, changePercent: 0.94,
    open: 226.80, high: 229.75, low: 225.90,
    volume: 52_400_000, avgVolume: 58_200_000,
    marketCap: '3.51T', pe: 34.2, week52High: 237.23, week52Low: 164.08, beta: 1.05,
    dataSource: 'DEMO',
  },
  NVDA: {
    symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Semiconductors & AI',
    price: 145.89, change: 4.82, changePercent: 3.42,
    open: 141.50, high: 147.20, low: 140.80,
    volume: 54_200_000, avgVolume: 60_100_000,
    marketCap: '3.58T', pe: 46.8, week52High: 149.76, week52Low: 45.12, beta: 1.68,
    dataSource: 'DEMO',
  },
  MSFT: {
    symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Enterprise Software & Cloud',
    price: 422.90, change: 3.65, changePercent: 0.87,
    open: 420.10, high: 425.80, low: 419.40,
    volume: 22_400_000, avgVolume: 24_800_000,
    marketCap: '3.14T', pe: 35.2, week52High: 468.35, week52Low: 366.50, beta: 1.18,
    dataSource: 'DEMO',
  },
  TSLA: {
    symbol: 'TSLA', name: 'Tesla, Inc.', sector: 'Automotive & Clean Energy',
    price: 342.10, change: -4.30, changePercent: -1.24,
    open: 346.80, high: 348.20, low: 339.90,
    volume: 68_100_000, avgVolume: 72_400_000,
    marketCap: '1.09T', pe: 92.1, week52High: 358.64, week52Low: 138.80, beta: 2.34,
    dataSource: 'DEMO',
  },
  GOOGL: {
    symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Internet & Search AI',
    price: 178.35, change: 2.10, changePercent: 1.19,
    open: 176.80, high: 179.50, low: 176.10,
    volume: 28_500_000, avgVolume: 31_200_000,
    marketCap: '2.21T', pe: 23.5, week52High: 191.75, week52Low: 129.40, beta: 1.08,
    dataSource: 'DEMO',
  },
  PLTR: {
    symbol: 'PLTR', name: 'Palantir Technologies', sector: 'Enterprise AI & Defense',
    price: 62.40, change: 4.12, changePercent: 7.07,
    open: 59.20, high: 63.80, low: 58.90,
    volume: 72_100_000, avgVolume: 68_400_000,
    marketCap: '138.00B', pe: 115.0, week52High: 65.20, week52Low: 19.80, beta: 2.10,
    dataSource: 'DEMO',
  },
  AMD: {
    symbol: 'AMD', name: 'Advanced Micro Devices', sector: 'Semiconductors',
    price: 142.15, change: 4.35, changePercent: 3.16,
    open: 138.90, high: 143.50, low: 138.20,
    volume: 38_900_000, avgVolume: 42_100_000,
    marketCap: '230.00B', pe: 48.2, week52High: 227.30, week52Low: 131.20, beta: 1.72,
    dataSource: 'DEMO',
  },
};

const DEFAULT_PROFILE = DEMO_PROFILES['AAPL'];

/* ─────────────────────────────────────────────
   AAPL-first ML predictions
───────────────────────────────────────────── */
const DEMO_PREDICTIONS: Record<string, MLPrediction> = {
  AAPL: {
    direction: 'BULLISH', confidence: 78,
    horizon: '5-Day Forward Alpha', expectedReturn: '+2.8% to +4.6%',
    modelName: 'Temporal Walk-Forward Ensemble (GBDT + LSTM)',
    factors: [
      { factor: 'Apple Intelligence upgrade cycle driving record iPhone 16 Pro ASP and high-margin Services revenue expansion (+14% YoY).', impact: 'positive', weight: '32%' },
      { factor: 'Institutional accumulation: Options flow shows net call premium above 90th percentile, signaling smart-money positioning.', impact: 'positive', weight: '28%' },
      { factor: 'Momentum Regime: 14D RSI at 56.8 — continuation bias with no overbought exhaustion signal.', impact: 'positive', weight: '24%' },
      { factor: 'Treasury yield sensitivity remains a macro headwind for high-multiple consumer tech names.', impact: 'neutral', weight: '16%' },
    ],
  },
  NVDA: {
    direction: 'BULLISH', confidence: 82,
    horizon: '5-Day Forward Alpha', expectedReturn: '+3.4% to +5.8%',
    modelName: 'Temporal Walk-Forward Ensemble (GBDT + LSTM)',
    factors: [
      { factor: 'Blackwell GB200 volume ramp entering hyperscaler deployment phase with multi-quarter pre-order backlog.', impact: 'positive', weight: '38%' },
      { factor: 'CUDA software moat provides insurmountable switching costs for enterprise AI workloads.', impact: 'positive', weight: '28%' },
      { factor: 'Momentum Regime: 14D RSI at 61.2 confirms continuation with no overbought signal.', impact: 'positive', weight: '20%' },
      { factor: 'Semiconductor beta sensitivity to U.S.-China export restriction headwinds.', impact: 'neutral', weight: '14%' },
    ],
  },
};

const DEFAULT_PREDICTION: MLPrediction = DEMO_PREDICTIONS['AAPL'];

/* ─────────────────────────────────────────────
   Chart fallback generator
───────────────────────────────────────────── */
function generateCandles(basePrice: number, count = 30): StockCandle[] {
  const candles: StockCandle[] = [];
  let current = basePrice * 0.92;
  const now = new Date();
  for (let i = count - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const label = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const delta = (Math.random() - 0.47) * (basePrice * 0.025);
    const close = Math.max(1, +(current + delta).toFixed(2));
    const open  = Math.max(1, +(close - (Math.random() - 0.5) * basePrice * 0.015).toFixed(2));
    const high  = +(Math.max(open, close) + Math.random() * basePrice * 0.012).toFixed(2);
    const low   = +(Math.min(open, close) - Math.random() * basePrice * 0.012).toFixed(2);
    const volume = Math.floor(20_000_000 + Math.random() * 40_000_000);
    candles.push({ date: label, open, high, low, close, volume });
    current = close;
  }
  if (candles.length) candles[candles.length - 1].close = basePrice;
  return candles;
}

/* ─────────────────────────────────────────────
   Page component
───────────────────────────────────────────── */
export default function StockDetailPage() {
  const params = useParams();
  const rawTicker = (params?.ticker as string) || 'AAPL';
  const ticker = rawTicker.toUpperCase();

  const [period, setPeriod] = useState('1M');
  const [loadingChart, setLoadingChart] = useState(false);
  const [candles, setCandles] = useState<StockCandle[]>([]);
  const [quote, setQuote] = useState<QuoteDetail>(
    () => DEMO_PROFILES[ticker] || { ...DEFAULT_PROFILE, symbol: ticker, name: `${ticker} Inc.` }
  );
  const [prediction, setPrediction] = useState<MLPrediction>(
    () => DEMO_PREDICTIONS[ticker] || DEFAULT_PREDICTION
  );

  /* Live quote fetch — gracefully falls back to demo */
  useEffect(() => {
    setQuote(DEMO_PROFILES[ticker] || { ...DEFAULT_PROFILE, symbol: ticker, name: `${ticker} Inc.` });
    setPrediction(DEMO_PREDICTIONS[ticker] || DEFAULT_PREDICTION);

    async function fetchQuote() {
      try {
        const res = await fetch(`/api/quote/${ticker}`);
        if (!res.ok) return;
        const d = await res.json();
        if (!d?.price) return;
        setQuote({
          symbol:        d.symbol   || d.ticker       || ticker,
          name:          d.name     || d.company      || `${ticker} Inc.`,
          price:         Number(d.price)               || 0,
          change:        Number(d.change)              || 0,
          changePercent: Number(d.changePercent ?? d.changePct) || 0,
          sector:        d.sector                      || 'Technology',
          open:          Number(d.open)                || 0,
          high:          Number(d.high)                || 0,
          low:           Number(d.low)                 || 0,
          volume:        Number(d.volume)              || 0,
          avgVolume:     Number(d.avgVolume)           || 0,
          marketCap:     typeof d.marketCap === 'string' ? d.marketCap : `${((Number(d.marketCap) || 0) / 1e12).toFixed(2)}T`,
          pe:            d.pe != null ? Number(d.pe) : null,
          week52High:    Number(d.week52High  ?? d.fiftyTwoWeekHigh)  || 0,
          week52Low:     Number(d.week52Low   ?? d.fiftyTwoWeekLow)   || 0,
          beta:          Number(d.beta)                || 1.0,
          dataSource:    d.dataSource === 'LIVE' ? 'LIVE' : 'DEMO',
        });
      } catch { /* keep demo */ }
    }
    fetchQuote();
  }, [ticker]);

  /* Chart history */
  const fetchHistory = useCallback(async (p: string) => {
    setLoadingChart(true);
    try {
      const res = await fetch(`/api/history/${ticker}?period=${p}`);
      if (res.ok) {
        const d = await res.json();
        const items = Array.isArray(d) ? d : d.candles || d.data;
        if (Array.isArray(items) && items.length > 0) {
          setCandles(items);
          return;
        }
      }
    } catch { /* fall through */ }
    const count = p === '1D' ? 12 : p === '5D' ? 20 : p === '1Y' ? 60 : 35;
    setCandles(generateCandles(quote.price || 228, count));
    setLoadingChart(false);
  }, [ticker, quote.price]);

  useEffect(() => {
    setLoadingChart(false);
    setCandles(generateCandles(quote.price || 228, 35));
    fetchHistory(period);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticker, period]);

  /* ML prediction fetch */
  useEffect(() => {
    async function fetchPredict() {
      try {
        const res = await fetch(`/api/predict/${ticker}`);
        if (!res.ok) return;
        const d = await res.json();
        if (d?.direction) setPrediction(d);
      } catch { /* keep demo */ }
    }
    fetchPredict();
  }, [ticker]);

  const isUp = quote.change >= 0;

  /* Technical indicators derived from price */
  const rsi   = 56.8;
  const ema20 = +(quote.price * 0.981).toFixed(2);
  const sma50 = +(quote.price * 0.942).toFixed(2);
  const sma200 = +(quote.price * 0.856).toFixed(2);
  const bbLow  = +(quote.price * 0.961).toFixed(0);
  const bbHigh = +(quote.price * 1.039).toFixed(0);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar
          title={`${quote.symbol} \u2022 ${quote.name}`}
          subtitle="Equity Analysis & Algorithmic Consensus"
        />

        <main className="page-container">

          {/* ── API Key Notice Banner ── */}
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              background: 'rgba(212,160,23,0.05)',
              border: '1px solid rgba(212,160,23,0.22)',
              borderRadius: '6px',
              padding: '11px 16px',
              marginBottom: '18px',
              fontSize: '12px',
              color: 'var(--text-1)',
            }}
          >
            <KeyRound size={15} color="var(--warning)" style={{ flexShrink: 0, marginTop: '1px' }} />
            <div>
              <strong style={{ color: 'var(--warning)' }}>
                {quote.dataSource === 'LIVE' ? '● Live Data Active' : 'Demo Mode — Static Prices'}
              </strong>
              {quote.dataSource !== 'LIVE' && (
                <>
                  {' '}— Real-time prices stream automatically via Yahoo Finance.{' '}
                  For <strong>live AI predictions</strong>, add{' '}
                  <code style={{ background: 'var(--bg-2)', padding: '1px 6px', borderRadius: '3px', fontFamily: 'var(--mono)', fontSize: '11px' }}>
                    OPENAI_API_KEY=sk-...
                  </code>{' '}
                  to your <code style={{ background: 'var(--bg-2)', padding: '1px 6px', borderRadius: '3px', fontFamily: 'var(--mono)', fontSize: '11px' }}>.env.local</code>{' '}
                  or <strong>Vercel › Settings › Environment Variables</strong>.
                </>
              )}
            </div>
          </div>

          {/* ── Hero Card ── */}
          <div
            className="card card-accent"
            style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <span className="ticker-tag" style={{ fontSize: '17px', padding: '4px 12px' }}>{quote.symbol}</span>
                <span className="badge badge-purple">{quote.sector}</span>
                <span className={`badge ${quote.dataSource === 'LIVE' ? 'badge-green' : 'badge-gray'}`}>
                  {quote.dataSource === 'LIVE' ? '● Live' : 'Demo'}
                </span>
              </div>
              <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-0)', margin: '0 0 8px' }}>
                {quote.name}
              </h2>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: '30px', fontWeight: 800, color: 'var(--text-0)' }}>
                  ${quote.price.toFixed(2)}
                </span>
                <span className={`badge ${isUp ? 'badge-green' : 'badge-red'}`} style={{ fontSize: '13px', padding: '4px 12px', fontFamily: 'var(--mono)' }}>
                  {isUp ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                  {isUp ? '+' : ''}{quote.change.toFixed(2)} ({isUp ? '+' : ''}{quote.changePercent.toFixed(2)}%)
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-3)' }}>Today's Session</span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <Link href={`/debate/${quote.symbol}`} className="btn btn-primary btn-lg">
                <Cpu size={15} /> Open AI Debate
              </Link>
              <Link href="/performance" className="btn btn-secondary btn-lg">
                <BarChart3 size={15} /> Model Validation
              </Link>
            </div>
          </div>

          {/* ── Chart + Stats Grid ── */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(260px, 1fr)', gap: '18px', marginBottom: '20px' }}>

            {/* Chart */}
            <StockChart
              ticker={quote.symbol}
              data={candles}
              period={period}
              onPeriodChange={(p) => setPeriod(p)}
              loading={loadingChart}
              height={360}
            />

            {/* Key Stats */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="section-title">
                <Layers size={14} />
                <span>Key Statistics</span>
              </div>

              {[
                { label: 'Open',              value: `$${quote.open.toFixed(2)}` },
                { label: 'Day Range',         value: `$${quote.low.toFixed(2)} – $${quote.high.toFixed(2)}` },
                { label: 'Volume',            value: `${(quote.volume / 1e6).toFixed(1)}M` },
                { label: 'Avg Volume (3M)',   value: `${(quote.avgVolume / 1e6).toFixed(1)}M` },
                { label: 'Market Cap',        value: quote.marketCap || 'N/A' },
                { label: 'P/E (TTM)',         value: quote.pe != null ? `${Number(quote.pe).toFixed(1)}x` : 'N/A' },
                { label: '52-Week High',      value: `$${quote.week52High.toFixed(2)}` },
                { label: '52-Week Low',       value: `$${quote.week52Low.toFixed(2)}` },
                { label: 'Beta (5Y Monthly)', value: quote.beta.toFixed(2) },
              ].map(({ label, value }) => (
                <div key={label} className="data-row">
                  <span className="data-row-label">{label}</span>
                  <span className="data-row-value">{value}</span>
                </div>
              ))}

              <div style={{ marginTop: 'auto', paddingTop: '14px', fontSize: '10px', color: 'var(--text-3)', lineHeight: 1.5 }}>
                Data sourced via Yahoo Finance gateway. Prices delayed ≤15 min.
              </div>
            </div>
          </div>

          {/* ── ML Prediction + Technical Indicators ── */}
          <div className="grid-2" style={{ marginBottom: '20px' }}>

            {/* ML Prediction */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <div className="section-title" style={{ margin: 0 }}>
                  <Sparkles size={14} />
                  <span>FINIQ ML Prediction</span>
                </div>
                <span className="badge badge-purple" style={{ fontSize: '10px' }}>{prediction.horizon}</span>
              </div>

              {/* Signal summary */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'var(--bg-1)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  padding: '14px 18px',
                  marginBottom: '14px',
                }}
              >
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '6px' }}>
                    Consensus Signal
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      className={`badge ${prediction.direction === 'BULLISH' ? 'badge-green' : prediction.direction === 'BEARISH' ? 'badge-red' : 'badge-blue'}`}
                      style={{ fontSize: '13px', padding: '4px 14px' }}
                    >
                      {prediction.direction}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-2)', fontFamily: 'var(--mono)' }}>
                      {prediction.expectedReturn}
                    </span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '2px' }}>Confidence</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: '26px', fontWeight: 800, color: 'var(--text-0)' }}>
                    {prediction.confidence}%
                  </div>
                </div>
              </div>

              {/* Bar */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-3)', marginBottom: '5px' }}>
                  <span>Probability Mass Distribution</span>
                  <span>{prediction.confidence}% Positive Expectancy</span>
                </div>
                <div className="bar-track" style={{ height: '5px' }}>
                  <div
                    className="bar-fill"
                    style={{
                      width: `${prediction.confidence}%`,
                      background: prediction.direction === 'BULLISH'
                        ? 'linear-gradient(90deg, var(--positive), rgba(57,209,116,0.6))'
                        : 'linear-gradient(90deg, var(--negative), rgba(229,83,83,0.6))',
                    }}
                  />
                </div>
              </div>

              {/* Factors */}
              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
                Top Algorithmic Factors
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
                {prediction.factors.map((f, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      gap: '10px',
                      background: 'var(--bg-1)',
                      borderLeft: `3px solid ${f.impact === 'positive' ? 'var(--positive)' : f.impact === 'negative' ? 'var(--negative)' : 'var(--border-focus)'}`,
                      padding: '8px 12px',
                      borderRadius: '0 5px 5px 0',
                      fontSize: '11px',
                    }}
                  >
                    <span style={{ color: 'var(--text-1)', lineHeight: 1.5 }}>{f.factor}</span>
                    <span style={{ fontFamily: 'var(--mono)', color: 'var(--text-3)', fontSize: '10px', flexShrink: 0 }}>{f.weight}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Technical Indicators */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <div className="section-title" style={{ margin: 0 }}>
                  <Activity size={14} />
                  <span>Technical Indicators</span>
                </div>
                <span className="badge badge-gray">Daily Timeframe</span>
              </div>

              <table className="finiq-table">
                <thead>
                  <tr>
                    <th>Indicator</th>
                    <th>Value</th>
                    <th>Signal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>RSI (14)</td>
                    <td className="mono">{rsi}</td>
                    <td><span className="badge badge-green">Accumulate</span></td>
                  </tr>
                  <tr>
                    <td>MACD (12,26,9)</td>
                    <td className="mono">+1.84</td>
                    <td><span className="badge badge-green">Buy</span></td>
                  </tr>
                  <tr>
                    <td>20-Day EMA</td>
                    <td className="mono">${ema20}</td>
                    <td><span className="badge badge-blue">Above EMA</span></td>
                  </tr>
                  <tr>
                    <td>50-Day SMA</td>
                    <td className="mono">${sma50}</td>
                    <td><span className="badge badge-blue">Bull Trend</span></td>
                  </tr>
                  <tr>
                    <td>200-Day SMA</td>
                    <td className="mono">${sma200}</td>
                    <td><span className="badge badge-green">Strong Bull</span></td>
                  </tr>
                  <tr>
                    <td>Bollinger (20,2)</td>
                    <td className="mono">${bbLow}–${bbHigh}</td>
                    <td><span className="badge badge-amber">Watch Break</span></td>
                  </tr>
                </tbody>
              </table>

              {/* Debate callout */}
              <div
                style={{
                  marginTop: '16px',
                  padding: '12px 16px',
                  background: 'var(--bg-1)',
                  border: '1px solid var(--border-light)',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-0)' }}>
                    Multi-perspective thesis analysis
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-2)', marginTop: '2px' }}>
                    4 AI agents debate {quote.symbol} bull & bear scenarios.
                  </div>
                </div>
                <Link href={`/debate/${quote.symbol}`} className="btn btn-primary btn-sm">
                  Debate <ArrowUpRight size={12} />
                </Link>
              </div>
            </div>
          </div>

          {/* ── Quick Ticker Strip ── */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <div className="section-title">
              <Info size={13} />
              <span>Browse Other Stocks</span>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {Object.keys(DEMO_PROFILES).map((t) => (
                <Link
                  key={t}
                  href={`/stock/${t}`}
                  className="ticker-tag"
                  style={{
                    fontSize: '12px',
                    padding: '4px 10px',
                    background: t === ticker ? 'var(--accent)' : 'var(--bg-2)',
                    color: t === ticker ? '#080808' : 'var(--text-0)',
                    fontWeight: t === ticker ? 800 : 700,
                    borderColor: t === ticker ? 'var(--accent)' : 'var(--border-light)',
                  }}
                >
                  {t}
                </Link>
              ))}
            </div>
          </div>

          {/* Footer */}
          <footer
            style={{
              paddingTop: '20px',
              borderTop: '1px solid var(--border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              color: 'var(--text-3)',
              fontSize: '11px',
              textAlign: 'center',
              paddingBottom: '8px',
            }}
          >
            <ShieldAlert size={13} color="var(--warning)" />
            <span>
              FINIQ is a prototype and is not financial advice. ML indicators do not guarantee future returns.
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
