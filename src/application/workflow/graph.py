"""
Orquestador de Agentes (LangGraph).
Define el flujo de trabajo asíncrono desde la extracción hasta la persistencia[cite: 11, 33].
"""
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from domain.models import VideoAnalysis
from infrastructure.adapters.youtube_adapter import YouTubeAdapter

class GraphState(TypedDict):
    video_url: str
    transcript: str
    metadata: Dict[str, Any]
    analysis: Dict[str, Any]
    errors: List[str]

# Inicialización de componentes (Inyección manual para este challenge)
yt_adapter = YouTubeAdapter()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
structured_llm = llm.with_structured_output(VideoAnalysis)

async def extraction_node(state: GraphState):
    """Nodo 1: Obtención de datos brutos[cite: 12]."""
    try:
        data = await yt_adapter.fetch_full_data(state["video_url"])
        return {**data, "errors": []}
    except Exception as e:
        return {"errors": [str(e)]}

async def analysis_node(state: GraphState):
    """Nodo 2 & 3: Análisis de sentimiento, tono y estructuración[cite: 13, 14]."""
    if state.get("errors"): return state
    
    prompt = f"Analiza esta transcripción y extrae sentimiento, tono y 3 puntos clave:\n\n{state['transcript']}"
    result = await structured_llm.ainvoke(prompt)
    return {"analysis": result.dict()}

async def persistence_node(state: GraphState):
    """Nodo 4: Persistencia final en base de datos[cite: 30]."""
    # Aquí irá la lógica del repositorio Django
    print("Guardando resultado en Postgres...")
    return state

# Configuración del Grafo
workflow = StateGraph(GraphState)
workflow.add_node("extract", extraction_node)
workflow.add_node("analyze", analysis_node)
workflow.add_node("persist", persistence_node)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "analyze")
workflow.add_edge("analyze", "persist")
workflow.add_edge("persist", END)

app = workflow.compile()