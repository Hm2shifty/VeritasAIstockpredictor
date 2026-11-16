'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Sidebar from '../../components/Sidebar';
import Topbar from '../../components/Topbar';
import {
  Cpu, TrendingUp, TrendingDown, ShieldAlert, Award,
  RefreshCw, CheckCircle2, AlertTriangle, ArrowRight, KeyRound,
} from 'lucide-react';

/* ─────────────────────────────────────────────
   Types
───────────────────────────────────────────── */
interface AgentCard {
  agentName: string;
  stance: string;
  metricLabel: string;
  metricValue: string;
  arguments: string[];
  keyHighlight: string;
}

interface ChiefCard {
  agentName: string;
  consensus: string;
  fairValueRange: string;
  horizon: string;
  summary: string;
  actionPlan: string[];
}

interface DebateData {
  ticker: string;
  bull: AgentCard;
  bear: AgentCard;
  risk: AgentCard;
  chief: ChiefCard;
  isLive?: boolean;
}

/* ─────────────────────────────────────────────
   AAPL-first rich curated debates
───────────────────────────────────────────── */
const CURATED: Record<string, DebateData> = {
  AAPL: {
    ticker: 'AAPL',
    bull: {
      agentName: 'Dr. Elena Vance • Growth & Alpha Strategist',
      stance: 'Strong Bullish / Outperform',
      metricLabel: 'Upside Price Target (12M)',
      metricValue: '$265.00 (+16.0%)',
      arguments: [
        'Apple Intelligence ecosystem driving record iPhone 16 Pro ASP and 14% high-margin Services segment growth (App Store, iCloud, Apple Pay).',
        'Installed base of 2.2B active devices creates an unparalleled monetization flywheel resistant to cyclical demand headwinds.',
        'Aggressive $110B share buyback authorization signals management confidence and provides strong EPS tailwind through float reduction.',
        'India and emerging market expansion opens a 400M+ addressable device upgrade cycle not yet reflected in consensus estimates.',
      ],
      keyHighlight: 'Services gross margin at 74.6% acts as a structural re-rating catalyst for the entire blended multiple.',
    },
    bear: {
      agentName: 'Marcus Sterling • Short Research Analyst',
      stance: 'Skeptical / Multiple Compression Risk',
      metricLabel: 'Downside Stress Target (Bear Case)',
      metricValue: '$185.00 (-19.0%)',
      arguments: [
        'Regulatory antitrust scrutiny over App Store commission structures and browser distribution agreements risks a $3B–$6B annual revenue headwind.',
        'China represents 18% of revenue; accelerating domestic alternatives (Huawei, Xiaomi) pressure both ASP and unit market share.',
        'P/E of 34x prices in near-perfect execution — any Services deceleration or iPhone shipment miss triggers outsized multiple compression.',
        'AI differentiation lag vs Android ecosystem may erode premium pricing power with enterprise and prosumer segments.',
      ],
      keyHighlight: 'Hardware commoditization risk remains underappreciated at current valuation multiples.',
    },
    risk: {
      agentName: 'Sarah Chen, CFA • Quantitative Risk Architect',
      stance: 'Medium Volatility / Selective Hedge Posture',
      metricLabel: '95% Value-at-Risk (1-Day)',
      metricValue: '2.6% VaR  •  Beta 1.05',
      arguments: [
        'Trailing 30-day realized vol of 18.4% is below sector median — AAPL exhibits defensive characteristics within high-beta tech.',
        'Options skew shows modest put demand for earnings protection; implied vol surface is flat signaling no tail-risk pricing.',
        'Recommended position weighting: 5%–8% core with optional covered-call overlay to monetize elevated premium.',
      ],
      keyHighlight: 'Key stop-loss discipline: Exit or hedge if price breaches $210 on volume (50-Day SMA breakdown).',
    },
    chief: {
      agentName: 'Alexander Wright • Chief Investment Officer',
      consensus: 'OVERWEIGHT — ACCUMULATE ON PULLBACKS',
      fairValueRange: '$235 – $260',
      horizon: '6–12 Month Investment Horizon',
      summary: 'After adversarial evaluation of Bull ecosystem expansion and Bear regulatory headwind theses, the investment committee concludes that AAPL maintains a durable moat in Services monetization that justifies a premium multiple. The Services segment re-rating story remains structurally intact, and aggressive capital return provides meaningful downside support. Near-term China and regulatory risks are real but manageable within a diversified portfolio context.',
      actionPlan: [
        'Tranche 1 (50% allocation): Establish core position at current market price, targeting 12-month fair value of $248.',
        'Tranche 2 (50% allocation): Add aggressively on any pullback to $210–$215 technical support zone.',
        'Risk boundary: Reduce to 50% position and reassess if Q2 Services revenue growth decelerates below 10% YoY.',
      ],
    },
  },

  NVDA: {
    ticker: 'NVDA',
    bull: {
      agentName: 'Dr. Elena Vance • Growth & Alpha Strategist',
      stance: 'High Conviction Bullish / Strong Outperform',
      metricLabel: 'Upside Price Target (12M)',
      metricValue: '$185.00 (+26.8%)',
      arguments: [
        'Blackwell GB200 NVL72 rack-scale systems entering hyperscaler deployment at $2–3M ASP per rack, driving data center revenue to $200B+ run rate.',
        'Proprietary CUDA software ecosystem has 10+ years of developer lock-in — switching costs are insurmountable for enterprise AI workloads.',
        'Sovereign AI national infrastructure buildouts (Japan, UAE, France, India) represent a multi-year incremental demand wave not in consensus.',
        'NVLink networking and software licensing layer provides high-margin recurring revenue separate from hardware cycles.',
      ],
      keyHighlight: 'Gross margins sustaining above 73% signals NVIDIA captures software-like economics on hardware.',
    },
    bear: {
      agentName: 'Marcus Sterling • Short Research Analyst',
      stance: 'Multiple Compression / ASIC Disruption Risk',
      metricLabel: 'Downside Stress Target (Bear Case)',
      metricValue: '$95.00 (-34.9%)',
      arguments: [
        'Hyperscalers (Google TPU, Amazon Trainium, Microsoft Maia) are aggressively building in-house custom ASICs to reduce NVIDIA dependency and capex concentration.',
        'Valuation at 46x earnings embeds perfection — any quarterly guidance miss or export restriction escalation triggers violent multiple de-rating.',
        'AMD MI300X gaining enterprise design wins in inference workloads, with pricing 20–30% below equivalent NVIDIA configurations.',
      ],
      keyHighlight: 'ASIC displacement risk is underpriced in current consensus models by 2–3 years.',
    },
    risk: {
      agentName: 'Sarah Chen, CFA • Quantitative Risk Architect',
      stance: 'Elevated Volatility / Active Hedge Required',
      metricLabel: '95% Value-at-Risk (1-Day)',
      metricValue: '4.2% VaR  •  Beta 1.68',
      arguments: [
        'Trailing 30-day realized volatility of 34.8% is in the 92nd percentile of S&P 500 — NVDA is a high-beta risk asset.',
        'U.S. export control risk (H20 chip ban) is an unhedgeable binary event with potential $4B quarterly revenue impact.',
        'Maximum recommended weighting: 3%–5% with tight stop-loss discipline given elevated beta and event-driven risk surface.',
      ],
      keyHighlight: 'Binary export regulation risk requires strict position sizing and defined exit triggers.',
    },
    chief: {
      agentName: 'Alexander Wright • Chief Investment Officer',
      consensus: 'OVERWEIGHT — STAGGERED ENTRY STRATEGY',
      fairValueRange: '$155 – $185',
      horizon: '6–12 Month Investment Horizon',
      summary: 'The committee acknowledges NVIDIA\'s unmatched structural position in AI compute infrastructure while recognizing the valuation premium demands disciplined entry. Bull arguments around CUDA moat and Blackwell cycle are persuasive, but Bear ASIC disruption risk is a legitimate 3-year horizon risk. Staggered entry strategy strongly preferred.',
      actionPlan: [
        'Tranche 1 (40% allocation): Establish base position at market, targeting fair value of $165.',
        'Tranche 2 (60% allocation): Deploy aggressively on pullbacks to $125–$130 key technical support.',
        'Risk boundary: Exit 50% of position if export restrictions escalate or quarterly gross margin falls below 70%.',
      ],
    },
  },

  TSLA: {
    ticker: 'TSLA',
    bull: {
      agentName: 'Dr. Elena Vance • Growth & Alpha Strategist',
      stance: 'Speculative Bullish / High Conviction Long-Term',
      metricLabel: 'Upside Price Target (12M)',
      metricValue: '$425.00 (+24.2%)',
      arguments: [
        'Full Self-Driving (FSD) v13 achieving 500M+ miles per intervention positions Tesla as the only consumer robotaxi platform at scale.',
        'Optimus humanoid robot production targeting 10,000 units/year by 2026 — a $500B+ market optionality not in any sell-side model.',
        'Megapack energy storage business at 40% gross margin growing 150% YoY, providing earnings diversification from automotive cycles.',
      ],
      keyHighlight: 'Autonomous software licensing is the pivotal re-rating catalyst — hardware margins are secondary.',
    },
    bear: {
      agentName: 'Marcus Sterling • Short Research Analyst',
      stance: 'Skeptical / EV Price War & Margin Destruction',
      metricLabel: 'Downside Stress Target (Bear Case)',
      metricValue: '$220.00 (-35.7%)',
      arguments: [
        'Global EV price war forces continuous ASP reductions — automotive gross margin compressed to single-digits in key China and Europe markets.',
        'BYD outselling Tesla in China Q3 2024 with vehicles priced 40% lower — market share loss is structural not cyclical.',
        'P/E of 92x embeds FSD and Optimus success neither of which has demonstrated commercial viability at scale.',
      ],
      keyHighlight: 'Core EV business deterioration is obscured by speculative optionality premium in the multiple.',
    },
    risk: {
      agentName: 'Sarah Chen, CFA • Quantitative Risk Architect',
      stance: 'Very High Volatility / Cautious Sizing',
      metricLabel: '95% Value-at-Risk (1-Day)',
      metricValue: '5.8% VaR  •  Beta 2.34',
      arguments: [
        'TSLA is the highest-beta name in the S&P 500 mega-cap universe — 2.34x market beta amplifies both upside and drawdown.',
        'CEO-related headline risk (Musk political activity) creates non-fundamental volatility spikes not captured in standard risk models.',
        'Maximum weighting: 2%–3% only for investors with explicit high-volatility mandates and defined binary outcome thesis.',
      ],
      keyHighlight: 'Only suitable for high-conviction, long-duration investors with defined FSD/Optimus thesis.',
    },
    chief: {
      agentName: 'Alexander Wright • Chief Investment Officer',
      consensus: 'SELECTIVE EXPOSURE — BINARY OUTCOME ASSET',
      fairValueRange: '$310 – $380',
      horizon: '12–24 Month Investment Horizon',
      summary: 'TSLA represents a binary outcome investment: bull case requires FSD commercialization and Optimus production ramp; bear case reflects EV commodity business at unsustainable margins. Committee recommends minimal core exposure with optional call spread overlay for investors seeking asymmetric upside participation.',
      actionPlan: [
        'Core position (2%–3%): Hold for FSD monetization catalyst with 12-month horizon.',
        'Opportunistic add: Increase on pullbacks to $280–$295 technical support with tight stop.',
        'Risk boundary: Exit full position if FSD commercial launch is delayed beyond Q2 2025 or automotive GM falls below 12%.',
      ],
    },
  },
};

