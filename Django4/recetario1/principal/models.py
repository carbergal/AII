#encoding:utf-8
from django.db import models
#usamos el modelo User de Django para almacenar los datos de los usuarios de la aplicación
from django.contrib.auth.models import User  

#datos de las recetas 
class Receta(models.Model):
    titulo = models.CharField(max_length=100, unique=True)
    ingredientes = models.TextField(help_text='Redacta los ingredientes')
    prepacion = models.TextField(verbose_name='Preparacion')
    #las imágenes de las recetas subidas por los usuarios se almacenan el el directorio 'recetas' dentro
    #del directorio 'media'. El directorio 'media' se indica en MEDIA_ROOT y MEDIA_URL (mirar settings.py)
    imagen = models.ImageField(upload_to= 'recetas', verbose_name='Imagen')
    tiempo_registro = models.DateTimeField(auto_now=True)
    #el modelo Receta tiene una relación uno a muchos con el modelo User
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.titulo

#comentarios de las recetas
class Comentario(models.Model):
    texto = models.TextField(help_text='Tu comentario', verbose_name='Comentario')
    #el modelo Comentario tiene una relación uno a muchos con el modelo Receta
    receta = models.ForeignKey(Receta,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.texto