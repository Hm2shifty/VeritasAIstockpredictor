import { NextResponse } from 'next/server';
import YahooFinance from 'yahoo-finance2';
import { getDemoQuote, DEMO_QUOTES } from '@/lib/demo-data';

export const dynamic = 'force-dynamic';
export const revalidate = 60;

// Initialize YahooFinance server client
const yahooFinance = new YahooFinance({
  suppressNotices: ['yahooSurvey', 'ripHistorical'],
});

function formatMarketCap(cap?: number | null): string {
  if (!cap || isNaN(cap)) return 'N/A';
  if (cap >= 1e12) return `${(cap / 1e12).toFixed(2)}T`;
  if (cap >= 1e9) return `${(cap / 1e9).toFixed(2)}B`;
  if (cap >= 1e6) return `${(cap / 1e6).toFixed(2)}M`;
  return cap.toLocaleString();
}

export async function GET(
  request: Request,
  props: { params: Promise<{ ticker: string }> | { ticker: string } }
) {
  const params = await props.params;
  const rawTicker = params.ticker || 'AAPL';
  const ticker = rawTicker.toUpperCase().trim();

  try {
    // Attempt live quote from Yahoo Finance
    const q = await yahooFinance.quote(ticker);

    if (!q || !q.regularMarketPrice) {
      throw new Error(`Incomplete quote data returned for ${ticker}`);
    }

    // Optional quoteSummary for sector & beta enrichment
    let sector = DEMO_QUOTES[ticker]?.sector || 'Technology';
    let beta = 1.0;

    try {
      const summary = await Promise.race([
        yahooFinance.quoteSummary(ticker, {
          modules: ['assetProfile', 'defaultKeyStatistics'],
        }),
        new Promise<null>((resolve) => setTimeout(() => resolve(null), 1500)),
      ]);

      if (summary) {
        if (summary.assetProfile?.sector) {
          sector = summary.assetProfile.sector;
        }
        if (summary.defaultKeyStatistics?.beta != null) {
          beta = Number(summary.defaultKeyStatistics.beta.toFixed(2));
        }
      }
    } catch {
      // Non-fatal, use fallback sector & beta
    }

    const price = Number((q.regularMarketPrice ?? 0).toFixed(2));
    const change = Number((q.regularMarketChange ?? 0).toFixed(2));
    const changePct = Number((q.regularMarketChangePercent ?? 0).toFixed(2));
    const open = Number((q.regularMarketOpen ?? price).toFixed(2));
    const high = Number((q.regularMarketDayHigh ?? price).toFixed(2));
    const low = Number((q.regularMarketDayLow ?? price).toFixed(2));
    const volume = q.regularMarketVolume ?? 0;
    const avgVolume = q.averageDailyVolume3Month ?? q.regularMarketVolume ?? volume;
    const pe = q.trailingPE
      ? Number(q.trailingPE.toFixed(2))
      : q.forwardPE
      ? Number(q.forwardPE.toFixed(2))
      : null;
    const week52High = Number((q.fiftyTwoWeekHigh ?? high).toFixed(2));
    const week52Low = Number((q.fiftyTwoWeekLow ?? low).toFixed(2));
    const company = q.shortName || q.longName || DEMO_QUOTES[ticker]?.company || `${ticker} Inc.`;
    const marketCap = formatMarketCap(q.marketCap);

    return NextResponse.json(
      {
        ticker,
        company,
        price,
        change,
        changePct,
        open,
        high,
        low,
        volume,
        avgVolume,
        marketCap,
        pe,
        week52High,
        week52Low,
        beta,
        sector,
        dataSource: 'LIVE',
        // Compatibility aliases
        symbol: ticker,
        name: company,
        changePercent: changePct,
      },
      {
        status: 200,
        headers: {
          'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
        },
      }
    );
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Unknown error';
    console.warn(`[API Quote] Failed fetching live quote for ${ticker}: ${errorMsg}. Falling back to demo data.`);

    // Fallback demo data
    const demo = getDemoQuote(ticker);
    return NextResponse.json(
      {
        ticker: demo.ticker,
        company: demo.company,
        price: demo.price,
        change: demo.change,
        changePct: demo.changePct,
        open: demo.open,
        high: demo.high,
        low: demo.low,
        volume: demo.volume,
        avgVolume: demo.avgVolume,
        marketCap: demo.marketCap,
        pe: demo.pe,
        week52High: demo.week52High,
        week52Low: demo.week52Low,
        beta: demo.beta,
        sector: demo.sector,
        dataSource: 'DEMO',
        // Compatibility aliases
        symbol: demo.ticker,
        name: demo.company,
        changePercent: demo.changePct,
      },
      {
        status: 200,
        headers: {
          'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
        },
      }
    );
  }
}
