"""Issue Navigator: the "describe your problem, get an action plan" entry point.

Unlike the general chat agent (intent classifier -> one specialist -> prose
reply), this one always returns the same structured shape — issue category,
forum/court, petition or document needed, a document checklist, a fee
estimate, and next steps — because that's what someone with a real-world
problem and no legal vocabulary actually needs, in one shot instead of a
back-and-forth conversation. Lawyer matching is *reused* from the existing
lawyer_agent, not reimplemented.
"""

import json
import re
from datetime import date, datetime

from app.agents.document_agent import TEMPLATES
from app.agents.lawyer_agent import lawyer_matching_node
from app.agents.state import AgentState
from app.services.claude import get_claude_response

# Same taxonomy the manual "New Case" form uses (frontend/src/pages/CaseAnalysis.tsx),
# plus Intellectual Property — the one bucket that app genuinely lacked.
ISSUE_TYPES = [
    "Criminal", "Civil", "Family", "Property", "Consumer",
    "Labour", "Corporate", "Constitutional", "Revenue",
    "Intellectual Property", "Other",
]

_TEMPLATE_CATALOG = "\n".join(
    f"- {t['id']}: {t['name']} — {t['description']}" for t in TEMPLATES.values()
)

ISSUE_NAV_SYSTEM = f"""You are Lawgic AI's intake triage specialist for India. A citizen with no legal
training is describing a real problem — civil, criminal, family, communal/religious, property, consumer,
labour, corporate, intellectual property, anything. Your job is to turn their plain description into a
precise, actionable plan: what kind of issue this is, which court/forum handles it, what petition or
document they need, what documents to gather, roughly what it costs, and what to do first.

CRITICAL LANGUAGE RULE: The user may write in any language (English, Hindi, or any other language,
including transliterated/Romanized text). Detect it and write every natural-language field of your
response (plain_summary, forum_reasoning, documents_needed, next_steps, disclaimer, estimated fees,
limitation_warning) IN THAT SAME LANGUAGE. Only "issue_type" and "document_template_id" stay in English
exactly as given below, since the app uses them internally.

issue_type MUST be exactly one of: {", ".join(ISSUE_TYPES)}

document_template_id: pick the closest match from this list of templates the app can already draft, or
null if none genuinely fits (don't force a bad match):
{_TEMPLATE_CATALOG}

Be realistic and specific — name the actual forum (e.g. "District Consumer Disputes Redressal Commission",
not just "consumer court"; "Magistrate Court under Section 154 CrPC" for an FIR; "Family Court" for
divorce/custody; "State Human Rights Commission" or "Magistrate under Section 154" for communal violence
depending on facts). If a limitation period or urgency applies (e.g. 30-day notice for cheque bounce,
3-month window for POSH complaints, evidence preservation for FIRs), say so plainly in limitation_warning;
otherwise set it to null.

You'll be told today's date. When limitation_warning applies AND the facts given let you compute (or
reasonably estimate) an actual calendar date it falls due, set deadline_date to that date in YYYY-MM-DD
format — this drives a real reminder email, so only set it when you can genuinely estimate a date from
what they told you (e.g. "the cheque bounced 20 days ago" + a 30-day notice window = a real date).
Otherwise, or if the warning is just general urgency with no computable date, set it to null.

Always end disclaimer with a line making clear this is AI guidance, not a substitute for a licensed
advocate reviewing the actual facts and documents.

Return ONLY a valid JSON object with EXACTLY this structure, no markdown fences, no extra text:
{{
  "detected_language": "<language name, e.g. Hindi, English, Tamil>",
  "issue_type": "<one of the fixed list above>",
  "case_title": "<short neutral title, under 70 chars, in English>",
  "plain_summary": "<2-3 sentences restating their issue in plain language, in their language>",
  "urgency": "<low|medium|high|critical, plus a short reason, in their language>",
  "limitation_warning": "<specific deadline/urgency note in their language, or null>",
  "deadline_date": "<YYYY-MM-DD if computable from today's date + the facts given, else null>",
  "recommended_forum": "<the specific court/authority/commission name>",
  "forum_reasoning": "<1-2 sentences on why this forum, in their language>",
  "petition_or_document": "<the specific petition/application/notice they need to file>",
  "document_template_id": "<id from the catalog above, or null>",
  "relevant_statutes": ["<law + section, e.g. Section 138, Negotiable Instruments Act 1881>"],
  "documents_needed": ["<concrete document/evidence to gather, in their language>"],
  "estimated_court_fee": "a real INR range as plain text, e.g. ₹500 - ₹2,000 (never a placeholder)",
  "estimated_lawyer_fee": "a real INR range as plain text, e.g. ₹5,000 - ₹25,000 (never a placeholder)",
  "next_steps": ["<ordered, concrete actions, in their language>"],
  "disclaimer": "<short disclaimer per the rule above, in their language>",
  "confidence_score": <float 0.0-1.0, how confident you are in this categorization given the description>
}}"""


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group() if match else text)


async def navigate_issue(message: str, city: str | None, db=None) -> dict:
    """Run the triage call, validate/clean it, then reuse lawyer_agent for matches."""
    today = date.today()
    prompt = f"""Today's date: {today.isoformat()}

Citizen's description of their problem:
---
{message}
---
{f"They are located in/near: {city}" if city else ""}

Analyze this and produce the full triage JSON."""

    response_text = await get_claude_response([{"role": "user", "content": prompt}], system=ISSUE_NAV_SYSTEM)
    analysis = _extract_json(response_text)

    # Guard against the model drifting off the fixed enum or inventing a template id.
    if analysis.get("issue_type") not in ISSUE_TYPES:
        analysis["issue_type"] = "Other"
    if analysis.get("document_template_id") not in TEMPLATES:
        analysis["document_template_id"] = None
    analysis["confidence_score"] = max(0.0, min(1.0, float(analysis.get("confidence_score", 0.6))))

    # Only trust a deadline_date that's a real, plausible, future-ish calendar date —
    # a scheduler job reminds the user by email based on this, so a malformed or wildly
    # implausible value here should just quietly not become a reminder, not error out.
    raw_deadline = analysis.get("deadline_date")
    deadline: date | None = None
    if raw_deadline:
        try:
            deadline = datetime.strptime(raw_deadline, "%Y-%m-%d").date()
            if not (today <= deadline <= today.replace(year=today.year + 2)):
                deadline = None
        except (ValueError, TypeError):
            deadline = None
    analysis["deadline_date"] = deadline.isoformat() if deadline else None

    # Reuse the existing lawyer matching agent rather than re-deriving matches here.
    lawyer_state: AgentState = {
        "messages": [],
        "user_query": message,
        "intent": "lawyer_matching",
        "case_context": {
            "case_type": analysis["issue_type"],
            "jurisdiction": city or "India",
            "budget_per_hour": None,
            "preferred_language": analysis.get("detected_language", "English"),
        },
        "research_results": [],
        "generated_document": None,
        "lawyer_matches": [],
        "final_response": "",
        "confidence_score": 0.0,
        "agent_logs": [],
        "language_target": None,
    }
    try:
        lawyer_state = await lawyer_matching_node(lawyer_state, db=db)
    except Exception:
        pass  # lawyer suggestions are a bonus, not a blocker — the action plan still stands without them

    analysis["matched_lawyers"] = lawyer_state.get("lawyer_matches", [])[:5]
    return analysis
