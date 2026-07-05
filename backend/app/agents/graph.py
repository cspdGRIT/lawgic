from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.case_agent import case_analysis_node
from app.agents.document_agent import document_generation_node
from app.agents.research_agent import legal_research_node
from app.agents.translator_agent import translation_node
from app.agents.lawyer_agent import lawyer_matching_node
from app.services.claude import get_claude_response

INTENT_SYSTEM = """You are an intent classifier for Lawgic, an Indian legal AI platform.
Classify the user's query into exactly ONE of these intents:
- case_analysis: User wants to analyze their legal case, predict outcome, get legal strategy
- document_generation: User wants to generate/draft a legal document
- legal_research: User wants to research Indian laws, find case law, understand statutes
- translation: User wants to translate legal text to/from an Indian language
- lawyer_matching: User wants to find or be matched with a lawyer
- general: General legal question, greeting, or anything that doesn't fit above categories

Return ONLY the intent string, nothing else."""


async def classify_intent_node(state: AgentState, db=None) -> AgentState:
    """Classify user intent to route to appropriate agent."""
    query = state.get("user_query", "")
    logs = list(state.get("agent_logs", []))
    logs.append("classifier: Determining intent")

    messages = [{"role": "user", "content": f"Query: {query}\n\nClassify this query's intent."}]
    try:
        intent = await get_claude_response(messages, system=INTENT_SYSTEM)
        intent = intent.strip().lower()
        valid_intents = {"case_analysis", "document_generation", "legal_research", "translation", "lawyer_matching", "general"}
        if intent not in valid_intents:
            intent = "general"
        logs.append(f"classifier: Intent = {intent}")
    except Exception:
        intent = "general"

    return {**state, "intent": intent, "agent_logs": logs}


async def general_response_node(state: AgentState, db=None) -> AgentState:
    """Handle general legal queries with Claude."""
    from app.services.claude import SYSTEM_PROMPT
    query = state.get("user_query", "")
    logs = list(state.get("agent_logs", []))
    logs.append("general_agent: Handling general query")

    messages = [{"role": "user", "content": query}]
    try:
        response = await get_claude_response(messages, system=SYSTEM_PROMPT)
        return {**state, "final_response": response, "confidence_score": 0.8, "agent_logs": logs}
    except Exception as e:
        return {**state, "final_response": f"Error: {str(e)}", "agent_logs": logs}


async def synthesize_node(state: AgentState, db=None) -> AgentState:
    """Final synthesis node - response is already in state from specialist agent."""
    logs = list(state.get("agent_logs", []))
    logs.append("synthesizer: Response ready")
    return {**state, "agent_logs": logs}


def route_by_intent(state: AgentState) -> str:
    return state.get("intent", "general")


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("case_analysis", case_analysis_node)
    graph.add_node("document_generation", document_generation_node)
    graph.add_node("legal_research", legal_research_node)
    graph.add_node("translation", translation_node)
    graph.add_node("lawyer_matching", lawyer_matching_node)
    graph.add_node("general", general_response_node)
    graph.add_node("synthesize", synthesize_node)

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "case_analysis": "case_analysis",
            "document_generation": "document_generation",
            "legal_research": "legal_research",
            "translation": "translation",
            "lawyer_matching": "lawyer_matching",
            "general": "general",
        },
    )

    for node in ["case_analysis", "document_generation", "legal_research", "translation", "lawyer_matching", "general"]:
        graph.add_edge(node, "synthesize")

    graph.add_edge("synthesize", END)

    return graph.compile()


# Singleton compiled graph
app_graph = build_graph()
