"""
Capa de Aplicación: Orquestación de casos de uso.
Aquí reside la lógica que conecta los adaptadores de entrada con el dominio y el workflow.
"""
from application.workflow.graph import app
from infrastructure.persistence.models import VideoRecord

class AnalyzeVideoUseCase:
    """
    Caso de Uso: Analizar y persistir información de un video.
    Encapsula el disparo del grafo y asegura la consistencia de los datos.
    """
    
    @staticmethod
    async def execute(video_url: str) -> VideoRecord:
        """
        Ejecuta el flujo de agentes y persiste el resultado.
        
        Args:
            video_url (str): URL validada del video.
            
        Returns:
            VideoRecord: Instancia del modelo guardada en DB.
        """
        # 1. Disparar el grafo de LangGraph de forma asíncrona
        initial_state = {"video_url": video_url, "errors": []}
        final_state = await app.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise ValueError(f"Error en el workflow: {final_state['errors'][0]}")

        # 2. Persistencia (Delegada aquí para asegurar el cumplimiento del nodo de persistencia [cite: 30])
        # Nota: En una arquitectura más estricta, esto iría dentro del persist_node 
        # usando un repositorio inyectado.
        record = VideoRecord.objects.create(
            url=video_url,
            title=final_state["metadata"]["title"],
            transcript=final_state["transcript"],
            duration_seconds=final_state["metadata"]["duration_seconds"],
            language_code=final_state["metadata"]["language_code"],
            sentiment=final_state["analysis"]["sentiment"],
            sentiment_score=final_state["analysis"]["sentiment_score"],
            tone=final_state["analysis"]["tone"],
            key_points=final_state["analysis"]["key_points"]
        )
        
        return record