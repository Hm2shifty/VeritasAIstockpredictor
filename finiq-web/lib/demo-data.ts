// FINIQ Demo Data — Realistic fallback data for all services

export const DEMO_QUOTES: Record<string, {
  company: string; sector: string; basePrice: number; volatility: number; trend: number;
}> = {
  AAPL:  { company: "Apple Inc.",              sector: "Technology",       basePrice: 189.50, volatility: 0.018, trend: 0.0003 },
  MSFT:  { company: "Microsoft Corp.",         sector: "Technology",       basePrice: 415.00, volatility: 0.016, trend: 0.0004 },
  GOOGL: { company: "Alphabet Inc.",           sector: "Technology",       basePrice: 175.30, volatility: 0.019, trend: 0.0003 },
  AMZN:  { company: "Amazon.com Inc.",         sector: "Consumer Disc.",   basePrice: 195.80, volatility: 0.021, trend: 0.0003 },
  NVDA:  { company: "NVIDIA Corp.",            sector: "Technology",       basePrice: 875.00, volatility: 0.035, trend: 0.0007 },
  META:  { company: "Meta Platforms Inc.",     sector: "Communication",    basePrice: 530.00, volatility: 0.024, trend: 0.0005 },
  TSLA:  { company: "Tesla Inc.",              sector: "Consumer Disc.",   basePrice: 248.00, volatility: 0.045, trend: 0.0001 },
  JPM:   { company: "JPMorgan Chase",          sector: "Financials",       basePrice: 215.00, volatility: 0.014, trend: 0.0002 },
  V:     { company: "Visa Inc.",               sector: "Financials",       basePrice: 285.00, volatility: 0.012, trend: 0.0002 },
  JNJ:   { company: "Johnson & Johnson",       sector: "Healthcare",       basePrice: 158.00, volatility: 0.011, trend: 0.0001 },
  AMD:   { company: "Advanced Micro Devices",  sector: "Technology",       basePrice: 165.00, volatility: 0.038, trend: 0.0005 },
  NFLX:  { company: "Netflix Inc.",            sector: "Communication",    basePrice: 625.00, volatility: 0.028, trend: 0.0004 },
  SPY:   { company: "SPDR S&P 500 ETF",        sector: "ETF",              basePrice: 510.00, volatility: 0.010, trend: 0.0003 },
  QQQ:   { company: "Invesco QQQ Trust",       sector: "ETF",              basePrice: 440.00, volatility: 0.012, trend: 0.0004 },
  DIS:   { company: "Walt Disney Co.",         sector: "Communication",    basePrice: 115.00, volatility: 0.022, trend: 0.0001 },
  PYPL:  { company: "PayPal Holdings",         sector: "Financials",       basePrice: 68.00,  volatility: 0.028, trend: -0.0001 },
  CRM:   { company: "Salesforce Inc.",         sector: "Technology",       basePrice: 295.00, volatility: 0.022, trend: 0.0003 },
  WMT:   { company: "Walmart Inc.",            sector: "Consumer Staples", basePrice: 68.00,  volatility: 0.011, trend: 0.0002 },
  BAC:   { company: "Bank of America",         sector: "Financials",       basePrice: 42.00,  volatility: 0.018, trend: 0.0002 },
  INTC:  { company: "Intel Corp.",             sector: "Technology",       basePrice: 42.00,  volatility: 0.025, trend: -0.0001 },
};

