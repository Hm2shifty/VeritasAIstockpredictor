'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';

export interface StockCandle {
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close: number;
  volume?: number;
}

interface StockChartProps {
  ticker: string;
  data: StockCandle[];
  period?: string;
  onPeriodChange?: (period: string) => void;
  loading?: boolean;
  height?: number;
}

const PERIODS = ['1D', '5D', '1M', '3M', '6M', '1Y', '2Y'];

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: StockCandle }>;
  label?: string;
}

const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
  if (!active || !payload || !payload.length) return null;
  const candle = payload[0].payload;

  return (
    <div
      style={{
        background: 'rgba(17, 25, 40, 0.95)',
        border: '1px solid var(--border-light)',
        backdropFilter: 'blur(8px)',
        borderRadius: '8px',
        padding: '10px 14px',
        fontSize: '12px',
        boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        zIndex: 100,
      }}
    >
      <div style={{ color: 'var(--text-2)', fontSize: '11px', marginBottom: '6px' }}>
        {candle.date}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'auto auto', gap: '4px 12px', fontFamily: 'var(--mono)' }}>
        <span style={{ color: 'var(--text-2)' }}>Close:</span>
        <span style={{ color: 'var(--text-0)', fontWeight: 700, textAlign: 'right' }}>
          ${candle.close?.toFixed(2)}
        </span>
        {candle.open !== undefined && (
          <>
            <span style={{ color: 'var(--text-2)' }}>Open:</span>
            <span style={{ color: 'var(--text-1)', textAlign: 'right' }}>${candle.open.toFixed(2)}</span>
          </>
        )}
        {candle.high !== undefined && (
          <>
            <span style={{ color: 'var(--text-2)' }}>High:</span>
            <span style={{ color: 'var(--positive)', textAlign: 'right' }}>${candle.high.toFixed(2)}</span>
          </>
        )}
        {candle.low !== undefined && (
          <>
            <span style={{ color: 'var(--text-2)' }}>Low:</span>
            <span style={{ color: 'var(--negative)', textAlign: 'right' }}>${candle.low.toFixed(2)}</span>
          </>
        )}
        {candle.volume !== undefined && (
          <>
            <span style={{ color: 'var(--text-2)' }}>Vol:</span>
            <span style={{ color: 'var(--text-2)', textAlign: 'right' }}>
              {(candle.volume / 1e6).toFixed(2)}M
            </span>
          </>
        )}
      </div>
    </div>
  );
};

export default function StockChart({
  ticker,
  data,
  period = '1M',
  onPeriodChange,
  loading = false,
  height = 360,
}: StockChartProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { isUp, firstClose, lastClose, change, changePct, minPrice, maxPrice } = useMemo(() => {
    if (!data || data.length === 0) {
      return { isUp: true, firstClose: 0, lastClose: 0, change: 0, changePct: 0, minPrice: 0, maxPrice: 100 };
    }
    const first = data[0].close ?? 0;
    const last = data[data.length - 1].close ?? 0;
    const chg = last - first;
    const pct = first > 0 ? (chg / first) * 100 : 0;

    let min = Infinity;
    let max = -Infinity;
    data.forEach((d) => {
      if (d.close < min) min = d.close;
      if (d.close > max) max = d.close;
    });

    const padding = (max - min) * 0.08 || 5;
    return {
      isUp: last >= first,
      firstClose: first,
      lastClose: last,
      change: chg,
      changePct: pct,
      minPrice: Math.max(0, Math.floor(min - padding)),
      maxPrice: Math.ceil(max + padding),
    };
  }, [data]);

  const strokeColor = isUp ? '#0ECB81' : '#F6465D';
  const gradientId = `chartGradient_${ticker}_${isUp ? 'up' : 'down'}`;

  return (
    <div className="chart-container">
      {/* Top Header Controls: Price chip and Period selector */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '16px',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
            <span className="price-chip">
              ${lastClose ? lastClose.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '—'}
            </span>
            <span
              className={`badge ${isUp ? 'badge-green' : 'badge-red'}`}
              style={{ fontSize: '13px', padding: '3px 10px', fontFamily: 'var(--mono)' }}
            >
              {isUp ? '+' : ''}
              {change.toFixed(2)} ({isUp ? '+' : ''}
              {changePct.toFixed(2)}%)
            </span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-3)', marginTop: '4px' }}>
            {ticker} • Historical Price & Volume Performance ({period})
          </div>
        </div>

        {/* Period Selector Tabs */}
        <div
          style={{
            display: 'flex',
            background: 'var(--bg-1)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            padding: '2px',
            gap: '2px',
          }}
        >
          {PERIODS.map((p) => {
            const active = p === period;
            return (
              <button
                key={p}
                onClick={() => onPeriodChange?.(p)}
                style={{
                  padding: '5px 10px',
                  fontSize: '11px',
                  fontWeight: 600,
                  fontFamily: 'var(--mono)',
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer',
                  background: active ? 'var(--accent)' : 'transparent',
                  color: active ? '#ffffff' : 'var(--text-2)',
                  transition: 'all 0.15s ease',
                }}
              >
                {p}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Chart Body */}
      {loading || !mounted ? (
        <div
          className="skeleton"
          style={{
            width: '100%',
            height: `${height}px`,
            borderRadius: '8px',
          }}
        />
      ) : data.length === 0 ? (
        <div
          style={{
            height: `${height}px`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-3)',
            fontSize: '13px',
          }}
        >
          No historical chart data available for {ticker}
        </div>
      ) : (
        <div style={{ width: '100%', height: `${height}px` }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={strokeColor} stopOpacity={0.35} />
                  <stop offset="95%" stopColor={strokeColor} stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                stroke="var(--text-3)"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: 'var(--border)' }}
                minTickGap={40}
              />
              <YAxis
                domain={[minPrice, maxPrice]}
                stroke="var(--text-3)"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: 'var(--border)' }}
                tickFormatter={(val) => `$${val}`}
                orientation="right"
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="close"
                stroke={strokeColor}
                strokeWidth={2}
                fillOpacity={1}
                fill={`url(#${gradientId})`}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
