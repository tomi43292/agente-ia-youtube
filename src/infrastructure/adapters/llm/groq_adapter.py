"""
Adaptador para Groq Cloud.

Implementación concreta de LLMInterface para el servicio Groq, que ofrece
inferencia ultra-rápida de modelos open source como Llama 3.3 y Mixtral.

Groq es conocido por su velocidad de inferencia excepcional gracias a sus
chips LPU (Language Processing Unit) diseñados específicamente para LLMs.

Environment Variables:
    GROQ_API_KEY: API key de Groq Console (requerido).
    GROQ_MODEL: Modelo a utilizar (default: llama-3.3-70b-versatile).

Free Tier Limits (aproximados):
    - llama-3.3-70b-versatile: 6,000 tokens/min, ~14,400 req/día
    - llama-3.1-8b-instant: 20,000 tokens/min
    - mixtral-8x7b-32768: 5,000 tokens/min

Example:
    >>> adapter = GroqAdapter(model="llama-3.3-70b-versatile")
    >>> structured = adapter.with_structured_output(VideoAnalysis)
    >>> result = await structured.ainvoke("Analiza este video...")
"""
import os
from typing import Type, TypeVar

from pydantic import BaseModel
from langchain_groq import ChatGroq

from .interface import LLMInterface, StructuredLLM
from .exceptions import LLMInferenceError, LLMConfigurationError


T = TypeVar('T', bound=BaseModel)


class GroqStructuredLLM(StructuredLLM[T]):
    """
    Wrapper para Groq con salida estructurada.
    
    Utiliza el método with_structured_output de LangChain para garantizar
    que las respuestas cumplan con el schema Pydantic especificado.
    """
    
    def __init__(self, llm_with_schema):
        """
        Inicializa el wrapper estructurado.
        
        Args:
            llm_with_schema: Instancia de ChatGroq configurada
                           con with_structured_output().
        """
        self._llm = llm_with_schema.with_retry()
    
    async def ainvoke(self, prompt: str) -> T:
        """
        Invoca Groq de forma asíncrona.
        
        Args:
            prompt: Texto de entrada para el modelo.
        
        Returns:
            Instancia del schema Pydantic con los datos extraídos.
        
        Raises:
            LLMInferenceError: Si Groq falla al procesar la solicitud.
        """
        try:
            result = await self._llm.ainvoke(prompt)
            return result
        except Exception as e:
            raise LLMInferenceError(
                message=f"Error calling Groq: {str(e)}",
                provider="groq",
                original_error=e
            )


class GroqAdapter(LLMInterface[T]):
    """
    Adaptador para Groq Cloud.
    
    Implementa LLMInterface para proporcionar acceso a modelos open source
    con inferencia ultra-rápida a través de Groq.
    
    Attributes:
        model: Nombre del modelo (ej: llama-3.3-70b-versatile).
        temperature: Control de creatividad (0-1).
    
    Raises:
        LLMConfigurationError: Si GROQ_API_KEY no está configurada.
    """
    
    # Modelos disponibles con sus características
    AVAILABLE_MODELS = {
        "llama-3.3-70b-versatile": "Modelo más capaz, excelente para análisis",
        "llama-3.1-8b-instant": "Ultra rápido, bueno para tareas simples",
        "llama-3.1-70b-versatile": "Versión anterior, muy estable",
        "mixtral-8x7b-32768": "Contexto largo (32K tokens), buen balance",
        "gemma2-9b-it": "Modelo de Google, compacto y eficiente",
    }
    
    def __init__(
        self, 
        model: str = None, 
        temperature: float = 0.0
    ):
        """
        Inicializa el adaptador de Groq.
        
        Args:
            model: Nombre del modelo. Si no se especifica, usa GROQ_MODEL
                  de las variables de entorno o "llama-3.3-70b-versatile".
            temperature: Nivel de creatividad (0 = determinístico).
        
        Raises:
            LLMConfigurationError: Si falta la API key.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "GROQ_API_KEY no está configurada. "
                "Obtén una gratis en: https://console.groq.com/"
            )
        
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = temperature
        
        self._llm = ChatGroq(
            model=self.model,
            temperature=self.temperature,
            groq_api_key=api_key
        )
    
    def with_structured_output(self, schema: Type[T]) -> GroqStructuredLLM[T]:
        """
        Configura Groq para devolver respuestas estructuradas.
        
        Args:
            schema: Clase Pydantic que define la estructura de respuesta.
        
        Returns:
            GroqStructuredLLM configurado con el schema.
        """
        llm_with_schema = self._llm.with_structured_output(schema)
        return GroqStructuredLLM(llm_with_schema)
    
    def __repr__(self) -> str:
        return f"GroqAdapter(model='{self.model}', temperature={self.temperature})"
