from django.contrib import admin
from principal.models import Receta, Comentario

#registramos en el administrador de django los modelos Receta y Comentario para poder modificarlas
#el modelo User ya está disponible en el admin 
admin.site.register(Receta)
admin.site.register(Comentario)