import { NextResponse } from 'next/server';
import YahooFinance from 'yahoo-finance2';
import { DEMO_INDICES } from '@/lib/demo-data';

export const dynamic = 'force-dynamic';
export const revalidate = 60;

const yahooFinance = new YahooFinance({
  suppressNotices: ['yahooSurvey', 'ripHistorical'],
});

interface IndexTarget {
  name: string;
  ticker: string;
  fallbackPrice: number;
  fallbackChange: number;
  fallbackPct: number;
}

const INDEX_TARGETS: IndexTarget[] = [
  {
    name: 'S&P 500',
    ticker: '^GSPC',
    fallbackPrice: 5864.20,
    fallbackChange: 18.50,
    fallbackPct: 0.32,
  },
  {
    name: 'NASDAQ',
    ticker: '^IXIC',
    fallbackPrice: 18518.60,
    fallbackChange: 92.40,
    fallbackPct: 0.50,
  },
  {
    name: 'Dow Jones',
    ticker: '^DJI',
    fallbackPrice: 43444.90,
    fallbackChange: -42.80,
    fallbackPct: -0.10,
  },
  {
    name: 'VIX Volatility',
    ticker: '^VIX',
    fallbackPrice: 15.65,
    fallbackChange: -0.45,
    fallbackPct: -2.80,
  },
];

export async function GET() {
  try {
    const results = await Promise.allSettled(
      INDEX_TARGETS.map(async (target) => {
        const q = await yahooFinance.quote(target.ticker);
        if (!q || q.regularMarketPrice == null) {
          throw new Error(`Incomplete quote for ${target.ticker}`);
        }
        return {
          name: target.name,
          ticker: target.ticker,
          price: Number(q.regularMarketPrice.toFixed(2)),
          change: Number((q.regularMarketChange ?? 0).toFixed(2)),
          changePct: Number((q.regularMarketChangePercent ?? 0).toFixed(2)),
          dataSource: 'LIVE' as const,
        };
      })
    );

    const data = results.map((res, idx) => {
      const target = INDEX_TARGETS[idx];
      if (res.status === 'fulfilled') {
        return res.value;
      }

      // Check if DEMO_INDICES has matching ticker
      const fallbackFromDemo = DEMO_INDICES.find((d) => d.ticker === target.ticker);
      return {
        name: target.name,
        ticker: target.ticker,
        price: fallbackFromDemo?.price ?? target.fallbackPrice,
        change: fallbackFromDemo?.change ?? target.fallbackChange,
        changePct: fallbackFromDemo?.changePct ?? target.fallbackPct,
        dataSource: 'DEMO' as const,
      };
    });

    return NextResponse.json(data, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
      },
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Unknown error';
    console.warn(`[API Indices] Fallback triggered: ${errorMsg}`);

    const fallbackData = INDEX_TARGETS.map((target) => {
      const fallbackFromDemo = DEMO_INDICES.find((d) => d.ticker === target.ticker);
      return {
        name: target.name,
        ticker: target.ticker,
        price: fallbackFromDemo?.price ?? target.fallbackPrice,
        change: fallbackFromDemo?.change ?? target.fallbackChange,
        changePct: fallbackFromDemo?.changePct ?? target.fallbackPct,
        dataSource: 'DEMO' as const,
      };
    });

    return NextResponse.json(fallbackData, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
      },
    });
  }
}
