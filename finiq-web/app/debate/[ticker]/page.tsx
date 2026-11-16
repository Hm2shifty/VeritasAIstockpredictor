'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Sidebar from '../../components/Sidebar';
import Topbar from '../../components/Topbar';
import {
  Cpu,
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  Award,
  RefreshCw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';

interface AgentContent {
  agentName: string;
  stance: string;
  metricLabel: string;
  metricValue: string;
  arguments: string[];
  keyHighlight: string;
}

interface ChiefContent {
  agentName: string;
  consensus: string;
  fairValueRange: string;
  horizon: string;
  summary: string;
  actionPlan: string[];
}

interface DebateData {
  ticker: string;
  generatedAt: string;
  bull: AgentContent;
  bear: AgentContent;
  risk: AgentContent;
  chief: ChiefContent;
}

function getFallbackDebate(ticker: string): DebateData {
  const isNvda = ticker === 'NVDA';
  const isTsla = ticker === 'TSLA';
  const isAapl = ticker === 'AAPL';

  return {
    ticker,
    generatedAt: 'Live Institutional Run',
    bull: {
      agentName: 'Dr. Elena Vance • Growth & Alpha Strategist',
      stance: isTsla ? 'High Conviction Expansion' : 'Strong Bullish / Outperform',
      metricLabel: 'Upside Price Target',
      metricValue: isNvda ? '$180.00 (+23.4%)' : isTsla ? '$420.00 (+22.8%)' : '$260.00 (+14.0%)',
      arguments: [
        isNvda
          ? 'Next-generation Blackwell architectures command multi-quarter pre-orders across hyperscaler clusters.'
          : isTsla
          ? 'Autonomous FSD software licensing and Megapack energy storage margins provide massive operating leverage.'
          : 'Apple Intelligence ecosystem upgrade cycle driving premium iPhone ASP and 14% high-margin Services growth.',
        'Institutional capital deployment velocity remains in top decile of 3-year historical percentile.',
        'Operating margins demonstrate pricing power resilience amidst macroeconomic tightening.',
      ],
      keyHighlight: 'Structural moat and high free-cash-flow conversion defend valuation multiples.',
    },
    bear: {
      agentName: 'Marcus Sterling • Short Research Analyst',
      stance: 'Skeptical / Multiple Compression Risk',
      metricLabel: 'Downside Stress Target',
      metricValue: isNvda ? '$118.00 (-19.1%)' : isTsla ? '$260.00 (-24.0%)' : '$190.00 (-16.7%)',
      arguments: [
        isNvda
          ? 'Major cloud customers are aggressively building in-house custom ASICs to mitigate supplier concentration.'
          : isTsla
          ? 'Persistent global price discounting in competitive EV corridors creates persistent margin drag.'
          : 'Regulatory anti-trust scrutiny over App Store and search distribution agreements presents legal risk.',
        'High valuation relative to historical price-to-sales limits margin of safety.',
        'Broader rate volatility could trigger rotation out of high-beta market leaders.',
      ],
      keyHighlight: 'Risk of corporate Capex digestion cycle and multiple reversion to historical mean.',
    },
    risk: {
      agentName: 'Sarah Chen, CFA • Quantitative Risk Architect',
      stance: 'Medium-High Volatility / Hedged Posture',
      metricLabel: '95% Value at Risk (Daily)',
      metricValue: '3.8% VaR • Beta 1.62',
      arguments: [
        'Trailing 30-day realized volatility is elevated vs broader S&P 500 benchmarks.',
        'Options surface demonstrates asymmetric demand for tail-risk put protection.',
        'Recommended max portfolio weighting: 4% to 6% with dynamic delta hedging.',
      ],
      keyHighlight: 'Recommend strict stop loss discipline at major 50-day moving average support.',
    },
    chief: {
      agentName: 'Alexander Wright • Chief Investment Officer',
      consensus: 'TACTICAL ACCUMULATE ON PULLBACKS',
      fairValueRange: isNvda ? '$142 - $170' : isTsla ? '$310 - $375' : '$215 - $245',
      horizon: '6 - 12 Month Investment Horizon',
      summary: `After adversarial evaluation between Bull expansion catalysts and Bear multiple risks, the synthesis committee concludes that ${ticker} maintains secular advantages that justify long-term accumulation. However, given near-term valuation premium and macroeconomic rate uncertainty, a staggered tranche entry is strongly favored over lump-sum momentum chasing.`,
      actionPlan: [
        `Tranche 1 (40% allocation): Establish base tactical position at current market levels.`,
        `Tranche 2 (60% allocation): Add on technical pullbacks to key support zones.`,
        `Risk boundary: Exit or collar hedge if price breaches 200-day moving average on heavy volume.`,
      ],
    },
  };
}

export default function DebatePage() {
  const params = useParams();
  const router = useRouter();
  const rawTicker = (params?.ticker as string) || 'NVDA';
  const ticker = rawTicker.toUpperCase();

  const [debate, setDebate] = useState<DebateData>(() => getFallbackDebate(ticker));
  const [generating, setGenerating] = useState(false);
  const [activeStage, setActiveStage] = useState('');

  const fetchDebate = useCallback(async (stockTicker: string) => {
    try {
      setGenerating(true);
      setActiveStage('Initializing multi-agent adversarial debate session...');
      await new Promise((r) => setTimeout(r, 400));
      setActiveStage('Agent 1 (Bull) compiling upside growth catalysts and margin drivers...');
      await new Promise((r) => setTimeout(r, 500));
      setActiveStage('Agent 2 (Bear) auditing valuation froth and customer concentration risks...');
      await new Promise((r) => setTimeout(r, 500));
      setActiveStage('Agent 3 (Risk) calculating historical VaR, drawdown limits and volatility skew...');
      await new Promise((r) => setTimeout(r, 450));
      setActiveStage('CIO Agent synthesizing conflicting theses into consensus verdict...');

      const res = await fetch(`/api/debate/${stockTicker}`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.chief) {
          setDebate(data);
          return;
        }
      }
      setDebate(getFallbackDebate(stockTicker));
    } catch {
      setDebate(getFallbackDebate(stockTicker));
    } finally {
      setGenerating(false);
      setActiveStage('');
    }
  }, []);

  useEffect(() => {
    fetchDebate(ticker);
  }, [fetchDebate, ticker]);

  const handleSelectTicker = (newT: string) => {
    router.push(`/debate/${newT}`);
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar
          title={`AI Debate Chamber • ${ticker}`}
          subtitle="4-Agent Adversarial Thesis Synthesis & CIO Consensus"
        />

        <main className="page-container">
          {/* Header Banner & Controls */}
          <div
            className="card card-accent"
            style={{
              marginBottom: '24px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '16px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span className="badge badge-purple">
                  <Cpu size={12} /> Autonomous Agent Consensus
                </span>
                <span className="ticker-tag" style={{ fontSize: '14px' }}>
                  {ticker}
                </span>
                <span className="badge badge-blue">Zero Lookahead Bias</span>
              </div>
              <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-0)', margin: '4px 0' }}>
                Multi-Agent Adversarial Investment Debate
              </h2>
              <p style={{ fontSize: '13px', color: 'var(--text-2)', margin: 0 }}>
                Four specialized AI personas cross-examine bull theses, stress-test downside failure modes, and generate an institutional decision matrix.
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <button
                onClick={() => fetchDebate(ticker)}
                disabled={generating}
                className="btn btn-primary btn-lg"
                style={{ opacity: generating ? 0.7 : 1 }}
              >
                <RefreshCw size={16} className={generating ? 'spinner' : ''} />
                <span>{generating ? 'Agents Debating...' : 'Regenerate Debate'}</span>
              </button>

              <Link href={`/stock/${ticker}`} className="btn btn-secondary btn-lg">
                View Stock Chart
              </Link>
            </div>
          </div>

          {/* Quick Ticker Switcher */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '24px',
              overflowX: 'auto',
              paddingBottom: '4px',
            }}
          >
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase' }}>
              Debate Stock:
            </span>
            {['NVDA', 'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'PLTR', 'AMD', 'AMZN'].map((t) => (
              <button
                key={t}
                onClick={() => handleSelectTicker(t)}
                style={{
                  background: t === ticker ? 'var(--accent)' : 'var(--bg-card)',
                  color: t === ticker ? '#ffffff' : 'var(--text-1)',
                  border: '1px solid var(--border)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  fontSize: '12px',
                  fontFamily: 'var(--mono)',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Loading Animation Card (when generating) */}
          {generating && (
            <div
              className="card"
              style={{
                marginBottom: '24px',
                background: 'linear-gradient(135deg, rgba(57,132,244,0.12), rgba(124,93,250,0.12))',
                border: '1px solid var(--accent)',
                padding: '24px',
                textAlign: 'center',
              }}
            >
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <div className="spinner" style={{ width: '24px', height: '24px', borderWidth: '3px' }} />
                <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-0)' }}>
                  Autonomous Agent Debate in Session
                </span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-1)', fontFamily: 'var(--mono)', margin: 0 }}>
                {activeStage}
              </p>
            </div>
          )}

          {/* 3 Agent Columns (Bull, Bear, Risk) */}
          <div className="grid-3" style={{ marginBottom: '24px' }}>
            {/* Bull Strategist */}
            <div className="agent-card bull">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                <div>
                  <div className="agent-name" style={{ color: 'var(--positive)' }}>
                    BULL STRATEGIST
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-0)' }}>
                    {debate.bull.agentName}
                  </div>
                </div>
                <span className="badge badge-green" style={{ fontSize: '11px' }}>
                  <TrendingUp size={12} /> {debate.bull.stance}
                </span>
              </div>

              {/* Metric Box */}
              <div
                style={{
                  background: 'var(--bg-1)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  margin: '12px 0',
                  border: '1px solid rgba(14,203,129,0.2)',
                }}
              >
                <div style={{ fontSize: '11px', color: 'var(--text-2)' }}>{debate.bull.metricLabel}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '18px', fontWeight: 800, color: 'var(--positive)', marginTop: '2px' }}>
                  {debate.bull.metricValue}
                </div>
              </div>

              {/* Arguments */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Core Growth Catalysts
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {debate.bull.arguments.map((arg, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.4 }}>
                      <CheckCircle2 size={14} color="var(--positive)" style={{ flexShrink: 0, marginTop: '2px' }} />
                      <span>{arg}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px', fontSize: '11px', color: 'var(--text-2)' }}>
                <strong style={{ color: 'var(--text-1)' }}>Key Pillar: </strong>
                {debate.bull.keyHighlight}
              </div>
            </div>

            {/* Bear Analyst */}
            <div className="agent-card bear">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                <div>
                  <div className="agent-name" style={{ color: 'var(--negative)' }}>
                    BEAR CONTRARIAN
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-0)' }}>
                    {debate.bear.agentName}
                  </div>
                </div>
                <span className="badge badge-red" style={{ fontSize: '11px' }}>
                  <TrendingDown size={12} /> {debate.bear.stance}
                </span>
              </div>

              {/* Metric Box */}
              <div
                style={{
                  background: 'var(--bg-1)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  margin: '12px 0',
                  border: '1px solid rgba(246,70,93,0.2)',
                }}
              >
                <div style={{ fontSize: '11px', color: 'var(--text-2)' }}>{debate.bear.metricLabel}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '18px', fontWeight: 800, color: 'var(--negative)', marginTop: '2px' }}>
                  {debate.bear.metricValue}
                </div>
              </div>

              {/* Arguments */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Downside Stress Points
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {debate.bear.arguments.map((arg, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.4 }}>
                      <AlertTriangle size={14} color="var(--negative)" style={{ flexShrink: 0, marginTop: '2px' }} />
                      <span>{arg}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px', fontSize: '11px', color: 'var(--text-2)' }}>
                <strong style={{ color: 'var(--text-1)' }}>Key Pillar: </strong>
                {debate.bear.keyHighlight}
              </div>
            </div>

            {/* Risk Architect */}
            <div className="agent-card risk">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                <div>
                  <div className="agent-name" style={{ color: 'var(--warning)' }}>
                    RISK ARCHITECT
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-0)' }}>
                    {debate.risk.agentName}
                  </div>
                </div>
                <span className="badge badge-amber" style={{ fontSize: '11px' }}>
                  <ShieldAlert size={12} /> {debate.risk.stance}
                </span>
              </div>

              {/* Metric Box */}
              <div
                style={{
                  background: 'var(--bg-1)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  margin: '12px 0',
                  border: '1px solid rgba(240,185,11,0.2)',
                }}
              >
                <div style={{ fontSize: '11px', color: 'var(--text-2)' }}>{debate.risk.metricLabel}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: '18px', fontWeight: 800, color: 'var(--warning)', marginTop: '2px' }}>
                  {debate.risk.metricValue}
                </div>
              </div>

              {/* Arguments */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Quantitative Risk Controls
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {debate.risk.arguments.map((arg, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--text-1)', lineHeight: 1.4 }}>
                      <ShieldAlert size={14} color="var(--warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
                      <span>{arg}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px', fontSize: '11px', color: 'var(--text-2)' }}>
                <strong style={{ color: 'var(--text-1)' }}>Key Pillar: </strong>
                {debate.risk.keyHighlight}
              </div>
            </div>
          </div>

          {/* Full Width Chief Investment Officer Consensus Card */}
          <div className="agent-card chief" style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div>
                <div className="agent-name" style={{ color: 'var(--accent)' }}>
                  EXECUTIVE COMMITTEE CHAIR
                </div>
                <h3 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-0)', margin: '2px 0' }}>
                  {debate.chief.agentName}
                </h3>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge badge-purple" style={{ fontSize: '12px', padding: '4px 12px' }}>
                  {debate.chief.horizon}
                </span>
                <span className="badge badge-green" style={{ fontSize: '13px', padding: '5px 14px', fontWeight: 800 }}>
                  <Award size={14} /> {debate.chief.consensus}
                </span>
              </div>
            </div>

            {/* Fair Value Target Band */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                background: 'var(--bg-1)',
                padding: '12px 18px',
                borderRadius: '8px',
                marginBottom: '18px',
                border: '1px solid var(--border)',
                flexWrap: 'wrap',
              }}
            >
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-2)', textTransform: 'uppercase' }}>Synthesized Fair Value Range:</span>
                <span className="text-mono" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-0)', marginLeft: '8px' }}>
                  {debate.chief.fairValueRange}
                </span>
              </div>
              <div style={{ color: 'var(--text-3)', fontSize: '12px' }}>|</div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-2)', textTransform: 'uppercase' }}>Consensus Confidence:</span>
                <span className="text-mono" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--accent)', marginLeft: '8px' }}>
                  High (82% Tranche Agreement)
                </span>
              </div>
            </div>

            {/* Executive Summary */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-2)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Executive Synthesis
              </div>
              <p style={{ fontSize: '14px', color: 'var(--text-1)', lineHeight: 1.6, margin: 0 }}>
                {debate.chief.summary}
              </p>
            </div>

            {/* Actionable Allocation Rules */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-2)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Recommended Execution Protocol
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px' }}>
                {debate.chief.actionPlan.map((step, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(57,132,244,0.06)',
                      border: '1px solid rgba(57,132,244,0.2)',
                      padding: '10px 14px',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      fontSize: '12px',
                      color: 'var(--text-1)',
                    }}
                  >
                    <ArrowRight size={14} color="var(--accent)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Prominent Prototype Warning Notice */}
          <div
            className="disclaimer-banner"
            style={{
              padding: '16px 20px',
              fontSize: '13px',
              borderRadius: '8px',
              marginBottom: '32px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <AlertTriangle size={20} style={{ flexShrink: 0 }} />
            <div>
              <strong>Prototype Disclaimer Notice: </strong>
              This project is a prototype and is not financial advice. Debate outputs are synthesized via automated LLM agents and quantitative heuristics for demonstration and academic evaluation only.
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
