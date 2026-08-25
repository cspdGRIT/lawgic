from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import require_approved_access
from app.core.database import get_db
from app.core.limits import require_feature
from app.core.config import settings
from app.models.user import User
from app.agents.research_agent import legal_research_node, search_knowledge_base
from app.agents.state import AgentState
from app.services.indian_kanoon import search_cases

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    jurisdiction: Optional[str] = None


@router.post("/search")
async def search_legal_knowledge(
    request: SearchRequest,
    current_user: User = Depends(require_approved_access),
    db: AsyncSession = Depends(get_db),
    _limit: None = Depends(require_feature("research")),
):
    initial_state: AgentState = {
        "messages": [],
        "user_query": request.query,
        "intent": "legal_research",
        "case_context": {"category": request.category, "jurisdiction": request.jurisdiction},
        "research_results": [],
        "generated_document": None,
        "lawyer_matches": [],
        "final_response": "",
        "confidence_score": 0.0,
        "agent_logs": [],
        "language_target": None,
    }

    final_state = await legal_research_node(initial_state)

    # Use Indian Kanoon if API key is set, fall back to local KB
    if settings.INDIAN_KANOON_API_KEY:
        ik_data = await search_cases(request.query, doc_type=_map_category(request.category))
        results = ik_data.get("results", [])
        total = ik_data.get("total", 0)
        source = "indiankanoon"
    else:
        kb = search_knowledge_base(request.query, category=request.category)
        results = kb
        total = len(kb)
        source = "local"

    return {
        "results": results,
        "ai_summary": final_state.get("final_response", ""),
        "query": request.query,
        "total": total,
        "source": source,
    }


def _map_category(category: Optional[str]) -> Optional[str]:
    mapping = {
        "case": "judgment",
        "statute": "act",
        "statutes": "act",
        "case law": "judgment",
    }
    return mapping.get((category or "").lower())
