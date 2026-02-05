"""
Orquestador de Agentes (LangGraph).
Implementa aristas condicionales y reintentos para resiliencia [cite: 40-41].
"""
import operator
from typing import Dict, Any, TypedDict, List, Annotated, Union
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from domain.models import VideoAnalysis
from infrastructure.adapters.youtube_adapter import YouTubeAdapter, YouTubeError

# --- 1. Estado con Reductor de Errores ---
class GraphState(TypedDict):
    video_url: str
    transcript: str
    metadata: Dict[str, Any]
    analysis: Dict[str, Any]
    # annotated con operator.add permite que múltiples nodos acumulen errores
    errors: Annotated[List[str], operator.add]

# --- 2. Inicialización con Reintentos ---
yt_adapter = YouTubeAdapter()
# with_retry activa el mecanismo de backoff exponencial ante cuotas de API
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0).with_retry()
structured_llm = llm.with_structured_output(VideoAnalysis)

async def extraction_node(state: GraphState):
    """Nodo de extracción con captura de errores clasificados."""
    try:
        data = await yt_adapter.fetch_full_data(state["video_url"])
        return {**data, "errors": []}
    except YouTubeError as e:
        return {"errors": [str(e)]}

async def analysis_node(state: GraphState):
    """Análisis con Gemini garantizando la estructura de salida."""
    prompt = f"Analiza esta transcripción:\n\n{state['transcript']}"
    try:
        result = await structured_llm.ainvoke(prompt)
        return {"analysis": result.dict()}
    except Exception as e:
        return {"errors": [f"Fallo en LLM: {str(e)}"]}

# --- 3. Lógica de Ruteo (Conditional Edge) ---
def should_continue(state: GraphState) -> str:
    """Determina si el flujo debe abortar por errores críticos[cite: 40]."""
    if state.get("errors"):
        return "end"
    return "continue"

workflow = StateGraph(GraphState)
workflow.add_node("extract", extraction_node)
workflow.add_node("analyze", analysis_node)

workflow.set_entry_point("extract")

# Arista condicional: si falla la extracción, termina el flujo
workflow.add_conditional_edges(
    "extract",
    should_continue,
    {"continue": "analyze", "end": END}
)

workflow.add_edge("analyze", END)

app = workflow.compile()