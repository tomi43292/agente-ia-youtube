"""
Módulo de Vistas: Adaptadores de entrada para el protocolo HTTP.
Implementa controladores asíncronos para maximizar el throughput de la API.
"""
from adrf.views import APIView  # pip install django-adrf para soporte async nativo en DRF
from rest_framework.response import Response
from rest_framework import status
from .serializers import VideoInputSerializer, VideoRecordSerializer
from application.use_cases.use_cases import AnalyzeVideoUseCase

class VideoAnalysisView(APIView):
    """
    Endpoint principal para disparar el grafo de análisis[cite: 11].
    Soporta ejecución asíncrona para no bloquear el servidor durante el procesamiento de la IA.
    """

    async def post(self, request):
        """
        Recibe una URL de video y retorna el análisis estructurado.
        """
        serializer = VideoInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            video_url = serializer.validated_data['video_url']
            
            # Ejecución del Caso de Uso
            result_record = await AnalyzeVideoUseCase.execute(video_url)
            
            # Respuesta serializada
            output_serializer = VideoRecordSerializer(result_record)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Senior error handling: Logging detallado y respuesta amigable
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )