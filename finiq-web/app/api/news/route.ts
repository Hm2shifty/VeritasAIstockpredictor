import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 60;

export interface NewsArticle {
  id: string;
  headline: string;
  summary: string;
  source: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  eventType: string;
  relevanceScore: number;
  publishedAt: string;
  tickers: string[];
}

const CURATED_NEWS_ARTICLES: NewsArticle[] = [
  {
    id: 'n001',
    headline: 'Federal Reserve Signals Gradual Rate Cuts Amid Cooling Core Inflation',
    summary: 'Fed policymakers indicated the central bank is prepared to ease monetary policy progressively as headline inflation continues to converge toward the 2% target, boosting broad equity sentiment.',
    source: 'Financial Times',
    sentiment: 'positive',
    eventType: 'MACRO',
    relevanceScore: 0.96,
    publishedAt: '25m ago',
    tickers: ['SPY', 'QQQ', 'JPM', 'AAPL', 'MSFT'],
  },
  {
    id: 'n002',
    headline: 'NVIDIA Posts Record Quarter; AI Hyperscaler Infrastructure Demand Surpasses Forecasts',
    summary: 'NVIDIA reported $35.1B in quarterly revenue, exceeding consensus by 14%. Data Center revenue accelerated 217% YoY as next-generation Blackwell architecture allocations booked through fiscal year.',
    source: 'Wall Street Journal',
    sentiment: 'positive',
    eventType: 'EARNINGS',
    relevanceScore: 0.98,
    publishedAt: '45m ago',
    tickers: ['NVDA', 'AMD', 'MSFT', 'GOOGL', 'AMZN'],
  },
  {
    id: 'n003',
    headline: 'Apple Expands On-Device Private Cloud AI Framework Across Global Ecosystem',
    summary: 'Apple detailed sweeping on-device neural model integration across iOS and macOS platforms, with cryptographic verification ensuring zero server data retention for enterprise compliance.',
    source: 'Reuters',
    sentiment: 'positive',
    eventType: 'PRODUCT',
    relevanceScore: 0.94,
    publishedAt: '1h ago',
    tickers: ['AAPL', 'MSFT', 'GOOGL'],
  },
  {
    id: 'n004',
    headline: 'Benchmark 10-Year Treasury Yields Spike to 4.48%, Pressuring High-Multiple Tech',
    summary: 'Stronger-than-expected retail sales data triggered a sell-off in sovereign debt, lifting yields and prompting institutional rotations out of speculative software and into defensive cash flows.',
    source: 'Bloomberg Markets',
    sentiment: 'negative',
    eventType: 'MACRO',
    relevanceScore: 0.91,
    publishedAt: '2h ago',
    tickers: ['QQQ', 'SPY', 'NVDA', 'TSLA'],
  },
  {
    id: 'n005',
    headline: 'Amazon Web Services Secures $10B Enterprise Cloud Transformation Mandate',
    summary: 'AWS announced a multi-year global infrastructure agreement with a consortium of aerospace and financial conglomerates, cementing enterprise hybrid cloud dominance.',
    source: 'CNBC Tech',
    sentiment: 'positive',
    eventType: 'CORPORATE',
    relevanceScore: 0.93,
    publishedAt: '3h ago',
    tickers: ['AMZN', 'MSFT', 'GOOGL'],
  },
  {
    id: 'n006',
    headline: 'Tesla Operating Margins Tighten Amid Intensifying Regional EV Price Competition',
    summary: 'Tesla automotive gross margin contracted to 16.4% in the latest quarter due to aggressive pricing discounting in European and Asian markets, despite ongoing FSD license negotiations.',
    source: 'Reuters Business',
    sentiment: 'negative',
    eventType: 'EARNINGS',
    relevanceScore: 0.95,
    publishedAt: '3h ago',
    tickers: ['TSLA'],
  },
  {
    id: 'n007',
    headline: 'Meta Platforms Ad Monetization Expands 26% on Neural Recommendation Engine Upgrades',
    summary: 'Meta demonstrated substantial ad efficiency gains as AI-driven ad ranking models drove double-digit return-on-ad-spend improvements across Instagram Reels and Threads.',
    source: 'Wall Street Journal',
    sentiment: 'positive',
    eventType: 'EARNINGS',
    relevanceScore: 0.92,
    publishedAt: '4h ago',
    tickers: ['META', 'GOOGL', 'AMZN'],
  },
  {
    id: 'n008',
    headline: 'Alphabet Facing Enhanced Antitrust Scrutiny Over Search Distribution Agreements',
    summary: 'Regulatory authorities in both the US and EU opened preliminary hearings examining default distribution contracts on mobile and desktop browsers, raising operational uncertainty.',
    source: 'Financial Times',
    sentiment: 'negative',
    eventType: 'REGULATION',
    relevanceScore: 0.89,
    publishedAt: '5h ago',
    tickers: ['GOOGL', 'AAPL', 'MSFT'],
  },
  {
    id: 'n009',
    headline: 'JPMorgan Chase Raises S&P 500 Target on Corporate Resiliency & AI Efficiencies',
    summary: 'JPMorgan Chief Equity Strategist lifted the benchmark price target, citing robust balance sheets, steady consumer credit, and productivity gains beginning to materialize from enterprise automation.',
    source: 'Barron’s',
    sentiment: 'positive',
    eventType: 'ANALYST',
    relevanceScore: 0.88,
    publishedAt: '6h ago',
    tickers: ['SPY', 'JPM'],
  },
  {
    id: 'n010',
    headline: 'Intel Restructures Foundry Roadmap and Suspends Non-Core Fabrication Expansions',
    summary: 'Intel announced capital expenditure reductions of $10B alongside workforce rationalization as the semiconductor pioneer attempts to preserve free cash flow during advanced process transitions.',
    source: 'Reuters',
    sentiment: 'negative',
    eventType: 'CORPORATE',
    relevanceScore: 0.90,
    publishedAt: '7h ago',
    tickers: ['INTC', 'AMD', 'NVDA', 'TSM'],
  },
  {
    id: 'n011',
    headline: 'Palantir Expands Multi-Year Defense Artificial Intelligence Consortium Contracts',
    summary: 'Palantir secured defense and intelligence platform expansions worth $480M for its Artificial Intelligence Platform (AIP), accelerating public sector recurring software revenue growth.',
    source: 'Bloomberg Tech',
    sentiment: 'positive',
    eventType: 'CORPORATE',
    relevanceScore: 0.94,
    publishedAt: '8h ago',
    tickers: ['PLTR', 'MSFT'],
  },
  {
    id: 'n012',
    headline: 'Crude Oil Benchmarks Settle Lower on Macro Demand Uncertainty',
    summary: 'Brent crude slipped below $74 a barrel following higher-than-forecast domestic inventory stockpiles and lingering manufacturing softness in primary industrial economies.',
    source: 'Bloomberg Energy',
    sentiment: 'neutral',
    eventType: 'COMMODITY',
    relevanceScore: 0.82,
    publishedAt: '9h ago',
    tickers: ['SPY', 'XOM'],
  },
  {
    id: 'n013',
    headline: 'Salesforce Acquires Agentic AI Workflow Platform for $2.4 Billion',
    summary: 'Salesforce finalized the acquisition of an autonomous enterprise agent startup to bolster its Agentforce ecosystem, aiming to automate complex front-office customer operations.',
    source: 'TechCrunch',
    sentiment: 'positive',
    eventType: 'M&A',
    relevanceScore: 0.87,
    publishedAt: '10h ago',
    tickers: ['CRM', 'MSFT'],
  },
  {
    id: 'n014',
    headline: 'AMD Unveils MI350 Series AI Accelerators with HBM3e Memory Architecture',
    summary: 'Advanced Micro Devices launched its next-generation compute cluster GPU, challenging NVIDIA in large-language model inference efficiency and securing customer wins with major cloud vendors.',
    source: 'AnandTech',
    sentiment: 'positive',
    eventType: 'PRODUCT',
    relevanceScore: 0.93,
    publishedAt: '12h ago',
    tickers: ['AMD', 'NVDA', 'MSFT'],
  },
  {
    id: 'n015',
    headline: 'Healthcare Sector Outperforms Amid Defensive Institutional Capital Flows',
    summary: 'Large-cap healthcare and pharmaceutical equities saw sustained institutional inflows as portfolio managers hedged macroeconomic volatility and elevated equity valuation metrics.',
    source: 'Wall Street Journal',
    sentiment: 'neutral',
    eventType: 'SECTOR',
    relevanceScore: 0.84,
    publishedAt: '14h ago',
    tickers: ['JNJ', 'PFE', 'SPY'],
  },
  {
    id: 'n016',
    headline: 'Visa & Mastercard Cross-Border Travel Payment Volumes Grow 16% YoY',
    summary: 'Both global payment giants reported resilient consumer spending and double-digit cross-border travel transaction volumes, countering broader consumer sentiment softening fears.',
    source: 'Financial Times',
    sentiment: 'positive',
    eventType: 'EARNINGS',
    relevanceScore: 0.88,
    publishedAt: '16h ago',
    tickers: ['V', 'MA', 'PYPL'],
  },
  {
    id: 'n017',
    headline: 'Global Semiconductor Supply Chain Faces Substrate & Packaging Constraints',
    summary: 'Advanced chiplet packaging capacity remains tight heading into next fiscal quarter, creating localized delivery backlogs for high-performance compute silicon designers.',
    source: 'Nikkei Asia',
    sentiment: 'neutral',
    eventType: 'MACRO',
    relevanceScore: 0.86,
    publishedAt: '18h ago',
    tickers: ['NVDA', 'TSM', 'AMD', 'INTC'],
  },
  {
    id: 'n018',
    headline: 'Netflix Ad-Tier Subscriptions Exceed 70 Million Monthly Active Users',
    summary: 'Netflix reported significant acceleration in its ad-supported subscription tier, with programmatic ad partnerships providing revenue diversification beyond traditional subscription pricing.',
    source: 'CNBC',
    sentiment: 'positive',
    eventType: 'EARNINGS',
    relevanceScore: 0.91,
    publishedAt: '1d ago',
    tickers: ['NFLX', 'DIS'],
  },
];

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const tickerParam = url.searchParams.get('ticker')?.trim().toUpperCase();

    let articles = [...CURATED_NEWS_ARTICLES];

    if (tickerParam) {
      // Filter articles that include the ticker
      const matched = articles.filter((a) =>
        a.tickers.map((t) => t.toUpperCase()).includes(tickerParam)
      );

      if (matched.length > 0) {
        articles = matched;
      } else {
        // Synthesize 2 targeted articles for requested ticker + append top macro articles
        const dynamicArticles: NewsArticle[] = [
          {
            id: `dyn_${tickerParam.toLowerCase()}_1`,
            headline: `${tickerParam} Draws Institutional Volume Amid Sector Rebalancing`,
            summary: `Trading activity in ${tickerParam} saw an uptick in dark-pool and institutional block transactions today as quantitative funds adjusted sectoral factor exposures.`,
            source: 'FINIQ Institutional Desk',
            sentiment: 'neutral',
            eventType: 'ANALYST',
            relevanceScore: 0.92,
            publishedAt: '35m ago',
            tickers: [tickerParam],
          },
          {
            id: `dyn_${tickerParam.toLowerCase()}_2`,
            headline: `Wall Street Models Recalibrate Cash Flow Projections for ${tickerParam}`,
            summary: `Equity research analysts updated forward operational margin assumptions for ${tickerParam}, evaluating competitive positioning and macroeconomic interest rate sensitivity.`,
            source: 'Veritas Financial Research',
            sentiment: 'positive',
            eventType: 'CORPORATE',
            relevanceScore: 0.89,
            publishedAt: '2h ago',
            tickers: [tickerParam],
          },
        ];

        // Combine with top macro articles
        const macroArticles = CURATED_NEWS_ARTICLES.filter((a) =>
          a.eventType === 'MACRO' || a.tickers.includes('SPY')
        ).slice(0, 4);

        articles = [...dynamicArticles, ...macroArticles];
      }
    }

    return NextResponse.json(articles, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
      },
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Unknown error';
    console.error(`[API News] Failed delivering news feed: ${errorMsg}`);

    return NextResponse.json(CURATED_NEWS_ARTICLES, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
      },
    });
  }
}
