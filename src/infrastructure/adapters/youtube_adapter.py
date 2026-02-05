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
    def __init__(self):
        self.api = YouTubeTranscriptApi()

    async def fetch_full_data(self, video_url: str) -> Dict[str, Any]:
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
        if "v=" in url: return url.split("v=")[1][:11]
        return url.split("/")[-1][:11]

    def _get_transcript(self, video_id: str) -> str:
        # Nueva API usa fetch() en instancia en lugar de get_transcript() estático
        transcript = self.api.fetch(video_id, languages=['es', 'en'])
        # Convertir a texto plano
        return " ".join([entry.text for entry in transcript])