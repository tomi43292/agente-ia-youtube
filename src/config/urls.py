"""
URL principal del proyecto. 
Orquesta los diferentes módulos del sistema mediante el patrón 'include'.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/videos/', include('infrastructure.api.urls')),
]