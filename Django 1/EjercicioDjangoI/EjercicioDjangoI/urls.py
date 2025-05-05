
from django.contrib import admin
from django.urls import path
from principal import views

urlpatterns = [  
    path('', views.inicio),
    path('estadiosMayores/', views.estadios_mayores),
    path('ultimaTemporada/', views.ultima_temporada),
    path('cargar/', views.cargar),
    path('equipos/', views.lista_equipos),
    path('equipos/equipo/<int:id_equipo>', views.detalle_equipo),
    path('admin/', admin.site.urls),
]
