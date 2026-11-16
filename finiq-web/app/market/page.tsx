'use client';

import { useState } from 'react';
import Link from 'next/link';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart2,
  Globe,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from 'lucide-react';

interface SectorData {
  name: string;
  change: number;
  volume: string;
  topStock: string;
}

interface IndexData {
  name: string;
  symbol: string;
  price: string;
  change: number;
  changePercent: number;
  ytd: string;
  high52w: string;
  low52w: string;
}

interface MoverData {
  symbol: string;
  name: string;
  price: string;
  change: number;
  changePercent: number;
  volume: string;
}

const SECTORS: SectorData[] = [
  { name: 'Technology',      change: +2.14, volume: '8.2B', topStock: 'NVDA' },
  { name: 'Financials',      change: +0.87, volume: '5.1B', topStock: 'JPM'  },
  { name: 'Healthcare',      change: +0.33, volume: '3.4B', topStock: 'UNH'  },
  { name: 'Consumer Disc.',  change: -0.42, volume: '4.0B', topStock: 'AMZN' },
  { name: 'Industrials',     change: +0.61, volume: '2.6B', topStock: 'GE'   },
  { name: 'Energy',          change: -1.08, volume: '3.3B', topStock: 'XOM'  },
  { name: 'Utilities',       change: -0.25, volume: '1.1B', topStock: 'NEE'  },
  { name: 'Real Estate',     change: -0.77, volume: '1.4B', topStock: 'PLD'  },
  { name: 'Materials',       change: +0.19, volume: '1.8B', topStock: 'FCX'  },
  { name: 'Comm. Services',  change: +1.22, volume: '4.5B', topStock: 'META' },
  { name: 'Consumer Staples',change: +0.05, volume: '2.0B', topStock: 'PG'   },
];

const INDICES: IndexData[] = [
  { name: 'S&P 500',          symbol: '^GSPC', price: '5,983.25', change: 32.18,   changePercent: 0.54,  ytd: '+24.3%', high52w: '6,147.43', low52w: '4,682.85' },
  { name: 'Nasdaq Composite', symbol: '^IXIC', price: '19,281.40',change: 145.22,  changePercent: 0.76,  ytd: '+31.7%', high52w: '20,204.58',low52w: '14,477.57'},
  { name: 'Dow Jones',        symbol: '^DJI',  price: '43,628.10',change: 211.44,  changePercent: 0.49,  ytd: '+16.8%', high52w: '44,860.31',low52w: '37,122.95'},
  { name: 'Russell 2000',     symbol: '^RUT',  price: '2,284.70', change: -8.32,   changePercent: -0.36, ytd: '+11.2%', high52w: '2,466.49', low52w: '1,931.74' },
  { name: 'VIX',              symbol: '^VIX',  price: '14.85',    change: -0.62,   changePercent: -4.01, ytd: '-32.1%', high52w: '65.73',    low52w: '11.85'    },
  { name: 'DXY (Dollar)',     symbol: 'DXY',   price: '104.21',   change: 0.14,    changePercent: 0.13,  ytd: '+2.1%',  high52w: '107.35',   low52w: '99.58'    },
];

const GAINERS: MoverData[] = [
  { symbol: 'PLTR', name: 'Palantir Technologies', price: '62.40',  change: 4.12,  changePercent: 7.07, volume: '72.1M' },
  { symbol: 'CRWD', name: 'CrowdStrike Holdings',  price: '348.60', change: 18.20, changePercent: 5.51, volume: '6.8M'  },
  { symbol: 'ARM',  name: 'Arm Holdings plc',      price: '138.90', change: 6.40,  changePercent: 4.83, volume: '14.2M' },
  { symbol: 'NVDA', name: 'NVIDIA Corporation',    price: '145.89', change: 4.82,  changePercent: 3.42, volume: '54.2M' },
  { symbol: 'AMD',  name: 'Advanced Micro Devices',price: '142.15', change: 4.35,  changePercent: 3.16, volume: '38.9M' },
];

