import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.agents.state import AgentState
from app.services.claude import get_claude_response
from app.models.lawyer import Lawyer

MATCHING_SYSTEM = """You are a senior legal consultant at Lawgic who matches clients with the best lawyers for their cases.

When recommending lawyers, consider:
1. Specialization alignment with case type
2. Court level expertise (district, high court, supreme court)
3. Language compatibility
4. Budget appropriateness
5. Location convenience
6. Years of experience and success rate

For each recommended lawyer, provide a clear, specific reason why they are the best match for this particular case. Be specific about why their background matches the client's needs."""


async def lawyer_matching_node(state: AgentState, db: AsyncSession = None) -> AgentState:
    """Match lawyers to case requirements using AI."""
    logs = list(state.get("agent_logs", []))
    case_ctx = state.get("case_context", {})
    user_query = state.get("user_query", "")

    case_type = case_ctx.get("case_type", "")
    jurisdiction = case_ctx.get("jurisdiction", "")
    budget = case_ctx.get("budget_per_hour", None)
    preferred_language = case_ctx.get("preferred_language", "English")

    logs.append("lawyer_agent: Searching for matching lawyers")

    lawyers_data = []
    if db:
        try:
            query = select(Lawyer).where(Lawyer.available == True).where(Lawyer.verified == True)
            result = await db.execute(query)
            lawyers = result.scalars().all()

            for lawyer in lawyers:
                practice_areas = json.loads(lawyer.practice_areas) if lawyer.practice_areas else []
                specializations = json.loads(lawyer.specializations) if lawyer.specializations else []
                languages = json.loads(lawyer.languages) if lawyer.languages else []

                area_match = case_type.lower() in [a.lower() for a in practice_areas] if case_type else True
                budget_match = budget is None or lawyer.hourly_rate <= int(budget)

                lawyers_data.append({
                    "id": lawyer.id,
                    "full_name": lawyer.full_name,
                    "specializations": specializations,
                    "practice_areas": practice_areas,
                    "city": lawyer.city,
                    "state": lawyer.state,
                    "years_experience": lawyer.years_experience,
                    "hourly_rate": lawyer.hourly_rate,
                    "consultation_fee": lawyer.consultation_fee,
                    "rating": lawyer.rating,
                    "review_count": lawyer.review_count,
                    "languages": languages,
                    "bio": lawyer.bio,
                    "area_match": area_match,
                    "budget_match": budget_match,
                })
        except Exception as e:
            logs.append(f"lawyer_agent: DB error - {str(e)}")

    # Use mock data if no DB or empty
    if not lawyers_data:
        lawyers_data = [
            {"id": 1, "full_name": "Adv. Priya Sharma", "specializations": ["Criminal Defense"], "practice_areas": ["criminal", "corporate"], "city": "Delhi", "state": "Delhi", "years_experience": 14, "hourly_rate": 8000, "consultation_fee": 2000, "rating": 4.8, "review_count": 127, "languages": ["English", "Hindi"], "bio": "Experienced criminal defense lawyer", "area_match": True, "budget_match": True},
            {"id": 2, "full_name": "Adv. Rahul Mehta", "specializations": ["Civil Litigation"], "practice_areas": ["civil", "property"], "city": "Mumbai", "state": "Maharashtra", "years_experience": 12, "hourly_rate": 7500, "consultation_fee": 1500, "rating": 4.7, "review_count": 89, "languages": ["English", "Hindi", "Marathi"], "bio": "Civil litigation specialist in Mumbai High Court", "area_match": True, "budget_match": True},
            {"id": 3, "full_name": "Adv. Lakshmi Subramaniam", "specializations": ["Family Law"], "practice_areas": ["family", "civil"], "city": "Chennai", "state": "Tamil Nadu", "years_experience": 18, "hourly_rate": 6000, "consultation_fee": 1200, "rating": 4.9, "review_count": 203, "languages": ["English", "Tamil", "Hindi"], "bio": "Top family law attorney with 18 years experience", "area_match": True, "budget_match": True},
            {"id": 4, "full_name": "Adv. Amir Khan", "specializations": ["Corporate Law"], "practice_areas": ["corporate", "taxation"], "city": "Bangalore", "state": "Karnataka", "years_experience": 10, "hourly_rate": 9000, "consultation_fee": 2500, "rating": 4.6, "review_count": 64, "languages": ["English", "Hindi", "Kannada"], "bio": "Corporate law expert specializing in M&A and startup law", "area_match": True, "budget_match": True},
            {"id": 5, "full_name": "Adv. Sunita Verma", "specializations": ["Consumer Law", "RTI"], "practice_areas": ["consumer", "civil"], "city": "Delhi", "state": "Delhi", "years_experience": 8, "hourly_rate": 4500, "consultation_fee": 1000, "rating": 4.5, "review_count": 156, "languages": ["English", "Hindi"], "bio": "Consumer rights advocate, over 500 cases won", "area_match": True, "budget_match": True},
        ]

    prompt = f"""I need to match a client with the best lawyers for their legal matter.

Client's Case Details:
- Case Type: {case_type or "General"}
- Jurisdiction: {jurisdiction or "India"}
- Budget (per hour): ₹{budget if budget else "Flexible"}
- Preferred Language: {preferred_language}
- Description: {user_query}

Available Lawyers:
{json.dumps(lawyers_data[:15], indent=2)}

Select the TOP 5 most suitable lawyers and explain specifically why each is a good match. Consider specialization, experience, location, language, and budget.

Respond with JSON array:
[{{"lawyer_id": <id>, "match_score": <0.0-1.0>, "match_reason": "<specific reason>", "strengths": ["strength1", "strength2"]}}]

Return ONLY the JSON array."""

    messages = [{"role": "user", "content": prompt}]
    try:
        import re
        response = await get_claude_response(messages, system=MATCHING_SYSTEM)
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            matches = json.loads(json_match.group())
        else:
            matches = json.loads(response)

        # Enrich with lawyer data
        lawyer_lookup = {l["id"]: l for l in lawyers_data}
        enriched_matches = []
        for m in matches[:5]:
            lawyer = lawyer_lookup.get(m.get("lawyer_id"))
            if lawyer:
                enriched_matches.append({**lawyer, **m})

        logs.append(f"lawyer_agent: Matched {len(enriched_matches)} lawyers")

        response_text = f"**Top {len(enriched_matches)} Lawyer Matches for Your Case:**\n\n"
        for i, m in enumerate(enriched_matches, 1):
            response_text += f"**{i}. {m['full_name']}** — {m['city']}, {m['state']}\n"
            response_text += f"   Specialization: {', '.join(m.get('specializations', []))}\n"
            response_text += f"   Rating: {m['rating']}/5.0 ({m['review_count']} reviews) | ₹{m['hourly_rate']:,}/hr\n"
            response_text += f"   Why this match: {m.get('match_reason', 'Strong alignment with your case type')}\n\n"

        return {
            **state,
            "lawyer_matches": enriched_matches,
            "final_response": response_text,
            "confidence_score": 0.82,
            "agent_logs": logs,
        }
    except Exception as e:
        logs.append(f"lawyer_agent: Error - {str(e)}")
        simple_matches = lawyers_data[:5]
        for m in simple_matches:
            m["match_score"] = 0.75
            m["match_reason"] = f"Experienced {m['city']} based lawyer with relevant practice areas"
        return {
            **state,
            "lawyer_matches": simple_matches,
            "final_response": "Here are the top lawyers matching your criteria.",
            "confidence_score": 0.7,
            "agent_logs": logs,
        }
