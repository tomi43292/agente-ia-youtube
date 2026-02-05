"""
Configuración de rutas para el módulo de API.
Define los puntos de entrada para la funcionalidad de análisis de video.
"""
from django.urls import path
from .views import VideoAnalysisView

urlpatterns = [
    path('analyze/', VideoAnalysisView.as_view(), name='video-analyze'),
]