const LOSERS: MoverData[] = [
  { symbol: 'INTC', name: 'Intel Corporation', price: '23.40',  change: -0.95, changePercent: -3.90, volume: '61.2M' },
  { symbol: 'BA',   name: 'Boeing Company',    price: '146.50', change: -4.80, changePercent: -3.17, volume: '11.4M' },
  { symbol: 'NKE',  name: 'Nike Inc',          price: '74.80',  change: -1.90, changePercent: -2.48, volume: '15.3M' },
  { symbol: 'TSLA', name: 'Tesla Inc',         price: '342.10', change: -4.30, changePercent: -1.24, volume: '68.1M' },
  { symbol: 'PFE',  name: 'Pfizer Inc',        price: '26.15',  change: -0.32, changePercent: -1.21, volume: '24.7M' },
];

const BREADTH = {
  advancing: 312,
  declining: 183,
  unchanged: 5,
  newHighs: 48,
  newLows: 12,
  upVolume: '14.2B',
  downVolume: '6.8B',
  putCallRatio: 0.82,
  advanceDeclineRatio: '1.70:1',
};

function sectorColor(change: number): string {
  if (change > 1.5)  return 'rgba(74,222,128,0.18)';
  if (change > 0.5)  return 'rgba(74,222,128,0.10)';
  if (change > 0)    return 'rgba(74,222,128,0.05)';
  if (change > -0.5) return 'rgba(248,113,113,0.05)';
  if (change > -1.5) return 'rgba(248,113,113,0.10)';
  return 'rgba(248,113,113,0.18)';
}

function sectorBorder(change: number): string {
  if (change > 0) return '1px solid rgba(74,222,128,0.2)';
  if (change < 0) return '1px solid rgba(248,113,113,0.2)';
  return '1px solid var(--border)';
}

