"""
Excepciones personalizadas para adaptadores LLM.

Define una jerarquía de excepciones específicas para clasificar diferentes
tipos de errores que pueden ocurrir durante la inferencia con LLMs.
"""


class LLMError(Exception):
    """Excepción base para todos los errores relacionados con LLM."""
    pass


class LLMInferenceError(LLMError):
    """
    Error durante la inferencia del modelo.
    
    Se lanza cuando el LLM no puede generar una respuesta válida,
    ya sea por problemas de red, rate limiting, o errores del servicio.
    
    Attributes:
        provider: Nombre del proveedor (gemini, groq, etc.)
        model: Modelo específico que falló.
        original_error: Excepción original capturada.
    """
    
    def __init__(self, message: str, provider: str = None, model: str = None, original_error: Exception = None):
        self.provider = provider
        self.model = model
        self.original_error = original_error
        super().__init__(message)


class LLMRateLimitError(LLMError):
    """
    Error por exceder límites de rate del API.
    
    Indica que se debe esperar antes de reintentar la solicitud.
    
    Attributes:
        retry_after_seconds: Tiempo sugerido de espera antes de reintentar.
    """
    
    def __init__(self, message: str, retry_after_seconds: float = None):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(message)


class LLMConfigurationError(LLMError):
    """
    Error de configuración del adaptador LLM.
    
    Se lanza cuando faltan API keys, el proveedor no es válido,
    o hay problemas con las variables de entorno.
    """
    pass
