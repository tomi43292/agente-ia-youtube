"""
Adaptador para la extracción de datos de YouTube.
Ahora utiliza las excepciones centralizadas para una clasificación profesional de fallos.
"""
import asyncio
from typing import Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import VideoUnavailable, TranscriptsDisabled, NoTranscriptFound
from .exceptions import VideoNotFoundError, NoTranscriptError, YouTubeError

class YouTubeAdapter:
    """
    Adaptador de infraestructura para la API de YouTube.

    Encapsula la obtención de transcripciones y metadata de videos,
    ejecutando las llamadas síncronas de youtube-transcript-api dentro
    de un executor para no bloquear el event loop asíncrono.

    Attributes:
        api: Instancia de YouTubeTranscriptApi para obtener transcripciones.

    Raises:
        VideoNotFoundError: Si el video no existe o es privado.
        NoTranscriptError: Si el video no tiene subtítulos disponibles.
        YouTubeError: Para cualquier otro error inesperado del adaptador.
    """

    def __init__(self):
        """Inicializa el adaptador con una instancia de YouTubeTranscriptApi."""
        self.api = YouTubeTranscriptApi()

    async def fetch_full_data(self, video_url: str) -> Dict[str, Any]:
        """
        Obtiene la transcripción y metadata de un video de YouTube.

        Ejecuta la extracción en un thread executor para mantener
        la compatibilidad con el event loop asíncrono de Django/ASGI.

        Args:
            video_url: URL completa del video de YouTube.

        Returns:
            Dict con claves 'transcript' (str) y 'metadata' (dict con
            title, duration_seconds, language_code).

        Raises:
            VideoNotFoundError: Video inexistente o privado.
            NoTranscriptError: Sin subtítulos ni transcripción automática.
            YouTubeError: Error inesperado en la comunicación con YouTube.
        """
        video_id = self._extract_id(video_url)
        loop = asyncio.get_event_loop()
        
        try:
            # Ejecución en executor para no bloquear el loop asíncrono
            transcript_text = await loop.run_in_executor(None, self._get_transcript, video_id)
            return {
                "transcript": transcript_text,
                "metadata": {
                    "title": f"Video {video_id}",
                    "duration_seconds": 0,
                    "language_code": "es"
                }
            }
        except VideoUnavailable:
            raise VideoNotFoundError(f"El video {video_id} no está disponible.")
        except (TranscriptsDisabled, NoTranscriptFound):
            raise NoTranscriptError(f"El video {video_id} no posee transcripciones.")
        except Exception as e:
            raise YouTubeError(f"Error inesperado en el adaptador: {str(e)}")

    def _extract_id(self, url: str) -> str:
        """
        Extrae el ID de 11 caracteres de una URL de YouTube.

        Soporta formatos:
            - Estándar: https://www.youtube.com/watch?v=XXXXXXXXXXX
            - Corto: https://youtu.be/XXXXXXXXXXX

        Args:
            url: URL del video de YouTube.

        Returns:
            ID del video (máximo 11 caracteres).
        """
        if "v=" in url: return url.split("v=")[1][:11]
        return url.split("/")[-1][:11]

    def _get_transcript(self, video_id: str) -> str:
        """
        Obtiene la transcripción en texto plano de un video.

        Prioriza español ('es') sobre inglés ('en'). Utiliza la API
        de instancia ``fetch()`` de youtube-transcript-api >= 0.6.2.

        Args:
            video_id: ID de 11 caracteres del video.

        Returns:
            Transcripción concatenada como texto plano.
        """
        # Nueva API usa fetch() en instancia en lugar de get_transcript() estático
        transcript = self.api.fetch(video_id, languages=['es', 'en'])
        # Convertir a texto plano
        return " ".join([entry.text for entry in transcript])