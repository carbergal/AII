from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('ocupaciones_usuarios/',views.mostrar_ocupaciones),
    path('puntuaciones_usuario/',views.mostrar_puntuaciones_usuario),
    #pasamos el parametro <int:pag> para la paginacion
    path('mejores_peliculas/<int:pag>',views.mostrar_mejores_peliculas),
    path('busqueda_peliculas/',views.mostrar_peliculas_year),
    path('',views.index),
    path('index.html/', views.index),
    path('populate/', views.populateDatabase),
    path('ingresar/', views.ingresar),    
    path('admin/',admin.site.urls),
    ]
