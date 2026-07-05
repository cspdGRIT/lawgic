"""
Indian Kanoon API client — free for non-commercial use.
Get your token at: https://api.indiankanoon.org/
Set INDIAN_KANOON_API_KEY in .env
"""
import httpx
from typing import Optional
from app.core.config import settings

IK_BASE = "https://api.indiankanoon.org"


def _headers() -> dict:
    if settings.INDIAN_KANOON_API_KEY:
        return {"Authorization": f"Token {settings.INDIAN_KANOON_API_KEY}"}
    return {}


async def search_cases(query: str, page: int = 0, doc_type: Optional[str] = None) -> dict:
    """
    Search Indian Kanoon for case law, statutes, documents.
    doc_type: 'judgment', 'act', 'article', 'rule', 'regulation', 'notification', 'circular'
    """
    params = {"formInput": query, "pagenum": page}
    if doc_type:
        params["formInput"] = f"{query} doctypes:{doc_type}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{IK_BASE}/search/",
            data=params,
            headers=_headers(),
        )
        if resp.status_code != 200:
            return {"docs": [], "total": 0, "error": f"Indian Kanoon returned {resp.status_code}"}
        data = resp.json()
        docs = data.get("docs", [])
        results = []
        for doc in docs[:8]:
            results.append({
                "title": doc.get("title", ""),
                "doc_id": doc.get("tid", ""),
                "headline": doc.get("headline", ""),
                "doc_type": doc.get("doctype", ""),
                "court": doc.get("docsource", ""),
                "date": doc.get("publishdate", ""),
                "url": f"https://indiankanoon.org/doc/{doc.get('tid', '')}/",
                "citations": doc.get("numcitedby", 0),
            })
        return {"results": results, "total": data.get("total", 0)}


async def get_document(doc_id: str) -> dict:
    """Fetch full text of a specific document."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{IK_BASE}/doc/{doc_id}/",
            headers=_headers(),
        )
        if resp.status_code != 200:
            return {"error": f"Document not found"}
        data = resp.json()
        return {
            "title": data.get("title", ""),
            "content": data.get("doc", ""),
            "court": data.get("docsource", ""),
            "date": data.get("publishdate", ""),
            "citations": data.get("numcitedby", 0),
            "url": f"https://indiankanoon.org/doc/{doc_id}/",
        }
