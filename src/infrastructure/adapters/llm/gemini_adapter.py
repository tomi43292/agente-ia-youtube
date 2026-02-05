"""
Adaptador para Google Gemini.

Implementación concreta de LLMInterface para el servicio Google Generative AI (Gemini).
Proporciona acceso a los modelos gemini-2.0-flash, gemini-1.5-flash y otros.

Environment Variables:
    GOOGLE_API_KEY: API key de Google AI Studio (requerido).
    GEMINI_MODEL: Modelo a utilizar (default: gemini-2.0-flash).


Example:
    >>> adapter = GeminiAdapter(model="gemini-2.0-flash")
    >>> structured = adapter.with_structured_output(VideoAnalysis)
    >>> result = await structured.ainvoke("Analiza este video...")
"""
import os
from typing import Type, TypeVar

from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

from .interface import LLMInterface, StructuredLLM
from .exceptions import LLMInferenceError, LLMConfigurationError


T = TypeVar('T', bound=BaseModel)


class GeminiStructuredLLM(StructuredLLM[T]):
    """
    Wrapper para Gemini con salida estructurada.
    
    Utiliza el método with_structured_output de LangChain para garantizar
    que las respuestas cumplan con el schema Pydantic especificado.
    """
    
    def __init__(self, llm_with_schema):
        """
        Inicializa el wrapper estructurado.
        
        Args:
            llm_with_schema: Instancia de ChatGoogleGenerativeAI configurada
                           con with_structured_output().
        """
        self._llm = llm_with_schema.with_retry()
    
    async def ainvoke(self, prompt: str) -> T:
        """
        Invoca Gemini de forma asíncrona.
        
        Args:
            prompt: Texto de entrada para el modelo.
        
        Returns:
            Instancia del schema Pydantic con los datos extraídos.
        
        Raises:
            LLMInferenceError: Si Gemini falla al procesar la solicitud.
        """
        try:
            result = await self._llm.ainvoke(prompt)
            return result
        except Exception as e:
            raise LLMInferenceError(
                message=f"Error calling Gemini: {str(e)}",
                provider="gemini",
                original_error=e
            )


class GeminiAdapter(LLMInterface[T]):
    """
    Adaptador para Google Gemini.
    
    Implementa LLMInterface para proporcionar acceso a los modelos de
    Google Generative AI a través de LangChain.
    
    Attributes:
        model: Nombre del modelo (ej: gemini-2.0-flash).
        temperature: Control de creatividad (0-1).
    
    Raises:
        LLMConfigurationError: Si GOOGLE_API_KEY no está configurada.
    """
    
    # Modelos disponibles con sus características
    AVAILABLE_MODELS = {
        "gemini-2.0-flash": "Rápido, ideal para tareas generales",
        "gemini-2.0-flash-lite": "Más económico, menor latencia",
        "gemini-1.5-flash": "Balance entre velocidad y calidad",
        "gemini-1.5-pro": "Mayor calidad, más costoso",
    }
    
    def __init__(
        self, 
        model: str = None, 
        temperature: float = 0.0
    ):
        """
        Inicializa el adaptador de Gemini.
        
        Args:
            model: Nombre del modelo. Si no se especifica, usa GEMINI_MODEL
                  de las variables de entorno o "gemini-2.0-flash" por defecto.
            temperature: Nivel de creatividad (0 = determinístico).
        
        Raises:
            LLMConfigurationError: Si falta la API key.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "GOOGLE_API_KEY no está configurada. "
                "Obtén una en: https://aistudio.google.com/"
            )
        
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.temperature = temperature
        
        self._llm = ChatGoogleGenerativeAI(
            model=self.model,
            temperature=self.temperature,
            google_api_key=api_key
        )
    
    def with_structured_output(self, schema: Type[T]) -> GeminiStructuredLLM[T]:
        """
        Configura Gemini para devolver respuestas estructuradas.
        
        Args:
            schema: Clase Pydantic que define la estructura de respuesta.
        
        Returns:
            GeminiStructuredLLM configurado con el schema.
        """
        llm_with_schema = self._llm.with_structured_output(schema)
        return GeminiStructuredLLM(llm_with_schema)
    
    def __repr__(self) -> str:
        return f"GeminiAdapter(model='{self.model}', temperature={self.temperature})"
