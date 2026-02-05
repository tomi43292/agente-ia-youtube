"""
Interface abstracta para proveedores de LLM.

Este módulo define el contrato que todos los adaptadores LLM deben implementar,
siguiendo el Principio de Inversión de Dependencias (DIP) de SOLID.

Al usar una interface abstracta, la capa de aplicación (graph.py) depende de
abstracciones en lugar de implementaciones concretas, permitiendo cambiar
fácilmente entre Gemini, Groq u otros proveedores sin modificar el código
de negocio.

Example:
    >>> from infrastructure.adapters.llm.factory import get_llm_adapter
    >>> adapter = get_llm_adapter()  # Lee LLM_PROVIDER de .env
    >>> structured_llm = adapter.with_structured_output(VideoAnalysis)
    >>> result = await structured_llm.ainvoke("Analiza este texto...")
"""
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class LLMInterface(ABC, Generic[T]):
    """
    Interface abstracta para adaptadores de LLM.
    
    Define el contrato mínimo que cualquier proveedor de LLM debe cumplir
    para ser compatible con el sistema de análisis de videos.
    
    Attributes:
        model: Nombre del modelo a utilizar.
        temperature: Parámetro de creatividad (0 = determinístico, 1 = creativo).
    
    Note:
        Los adaptadores concretos (GeminiAdapter, GroqAdapter) deben implementar
        todos los métodos abstractos definidos aquí.
    """
    
    @abstractmethod
    def with_structured_output(self, schema: Type[T]) -> 'StructuredLLM[T]':
        """
        Configura el LLM para devolver respuestas estructuradas.
        
        Args:
            schema: Clase Pydantic que define la estructura esperada de la respuesta.
                   El LLM será instruido para generar JSON válido según este schema.
        
        Returns:
            StructuredLLM: Wrapper que garantiza respuestas tipadas según el schema.
        
        Example:
            >>> structured = adapter.with_structured_output(VideoAnalysis)
            >>> result = await structured.ainvoke("Analiza...")
            >>> print(result.sentiment)  # Acceso tipado
        """
        pass


class StructuredLLM(ABC, Generic[T]):
    """
    Wrapper para LLM con salida estructurada.
    
    Encapsula la lógica de parsing y validación de respuestas del LLM
    contra un schema Pydantic específico.
    """
    
    @abstractmethod
    async def ainvoke(self, prompt: str) -> T:
        """
        Invoca el LLM de forma asíncrona y devuelve una respuesta estructurada.
        
        Args:
            prompt: Texto de entrada para el LLM.
        
        Returns:
            Instancia del schema Pydantic configurado con los datos extraídos.
        
        Raises:
            LLMInferenceError: Si el LLM falla al generar una respuesta válida.
            ValidationError: Si la respuesta no cumple con el schema Pydantic.
        """
        pass