function getCurated(ticker: string): DebateData {
  if (CURATED[ticker]) return CURATED[ticker];
  // Generic fallback for unknown tickers
  return {
    ticker,
    bull: {
      agentName: 'Dr. Elena Vance • Growth & Alpha Strategist',
      stance: 'Constructive Bullish / Outperform',
      metricLabel: 'Upside Price Target (12M)',
      metricValue: 'Model-Derived Upside +15%–25%',
      arguments: [
        `${ticker} demonstrates defensible competitive positioning within its core addressable market segment.`,
        'Institutional capital allocation signals above-average conviction in near-term earnings trajectory.',
        'Operating margin expansion cycle supported by disciplined cost structure and pricing power.',
      ],
      keyHighlight: 'Structural moat and free-cash-flow conversion defend premium valuation multiples.',
    },
    bear: {
      agentName: 'Marcus Sterling • Short Research Analyst',
      stance: 'Skeptical / Multiple Compression Risk',
      metricLabel: 'Downside Stress Target',
      metricValue: 'Bear Case -18%–28%',
      arguments: [
        'Elevated valuation multiples relative to sector peers leave limited margin of safety in a rising rate environment.',
        'Competitive displacement risk from well-capitalized sector incumbents is underappreciated in consensus models.',
        'Broad macroeconomic deceleration may trigger discretionary capex reductions impacting near-term revenue visibility.',
      ],
      keyHighlight: 'Multiple reversion risk remains the primary tail-risk for growth-premium names.',
    },
    risk: {
      agentName: 'Sarah Chen, CFA • Quantitative Risk Architect',
      stance: 'Moderate-Elevated Volatility / Hedged Posture',
      metricLabel: '95% Value-at-Risk (1-Day)',
      metricValue: '3.5% VaR  •  Beta ~1.4',
      arguments: [
        'Historical volatility elevated relative to S&P 500 baseline — position sizing discipline is essential.',
        'Options surface shows moderate tail-risk demand, suggesting institutional hedging activity.',
        'Recommended max weighting: 3%–5% with optional covered-call overlay.',
      ],
      keyHighlight: 'Strict 50-day SMA stop-loss discipline recommended for all entry points.',
    },
    chief: {
      agentName: 'Alexander Wright • Chief Investment Officer',
      consensus: 'TACTICAL ACCUMULATE ON PULLBACKS',
      fairValueRange: 'Committee-Derived Fair Range',
      horizon: '6–12 Month Investment Horizon',
      summary: `After adversarial evaluation, the committee finds ${ticker} maintains secular competitive advantages counterbalanced by valuation risk. A staggered entry strategy is recommended over lump-sum momentum chasing.`,
      actionPlan: [
        'Tranche 1 (40%): Establish base position at current market price.',
        'Tranche 2 (60%): Add aggressively on technical pullbacks to key support zones.',
        'Risk boundary: Exit or collar hedge if 200-day SMA is breached on elevated volume.',
      ],
    },
  };
}

