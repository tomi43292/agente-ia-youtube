"""
Domain Layer Package.

Contiene los modelos de dominio y reglas de negocio de la aplicación.
Esta es la capa central de Clean Architecture, independiente de frameworks.

Exports:
    VideoAnalysis: Modelo Pydantic para el resultado del análisis de IA.
    VideoMetadata: Modelo Pydantic para metadata técnica del video.
"""
from .models import VideoAnalysis, VideoMetadata

__all__ = ["VideoAnalysis", "VideoMetadata"]
