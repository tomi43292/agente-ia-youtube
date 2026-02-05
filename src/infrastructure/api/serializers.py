"""
Módulo de Serialización: Define los contratos de entrada y salida para la API REST.
Utiliza Django REST Framework para validar la integridad de las peticiones HTTP.
"""
from rest_framework import serializers
from infrastructure.persistence.models import VideoRecord

class VideoInputSerializer(serializers.Serializer):
    """
    DTO (Data Transfer Object) para la entrada de datos.
    Valida que la URL proporcionada sea sintácticamente correcta antes de procesarla.
    """
    video_url = serializers.URLField(
        required=True, 
        help_text="URL del video de YouTube a procesar"
    )

class VideoRecordSerializer(serializers.ModelSerializer):
    """
    Mapea el modelo de persistencia a una respuesta JSON estructurada.
    Incluye todos los campos requeridos por el desafío [cite: 15-29].
    """
    class Meta:
        model = VideoRecord
        fields = [
            'id', 'url', 'title', 'transcript', 'duration_seconds', 
            'language_code', 'sentiment', 'sentiment_score', 
            'tone', 'key_points', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']