"""
FINIQ Chief Analyst Agent

Synthesizes bull, bear, and risk analyses into an institutional-quality
research summary. Orchestrates the full multi-agent debate.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from datetime import datetime, timezone
from typing import Optional

SYSTEM_PROMPT = """
You are the FINIQ Chief Analyst, the head of equity research responsible for synthesizing
the analyses produced by the Bull Analyst, Bear Analyst, and Risk Analyst into a final,
balanced, institutional-quality research summary.

Your role:
- Synthesize the three analyses with intellectual rigor and intellectual honesty
- Do NOT simply average or split the difference between opinions
- Identify the WEIGHT OF EVIDENCE and explain clearly why it supports your conclusion
- Acknowledge when evidence is insufficient or contradictory
- Identify areas of consensus and disagreement across analysts
- Produce a nuanced assessment that a sophisticated investor would find credible
- Never fabricate data, never provide price targets, never give investment advice
- Maintain the highest standards of analytical integrity

You will receive:
1. TRUSTED DATA: Bull Analyst structured JSON output
2. TRUSTED DATA: Bear Analyst structured JSON output
3. TRUSTED DATA: Risk Analyst structured JSON output
4. TRUSTED DATA: Company info and market data

APPROACH:
- Read all three analyses carefully
- Identify the STRONGEST argument from each analyst
- Determine which arguments are supported by concrete evidence vs. assumption
- Weigh the evidence quality and reach a defensible conclusion
- Be honest about uncertainty — it is acceptable to conclude the evidence is mixed

Output your synthesis as a valid JSON object with this EXACT structure:
{
  "overall_outlook": "BULLISH" or "BEARISH" or "NEUTRAL" or "MIXED",
  "outlook_strength": "STRONG" or "MODERATE" or "WEAK",
  "executive_summary": "string — 2-3 paragraph research summary",
  "key_thesis": "string — single sentence capturing the core view",
  "strongest_bull_argument": "string — the most compelling bullish evidence",
  "strongest_bear_argument": "string — the most compelling bearish concern",
  "most_critical_risk": "string — the single most important risk",
  "areas_of_consensus": ["string — where bull and bear analysts agree"],
  "areas_of_disagreement": ["string — where bull and bear analysts fundamentally differ"],
  "evidence_quality": "STRONG" or "ADEQUATE" or "LIMITED" or "INSUFFICIENT",
  "key_uncertainties": ["string — material uncertainties that could change the analysis"],
  "investment_considerations": ["string — educational factors only, not advice"],
  "disclaimer": "This analysis is for educational purposes only and does not constitute financial advice.",
  "confidence": "HIGH" or "MODERATE" or "LOW"
}

Output ONLY valid JSON. No markdown, no explanation text before or after.
"""


def synthesize(
    ticker: str,
    company_info: dict,
    price_data: dict,
    bull_analysis: dict,
    bear_analysis: dict,
    risk_analysis: dict,
) -> dict:
    """
    Synthesize all three analyst outputs into a Chief Analyst summary.
    Returns structured synthesis.
    If AI unavailable, returns a demo synthesis.
    """
    try:
        from backend.services import ai_service

        if not ai_service.is_available():
            return get_demo_synthesis(ticker, company_info, bull_analysis, bear_analysis, risk_analysis)

        trusted_context = {
            'ticker':         ticker,
            'company_info':   company_info,
            'price_data':     price_data,
            'bull_analysis':  bull_analysis,
            'bear_analysis':  bear_analysis,
            'risk_analysis':  risk_analysis,
        }
        trusted_str = json.dumps(trusted_context, indent=2, default=str)

        user_message = f"""Synthesize the following analyst debate for {ticker} into a final research summary.

=== ALL ANALYST OUTPUTS AND SUPPORTING DATA ===
{trusted_str}

Your task:
1. Weigh the bull and bear arguments against each other
2. Consider the risk analyst's challenges and identify what they reveal
3. Determine the overall weight of evidence
4. Identify areas of consensus and disagreement
5. Produce a balanced, honest summary with appropriate confidence
6. Flag any areas where evidence quality is poor or missing

