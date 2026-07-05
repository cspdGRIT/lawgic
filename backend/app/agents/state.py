from typing import TypedDict, Optional, List, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    intent: str  # case_analysis, document_generation, legal_research, translation, lawyer_matching, general
    case_context: Optional[dict]
    research_results: List[dict]
    generated_document: Optional[str]
    lawyer_matches: List[dict]
    final_response: str
    confidence_score: float
    agent_logs: List[str]
    language_target: Optional[str]