/** Deterministic seeded PRNG */
function mulberry32(seed: number) {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function tickerSeed(ticker: string): number {
  return ticker.split("").reduce((acc, c) => acc + c.charCodeAt(0) * 37, 0) % (2 ** 31);
}

export function getDemoQuote(ticker: string) {
  const upper = ticker.toUpperCase();
  const profile = DEMO_QUOTES[upper] ?? {
    company: `${upper} Corp.`, sector: "Unknown",
    basePrice: 100, volatility: 0.02, trend: 0.0002,
  };
  const rng = mulberry32(tickerSeed(upper));
  const changePct = (rng() - 0.5) * 2 * profile.volatility * 100;
  const price = profile.basePrice * (1 + changePct / 100);
  const change = price - profile.basePrice;
  return {
    ticker: upper,
    company: profile.company,
    sector: profile.sector,
    price: +price.toFixed(2),
    change: +change.toFixed(2),
    changePct: +changePct.toFixed(2),
    open: +(price * 0.998).toFixed(2),
    high: +(price * (1 + profile.volatility * 0.5)).toFixed(2),
    low: +(price * (1 - profile.volatility * 0.5)).toFixed(2),
    volume: Math.floor(rng() * 50_000_000 + 5_000_000),
    avgVolume: Math.floor(rng() * 40_000_000 + 10_000_000),
    marketCap: price > 500 ? `${(price * rng() * 3 + 1).toFixed(1)}T` : `${(price * rng() * 500 + 100).toFixed(0)}B`,
    pe: +(rng() * 40 + 10).toFixed(1),
    week52High: +(profile.basePrice * 1.35).toFixed(2),
    week52Low: +(profile.basePrice * 0.65).toFixed(2),
    beta: +(profile.volatility / 0.012).toFixed(2),
    dataSource: "DEMO" as const,
  };
}

export function getDemoHistory(ticker: string, days: number = 365) {
  const upper = ticker.toUpperCase();
  const profile = DEMO_QUOTES[upper] ?? { basePrice: 100, volatility: 0.02, trend: 0.0002 };
  const rng = mulberry32(tickerSeed(upper) + days);
  const closes: number[] = [profile.basePrice];
  for (let i = 1; i < days; i++) {
    const r = (rng() - 0.5) * 2 * profile.volatility + profile.trend;
    closes.push(closes[i - 1] * (1 + r));
  }
  const result = [];
  const endDate = new Date();
  for (let i = 0; i < days; i++) {
    const d = new Date(endDate);
    d.setDate(d.getDate() - (days - i));
    if (d.getDay() === 0 || d.getDay() === 6) continue;
    const c = closes[i];
    const vol = profile.volatility;
    const h = c * (1 + rng() * vol);
    const l = c * (1 - rng() * vol);
    const o = i === 0 ? c : closes[i - 1];
    result.push({
      date: d.toISOString().split("T")[0],
      open: +o.toFixed(2),
      high: +h.toFixed(2),
      low: +l.toFixed(2),
      close: +c.toFixed(2),
      volume: Math.floor(rng() * 20_000_000 + 2_000_000),
    });
  }
  return result;
}

export const DEMO_NEWS = [
  {
    id: "n001",
    headline: "Federal Reserve Signals Gradual Rate Cuts Amid Cooling Inflation",
    summary: "Fed Chair indicated the central bank is prepared to ease monetary policy as inflation continues to trend toward the 2% target, boosting risk assets across equity markets.",
    source: "Financial Times", sentiment: "positive", eventType: "MACRO", relevanceScore: 0.95,
    publishedAt: "2h ago", tickers: ["SPY", "QQQ", "JPM"],
  },
  {
    id: "n002",
    headline: "NVIDIA Posts Record Quarter; AI Chip Demand Surpasses All Forecasts",
    summary: "NVIDIA reported $22.1B in quarterly revenue, exceeding analyst estimates by 18%. Data center segment grew 427% year-over-year as hyperscalers accelerate AI infrastructure buildout.",
    source: "Wall Street Journal", sentiment: "positive", eventType: "EARNINGS", relevanceScore: 0.98,
    publishedAt: "4h ago", tickers: ["NVDA", "AMD", "MSFT"],
  },
  {
    id: "n003",
    headline: "Apple Unveils Next-Generation AI Features Across Product Line",
    summary: "Apple announced sweeping on-device AI integration across iPhone, Mac, and iPad. The company emphasized privacy-first design with no cloud data exposure.",
    source: "Reuters", sentiment: "positive", eventType: "PRODUCT", relevanceScore: 0.92,
    publishedAt: "6h ago", tickers: ["AAPL", "MSFT"],
  },
  {
    id: "n004",
    headline: "Rising Treasury Yields Put Pressure on Tech Valuations",
    summary: "10-year Treasury yields climbed to 4.52%, their highest in three months, triggering rotation out of growth stocks and into value-oriented sectors.",
    source: "Bloomberg", sentiment: "negative", eventType: "MACRO", relevanceScore: 0.89,
    publishedAt: "8h ago", tickers: ["QQQ", "NVDA", "TSLA"],
  },
  {
    id: "n005",
    headline: "Amazon Web Services Wins $10B Government Cloud Contract",
    summary: "AWS secured a multi-year contract with the Department of Defense, expanding its dominant cloud infrastructure position and validating its enterprise AI capabilities.",
    source: "CNBC", sentiment: "positive", eventType: "CORPORATE", relevanceScore: 0.94,
    publishedAt: "10h ago", tickers: ["AMZN", "MSFT", "GOOGL"],
  },
  {
    id: "n006",
    headline: "Tesla Faces Delivery Shortfall as EV Demand Softens in Key Markets",
    summary: "Tesla reported Q3 deliveries 8% below consensus estimates as competition from Chinese manufacturers intensifies and consumer EV adoption slows in Europe.",
    source: "Reuters", sentiment: "negative", eventType: "EARNINGS", relevanceScore: 0.96,
    publishedAt: "12h ago", tickers: ["TSLA"],
  },
  {
    id: "n007",
    headline: "Meta Platforms Ad Revenue Growth Accelerates; AI Tools Drive Engagement",
    summary: "Meta's advertising revenue grew 24% year-over-year as AI-powered ad targeting improvements lifted conversion rates across Facebook, Instagram, and WhatsApp.",
    source: "Wall Street Journal", sentiment: "positive", eventType: "EARNINGS", relevanceScore: 0.93,
    publishedAt: "14h ago", tickers: ["META", "GOOGL", "AMZN"],
  },
  {
    id: "n008",
    headline: "JPMorgan Raises S&P 500 Year-End Target to 5,800",
    summary: "JPMorgan's equity strategy team raised their year-end target, citing stronger-than-expected corporate earnings, resilient consumer spending, and AI productivity gains.",
    source: "Financial Times", sentiment: "positive", eventType: "ANALYST", relevanceScore: 0.88,
    publishedAt: "1d ago", tickers: ["SPY", "JPM"],
  },
  {
    id: "n009",
    headline: "Intel Announces 15,000 Layoffs in Sweeping Restructuring Plan",
    summary: "Intel announced sweeping restructuring plans including significant job cuts and a refocus on core semiconductor manufacturing as it battles market share losses to AMD and NVIDIA.",
    source: "Reuters", sentiment: "negative", eventType: "CORPORATE", relevanceScore: 0.91,
    publishedAt: "1d ago", tickers: ["INTC", "AMD", "NVDA"],
  },
  {
    id: "n010",
    headline: "PayPal Launches AI-Powered Fraud Detection System",
    summary: "PayPal unveiled a next-generation fraud detection platform powered by large language models, claiming a 40% reduction in false positives and $500M in annual fraud prevention.",
    source: "TechCrunch", sentiment: "positive", eventType: "PRODUCT", relevanceScore: 0.87,
    publishedAt: "1d ago", tickers: ["PYPL", "V", "MA"],
  },
  {
    id: "n011",
    headline: "Healthcare Sector Outperforms as Defensive Rotation Gains Momentum",
    summary: "Healthcare stocks hit 52-week highs as investors rotated into defensive sectors amid uncertainty over global growth outlook and elevated geopolitical risk.",
    source: "Bloomberg", sentiment: "neutral", eventType: "SECTOR", relevanceScore: 0.84,
    publishedAt: "2d ago", tickers: ["JNJ", "SPY"],
  },
  {
    id: "n012",
    headline: "Salesforce Acquires AI Startup for $2.1B to Bolster Enterprise Automation",
    summary: "Salesforce completed its acquisition of an AI workflow automation startup, integrating advanced LLM capabilities into its Einstein platform for enterprise customers.",
    source: "Financial Times", sentiment: "positive", eventType: "M&A", relevanceScore: 0.86,
    publishedAt: "2d ago", tickers: ["CRM", "MSFT"],
  },
  {
    id: "n013",
    headline: "Netflix Subscriber Growth Beats Estimates as Ad-Supported Tier Gains Traction",
    summary: "Netflix added 9.8M subscribers in Q3, exceeding estimates by 3.1M. The ad-supported tier now represents 30% of new sign-ups in key markets.",
    source: "CNBC", sentiment: "positive", eventType: "EARNINGS", relevanceScore: 0.90,
    publishedAt: "2d ago", tickers: ["NFLX", "DIS"],
  },
  {
    id: "n014",
    headline: "Oil Prices Fall 3% on Unexpected Inventory Build",
    summary: "Crude oil prices dropped sharply after the EIA reported a larger-than-expected weekly inventory build, raising concerns about softening global demand.",
    source: "Reuters", sentiment: "negative", eventType: "COMMODITY", relevanceScore: 0.80,
    publishedAt: "3d ago", tickers: ["SPY"],
  },
  {
    id: "n015",
    headline: "Visa and Mastercard Report Strong Cross-Border Transaction Growth",
    summary: "Both payment networks reported double-digit international transaction growth, driven by sustained travel recovery and expanding digital payment adoption in emerging markets.",
    source: "Bloomberg", sentiment: "positive", eventType: "EARNINGS", relevanceScore: 0.89,
    publishedAt: "3d ago", tickers: ["V", "MA", "PYPL"],
  },
];

export const DEMO_INDICES = [
  { name: "S&P 500",   ticker: "^GSPC", price: 5247.68, change: 28.14,  changePct: 0.54,  dataSource: "DEMO" as const },
  { name: "NASDAQ",    ticker: "^IXIC", price: 16845.72, change: 136.20, changePct: 0.82, dataSource: "DEMO" as const },
  { name: "DOW",       ticker: "^DJI",  price: 39188.90, change: -56.30, changePct: -0.14, dataSource: "DEMO" as const },
  { name: "VIX",       ticker: "^VIX",  price: 15.22,   change: -0.65,  changePct: -4.10, dataSource: "DEMO" as const },
];
