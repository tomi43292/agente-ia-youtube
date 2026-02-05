"""
Adaptador para la extracción de datos de YouTube.
Encapsula la complejidad de 'youtube-transcript-api' y maneja la concurrencia[cite: 12].
"""
import asyncio
from typing import Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

class YouTubeAdapter:
    def __init__(self):
        self.formatter = TextFormatter()

    async def fetch_full_data(self, video_url: str) -> Dict[str, Any]:
        """
        Obtiene la transcripción de forma asíncrona.
        Nota: 'youtube_transcript_api' es síncrona, por lo que se ejecuta en un thread aparte
        para no bloquear el event loop de la aplicación.
        """
        video_id = self._extract_id(video_url)
        
        # Ejecución en thread pool para mantener la asincronía de la app
        loop = asyncio.get_event_loop()
        transcript_text = await loop.run_in_executor(None, self._get_transcript, video_id)
        
        return {
            "transcript": transcript_text,
            "metadata": {
                "title": f"Video {video_id}", # Idealmente usar otra API para el título real
                "duration_seconds": 0,        # Placeholder
                "language_code": "es"
            }
        }

    def _extract_id(self, url: str) -> str:
        if "v=" in url: return url.split("v=")[1][:11]
        return url.split("/")[-1][:11]

    def _get_transcript(self, video_id: str) -> str:
        try:
            raw = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
            return self.formatter.format_transcript(raw)
        except Exception as e:
            raise ValueError(f"Error extrayendo audio/subtítulos: {str(e)} [cite: 41]")