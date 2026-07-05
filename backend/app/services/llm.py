"""
Unified LLM service via LiteLLM.
Supports: anthropic, openai, groq, google, cohere, nvidia, ollama, and 100+ more.

Set in .env:
  LLM_PROVIDER=anthropic          # active provider: anthropic|openai|groq|google|cohere|nvidia|ollama
  LLM_MODEL=                      # optional override (blank = use provider default)
  ANTHROPIC_API_KEY=sk-ant-...
  OPENAI_API_KEY=sk-...
  GROQ_API_KEY=gsk_...
  GOOGLE_API_KEY=AIza...
  COHERE_API_KEY=...
  NVIDIA_API_KEY=nvapi-...        # build.nvidia.com/nim → free credits
  OLLAMA_BASE_URL=http://localhost:11434
  REDIS_URL=redis://localhost:6379 # optional: enables Redis-backed LLM cache
"""
import asyncio
import hashlib
import json
import time
from typing import AsyncGenerator, Optional
import os
import litellm
from app.core.config import settings

litellm.telemetry = False

SYSTEM_PROMPT = """You are Lawgic AI, an expert legal assistant specializing in Indian law.
You have deep knowledge of:
- Indian Penal Code (IPC), Code of Criminal Procedure (CrPC), Code of Civil Procedure (CPC)
- Indian Contract Act, Companies Act, Insolvency and Bankruptcy Code (IBC)
- Consumer Protection Act, Right to Information Act, Motor Vehicles Act
- Family Law (Hindu Marriage Act, Muslim Personal Law, Special Marriage Act)
- Property Law (Transfer of Property Act, Registration Act, RERA)
- Labour Law (Industrial Disputes Act, Payment of Wages Act)
- Constitutional Law and Fundamental Rights
- Landmark Supreme Court and High Court judgments

Always provide practical, actionable advice. Mention relevant sections, statutes, and case citations.
Note that you provide legal information, not legal advice. Recommend consulting a qualified lawyer for specific cases.
Always respond in the same language the user writes in unless instructed otherwise."""

# Default model per provider
_PROVIDER_DEFAULTS: dict[str, str] = {
    "anthropic": "anthropic/claude-sonnet-4-6",
    "openai":    "openai/gpt-4o-mini",
    "groq":      "groq/llama-3.3-70b-versatile",
    "google":    "gemini/gemini-1.5-flash",
    "cohere":    "cohere/command-r",
    "nvidia":    "nvidia_nim/meta/llama-3.1-70b-instruct",
    "ollama":    "ollama/llama3.1",
}


def _resolve_model() -> str:
    """Return the litellm model string to use."""
    if settings.LLM_MODEL:
        return settings.LLM_MODEL
    provider = settings.LLM_PROVIDER.lower()
    return _PROVIDER_DEFAULTS.get(provider, f"{provider}/default")


def _set_env() -> None:
    """Push API keys into os.environ so litellm can pick them up."""
    if settings.ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    if settings.GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
    if settings.GOOGLE_API_KEY:
        os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
    if settings.COHERE_API_KEY:
        os.environ["COHERE_API_KEY"] = settings.COHERE_API_KEY
    if settings.NVIDIA_API_KEY:
        os.environ["NVIDIA_NIM_API_KEY"] = settings.NVIDIA_API_KEY
    if settings.OLLAMA_BASE_URL:
        os.environ["OLLAMA_API_BASE"] = settings.OLLAMA_BASE_URL


_set_env()


# ── LLM cache (in-memory + optional Redis) ────────────────────────────────────

# {cache_key: (response_text, expires_at_unix)}
_mem_cache: dict[str, tuple[str, float]] = {}


def _cache_key(model: str, messages: list, system: str) -> str:
    payload = json.dumps({"model": model, "system": system, "messages": messages}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


async def _redis_get(key: str) -> Optional[str]:
    if not settings.REDIS_URL:
        return None
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        val = await r.get(f"llm:{key}")
        await r.aclose()
        return val
    except Exception:
        return None


async def _redis_set(key: str, value: str, ttl: int) -> None:
    if not settings.REDIS_URL:
        return
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.setex(f"llm:{key}", ttl, value)
        await r.aclose()
    except Exception:
        pass


async def _cache_get(key: str) -> Optional[str]:
    now = time.monotonic()
    entry = _mem_cache.get(key)
    if entry:
        text, expires = entry
        if now < expires:
            return text
        del _mem_cache[key]
    return await _redis_get(key)


async def _cache_set(key: str, value: str) -> None:
    ttl = settings.LLM_CACHE_TTL_SECONDS
    _mem_cache[key] = (value, time.monotonic() + ttl)
    await _redis_set(key, value, ttl)


async def get_llm_response(messages: list, system: str = SYSTEM_PROMPT, use_cache: bool = True) -> str:
    """Non-streaming LLM call. Returns full response text. Cached by default."""
    model = _resolve_model()

    if use_cache:
        key = _cache_key(model, messages, system)
        cached = await _cache_get(key)
        if cached is not None:
            return cached

    full_messages = [{"role": "system", "content": system}] + messages
    response = await litellm.acompletion(
        model=model,
        messages=full_messages,
        max_tokens=4096,
    )
    text = response.choices[0].message.content

    if use_cache:
        await _cache_set(key, text)

    return text


async def stream_llm_response(
    messages: list, system: str = SYSTEM_PROMPT
) -> AsyncGenerator[str, None]:
    """Streaming LLM call. Yields text chunks as they arrive."""
    model = _resolve_model()
    full_messages = [{"role": "system", "content": system}] + messages
    response = await litellm.acompletion(
        model=model,
        messages=full_messages,
        max_tokens=4096,
        stream=True,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
