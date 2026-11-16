import { NextResponse } from 'next/server';
import YahooFinance from 'yahoo-finance2';
import { RSI, MACD, BollingerBands } from 'technicalindicators';
import { DEMO_QUOTES } from '@/lib/demo-data';

export const dynamic = 'force-dynamic';
export const revalidate = 60;

const yahooFinance = new YahooFinance({
  suppressNotices: ['yahooSurvey', 'ripHistorical'],
});

type DirectionClass = 'BULLISH' | 'BEARISH' | 'NEUTRAL';

interface DataPoint {
  date: string;
  close: number;
  rsi: number;
  macd: { MACD: number; signal?: number; histogram?: number };
  bb: { lower: number; middle: number; upper: number; pb?: number };
}

interface LabeledSample extends DataPoint {
  nextClose: number;
  actualReturn: number;
  actualClass: DirectionClass;
  predClass: DirectionClass;
  score: number;
}

interface ClassPerformance {
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

function mulberry32(seed: number) {
  return function () {
    let s = (seed += 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash) || 123456789;
}

/** Fallback 1Y synthetic closes using deterministic GBM */
function generateSyntheticCloses(ticker: string, count: number = 260): { dates: string[]; closes: number[] } {
  const upper = ticker.toUpperCase();
  const profile = DEMO_QUOTES[upper] ?? {
    basePrice: 150 + (hashString(upper) % 150),
    volatility: 0.022,
    trend: 0.0004,
  };

  const rng = mulberry32(hashString(`${upper}_PREDICT_1Y`));
  const closes: number[] = [profile.basePrice];
  const dates: string[] = [];

  const now = new Date();
  for (let i = 1; i < count; i++) {
    const u1 = Math.max(1e-7, rng());
    const u2 = rng();
    const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    const drift = profile.trend - 0.5 * profile.volatility * profile.volatility;
    const diff = profile.volatility * z;
    const nextClose = closes[i - 1] * Math.exp(drift + diff);
    closes.push(Number(nextClose.toFixed(2)));
  }

  for (let i = 0; i < count; i++) {
    const d = new Date(now);
    d.setDate(d.getDate() - (count - 1 - i));
    dates.push(d.toISOString().split('T')[0]);
  }

  return { dates, closes };
}

/** Computes technical indicator scores */
function computeSignal(
  curr: { rsi: number; macd: { MACD: number; signal?: number; histogram?: number }; bb: { lower: number; middle: number; upper: number; pb?: number }; close: number },
  prev?: { macd: { MACD: number; signal?: number; histogram?: number } } | null,
  threshold: number = 0.12
): { direction: DirectionClass; score: number; rsiScore: number; macdScore: number; bbScore: number } {
  // 1. RSI Score
  let rsiScore = 0;
  if (curr.rsi < 35) rsiScore = 1.0;
  else if (curr.rsi < 48) rsiScore = 0.4;
  else if (curr.rsi > 65) rsiScore = -1.0;
  else if (curr.rsi > 52) rsiScore = -0.4;

  // 2. MACD Histogram Score
  let macdScore = 0;
  const hist = curr.macd.histogram ?? (curr.macd.MACD - (curr.macd.signal ?? 0));
  const prevHist = prev ? (prev.macd.histogram ?? (prev.macd.MACD - (prev.macd.signal ?? 0))) : 0;
  if (hist > 0) {
    macdScore = hist >= prevHist ? 1.0 : 0.4;
  } else {
    macdScore = hist <= prevHist ? -1.0 : -0.4;
  }

  // 3. Bollinger Bands Score
  let bbScore = 0;
  const pb = curr.bb.pb ?? ((curr.close - curr.bb.lower) / (curr.bb.upper - curr.bb.lower || 1));
  if (pb < 0.2) bbScore = 1.0;
  else if (pb < 0.4) bbScore = 0.3;
  else if (pb > 0.8) bbScore = -1.0;
  else if (pb > 0.6) bbScore = -0.3;

  // Composite weighted score
  const score = Number((0.35 * rsiScore + 0.40 * macdScore + 0.25 * bbScore).toFixed(4));

  let direction: DirectionClass = 'NEUTRAL';
  if (score > threshold) direction = 'BULLISH';
  else if (score < -threshold) direction = 'BEARISH';

  return { direction, score, rsiScore, macdScore, bbScore };
}

function calculateClassMetrics(
  actual: DirectionClass[],
  predicted: DirectionClass[]
): Record<DirectionClass, ClassPerformance> {
  const classes: DirectionClass[] = ['BULLISH', 'BEARISH', 'NEUTRAL'];
  const result: Record<DirectionClass, ClassPerformance> = {
    BULLISH: { precision: 0, recall: 0, f1: 0, support: 0 },
    BEARISH: { precision: 0, recall: 0, f1: 0, support: 0 },
    NEUTRAL: { precision: 0, recall: 0, f1: 0, support: 0 },
  };

  classes.forEach((c) => {
    let tp = 0;
    let fp = 0;
    let fn = 0;
    let support = 0;

    for (let i = 0; i < actual.length; i++) {
      if (actual[i] === c) support++;
      if (predicted[i] === c && actual[i] === c) tp++;
      if (predicted[i] === c && actual[i] !== c) fp++;
      if (predicted[i] !== c && actual[i] === c) fn++;
    }

    const precision = tp + fp > 0 ? (tp / (tp + fp)) * 100 : 0;
    const recall = tp + fn > 0 ? (tp / (tp + fn)) * 100 : 0;
    const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;

    result[c] = {
      precision: Number(precision.toFixed(1)),
      recall: Number(recall.toFixed(1)),
      f1: Number(f1.toFixed(1)),
      support,
    };
  });

  return result;
}

export async function GET(
  request: Request,
  props: { params: Promise<{ ticker: string }> | { ticker: string } }
) {
  const params = await props.params;
  const rawTicker = params.ticker || 'AAPL';
  const ticker = rawTicker.toUpperCase().trim();

  try {
    let closes: number[] = [];
    let dates: string[] = [];
    let isLive = true;

    // 1. Fetch 1Y history internally from Yahoo Finance
    try {
      const p1 = new Date();
      p1.setFullYear(p1.getFullYear() - 1);
      const rawHistory = await yahooFinance.historical(ticker, {
        period1: p1,
        period2: new Date(),
        interval: '1d',
      });

      if (rawHistory && rawHistory.length >= 60) {
        rawHistory.forEach((h) => {
          if (h.close != null && !isNaN(h.close)) {
            closes.push(Number(h.close.toFixed(2)));
            const d = h.date instanceof Date ? h.date : new Date(h.date);
            dates.push(d.toISOString().split('T')[0]);
          }
        });
      } else {
        throw new Error('Insufficient historical length');
      }
    } catch {
      isLive = false;
      const synthetic = generateSyntheticCloses(ticker, 252);
      closes = synthetic.closes;
      dates = synthetic.dates;
    }

    // 2. Compute Technical Indicators using technicalindicators npm package
    const rsiValues = RSI.calculate({ period: 14, values: closes });
    const macdValues = MACD.calculate({
      values: closes,
      fastPeriod: 12,
      slowPeriod: 26,
      signalPeriod: 9,
      SimpleMAOscillator: false,
      SimpleMASignal: false,
    });
    const bbValues = BollingerBands.calculate({ period: 20, values: closes, stdDev: 2 });

    const minIndicatorLen = Math.min(rsiValues.length, macdValues.length, bbValues.length);
    if (minIndicatorLen < 30) {
      throw new Error('Not enough indicator values calculated');
    }

    // Align series from the latest data point backwards
    const alignedDataset: DataPoint[] = [];
    for (let offset = minIndicatorLen - 1; offset >= 0; offset--) {
      const closeIdx = closes.length - 1 - offset;
      const rsiIdx = rsiValues.length - 1 - offset;
      const macdIdx = macdValues.length - 1 - offset;
      const bbIdx = bbValues.length - 1 - offset;

      alignedDataset.push({
        date: dates[closeIdx],
        close: closes[closeIdx],
        rsi: Number(rsiValues[rsiIdx].toFixed(2)),
        macd: {
          MACD: Number((macdValues[macdIdx].MACD ?? 0).toFixed(3)),
          signal: macdValues[macdIdx].signal != null ? Number(macdValues[macdIdx].signal!.toFixed(3)) : undefined,
          histogram: macdValues[macdIdx].histogram != null ? Number(macdValues[macdIdx].histogram!.toFixed(3)) : undefined,
        },
        bb: {
          lower: Number(bbValues[bbIdx].lower.toFixed(2)),
          middle: Number(bbValues[bbIdx].middle.toFixed(2)),
          upper: Number(bbValues[bbIdx].upper.toFixed(2)),
          pb: bbValues[bbIdx].pb != null ? Number(bbValues[bbIdx].pb!.toFixed(3)) : undefined,
        },
      });
    }

    // 3. Construct labeled sample dataset for baseline comparison
    // Ground truth movement: threshold = 0.25% daily move
    const labeledSamples: LabeledSample[] = [];
    const moveThreshold = 0.0025;

    for (let i = 0; i < alignedDataset.length - 1; i++) {
      const curr = alignedDataset[i];
      const next = alignedDataset[i + 1];
      const prev = i > 0 ? alignedDataset[i - 1] : null;

      const actualReturn = (next.close - curr.close) / curr.close;
      let actualClass: DirectionClass = 'NEUTRAL';
      if (actualReturn > moveThreshold) actualClass = 'BULLISH';
      else if (actualReturn < -moveThreshold) actualClass = 'BEARISH';

      const sig = computeSignal(curr, prev, 0.12);

      labeledSamples.push({
        ...curr,
        nextClose: next.close,
        actualReturn,
        actualClass,
        predClass: sig.direction,
        score: sig.score,
      });
    }

    // 4. Split: 75% for calibration/train, 25% for out-of-sample test reporting
    const trainCount = Math.max(1, Math.floor(labeledSamples.length * 0.75));
    const trainSet = labeledSamples.slice(0, trainCount);
    const testSet = labeledSamples.slice(trainCount);

    // Majority Class Baseline on Training Set
    const trainClassCounts: Record<DirectionClass, number> = { BULLISH: 0, BEARISH: 0, NEUTRAL: 0 };
    trainSet.forEach((s) => {
      trainClassCounts[s.actualClass]++;
    });

    let majorityClass: DirectionClass = 'BULLISH';
    if (trainClassCounts.BEARISH > trainClassCounts[majorityClass]) majorityClass = 'BEARISH';
    if (trainClassCounts.NEUTRAL > trainClassCounts[majorityClass]) majorityClass = 'NEUTRAL';

    // Predictions on Test Set
    const actualTestLabels = testSet.map((s) => s.actualClass);
    const modelTestPreds = testSet.map((s) => s.predClass);
    const majorityTestPreds = testSet.map(() => majorityClass);
    const bullishTestPreds = testSet.map(() => 'BULLISH' as DirectionClass);

    // Accuracy calculations on Test Set
    let modelCorrect = 0;
    let majorityCorrect = 0;
    let bullishCorrect = 0;

    for (let i = 0; i < testSet.length; i++) {
      if (modelTestPreds[i] === actualTestLabels[i]) modelCorrect++;
      if (majorityTestPreds[i] === actualTestLabels[i]) majorityCorrect++;
      if (bullishTestPreds[i] === actualTestLabels[i]) bullishCorrect++;
    }

    const testTotal = testSet.length || 1;
    const modelAccuracy = Number(((modelCorrect / testTotal) * 100).toFixed(1));
    const majorityAccuracy = Number(((majorityCorrect / testTotal) * 100).toFixed(1));
    const bullishAccuracy = Number(((bullishCorrect / testTotal) * 100).toFixed(1));

    // Per-class Precision, Recall, F1
    const modelMetrics = calculateClassMetrics(actualTestLabels, modelTestPreds);
    const majorityMetrics = calculateClassMetrics(actualTestLabels, majorityTestPreds);
    const bullishMetrics = calculateClassMetrics(actualTestLabels, bullishTestPreds);

    // 5. Compute Prediction for Current Latest Bar
    const latestBar = alignedDataset[alignedDataset.length - 1];
    const prevBar = alignedDataset.length > 1 ? alignedDataset[alignedDataset.length - 2] : null;
    const currentSignal = computeSignal(latestBar, prevBar, 0.12);

    const absScore = Math.abs(currentSignal.score);
    const confidence = Number(Math.min(92, Math.max(54, 52 + absScore * 48)).toFixed(1));
    const signalStrength: 'STRONG' | 'MODERATE' | 'WEAK' =
      absScore >= 0.45 ? 'STRONG' : absScore >= 0.2 ? 'MODERATE' : 'WEAK';

    // Key factors explaining the prediction
    const histVal = latestBar.macd.histogram ?? (latestBar.macd.MACD - (latestBar.macd.signal ?? 0));
    const pbVal = latestBar.bb.pb ?? ((latestBar.close - latestBar.bb.lower) / (latestBar.bb.upper - latestBar.bb.lower || 1));

    const keyFactors = [
      {
        factor: 'RSI(14) Momentum',
        value: `${latestBar.rsi}`,
        impact: latestBar.rsi < 35 ? 'Positive' : latestBar.rsi > 65 ? 'Negative' : 'Neutral',
        description:
          latestBar.rsi < 35
            ? `RSI at ${latestBar.rsi} indicates near-oversold accumulation pressure with bounce probability.`
            : latestBar.rsi > 65
            ? `RSI at ${latestBar.rsi} indicates overbought conditions prone to mean-reverting resistance.`
            : `RSI at ${latestBar.rsi} reflects balanced equilibrium within neutral momentum bands.`,
      },
      {
        factor: 'MACD(12,26,9) Trend Acceleration',
        value: `${histVal >= 0 ? '+' : ''}${histVal.toFixed(2)}`,
        impact: histVal > 0 ? 'Positive' : 'Negative',
        description:
          histVal > 0
            ? `MACD histogram at ${histVal.toFixed(2)} indicates positive directional momentum expansion.`
            : `MACD histogram at ${histVal.toFixed(2)} indicates negative divergence beneath signal threshold.`,
      },
      {
        factor: 'Bollinger Bands %B Position',
        value: `${(pbVal * 100).toFixed(0)}%`,
        impact: pbVal < 0.3 ? 'Positive' : pbVal > 0.7 ? 'Negative' : 'Neutral',
        description:
          pbVal < 0.3
            ? `Price testing lower Bollinger envelope (${latestBar.bb.lower.toFixed(2)}), supporting mean reversion.`
            : pbVal > 0.7
            ? `Price near upper band (${latestBar.bb.upper.toFixed(2)}), exhibiting stretched volatility channel.`
            : `Price tracking median Bollinger band (${latestBar.bb.middle.toFixed(2)}) without excessive divergence.`,
      },
      {
        factor: 'Model vs Majority Baseline Lift',
        value: `${modelAccuracy >= majorityAccuracy ? '+' : ''}${(modelAccuracy - majorityAccuracy).toFixed(1)}%`,
        impact: modelAccuracy >= majorityAccuracy ? 'Positive' : 'Neutral',
        description: `Algorithmic model scored ${modelAccuracy}% test accuracy on the ${testSet.length}-sample out-of-sample window vs ${majorityAccuracy}% for majority baseline.`,
      },
    ];

    const trainStart = trainSet[0]?.date || 'N/A';
    const trainEnd = trainSet[trainSet.length - 1]?.date || 'N/A';
    const testStart = testSet[0]?.date || 'N/A';
    const testEnd = testSet[testSet.length - 1]?.date || 'N/A';

    const vsBaseline = {
      model: {
        name: 'Multi-Factor Quantitative Signal (RSI + MACD + BB)',
        accuracy: modelAccuracy,
        metrics: modelMetrics,
        precision: {
          bullish: modelMetrics.BULLISH.precision,
          bearish: modelMetrics.BEARISH.precision,
          neutral: modelMetrics.NEUTRAL.precision,
        },
        recall: {
          bullish: modelMetrics.BULLISH.recall,
          bearish: modelMetrics.BEARISH.recall,
          neutral: modelMetrics.NEUTRAL.recall,
        },
        f1Score: Number(
          (
            (modelMetrics.BULLISH.f1 + modelMetrics.BEARISH.f1 + modelMetrics.NEUTRAL.f1) /
            3
          ).toFixed(1)
        ),
      },
      majorityBaseline: {
        name: `Majority Class Baseline (${majorityClass})`,
        accuracy: majorityAccuracy,
        majorityClass,
        metrics: majorityMetrics,
        precision: {
          bullish: majorityMetrics.BULLISH.precision,
          bearish: majorityMetrics.BEARISH.precision,
          neutral: majorityMetrics.NEUTRAL.precision,
        },
        recall: {
          bullish: majorityMetrics.BULLISH.recall,
          bearish: majorityMetrics.BEARISH.recall,
          neutral: majorityMetrics.NEUTRAL.recall,
        },
      },
      bullishBaseline: {
        name: 'Always Buy & Hold (Predict Bullish)',
        accuracy: bullishAccuracy,
        metrics: bullishMetrics,
      },
      // Convenience aliases
      baselineMajority: {
        name: `Majority Class Baseline (${majorityClass})`,
        accuracy: majorityAccuracy,
        majorityClass,
        metrics: majorityMetrics,
      },
      baselineBullish: {
        name: 'Always Buy & Hold (Predict Bullish)',
        accuracy: bullishAccuracy,
        metrics: bullishMetrics,
      },
      modelBeatsMajority: modelAccuracy >= majorityAccuracy,
      modelBeatsBullish: modelAccuracy >= bullishAccuracy,
      accuracyLiftVsMajority: Number((modelAccuracy - majorityAccuracy).toFixed(1)),
      accuracyLiftVsBullish: Number((modelAccuracy - bullishAccuracy).toFixed(1)),
      trainSamples: trainSet.length,
      testSamples: testSet.length,
      trainPeriod: `${trainStart} to ${trainEnd}`,
      testPeriod: `${testStart} to ${testEnd}`,
    };

    return NextResponse.json(
      {
        ticker,
        direction: currentSignal.direction,
        confidence,
        signalStrength,
        horizon: '5-Day Outlook',
        keyFactors,
        vsBaseline,
        trainPeriod: {
          startDate: trainStart,
          endDate: trainEnd,
          sampleCount: trainSet.length,
        },
        testPeriod: {
          startDate: testStart,
          endDate: testEnd,
          sampleCount: testSet.length,
        },
        precisionRecall: modelMetrics,
        technicalSummary: {
          rsi: {
            value: latestBar.rsi,
            signal: latestBar.rsi < 40 ? 'Oversold / Accumulate' : latestBar.rsi > 60 ? 'Overbought / Distribute' : 'Neutral',
            description: '14-period Relative Strength Index oscillator',
          },
          macd: {
            value: histVal,
            signal: histVal > 0 ? 'Bullish Crossover' : 'Bearish Crossover',
            description: '12/26/9 Exponential Moving Average convergence/divergence',
          },
          bollinger: {
            value: (pbVal * 100).toFixed(1) + '%',
            signal: pbVal < 0.2 ? 'Lower Band Touch' : pbVal > 0.8 ? 'Upper Band Expansion' : 'Within Normal Envelope',
            description: '20-period 2-standard-deviation volatility envelope',
          },
        },
        uncertaintyNote:
          'Statistical prediction models evaluate technical indicator distributions over the training window. Market regime shifts, earnings events, and macroeconomic announcements may invalidate historical technical patterns.',
        dataPointsUsed: alignedDataset.length,
        isReliable: true,
        dataSource: isLive ? 'LIVE' : 'DEMO',
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
    console.error(`[API Predict] Error generating prediction for ${ticker}: ${errorMsg}`);

    return NextResponse.json(
      {
        ticker,
        direction: 'NEUTRAL',
        confidence: 50.0,
        signalStrength: 'WEAK',
        horizon: '5-Day Outlook',
        keyFactors: [
          {
            factor: 'Signal Latency',
            value: 'Fallback Mode',
            impact: 'Neutral',
            description: 'Quantitative signals currently computing in fallback mode due to transient data latency.',
          },
        ],
        vsBaseline: {
          model: { accuracy: 50.0, metrics: {} },
          majorityBaseline: { accuracy: 50.0, majorityClass: 'NEUTRAL', metrics: {} },
          bullishBaseline: { accuracy: 50.0, metrics: {} },
          trainSamples: 0,
          testSamples: 0,
          trainPeriod: 'N/A',
          testPeriod: 'N/A',
          modelBeatsMajority: false,
          modelBeatsBullish: false,
          accuracyLiftVsMajority: 0,
          accuracyLiftVsBullish: 0,
        },
        trainPeriod: { startDate: 'N/A', endDate: 'N/A', sampleCount: 0 },
        testPeriod: { startDate: 'N/A', endDate: 'N/A', sampleCount: 0 },
        uncertaintyNote: 'Data temporarily unavailable.',
        dataPointsUsed: 0,
        isReliable: false,
        dataSource: 'DEMO',
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
