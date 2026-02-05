"""
Módulo de Dominio: Contiene las entidades y esquemas base del negocio.
Utiliza Pydantic para garantizar la integridad de los datos en tiempo de ejecución,
actuando como el contrato principal entre los nodos del grafo.
"""
from pydantic import BaseModel, Field
from typing import List

class VideoAnalysis(BaseModel):
    """
    Representa el resultado final del análisis de IA sobre un video.
    Cumple con el esquema de datos requerido por el challenge.
    """
    sentiment: str = Field(
        ..., 
        description="Sentimiento predominante: 'positivo', 'negativo' o 'neutral'"
    )
    sentiment_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Puntaje de confianza o intensidad del sentimiento"
    )
    tone: str = Field(..., description="Tono detectado del orador")
    key_points: List[str] = Field(
        ..., 
        min_items=3, 
        max_items=3, 
        description="Resumen de los 3 puntos clave del video"
    )

class VideoMetadata(BaseModel):
    """
    Contiene la información técnica extraída del video de YouTube.
    """
    title: str = Field(..., description="Título oficial del video")
    duration_seconds: int = Field(..., description="Duración total en segundos")
    language_code: str = Field(..., description="Código ISO 639-1 del idioma principal")