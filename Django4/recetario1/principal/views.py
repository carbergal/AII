#encoding:utf-8
from principal.models import Receta, Comentario
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.conf import settings

#muestra una pantalla con el título del proyecto. Es un html estático
def sobre(request):
    html="<html><body>Proyecto de ejemplo de vistas</body></htm>"
    return HttpResponse(html)

#muestra los títulos de las recetas que están registradas
def inicio(request):
    recetas=Receta.objects.all()
    return render(request,'inicio.html', {'recetas':recetas})

#muestra los datos de los usuarios y las recetas que han registrado
def usuarios(request):
    usuarios=User.objects.all()
    return render(request,'usuarios.html', {'usuarios':usuarios})

#muestra el título de las recetas registradas (con un enlace a detalle de la misma) y una foto
def lista_recetas(request):
    recetas=Receta.objects.all()
    return render(request,'recetas.html', {'datos':recetas,'MEDIA_URL': settings.MEDIA_URL})

#muestra detalles de una receta (imagen, ingredientes, preparación y comentarios de los usuarios)
def detalle_receta(request, id_receta):
    dato = get_object_or_404(Receta, pk=id_receta)
    comentarios=Comentario.objects.filter(receta=dato)
    return render(request,'receta.html',{'receta':dato, 'comentarios':comentarios,'MEDIA_URL': settings.MEDIA_URL})