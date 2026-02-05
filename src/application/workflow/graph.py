"""
Orquestador de Agentes (LangGraph).
Implementa aristas condicionales y reintentos para resiliencia.
"""
import operator
from typing import Dict, Any, TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from domain.models import VideoAnalysis
from infrastructure.adapters.youtube_adapter import YouTubeAdapter
from infrastructure.adapters.exceptions import InfrastructureError

class GraphState(TypedDict):
    video_url: str
    transcript: str
    metadata: Dict[str, Any]
    analysis: Dict[str, Any]
    # Annotated con operator.add permite acumular errores de múltiples nodos
    errors: Annotated[List[str], operator.add]

# --- Inicialización de Componentes ---
yt_adapter = YouTubeAdapter()

# 1. Instanciar el modelo base de Gemini
llm_base = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# 2. Configurar la salida estructurada y LUEGO aplicar la lógica de reintento.
# Esto asegura que el retry cubra tanto la generación como el parseo del esquema.
structured_llm = llm_base.with_structured_output(VideoAnalysis).with_retry()

async def extraction_node(state: GraphState):
    """Nodo 1: Extracción con captura de errores clasificados."""
    try:
        data = await yt_adapter.fetch_full_data(state["video_url"])
        return {**data, "errors": []}
    except InfrastructureError as e:
        return {"errors": [str(e)]}

async def analysis_node(state: GraphState):
    """Nodo 2: Análisis de IA con validación de esquema."""
    if state.get("errors"): return state
    try:
        prompt = f"Analiza esta transcripción y extrae sentimiento, tono y 3 puntos clave:\n\n{state['transcript']}"
        result = await structured_llm.ainvoke(prompt)
        return {"analysis": result.dict()}
    except Exception as e:
        return {"errors": [f"Error en análisis de IA: {str(e)}"]}

def should_continue(state: GraphState) -> str:
    """Router para manejo de errores en el flujo."""
    return "end" if state.get("errors") else "continue"

# --- Configuración del Grafo ---
workflow = StateGraph(GraphState)
workflow.add_node("extract", extraction_node)
workflow.add_node("analyze", analysis_node)

workflow.set_entry_point("extract")
workflow.add_conditional_edges("extract", should_continue, {"continue": "analyze", "end": END})
workflow.add_edge("analyze", END)

app = workflow.compile()