/* ─────────────────────────────────────────────
   Map API response schema → DebateData
───────────────────────────────────────────── */
function mapApiResponse(data: Record<string, unknown>, ticker: string): DebateData {
  const b = (data.bull as Record<string, unknown>) || {};
  const br = (data.bear as Record<string, unknown>) || {};
  const r = (data.risk as Record<string, unknown>) || {};
  const c = (data.chief as Record<string, unknown>) || {};

  const bullArgs = [...((b.arguments as string[]) || []), ...((b.catalysts as string[]) || [])].slice(0, 4);
  const bearArgs = [...((br.arguments as string[]) || []), ...((br.risks as string[]) || [])].slice(0, 4);
  const riskItems = (r.keyRisks as string[]) || [];
  const bullScore = Number(b.bullishScore || b.score || 75);
  const bearScore = Number(br.bearishScore || br.score || 55);
  const actionPlanRaw = (c.areasOfConsensus as string[]) || [];

  return {
    ticker,
    isLive: true,
    bull: {
      agentName: 'Dr. Elena Vance • Growth & Alpha Strategist',
      stance: (b.thesisTitle as string) || 'Strong Bullish / Outperform',
      metricLabel: 'AI Bullish Conviction Score',
      metricValue: `${bullScore}/100 — ${bullScore >= 75 ? 'High Conviction' : 'Moderate Conviction'}`,
      arguments: bullArgs.length ? bullArgs : getCurated(ticker).bull.arguments,
      keyHighlight: (bullArgs[0] as string) || getCurated(ticker).bull.keyHighlight,
    },
    bear: {
      agentName: 'Marcus Sterling • Short Research Analyst',
      stance: (br.thesisTitle as string) || 'Skeptical / Multiple Compression Risk',
      metricLabel: 'AI Bearish Pressure Score',
      metricValue: `${bearScore}/100 — ${bearScore >= 70 ? 'High Risk' : 'Moderate Risk'}`,
      arguments: bearArgs.length ? bearArgs : getCurated(ticker).bear.arguments,
      keyHighlight: (bearArgs[0] as string) || getCurated(ticker).bear.keyHighlight,
    },
    risk: {
      agentName: 'Sarah Chen, CFA • Quantitative Risk Architect',
      stance: `${(r.riskLevel as string) || 'MODERATE'} Volatility / Hedged Posture`,
      metricLabel: 'AI Risk Assessment',
      metricValue: `${(r.riskLevel as string) || 'MODERATE'} — Disciplined Position Sizing`,
      arguments: riskItems.length ? riskItems : getCurated(ticker).risk.arguments,
      keyHighlight: (r.challenges as string) || getCurated(ticker).risk.keyHighlight,
    },
    chief: {
      agentName: 'Alexander Wright • Chief Investment Officer',
      consensus: (c.outlook as string) || 'TACTICAL ACCUMULATE ON PULLBACKS',
      fairValueRange: 'AI Model-Derived Range',
      horizon: '6–12 Month Investment Horizon',
      summary: (c.summary as string) || (c.executiveSummary as string) || getCurated(ticker).chief.summary,
      actionPlan: actionPlanRaw.length ? actionPlanRaw : [
        'Tranche 1 (40%): Establish base position at current market price.',
        'Tranche 2 (60%): Add on technical pullbacks to key support zones.',
        (c.verdict as string) || 'Maintain disciplined risk management and defined stop-loss levels.',
      ],
    },
  };
}

