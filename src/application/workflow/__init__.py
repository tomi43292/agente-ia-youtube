"""
Application Workflow Package.

Contiene el orquestador de agentes basado en LangGraph que procesa
los videos de YouTube en un flujo de trabajo estructurado.

El grafo principal implementa:
    - Extracción de transcripciones y metadata
    - Análisis de sentimiento, tono y puntos clave con LLM
    - Manejo de errores mediante aristas condicionales

Exports:
    app: Grafo compilado listo para invocar.
"""
from .graph import app

__all__ = ["app"]
