"""
Factory para proveedores de LLM.

Implementa el patrón Factory para crear el adaptador LLM correcto basándose
en la configuración de variables de entorno. Esto permite cambiar de proveedor
(Gemini, Groq, etc.) sin modificar código, solo cambiando variables de entorno.

La selección del proveedor sigue esta prioridad:
1. Parámetro `provider` pasado directamente a la función
2. Variable de entorno `LLM_PROVIDER`
3. Default: "gemini"

Environment Variables:
    LLM_PROVIDER: Proveedor a usar ("gemini" o "groq").
    GOOGLE_API_KEY: Requerido si LLM_PROVIDER=gemini.
    GROQ_API_KEY: Requerido si LLM_PROVIDER=groq.
    GEMINI_MODEL: Modelo de Gemini (opcional).
    GROQ_MODEL: Modelo de Groq (opcional).

Example:
    >>> # Uso básico (lee LLM_PROVIDER de .env)
    >>> adapter = get_llm_adapter()
    >>> 
    >>> # Forzar un proveedor específico
    >>> groq_adapter = get_llm_adapter(provider="groq")
    >>> 
    >>> # Usar en el workflow
    >>> structured_llm = adapter.with_structured_output(VideoAnalysis)
    >>> result = await structured_llm.ainvoke("Analiza...")
"""
import os
import logging
from typing import Optional

from .interface import LLMInterface
from .gemini_adapter import GeminiAdapter
from .groq_adapter import GroqAdapter
from .exceptions import LLMConfigurationError


logger = logging.getLogger(__name__)


# Registro de proveedores disponibles
_PROVIDERS = {
    "gemini": GeminiAdapter,
    "groq": GroqAdapter,
}


def get_llm_adapter(provider: Optional[str] = None) -> LLMInterface:
    """
    Factory principal para obtener un adaptador LLM.
    
    Crea y devuelve una instancia del adaptador LLM correspondiente
    al proveedor especificado o al configurado en las variables de entorno.
    
    Args:
        provider: Nombre del proveedor ("gemini", "groq"). 
                 Si es None, usa la variable LLM_PROVIDER.
    
    Returns:
        LLMInterface: Instancia del adaptador configurado y listo para usar.
    
    Raises:
        LLMConfigurationError: Si el proveedor no es válido o falta configuración.
    
    Example:
        >>> # Uso típico en graph.py
        >>> from infrastructure.adapters.llm import get_llm_adapter
        >>> adapter = get_llm_adapter()
        >>> structured_llm = adapter.with_structured_output(VideoAnalysis)
    
    Note:
        Para agregar un nuevo proveedor:
        1. Crear clase que implemente LLMInterface
        2. Agregar al diccionario _PROVIDERS
        3. Agregar variables de entorno correspondientes
    """
    provider_name = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
    
    if provider_name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise LLMConfigurationError(
            f"Proveedor LLM '{provider_name}' no soportado. "
            f"Opciones disponibles: {available}"
        )
    
    adapter_class = _PROVIDERS[provider_name]
    
    logger.info(f"Inicializando LLM adapter: {provider_name}")
    
    try:
        adapter = adapter_class()
        logger.info(f"LLM adapter creado: {adapter}")
        return adapter
    except LLMConfigurationError:
        raise
    except Exception as e:
        raise LLMConfigurationError(
            f"Error al inicializar {provider_name}: {str(e)}"
        )


def list_available_providers() -> dict:
    """
    Lista los proveedores LLM disponibles y sus modelos.
    
    Returns:
        dict: Diccionario con proveedores y sus modelos disponibles.
    
    Example:
        >>> providers = list_available_providers()
        >>> print(providers)
        {
            'gemini': ['gemini-2.0-flash', 'gemini-1.5-flash', ...],
            'groq': ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768', ...]
        }
    """
    return {
        name: list(cls.AVAILABLE_MODELS.keys())
        for name, cls in _PROVIDERS.items()
    }
