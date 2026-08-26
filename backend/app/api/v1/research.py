from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import require_quota_or_credit
from app.core.database import get_db
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
    current_user: User = Depends(require_quota_or_credit("research")),
    db: AsyncSession = Depends(get_db),
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

    # Use Indian Kanoon if API key is set, fall back to local KB. Both branches are
    # normalized to a common {title, content, category, keywords, source} shape below —
    # the raw KB items use type/excerpt/full_text and Indian Kanoon uses
    # doc_type/headline, neither of which the frontend understands directly.
    if settings.INDIAN_KANOON_API_KEY:
        ik_data = await search_cases(request.query, doc_type=_map_category(request.category))
        if ik_data.get("error"):
            # Indian Kanoon call failed (bad key, quota, network) — don't silently
            # report an empty result set as if the search genuinely found nothing.
            kb = search_knowledge_base(request.query, category=request.category)
            results = [_normalize_kb(item) for item in kb]
            total = len(kb)
            source = "local"
        else:
            results = [_normalize_ik(item) for item in ik_data.get("results", [])]
            total = ik_data.get("total", 0)
            source = "indiankanoon"
    else:
        kb = search_knowledge_base(request.query, category=request.category)
        results = [_normalize_kb(item) for item in kb]
        total = len(kb)
        source = "local"

    return {
        "results": results,
        "ai_summary": final_state.get("final_response", ""),
        "query": request.query,
        "total": total,
        "source": source,
    }


def _normalize_kb(item: dict) -> dict:
    return {
        "title": item.get("title", ""),
        "content": item.get("full_text") or item.get("excerpt", ""),
        "category": item.get("type", ""),
        "keywords": item.get("keywords", []),
        "source": "Lawgic Knowledge Base",
    }


def _normalize_ik(item: dict) -> dict:
    return {
        "title": item.get("title", ""),
        "content": item.get("headline", ""),
        "category": item.get("doc_type", ""),
        "keywords": [],
        "source": item.get("court") or "Indian Kanoon",
    }


def _map_category(category: Optional[str]) -> Optional[str]:
    mapping = {
        "case": "judgment",
        "statute": "act",
        "statutes": "act",
        "case law": "judgment",
    }
    return mapping.get((category or "").lower())
