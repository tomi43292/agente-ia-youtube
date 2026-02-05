"""
Módulo de Excepciones de Infraestructura.
Define la jerarquía de errores para los adaptadores externos, permitiendo
que la capa de aplicación reaccione de forma específica a fallos técnicos.
"""

class InfrastructureError(Exception):
    """Excepción base para todos los errores de la capa de infraestructura."""
    pass

class YouTubeError(InfrastructureError):
    """Excepción base para fallos relacionados con la API o librería de YouTube."""
    pass

class VideoNotFoundError(YouTubeError):
    """Se lanza cuando el video solicitado no existe o es privado[cite: 41]."""
    pass

class NoTranscriptError(YouTubeError):
    """Se lanza cuando el video no tiene audio procesable o subtítulos[cite: 41]."""
    pass

class LLMError(InfrastructureError):
    """Excepción para fallos en la comunicación con el proveedor de IA (Gemini)."""
    pass