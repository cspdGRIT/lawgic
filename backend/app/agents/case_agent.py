import json
import re
from app.agents.state import AgentState
from app.services.claude import get_claude_response

CASE_ANALYSIS_SYSTEM = """You are a senior Indian litigation attorney with 25 years of experience in all Indian courts.
You analyze cases with deep knowledge of:
- IPC, CrPC, CPC, Evidence Act
- Constitutional provisions and fundamental rights
- Landmark Supreme Court and High Court judgments
- Indian court procedures, timelines, and costs
- State-specific laws and jurisdiction-specific precedents

When analyzing a case, be realistic about win probability based on:
- Strength of evidence described
- Applicable law and precedents
- Jurisdiction and court level
- Common outcomes in similar Indian cases

ALWAYS return a valid JSON object with EXACTLY this structure:
{
  "win_probability": <integer 0-100>,
  "key_issues": [<list of strings identifying core legal issues>],
  "legal_strategy": "<string with recommended approach>",
  "relevant_statutes": [<list of applicable laws with section numbers>],
  "similar_cases": [{"name": "<case name>", "court": "<court>", "year": <year>, "outcome": "<outcome>"}],
  "next_steps": [<list of actionable steps>],
  "risk_factors": [<list of risks>],
  "estimated_duration": "<realistic timeframe in Indian courts>",
  "estimated_cost": "<cost range in INR>",
  "summary": "<brief case summary>"
}

Return ONLY the JSON object, no other text."""


async def case_analysis_node(state: AgentState, db=None) -> AgentState:
    """Analyze a legal case using Claude and return structured analysis."""
    case_ctx = state.get("case_context", {})
    user_query = state.get("user_query", "")
    logs = list(state.get("agent_logs", []))
    logs.append("case_agent: Starting case analysis")

    if not case_ctx:
        # Try to extract case details from the query itself
        case_ctx = {"description": user_query}

    prompt = f"""Analyze the following legal case and provide a comprehensive assessment:

Case Title: {case_ctx.get('title', 'Not provided')}
Case Type: {case_ctx.get('case_type', 'Not specified')}
Jurisdiction: {case_ctx.get('jurisdiction', 'India')}
Court Level: {case_ctx.get('court_level', 'Not specified')}
Description: {case_ctx.get('description', '')}
Key Facts: {case_ctx.get('key_facts', 'Not provided')}
Opposing Party: {case_ctx.get('opposing_party', 'Not specified')}

User's specific question/concern: {user_query}

Provide a thorough legal analysis as a senior Indian litigator."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response_text = await get_claude_response(messages, system=CASE_ANALYSIS_SYSTEM)

        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
        else:
            analysis = json.loads(response_text)

        confidence = analysis.get("win_probability", 50) / 100.0
        logs.append(f"case_agent: Analysis complete. Win probability: {analysis.get('win_probability')}%")

        final_response = f"""**Case Analysis Complete**

**Win Probability:** {analysis.get('win_probability')}%

**Key Issues:**
{chr(10).join(f"• {issue}" for issue in analysis.get('key_issues', []))}

**Legal Strategy:**
{analysis.get('legal_strategy', '')}

**Relevant Statutes:**
{chr(10).join(f"• {statute}" for statute in analysis.get('relevant_statutes', []))}

**Next Steps:**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(analysis.get('next_steps', [])))}

**Risk Factors:**
{chr(10).join(f"• {risk}" for risk in analysis.get('risk_factors', []))}

**Estimated Duration:** {analysis.get('estimated_duration', 'Varies')}
**Estimated Cost:** {analysis.get('estimated_cost', 'Varies')}"""

        return {
            **state,
            "final_response": final_response,
            "case_context": {**case_ctx, "ai_analysis": analysis},
            "confidence_score": confidence,
            "agent_logs": logs,
        }

    except (json.JSONDecodeError, Exception) as e:
        logs.append(f"case_agent: Error parsing analysis: {str(e)}")
        fallback_response = await get_claude_response(
            [{"role": "user", "content": f"Please analyze this Indian legal case:\n\n{json.dumps(case_ctx, indent=2)}\n\nUser question: {user_query}"}],
            system="You are Lawgic AI, an expert in Indian law. Provide a thorough case analysis."
        )
        return {
            **state,
            "final_response": fallback_response,
            "confidence_score": 0.6,
            "agent_logs": logs,
        }
