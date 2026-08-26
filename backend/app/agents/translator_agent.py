from app.agents.state import AgentState
from app.services.claude import get_claude_response

INDIAN_LANGUAGES = {
    "hindi": "Hindi (हिन्दी)",
    "tamil": "Tamil (தமிழ்)",
    "telugu": "Telugu (తెలుగు)",
    "kannada": "Kannada (ಕನ್ನಡ)",
    "malayalam": "Malayalam (മലയാളം)",
    "bengali": "Bengali (বাংলা)",
    "gujarati": "Gujarati (ગુજરાતી)",
    "marathi": "Marathi (मराठी)",
    "punjabi": "Punjabi (ਪੰਜਾਬੀ)",
    "odia": "Odia (ଓଡ଼ିଆ)",
    "assamese": "Assamese (অসমীয়া)",
    "urdu": "Urdu (اردو)",
    "sanskrit": "Sanskrit (संस्कृतम्)",
    "sindhi": "Sindhi (سنڌي)",
    "konkani": "Konkani (कोंकणी)",
    "manipuri": "Manipuri (মৈতৈলোন্)",
    "nepali": "Nepali (नेपाली)",
    "bodo": "Bodo (बड़ो)",
    "santhali": "Santhali (ᱥᱟᱱᱛᱟᱲᱤ)",
    "kashmiri": "Kashmiri (كٲشُر)",
    "dogri": "Dogri (डोगरी)",
    "maithili": "Maithili (मैथिली)",
}

TRANSLATION_SYSTEM = """You are an expert legal translator specializing in translating Indian legal documents between English and all 22 official Indian languages.

When translating:
1. Preserve all legal terminology accurately - use standard legal terms in the target language
2. Keep proper nouns (names, places, case numbers) unchanged
3. Maintain the formal, legal tone of the original
4. For legal terms with no direct translation, use the English term in parentheses after the translated term
5. Ensure the translated text is grammatically correct and natural in the target language
6. Section numbers, article references, and statute names should remain in English/numbers"""


async def translation_node(state: AgentState, db=None) -> AgentState:
    """Translate legal text to specified Indian language."""
    logs = list(state.get("agent_logs", []))
    text_to_translate = state.get("user_query", "")
    target_language = state.get("language_target") or "hindi"
    case_ctx = state.get("case_context") or {}

    if case_ctx.get("text"):
        text_to_translate = case_ctx["text"]

    language_display = INDIAN_LANGUAGES.get(target_language.lower(), target_language)
    logs.append(f"translator_agent: Translating to {language_display}")

    prompt = f"""Translate the following Indian legal text to {language_display}:

---
{text_to_translate}
---

Provide ONLY the translated text, no explanations or notes. Maintain legal accuracy."""

    messages = [{"role": "user", "content": prompt}]
    try:
        translated_text = await get_claude_response(messages, system=TRANSLATION_SYSTEM)
        logs.append(f"translator_agent: Translation complete to {language_display}")
        return {
            **state,
            "final_response": translated_text,
            "confidence_score": 0.88,
            "agent_logs": logs,
        }
    except Exception as e:
        logs.append(f"translator_agent: Error - {str(e)}")
        return {**state, "final_response": f"Translation error: {str(e)}", "agent_logs": logs}


def get_supported_languages() -> dict:
    return INDIAN_LANGUAGES
