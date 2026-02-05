import os
from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# --- 1. Esquemas de Validación (Pydantic) ---
# Estos modelos aseguran que Gemini responda con el formato JSON requerido [cite: 15-29]

class AnalysisSchema(BaseModel):
    sentiment: str = Field(description="Sentimiento: 'positivo', 'negativo' o 'neutral'")
    sentiment_score: float = Field(description="Score de 0.0 a 1.0", ge=0, le=1)
    tone: str = Field(description="Tono del orador (formal, técnico, etc.)")
    key_points: List[str] = Field(description="Lista de los 3 puntos clave")

class VideoMetadataSchema(BaseModel):
    title: str
    duration_seconds: int
    language_code: str

# --- 2. Definición del Estado del Grafo ---
class GraphState(TypedDict):
    video_url: str
    transcript: str
    metadata: Dict[str, Any]
    analysis: Dict[str, Any]
    errors: List[str]

# --- 3. Inicialización de Gemini ---
# Usamos el modelo flash para velocidad o pro para razonamiento profundo
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
structured_llm = llm.with_structured_output(AnalysisSchema)

# --- 4. Definición de Nodos Asíncronos ---

async def extraction_node(state: GraphState) -> Dict[str, Any]:
    """Extrae la transcripción y metadata (Placeholder para lógica de YouTube)[cite: 12]."""
    # Aquí irá la lógica de youtube-transcript-api
    return {
        "transcript": "Texto de ejemplo extraído del video...",
        "metadata": {
            "title": "Video de Prueba",
            "duration_seconds": 120,
            "language_code": "es"
        }
    }

async def analysis_node(state: GraphState) -> Dict[str, Any]:
    """Usa Gemini para analizar sentimiento, tono y puntos clave[cite: 13, 14]."""
    prompt = f"Analiza la siguiente transcripción de video:\n\n{state['transcript']}"
    
    # Invocación estructurada para garantizar el JSON Output [cite: 14]
    response = await structured_llm.ainvoke(prompt)
    
    return {"analysis": response.dict()}

async def persistence_node(state: GraphState) -> Dict[str, Any]:
    """Persiste los resultados en PostgreSQL mediante el ORM de Django[cite: 30]."""
    # Aquí llamaremos a nuestro adaptador de persistencia (Arquitectura Hexagonal)
    print(f"Guardando en DB: {state['metadata']['title']}")
    return state

# --- 5. Construcción del Grafo ---
workflow = StateGraph(GraphState)

workflow.add_node("extract", extraction_node)
workflow.add_node("analyze", analysis_node)
workflow.add_node("persist", persistence_node)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "analyze")
workflow.add_edge("analyze", "persist")
workflow.add_edge("persist", END)

app = workflow.compile()