"""Legacy shim — delegates to the unified LLM service."""
from app.services.llm import get_llm_response, stream_llm_response, SYSTEM_PROMPT

get_claude_response = get_llm_response
stream_claude_response = stream_llm_response

__all__ = ["get_claude_response", "stream_claude_response", "SYSTEM_PROMPT"]