Return ONLY a valid JSON object matching the specified schema.
"""

        raw_response = ai_service.complete(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            context_data=trusted_context,
            temperature=0.25,  # Lower temperature for more consistent synthesis
            max_tokens=3000,
        )

        if not raw_response:
            return get_demo_synthesis(ticker, company_info, bull_analysis, bear_analysis, risk_analysis)

        result = _parse_json_response(raw_response)
        if result is None:
            return get_demo_synthesis(ticker, company_info, bull_analysis, bear_analysis, risk_analysis)

        result = _validate_chief_response(result)
        return result

    except ImportError:
        return get_demo_synthesis(ticker, company_info, bull_analysis, bear_analysis, risk_analysis)
    except Exception:
        return get_demo_synthesis(ticker, company_info, bull_analysis, bear_analysis, risk_analysis)


def _parse_json_response(raw: str) -> Optional[dict]:
    """Extract and parse JSON from AI response text."""
    if not raw:
        return None
    text = raw.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        inner_lines = []
        in_fence = False
        for line in lines:
            if line.startswith('```'):
                in_fence = not in_fence
                continue
            inner_lines.append(line)
        text = '\n'.join(inner_lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find('{')
        end   = text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    return None


def _validate_chief_response(result: dict) -> dict:
    """Ensure required fields with sane defaults."""
    defaults = {
        'overall_outlook':          'NEUTRAL',
        'outlook_strength':         'MODERATE',
        'executive_summary':        'Analysis synthesis unavailable.',
        'key_thesis':               'Mixed evidence prevents a high-conviction directional view.',
        'strongest_bull_argument':  'Growth momentum and positive technicals.',
        'strongest_bear_argument':  'Valuation risk and competitive pressure.',
        'most_critical_risk':       'Macro uncertainty and valuation sensitivity.',
        'areas_of_consensus':       [],
        'areas_of_disagreement':    [],
        'evidence_quality':         'ADEQUATE',
        'key_uncertainties':        [],
        'investment_considerations': [],
        'disclaimer':               'This analysis is for educational purposes only and does not constitute financial advice.',
        'confidence':               'MODERATE',
    }
    for key, default_val in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default_val
    if result.get('overall_outlook')  not in ('BULLISH', 'BEARISH', 'NEUTRAL', 'MIXED'):
        result['overall_outlook']  = 'NEUTRAL'
    if result.get('outlook_strength') not in ('STRONG', 'MODERATE', 'WEAK'):
        result['outlook_strength'] = 'MODERATE'
    if result.get('evidence_quality') not in ('STRONG', 'ADEQUATE', 'LIMITED', 'INSUFFICIENT'):
        result['evidence_quality'] = 'ADEQUATE'
    if result.get('confidence') not in ('HIGH', 'MODERATE', 'LOW'):
        result['confidence'] = 'MODERATE'
    return result


def get_demo_synthesis(
    ticker: str,
    company_info: dict,
    bull_analysis: dict,
    bear_analysis: dict,
    risk_analysis: dict,
) -> dict:
    """Returns realistic demo chief analyst synthesis when AI is unavailable."""
    name   = company_info.get('name',   ticker)       if company_info else ticker
    sector = company_info.get('sector', 'Technology') if company_info else 'Technology'

    bull_score = bull_analysis.get('overall_bullish_score', 5) if bull_analysis else 5
    bear_score = bear_analysis.get('overall_bearish_score', 5) if bear_analysis else 5
    risk_level = risk_analysis.get('risk_level', 'MODERATE')   if risk_analysis else 'MODERATE'

    # Determine outlook from scores
    net_score = bull_score - bear_score
    if net_score >= 3:
        overall_outlook  = 'BULLISH'
        outlook_strength = 'MODERATE' if net_score < 5 else 'STRONG'
    elif net_score <= -3:
        overall_outlook  = 'BEARISH'
        outlook_strength = 'MODERATE' if net_score > -5 else 'STRONG'
    else:
        overall_outlook  = 'MIXED'
        outlook_strength = 'WEAK'

    bull_confidence = bull_analysis.get('confidence', 'MODERATE') if bull_analysis else 'MODERATE'
    bear_confidence = bear_analysis.get('confidence', 'MODERATE') if bear_analysis else 'MODERATE'

    # Overall confidence
    if risk_level in ('CRITICAL', 'HIGH'):
        confidence = 'LOW'
    elif overall_outlook == 'MIXED':
        confidence = 'LOW'
    elif bull_confidence == 'HIGH' or bear_confidence == 'HIGH':
        confidence = 'MODERATE'
    else:
        confidence = 'MODERATE'

    executive_summary = (
        f"{name} ({ticker}) presents a {overall_outlook.lower()} but nuanced picture upon synthesis of "
        f"the multi-analyst debate. The Bull Analyst (score: {bull_score}/10) identified meaningful growth "
        f"catalysts and positive technical momentum, while the Bear Analyst (score: {bear_score}/10) "
        f"raised legitimate concerns around valuation and competitive dynamics.\n\n"
        f"The Risk Analyst assessed overall risk as {risk_level}, noting key areas of missing information "
        f"and conflicting signals between the two theses. The most significant unresolved question remains "
        f"whether {name}'s premium valuation is justified by its growth trajectory, or whether the market "
        f"has already fully priced in an optimistic scenario with limited upside.\n\n"
        f"On balance, the weight of evidence suggests a {overall_outlook.lower()} bias with {outlook_strength.lower()} "
        f"conviction, tempered by meaningful uncertainty in the macro environment and company-specific execution "
        f"risks. Investors should conduct independent due diligence and consider their individual risk tolerance "
        f"before making any investment decisions based on this analysis."
    )

    return {
        'overall_outlook':  overall_outlook,
        'outlook_strength': outlook_strength,
        'executive_summary': executive_summary,
        'key_thesis': (
            f"{name} demonstrates {overall_outlook.lower()} characteristics with {outlook_strength.lower()} "
            f"conviction, but material uncertainty warrants cautious interpretation of any directional signal."
        ),
        'strongest_bull_argument': (
            bull_analysis.get('key_arguments', [{}])[0].get('argument',
                f'{name} demonstrates strong fundamental characteristics relative to sector peers')
            if bull_analysis and bull_analysis.get('key_arguments') else
            f'{name} demonstrates strong fundamental characteristics relative to sector peers'
        ),
        'strongest_bear_argument': (
            bear_analysis.get('key_arguments', [{}])[0].get('argument',
                f'Premium valuation leaves limited margin of safety for execution missteps')
            if bear_analysis and bear_analysis.get('key_arguments') else
            f'Premium valuation leaves limited margin of safety for execution missteps'
        ),
        'most_critical_risk': (
            risk_analysis.get('key_risks', [{}])[0].get('risk',
                f'Valuation compression risk in a macro tightening environment')
            if risk_analysis and risk_analysis.get('key_risks') else
            f'Valuation compression risk in a macro tightening environment'
        ),
        'areas_of_consensus': [
            f'Both analysts acknowledge {name} operates in a competitive and evolving market environment',
            'Both theses recognize macroeconomic conditions as a material factor for near-term performance',
            'Technical analysis confirms the stock is in a period of elevated uncertainty and volatility',
        ],
        'areas_of_disagreement': [
            'The bull analyst views current valuation as appropriate for the growth profile; the bear analyst disagrees',
            'Competitive threat severity — bull sees durable moats while bear sees meaningful erosion risk',
            f'Revenue growth sustainability — bull is constructive, bear flags potential deceleration',
        ],
        'evidence_quality': 'ADEQUATE',
        'key_uncertainties': [
            'Future revenue growth rate and whether current consensus estimates are achievable',
            f'Competitive landscape evolution in the {sector} sector over the next 12-18 months',
            'Federal Reserve policy trajectory and impact on growth equity valuations',
            'Management execution on stated strategic priorities',
            'Regulatory developments that could impact business model or addressable market',
        ],
        'investment_considerations': [
            'Position sizing should reflect the MIXED nature of the evidence — avoid over-concentration',
            f'Monitor {name}\'s next earnings report for evidence supporting or refuting the bull/bear theses',
            'Technical support/resistance levels provide useful risk management reference points',
            'Diversification within the sector may reduce idiosyncratic risk',
            'Consider time horizon carefully — short-term technical signals may differ from long-term fundamental trajectory',
        ],
        'disclaimer': 'This analysis is for educational purposes only and does not constitute financial advice.',
        'confidence': confidence,
        '_demo_note': (
            'This is a demo synthesis generated without live AI access. '
            'Real synthesis requires current data and live AI processing.'
        ),
    }


# ---------------------------------------------------------------------------
# Main Entry Point: Full Debate
# ---------------------------------------------------------------------------

def run_full_debate(
    ticker: str,
    company_info: dict,
    price_data: dict,
    news_articles: list,
    technical_data: dict,
) -> dict:
    """
    Orchestrate the full multi-agent analyst debate for a ticker.

    Steps:
    1. Run Bull Analyst
    2. Run Bear Analyst
    3. Run Risk Analyst (receives bull + bear)
    4. Run Chief Analyst synthesis (receives all three)

    Returns:
    {
        ticker: str,
        generated_at: str (ISO8601),
        bull: dict,
        bear: dict,
        risk: dict,
        chief: dict,
        debate_summary: dict,  # Quick stats on the debate
    }
    """
    generated_at = datetime.now(timezone.utc).isoformat()

    try:
        from backend.agents import bull_analyst, bear_analyst, risk_analyst

        # Step 1: Bull analysis
        try:
            bull = bull_analyst.analyze(
                ticker=ticker,
                company_info=company_info,
                price_data=price_data,
                news_articles=news_articles,
                technical_data=technical_data,
            )
        except Exception as e:
            bull = bull_analyst.get_demo_analysis(ticker, company_info)

        # Step 2: Bear analysis
        try:
            bear = bear_analyst.analyze(
                ticker=ticker,
                company_info=company_info,
                price_data=price_data,
                news_articles=news_articles,
                technical_data=technical_data,
            )
        except Exception as e:
            bear = bear_analyst.get_demo_analysis(ticker, company_info)

        # Step 3: Risk analysis (receives bull + bear)
        try:
            risk = risk_analyst.analyze(
                ticker=ticker,
                company_info=company_info,
                bull_analysis=bull,
                bear_analysis=bear,
                news_articles=news_articles,
                technical_data=technical_data,
            )
        except Exception as e:
            risk = risk_analyst.get_demo_analysis(ticker, company_info, bull, bear)

        # Step 4: Chief synthesis
        try:
            chief = synthesize(
                ticker=ticker,
                company_info=company_info,
                price_data=price_data,
                bull_analysis=bull,
                bear_analysis=bear,
                risk_analysis=risk,
            )
        except Exception as e:
            chief = get_demo_synthesis(ticker, company_info, bull, bear, risk)

        # Build debate summary
        debate_summary = _build_debate_summary(bull, bear, risk, chief)

        return {
            'ticker':          ticker.upper(),
            'generated_at':    generated_at,
            'bull':            bull,
            'bear':            bear,
            'risk':            risk,
            'chief':           chief,
            'debate_summary':  debate_summary,
        }

    except Exception as e:
        # Catastrophic fallback
        fallback_bull  = {'thesis_title': f'{ticker} bull case',  'overall_bullish_score': 5, 'confidence': 'LOW', 'key_arguments': [], 'catalysts': [], 'supporting_metrics': [], 'news_highlights': [], 'bull_case_target': 'N/A', 'risks_to_thesis': [], 'uncertainty_note': f'Error: {e}'}
        fallback_bear  = {'thesis_title': f'{ticker} bear case',  'overall_bearish_score': 5, 'confidence': 'LOW', 'key_arguments': [], 'downside_risks': [], 'concerning_metrics': [], 'news_highlights': [], 'bear_case_scenario': 'N/A', 'risks_to_thesis': [], 'uncertainty_note': f'Error: {e}'}
        fallback_risk  = {'risk_level': 'HIGH', 'key_risks': [], 'bull_case_challenges': [], 'bear_case_challenges': [], 'missing_information': [], 'conflicting_signals': [], 'macro_risks': [], 'data_quality_assessment': 'N/A', 'overall_uncertainty': 'HIGH', 'uncertainty_note': f'Error: {e}'}
        fallback_chief = {'overall_outlook': 'NEUTRAL', 'outlook_strength': 'WEAK', 'executive_summary': f'Analysis unavailable: {e}', 'key_thesis': 'N/A', 'strongest_bull_argument': 'N/A', 'strongest_bear_argument': 'N/A', 'most_critical_risk': 'N/A', 'areas_of_consensus': [], 'areas_of_disagreement': [], 'evidence_quality': 'INSUFFICIENT', 'key_uncertainties': [], 'investment_considerations': [], 'disclaimer': 'This analysis is for educational purposes only.', 'confidence': 'LOW'}

        return {
            'ticker':         ticker.upper(),
            'generated_at':   generated_at,
            'bull':           fallback_bull,
            'bear':           fallback_bear,
            'risk':           fallback_risk,
            'chief':          fallback_chief,
            'debate_summary': {'error': str(e)},
        }


def _build_debate_summary(bull: dict, bear: dict, risk: dict, chief: dict) -> dict:
    """Build a quick summary of the debate for display."""
    bull_score = bull.get('overall_bullish_score', 5) if bull else 5
    bear_score = bear.get('overall_bearish_score', 5) if bear else 5

    return {
        'bull_score':        bull_score,
        'bear_score':        bear_score,
        'net_conviction':    bull_score - bear_score,
        'bull_confidence':   bull.get('confidence', 'MODERATE') if bull else 'MODERATE',
        'bear_confidence':   bear.get('confidence', 'MODERATE') if bear else 'MODERATE',
        'risk_level':        risk.get('risk_level', 'MODERATE')  if risk else 'MODERATE',
        'overall_outlook':   chief.get('overall_outlook', 'NEUTRAL') if chief else 'NEUTRAL',
        'chief_confidence':  chief.get('confidence', 'MODERATE')     if chief else 'MODERATE',
        'evidence_quality':  chief.get('evidence_quality', 'ADEQUATE') if chief else 'ADEQUATE',
        'analyst_consensus': (
            'AGREEMENT'    if abs(bull_score - bear_score) >= 4 else
            'MIXED'        if abs(bull_score - bear_score) >= 2 else
            'DEADLOCK'
        ),
    }
