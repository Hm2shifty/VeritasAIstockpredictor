// FINIQ Shared Types

export interface Quote {
  ticker: string;
  company: string;
  sector: string;
  price: number;
  change: number;
  changePct: number;
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
  dataSource: "LIVE" | "DEMO";
}

export interface OHLCVBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketIndex {
  name: string;
  ticker: string;
  price: number;
  change: number;
  changePct: number;
  dataSource: "LIVE" | "DEMO";
}

export interface NewsArticle {
  id: string;
  headline: string;
  summary: string;
  source: string;
  sentiment: "positive" | "negative" | "neutral";
  eventType: string;
  relevanceScore: number;
  publishedAt: string;
  tickers: string[];
}

export interface KeyFactor {
  factor: string;
  value: string;
  impact: "Positive" | "Negative" | "Neutral";
  description: string;
}

export interface ClassMetrics {
  precision: number;
  recall: number;
  f1: number;
  support?: number;
}

export interface BaselineComparison {
  trainSamples: number;
  testSamples: number;
  trainPeriod: string;
  testPeriod: string;
  model: {
    name: string;
    accuracy: number;
    metrics: Record<string, ClassMetrics>;
  };
  baselineMajority: {
    name: string;
    accuracy: number;
    majorityClass: string;
    metrics: Record<string, ClassMetrics>;
  };
  baselineBullish: {
    name: string;
    accuracy: number;
    metrics: Record<string, ClassMetrics>;
  };
  modelBeatsMajority: boolean;
  modelBeatsBullish: boolean;
  accuracyLiftVsMajority: number;
  accuracyLiftVsBullish: number;
}

export interface PredictionResult {
  ticker: string;
  direction: "BULLISH" | "BEARISH" | "NEUTRAL";
  confidence: number;
  signalStrength: "STRONG" | "MODERATE" | "WEAK";
  horizon: string;
  keyFactors: KeyFactor[];
  technicalSummary: Record<string, { value: string | number; signal: string; description: string }>;
  vsBaseline: BaselineComparison;
  uncertaintyNote: string;
  dataPointsUsed: number;
  isReliable: boolean;
}

export interface DebateAgent {
  thesisTitle: string;
  score: number;
  confidence: string;
  arguments: string[];
  catalysts?: string[];
  risks?: string[];
  challenges?: string;
}

export interface DebateResult {
  ticker: string;
  generatedAt: string;
  bull: DebateAgent;
  bear: DebateAgent;
  risk: {
    riskLevel: string;
    confidence: string;
    keyRisks: string[];
    bullChallenges: string;
    bearChallenges: string;
  };
  chief: {
    outlook: string;
    outlookStrength: string;
    executiveSummary: string;
    keyThesis: string;
    strongestBull: string;
    strongestBear: string;
    areasOfConsensus: string[];
    disclaimer: string;
  };
}