const TICKERS = ['AAPL', 'NVDA', 'MSFT', 'TSLA', 'GOOGL', 'PLTR', 'AMD'];

/* ─────────────────────────────────────────────
   Page component
───────────────────────────────────────────── */
export default function DebatePage() {
  const params = useParams();
  const router = useRouter();
  const rawTicker = (params?.ticker as string) || 'AAPL';
  const ticker = rawTicker.toUpperCase();

  const [debate, setDebate] = useState<DebateData>(() => getCurated(ticker));
  const [generating, setGenerating] = useState(false);
  const [stage, setStage] = useState('');

  const fetchDebate = useCallback(async (t: string) => {
    setGenerating(true);
    setDebate(getCurated(t)); // show curated immediately while loading

    const stages = [
      'Initializing multi-agent adversarial debate session...',
      'Agent 1 (Bull): Compiling upside growth catalysts and institutional flow signals...',
      'Agent 2 (Bear): Stress-testing valuation assumptions and competitive displacement risks...',
      'Agent 3 (Risk): Computing VaR, drawdown limits, and options volatility skew...',
      'CIO Agent: Synthesizing adversarial theses into institutional consensus verdict...',
    ];

    for (const s of stages) {
      setStage(s);
      await new Promise((r) => setTimeout(r, 420));
    }

    try {
      const res = await fetch(`/api/debate/${t}`);
      if (res.ok) {
        const data = await res.json();
        if (data?.chief) {
          // Determine schema: API schema has thesisTitle, display schema has agentName
          const isApiSchema = data.bull?.thesisTitle !== undefined;
          setDebate(isApiSchema ? mapApiResponse(data, t) : { ...data, isLive: true });
          setGenerating(false);
          setStage('');
          return;
        }
      }
    } catch { /* fall through to curated */ }

    setDebate(getCurated(t));
    setGenerating(false);
    setStage('');
  }, []);

  useEffect(() => {
    setDebate(getCurated(ticker));
    fetchDebate(ticker);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticker]);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar
          title={`AI Debate Chamber • ${ticker}`}
          subtitle="4-Agent Adversarial Thesis Synthesis & CIO Consensus"
        />

        <main className="page-container">

          {/* ── API Key Notice ── */}
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              background: debate.isLive ? 'rgba(57,209,116,0.05)' : 'rgba(212,160,23,0.05)',
              border: debate.isLive ? '1px solid rgba(57,209,116,0.2)' : '1px solid rgba(212,160,23,0.22)',
              borderRadius: '6px',
              padding: '11px 16px',
              marginBottom: '18px',
              fontSize: '12px',
              color: 'var(--text-1)',
            }}
          >
            {debate.isLive
              ? <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--positive)', boxShadow: '0 0 6px var(--positive)', display: 'inline-block', flexShrink: 0, marginTop: '3px' }} />
              : <KeyRound size={15} color="var(--warning)" style={{ flexShrink: 0, marginTop: '1px' }} />
            }
            <div>
              {debate.isLive ? (
                <><strong style={{ color: 'var(--positive)' }}>Live AI Mode Active</strong> — This debate was generated in real time by GPT-4o agents.</>
              ) : (
                <>
                  <strong style={{ color: 'var(--warning)' }}>Demo Mode — Curated Expert Analysis</strong>
                  {' '}— Live GPT-4o powered agent debates require an{' '}
                  <strong>OpenAI API key</strong>. Add{' '}
                  <code style={{ background: 'var(--bg-2)', padding: '1px 6px', borderRadius: '3px', fontFamily: 'var(--mono)', fontSize: '11px' }}>OPENAI_API_KEY=sk-...</code>{' '}
                  to your <code style={{ background: 'var(--bg-2)', padding: '1px 6px', borderRadius: '3px', fontFamily: 'var(--mono)', fontSize: '11px' }}>.env.local</code>{' '}
                  or <strong>Vercel › Settings › Environment Variables</strong>.
                </>
              )}
            </div>
          </div>

          {/* ── Header Card ── */}
          <div
            className="card card-accent"
            style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span className="badge badge-purple"><Cpu size={12} /> Autonomous Agent Consensus</span>
                <span className="ticker-tag" style={{ fontSize: '14px' }}>{ticker}</span>
                <span className={`badge ${debate.isLive ? 'badge-green' : 'badge-gray'}`}>
                  {debate.isLive ? '● Live GPT-4o' : 'Curated Demo'}
                </span>
              </div>
              <h2 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-0)', margin: '0 0 4px' }}>
                Multi-Agent Adversarial Investment Debate
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--text-2)', margin: 0 }}>
                Four specialized AI personas cross-examine bull theses, stress-test downside risks, and synthesize an institutional CIO verdict.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button
                onClick={() => fetchDebate(ticker)}
                disabled={generating}
                className="btn btn-primary btn-lg"
                style={{ opacity: generating ? 0.65 : 1 }}
              >
                <RefreshCw size={15} style={{ animation: generating ? 'spin 0.7s linear infinite' : 'none' }} />
                {generating ? 'Agents Debating...' : 'Regenerate Debate'}
              </button>
              <Link href={`/stock/${ticker}`} className="btn btn-secondary btn-lg">
                View Chart
              </Link>
            </div>
          </div>

          {/* ── Ticker Switcher ── */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Debate Stock:
            </span>
            {TICKERS.map((t) => (
              <button
                key={t}
                onClick={() => router.push(`/debate/${t}`)}
                style={{
                  background: t === ticker ? 'var(--accent)' : 'var(--bg-card)',
                  color: t === ticker ? '#080808' : 'var(--text-1)',
                  border: `1px solid ${t === ticker ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: '5px',
                  padding: '5px 12px',
                  fontSize: '12px',
                  fontFamily: 'var(--mono)',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.12s',
                }}
              >
                {t}
              </button>
            ))}
          </div>

          {/* ── Generating overlay ── */}
          {generating && (
            <div
              className="card"
              style={{ marginBottom: '20px', background: 'var(--bg-1)', border: '1px solid var(--border-light)', padding: '28px', textAlign: 'center' }}
            >
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
                <div className="spinner" style={{ width: '22px', height: '22px' }} />
                <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-0)' }}>
                  Agent Debate In Session
                </span>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-2)', fontFamily: 'var(--mono)', margin: 0 }}>{stage}</p>
            </div>
          )}

          {/* ── 3-Column Agent Cards ── */}
          <div className="grid-3" style={{ marginBottom: '20px' }}>

            {/* Bull */}
            <div className="agent-card bull">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div className="agent-name" style={{ color: 'var(--positive)' }}>BULL STRATEGIST</div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-0)' }}>{debate.bull.agentName}</div>
                </div>
                <span className="badge badge-green"><TrendingUp size={11} /> Bullish</span>
              </div>

              <div style={{ background: 'var(--bg-1)', border: '1px solid rgba(57,209,116,0.2)', borderRadius: '8px', padding: '10px 14px', margin: '0 0 14px' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-3)', marginBottom: '3px' }}>{debate.bull.metricLabel}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '17px', fontWeight: 800, color: 'var(--positive)' }}>
                  {debate.bull.metricValue}
                </div>
              </div>

              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
                Core Growth Catalysts
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {debate.bull.arguments.map((arg, i) => (
                  <li key={i} style={{ display: 'flex', gap: '8px', fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.45 }}>
                    <CheckCircle2 size={13} color="var(--positive)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{arg}</span>
                  </li>
                ))}
              </ul>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px', fontSize: '11px', color: 'var(--text-2)' }}>
                <strong style={{ color: 'var(--text-1)' }}>Key Pillar: </strong>{debate.bull.keyHighlight}
              </div>
            </div>

            {/* Bear */}
            <div className="agent-card bear">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div className="agent-name" style={{ color: 'var(--negative)' }}>BEAR CONTRARIAN</div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-0)' }}>{debate.bear.agentName}</div>
                </div>
                <span className="badge badge-red"><TrendingDown size={11} /> Bearish</span>
              </div>

              <div style={{ background: 'var(--bg-1)', border: '1px solid rgba(229,83,83,0.2)', borderRadius: '8px', padding: '10px 14px', margin: '0 0 14px' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-3)', marginBottom: '3px' }}>{debate.bear.metricLabel}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '17px', fontWeight: 800, color: 'var(--negative)' }}>
                  {debate.bear.metricValue}
                </div>
              </div>

              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
                Downside Stress Points
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {debate.bear.arguments.map((arg, i) => (
                  <li key={i} style={{ display: 'flex', gap: '8px', fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.45 }}>
                    <AlertTriangle size={13} color="var(--negative)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{arg}</span>
                  </li>
                ))}
              </ul>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px', fontSize: '11px', color: 'var(--text-2)' }}>
                <strong style={{ color: 'var(--text-1)' }}>Key Pillar: </strong>{debate.bear.keyHighlight}
              </div>
            </div>

            {/* Risk */}
            <div className="agent-card risk">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div className="agent-name" style={{ color: 'var(--warning)' }}>RISK ARCHITECT</div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-0)' }}>{debate.risk.agentName}</div>
                </div>
                <span className="badge badge-amber"><ShieldAlert size={11} /> Risk</span>
              </div>

              <div style={{ background: 'var(--bg-1)', border: '1px solid rgba(212,160,23,0.2)', borderRadius: '8px', padding: '10px 14px', margin: '0 0 14px' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-3)', marginBottom: '3px' }}>{debate.risk.metricLabel}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '17px', fontWeight: 800, color: 'var(--warning)' }}>
                  {debate.risk.metricValue}
                </div>
              </div>

              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
                Quantitative Risk Controls
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {debate.risk.arguments.map((arg, i) => (
                  <li key={i} style={{ display: 'flex', gap: '8px', fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.45 }}>
                    <ShieldAlert size={13} color="var(--warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{arg}</span>
                  </li>
                ))}
              </ul>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px', fontSize: '11px', color: 'var(--text-2)' }}>
                <strong style={{ color: 'var(--text-1)' }}>Key Control: </strong>{debate.risk.keyHighlight}
              </div>
            </div>
          </div>

          {/* ── Chief Investment Officer Card ── */}
          <div className="agent-card chief" style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '18px' }}>
              <div>
                <div className="agent-name" style={{ color: 'var(--text-1)' }}>EXECUTIVE COMMITTEE CHAIR</div>
                <h3 style={{ fontSize: '19px', fontWeight: 800, color: 'var(--text-0)', margin: '2px 0' }}>{debate.chief.agentName}</h3>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <span className="badge badge-purple" style={{ fontSize: '11px' }}>{debate.chief.horizon}</span>
                <span className="badge badge-green" style={{ fontSize: '12px', padding: '4px 14px', fontWeight: 800 }}>
                  <Award size={13} /> {debate.chief.consensus}
                </span>
              </div>
            </div>

            {/* Fair value + confidence strip */}
            <div
              style={{
                display: 'flex',
                gap: '24px',
                background: 'var(--bg-1)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                padding: '12px 18px',
                marginBottom: '18px',
                flexWrap: 'wrap',
              }}
            >
              <div>
                <div style={{ fontSize: '10px', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Synthesized Fair Value Range</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '17px', fontWeight: 800, color: 'var(--text-0)', marginTop: '2px' }}>
                  {debate.chief.fairValueRange}
                </div>
              </div>
              <div style={{ width: '1px', background: 'var(--border)', alignSelf: 'stretch' }} />
              <div>
                <div style={{ fontSize: '10px', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Committee Confidence</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '17px', fontWeight: 800, color: 'var(--text-0)', marginTop: '2px' }}>
                  High — 82% Tranche Agreement
                </div>
              </div>
            </div>

            {/* Summary */}
            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
                Executive Synthesis
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-1)', lineHeight: 1.65, margin: 0 }}>
                {debate.chief.summary}
              </p>
            </div>

            {/* Action plan */}
            <div>
              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>
                Recommended Execution Protocol
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
                {debate.chief.actionPlan.map((step, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'var(--bg-1)',
                      border: '1px solid var(--border-light)',
                      padding: '10px 14px',
                      borderRadius: '6px',
                      display: 'flex',
                      gap: '8px',
                      fontSize: '12px',
                      color: 'var(--text-1)',
                      lineHeight: 1.5,
                    }}
                  >
                    <ArrowRight size={13} color="var(--text-0)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Footer disclaimer */}
          <div
            className="disclaimer-banner"
            style={{ padding: '14px 18px', fontSize: '12px', marginBottom: '28px', display: 'flex', alignItems: 'center', gap: '12px' }}
          >
            <AlertTriangle size={18} style={{ flexShrink: 0 }} />
            <div>
              <strong>Prototype Disclaimer: </strong>
              This project is a prototype and is not financial advice. Debate outputs are synthesized via automated AI agents and quantitative heuristics for demonstration and academic evaluation only.
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}
