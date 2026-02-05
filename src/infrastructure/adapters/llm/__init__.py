"""
LLM Adapters Package.

Proporciona una capa de abstracción para diferentes proveedores de LLM,
permitiendo cambiar entre Gemini, Groq y otros sin modificar código.

Usage:
    >>> from infrastructure.adapters.llm import get_llm_adapter
    >>> adapter = get_llm_adapter()  # Lee LLM_PROVIDER de .env
"""
from .factory import get_llm_adapter, list_available_providers
from .interface import LLMInterface, StructuredLLM
from .exceptions import LLMError, LLMInferenceError, LLMConfigurationError

__all__ = [
    "get_llm_adapter",
    "list_available_providers",
    "LLMInterface",
    "StructuredLLM",
    "LLMError",
    "LLMInferenceError",
    "LLMConfigurationError",
]
