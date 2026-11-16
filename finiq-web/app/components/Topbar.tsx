'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Search, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface IndexItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

interface TopbarProps {
  title: string;
  subtitle?: string;
}

const DEFAULT_INDICES: IndexItem[] = [
  { symbol: '^GSPC', name: 'S&P 500', price: 5983.25, change: 32.18, changePercent: 0.54 },
  { symbol: '^IXIC', name: 'NASDAQ', price: 19281.40, change: 145.22, changePercent: 0.76 },
  { symbol: '^VIX', name: 'VIX', price: 14.85, change: -0.62, changePercent: -4.01 },
];

export default function Topbar({ title, subtitle }: TopbarProps) {
  const router = useRouter();
  const [indices, setIndices] = useState<IndexItem[]>(DEFAULT_INDICES);
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingIndices, setLoadingIndices] = useState(false);

  const fetchIndices = useCallback(async () => {
    try {
      setLoadingIndices(true);
      const res = await fetch('/api/indices');
      if (res.ok) {
        const data = await res.json();
        const items = Array.isArray(data) ? data : data.indices || data.data;
        if (Array.isArray(items) && items.length > 0) {
          setIndices(items);
        }
      }
    } catch {
      // Use fallback defaults silently on error
    } finally {
      setLoadingIndices(false);
    }
  }, []);

  useEffect(() => {
    fetchIndices();
    const interval = setInterval(fetchIndices, 60000); // 60s auto refresh
    return () => clearInterval(interval);
  }, [fetchIndices]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = searchQuery.trim().toUpperCase();
    if (clean) {
      router.push(`/stock/${clean}`);
      setSearchQuery('');
    }
  };

  return (
    <header className="topbar">
      {/* Left: Page Title */}
      <div style={{ display: 'flex', flexDirection: 'column', minWidth: '160px' }}>
        <h1
          style={{
            fontSize: '16px',
            fontWeight: 700,
            color: 'var(--text-0)',
            margin: 0,
            lineHeight: 1.2,
          }}
        >
          {title}
        </h1>
        {subtitle && (
          <span style={{ fontSize: '11px', color: 'var(--text-2)', marginTop: '2px' }}>
            {subtitle}
          </span>
        )}
      </div>

      {/* Center: Live Market Indices */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          overflowX: 'auto',
          padding: '4px 0',
        }}
      >
        {indices.map((idx) => {
          const isUp = idx.change >= 0;
          return (
            <div key={idx.symbol} className="index-ticker">
              <span className="index-ticker-name">{idx.name}</span>
              <span className="index-ticker-value">
                {idx.price ? idx.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '—'}
              </span>
              <span
                className={`index-ticker-change ${isUp ? 'text-green' : 'text-red'}`}
                style={{ display: 'flex', alignItems: 'center', gap: '2px' }}
              >
                {isUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                <span>
                  {isUp ? '+' : ''}
                  {idx.changePercent ? idx.changePercent.toFixed(2) : '0.00'}%
                </span>
              </span>
            </div>
          );
        })}
      </div>

      {/* Right: Search Box + Disclaimer Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
        <form onSubmit={handleSearch} style={{ position: 'relative', width: '180px' }}>
          <Search
            size={14}
            style={{
              position: 'absolute',
              left: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-3)',
              pointerEvents: 'none',
            }}
          />
          <input
            type="text"
            className="finiq-input"
            placeholder="Search ticker (e.g. NVDA)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              paddingLeft: '30px',
              paddingTop: '6px',
              paddingBottom: '6px',
              fontSize: '12px',
              textTransform: 'uppercase',
            }}
          />
        </form>

        <div
          className="disclaimer-banner"
          style={{
            padding: '5px 10px',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
          }}
          title="This project is a prototype and is not financial advice."
        >
          <AlertTriangle size={13} />
          <span>⚠️ Not Financial Advice</span>
        </div>
      </div>
    </header>
  );
}