export default function MarketPage() {
  const [moversTab, setMoversTab] = useState<'gainers' | 'losers'>('gainers');
  const movers = moversTab === 'gainers' ? GAINERS : LOSERS;

  const advPct = Math.round((BREADTH.advancing / (BREADTH.advancing + BREADTH.declining + BREADTH.unchanged)) * 100);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar
          title="Market Overview"
          subtitle="Global indices, sector rotation & breadth intelligence"
        />

        <main className="page-container">

          {/* ── Page header ── */}
          <div className="page-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Globe size={16} color="var(--text-2)" />
              <span style={{ fontSize: '11px', color: 'var(--text-2)', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                Global Market Intelligence
              </span>
            </div>
            <h2 className="page-title">Market Command Center</h2>
            <p className="page-subtitle">
              Real-time snapshot of major indices, sector performance, and market breadth.
            </p>
          </div>

          {/* ── Major Indices Grid ── */}
          <section style={{ marginBottom: '28px' }}>
            <div className="section-title">
              <Activity size={14} />
              <span>Major Indices &amp; Benchmarks</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              {INDICES.map((idx) => {
                const up = idx.changePercent >= 0;
                return (
                  <div key={idx.symbol} className="metric-card" style={{ position: 'relative', overflow: 'hidden' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <div>
                        <div className="metric-label">{idx.name}</div>
                        <div style={{ fontSize: '9px', color: 'var(--text-3)', fontFamily: 'var(--mono)' }}>{idx.symbol}</div>
                      </div>
                      <span className={`badge ${up ? 'badge-green' : 'badge-red'}`}>
                        {up ? <ArrowUpRight size={11} /> : <ArrowDownRight size={11} />}
                        {up ? '+' : ''}{idx.changePercent.toFixed(2)}%
                      </span>
                    </div>
                    <div className="metric-value">{idx.price}</div>
                    <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-3)' }}>
                      <span>YTD <span style={{ color: up ? 'var(--positive)' : 'var(--negative)', fontWeight: 700 }}>{idx.ytd}</span></span>
                      <span>52W: {idx.low52w} – {idx.high52w}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ── Two-column layout: Sector Heatmap + Market Breadth ── */}
          <div className="grid-2" style={{ marginBottom: '28px' }}>

            {/* Sector Heatmap */}
            <div className="card">
              <div className="section-title">
                <BarChart2 size={14} />
                <span>Sector Performance Heatmap</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {SECTORS.sort((a, b) => b.change - a.change).map((sector) => {
                  const up = sector.change >= 0;
                  const absMax = 2.5;
                  const barWidth = Math.min(100, (Math.abs(sector.change) / absMax) * 100);
                  return (
                    <div
                      key={sector.name}
                      style={{
                        background: sectorColor(sector.change),
                        border: sectorBorder(sector.change),
                        borderRadius: '4px',
                        padding: '8px 12px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-0)' }}>{sector.name}</span>
                          <span
                            style={{
                              fontFamily: 'var(--mono)',
                              fontSize: '12px',
                              fontWeight: 700,
                              color: up ? 'var(--positive)' : 'var(--negative)',
                            }}
                          >
                            {up ? '+' : ''}{sector.change.toFixed(2)}%
                          </span>
                        </div>
                        <div className="bar-track" style={{ margin: 0 }}>
                          <div
                            className="bar-fill"
                            style={{
                              width: `${barWidth}%`,
                              background: up ? 'var(--positive)' : 'var(--negative)',
                              opacity: 0.6,
                            }}
                          />
                        </div>
                      </div>
                      <div style={{ marginLeft: '12px', textAlign: 'right', flexShrink: 0 }}>
                        <div style={{ fontSize: '9px', color: 'var(--text-3)' }}>VOL</div>
                        <div style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text-2)' }}>{sector.volume}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right column: Market Breadth + Movers */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

              {/* Market Breadth */}
              <div className="card">
                <div className="section-title">
                  <Activity size={14} />
                  <span>NYSE Market Breadth</span>
                </div>

                {/* Advance/Decline Bar */}
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '5px' }}>
                    <span style={{ color: 'var(--positive)', fontWeight: 700 }}>↑ {BREADTH.advancing} Advancing</span>
                    <span style={{ color: 'var(--text-2)' }}>{BREADTH.advanceDeclineRatio}</span>
                    <span style={{ color: 'var(--negative)', fontWeight: 700 }}>{BREADTH.declining} Declining ↓</span>
                  </div>
                  <div style={{ height: '8px', background: 'var(--bg-2)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                    <div style={{ width: `${advPct}%`, background: 'var(--positive)', borderRadius: '4px 0 0 4px', opacity: 0.8 }} />
                    <div style={{ flex: 1, background: 'var(--negative)', borderRadius: '0 4px 4px 0', opacity: 0.6 }} />
                  </div>
                </div>

                {/* Stat rows */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  {[
                    { label: 'New 52W Highs', value: BREADTH.newHighs, color: 'var(--positive)' },
                    { label: 'New 52W Lows',  value: BREADTH.newLows,  color: 'var(--negative)' },
                    { label: 'Up Volume',     value: BREADTH.upVolume,  color: 'var(--positive)' },
                    { label: 'Down Volume',   value: BREADTH.downVolume,color: 'var(--negative)' },
                    { label: 'Put/Call Ratio',value: BREADTH.putCallRatio, color: 'var(--text-0)' },
                    { label: 'Unchanged',     value: BREADTH.unchanged, color: 'var(--text-2)' },
                  ].map((item) => (
                    <div key={item.label} className="data-row" style={{ padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                      <span className="data-row-label">{item.label}</span>
                      <span className="data-row-value" style={{ color: item.color }}>{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Movers */}
              <div className="card" style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <div className="section-title" style={{ margin: 0 }}>
                    {moversTab === 'gainers' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    <span>Top Movers</span>
                  </div>
                  <div style={{ display: 'flex', background: 'var(--bg-1)', borderRadius: '4px', padding: '2px' }}>
                    <button
                      onClick={() => setMoversTab('gainers')}
                      style={{
                        border: 'none',
                        background: moversTab === 'gainers' ? 'var(--positive-dim)' : 'transparent',
                        color: moversTab === 'gainers' ? 'var(--positive)' : 'var(--text-2)',
                        fontSize: '11px', fontWeight: 600, padding: '3px 10px',
                        borderRadius: '3px', cursor: 'pointer',
                      }}
                    >
                      Gainers
                    </button>
                    <button
                      onClick={() => setMoversTab('losers')}
                      style={{
                        border: 'none',
                        background: moversTab === 'losers' ? 'var(--negative-dim)' : 'transparent',
                        color: moversTab === 'losers' ? 'var(--negative)' : 'var(--text-2)',
                        fontSize: '11px', fontWeight: 600, padding: '3px 10px',
                        borderRadius: '3px', cursor: 'pointer',
                      }}
                    >
                      Losers
                    </button>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                  {movers.map((m, i) => {
                    const up = m.changePercent >= 0;
                    return (
                      <Link
                        key={m.symbol}
                        href={`/stock/${m.symbol}`}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '9px 0',
                          borderBottom: i < movers.length - 1 ? '1px solid var(--border)' : 'none',
                          textDecoration: 'none',
                          transition: 'background 0.1s',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span style={{
                            fontFamily: 'var(--mono)', fontSize: '12px', fontWeight: 700,
                            color: 'var(--text-0)', background: 'var(--bg-2)',
                            border: '1px solid var(--border-light)', padding: '1px 6px',
                            borderRadius: '3px', minWidth: '48px', textAlign: 'center',
                          }}>
                            {m.symbol}
                          </span>
                          <span style={{ fontSize: '11px', color: 'var(--text-2)' }}>{m.name}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', textAlign: 'right' }}>
                          <span style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--text-0)', fontWeight: 600 }}>
                            ${m.price}
                          </span>
                          <span style={{
                            fontFamily: 'var(--mono)', fontSize: '11px', fontWeight: 700,
                            color: up ? 'var(--positive)' : 'var(--negative)',
                            minWidth: '54px', textAlign: 'right',
                          }}>
                            {up ? '+' : ''}{m.changePercent.toFixed(2)}%
                          </span>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* ── Full Width: All Sectors Table ── */}
          <div className="card" style={{ marginBottom: '28px' }}>
            <div className="section-title">
              <BarChart2 size={14} />
              <span>Sector Rotation Summary</span>
            </div>
            <table className="finiq-table">
              <thead>
                <tr>
                  <th>Sector</th>
                  <th>Change</th>
                  <th>Trend</th>
                  <th>Volume</th>
                  <th>Top Holding</th>
                  <th style={{ textAlign: 'right' }}>Signal</th>
                </tr>
              </thead>
              <tbody>
                {SECTORS.map((sector) => {
                  const up = sector.change >= 0;
                  return (
                    <tr key={sector.name}>
                      <td style={{ fontWeight: 600, color: 'var(--text-0)' }}>{sector.name}</td>
                      <td className={`mono ${up ? 'text-green' : 'text-red'}`} style={{ fontWeight: 700 }}>
                        {up ? '+' : ''}{sector.change.toFixed(2)}%
                      </td>
                      <td>
                        {up
                          ? <TrendingUp size={14} color="var(--positive)" />
                          : <TrendingDown size={14} color="var(--negative)" />}
                      </td>
                      <td className="mono" style={{ color: 'var(--text-2)' }}>{sector.volume}</td>
                      <td>
                        <Link href={`/stock/${sector.topStock}`} className="ticker-tag">
                          {sector.topStock}
                        </Link>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <span className={`badge ${up ? 'badge-green' : 'badge-red'}`}>
                          {Math.abs(sector.change) > 1.0
                            ? up ? 'Strong Buy' : 'Avoid'
                            : up ? 'Overweight' : 'Underweight'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Footer disclaimer */}
          <div className="disclaimer-banner" style={{ marginBottom: '24px', fontSize: '11px' }}>
            <Minus size={12} />
            <span>
              Market data is demonstrative only. FINIQ is a prototype and does not provide financial advice.
              Sector allocations are not investment recommendations.
            </span>
          </div>

        </main>
      </div>
    </div>
  );
}
