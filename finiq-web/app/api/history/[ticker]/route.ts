import { NextResponse } from 'next/server';
import YahooFinance from 'yahoo-finance2';
import { DEMO_QUOTES } from '@/lib/demo-data';

export const dynamic = 'force-dynamic';
export const revalidate = 60;

const yahooFinance = new YahooFinance({
  suppressNotices: ['yahooSurvey', 'ripHistorical'],
});

export interface HistoryBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/** Deterministic Mulberry32 PRNG */
function mulberry32(seed: number) {
  return function () {
    let s = (seed += 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Standard Normal Box-Muller transform */
function normalDistribution(rand: () => number): number {
  let u = 0;
  let v = 0;
  while (u === 0) u = rand();
  while (v === 0) v = rand();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

/** String hash for seed */
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash) || 123456789;
}

/**
 * Synthesizes realistic OHLCV market history using Geometric Brownian Motion (GBM)
 * dS = mu * S * dt + sigma * S * dW
 * Seeded by ticker for perfect reproducibility.
 */
function generateGBMHistory(ticker: string, period: string): HistoryBar[] {
  const upper = ticker.toUpperCase();
  const profile = DEMO_QUOTES[upper] ?? {
    basePrice: 120 + (hashString(upper) % 180),
    volatility: 0.022,
    trend: 0.0003,
  };

  const seed = hashString(`${upper}_${period}_FINIQ`);
  const rng = mulberry32(seed);

  let barCount = 30;
  let dt = 1 / 252;
  let isIntraday = false;

  switch (period) {
    case '1D':
      barCount = 26; // ~15m intervals during 6.5h trading session
      dt = 1 / (252 * 26);
      isIntraday = true;
      break;
    case '5D':
      barCount = 35; // 7 hourly bars per day * 5
      dt = 1 / (252 * 7);
      isIntraday = true;
      break;
    case '1M':
      barCount = 22;
      dt = 1 / 252;
      break;
    case '3M':
      barCount = 65;
      dt = 1 / 252;
      break;
    case '6M':
      barCount = 130;
      dt = 1 / 252;
      break;
    case '1Y':
      barCount = 252;
      dt = 1 / 252;
      break;
    case '2Y':
      barCount = 504;
      dt = 1 / 252;
      break;
    default:
      barCount = 30;
      dt = 1 / 252;
      break;
  }

  const mu = profile.trend * 252;
  const sigma = profile.volatility * Math.sqrt(252);
  let currentPrice = profile.basePrice;

  // Generate price path backwards from today or forward from basePrice
  const path: number[] = [currentPrice];
  for (let i = 1; i < barCount; i++) {
    const z = normalDistribution(rng);
    const drift = (mu - 0.5 * sigma * sigma) * dt;
    const diffusion = sigma * Math.sqrt(dt) * z;
    currentPrice = currentPrice * Math.exp(drift + diffusion);
    if (currentPrice < 1.0) currentPrice = 1.0;
    path.push(currentPrice);
  }

  const now = new Date();
  const bars: HistoryBar[] = [];

  for (let i = 0; i < barCount; i++) {
    const price = path[i];
    const prevPrice = i === 0 ? price * (1 - (rng() - 0.5) * 0.004) : path[i - 1];

    const open = prevPrice * (1 + (rng() - 0.5) * 0.002);
    const close = price;
    const maxOC = Math.max(open, close);
    const minOC = Math.min(open, close);

    const high = maxOC * (1 + Math.abs(normalDistribution(rng)) * (profile.volatility * 0.4));
    const low = minOC * (1 - Math.abs(normalDistribution(rng)) * (profile.volatility * 0.4));

    const pctMove = Math.abs(close - open) / (open || 1);
    const baseVol = 15_000_000 + (hashString(upper) % 25_000_000);
    const volume = Math.round(baseVol * (0.7 + rng() * 0.6 + pctMove * 12));

    let dateStr = '';
    if (isIntraday && period === '1D') {
      const barDate = new Date(now);
      const minutesOffset = (barCount - 1 - i) * 15;
      barDate.setMinutes(barDate.getMinutes() - minutesOffset);
      const hours = String(barDate.getHours()).padStart(2, '0');
      const mins = String(barDate.getMinutes()).padStart(2, '0');
      dateStr = `${hours}:${mins}`;
    } else if (isIntraday && period === '5D') {
      const barDate = new Date(now);
      const hoursOffset = (barCount - 1 - i) * 2;
      barDate.setHours(barDate.getHours() - hoursOffset);
      dateStr = barDate.toISOString().replace('T', ' ').substring(0, 16);
    } else {
      const barDate = new Date(now);
      barDate.setDate(barDate.getDate() - (barCount - 1 - i));
      dateStr = barDate.toISOString().split('T')[0];
    }

    bars.push({
      date: dateStr,
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
    });
  }

  return bars;
}

export async function GET(
  request: Request,
  props: { params: Promise<{ ticker: string }> | { ticker: string } }
) {
  const params = await props.params;
  const rawTicker = params.ticker || 'AAPL';
  const ticker = rawTicker.toUpperCase().trim();

  const url = new URL(request.url);
  const periodParam = (url.searchParams.get('period') || '1M').toUpperCase();
  const validPeriods = ['1D', '5D', '1M', '3M', '6M', '1Y', '2Y'];
  const period = validPeriods.includes(periodParam) ? periodParam : '1M';

  try {
    const period2 = new Date();
    const period1 = new Date();
    let interval: '1d' | '1wk' | '1mo' = '1d';

    switch (period) {
      case '1D':
        period1.setDate(period1.getDate() - 3);
        break;
      case '5D':
        period1.setDate(period1.getDate() - 7);
        break;
      case '1M':
        period1.setDate(period1.getDate() - 32);
        break;
      case '3M':
        period1.setDate(period1.getDate() - 95);
        break;
      case '6M':
        period1.setDate(period1.getDate() - 185);
        break;
      case '1Y':
        period1.setFullYear(period1.getFullYear() - 1);
        break;
      case '2Y':
        period1.setFullYear(period1.getFullYear() - 2);
        interval = '1d';
        break;
      default:
        period1.setMonth(period1.getMonth() - 1);
        break;
    }

    // Query historical data from Yahoo Finance
    const rawData = await yahooFinance.historical(ticker, {
      period1,
      period2,
      interval,
    });

    if (!rawData || !Array.isArray(rawData) || rawData.length === 0) {
      throw new Error(`Empty historical data returned for ${ticker}`);
    }

    const bars: HistoryBar[] = rawData
      .filter((item) => item.close != null && item.open != null)
      .map((item) => {
        const d = item.date instanceof Date ? item.date : new Date(item.date);
        return {
          date: d.toISOString().split('T')[0],
          open: Number(Number(item.open ?? item.close).toFixed(2)),
          high: Number(Number(item.high ?? Math.max(item.open ?? 0, item.close ?? 0)).toFixed(2)),
          low: Number(Number(item.low ?? Math.min(item.open ?? 0, item.close ?? 0)).toFixed(2)),
          close: Number(Number(item.close).toFixed(2)),
          volume: Math.round(item.volume ?? 0),
        };
      });

    return NextResponse.json(bars, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
      },
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Unknown error';
    console.warn(`[API History] Yahoo historical failed for ${ticker} (${period}): ${errorMsg}. Using GBM synthesis.`);

    const demoBars = generateGBMHistory(ticker, period);
    return NextResponse.json(demoBars, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
      },
    });
  }
}
