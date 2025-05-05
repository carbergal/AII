"""recetario1 URL Configuration


"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
import django.views
from principal import views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # permite visualizar imagenes con la url http://127.0.0.1:8000/media/recetas/nombre-imagen.jpg
    path('media/<path>', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    path('sobre/',views.sobre),
    path('usuarios/', views.usuarios),
    path('recetas/', views.lista_recetas),
    path('recetas/receta/<int:id_receta>',views.detalle_receta),
    path('',views.inicio),
    ]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# agregado de static para permitir la visulaización de las imagenes desde la BD en las plantillas
