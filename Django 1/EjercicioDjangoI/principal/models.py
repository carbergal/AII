#encoding:utf-8
from django.db import models


#datos de las temporadas
class Temporada(models.Model):
    #una temporada consta del anyo almacenado y el siguiente
    anyo = models.PositiveSmallIntegerField(unique=True)
    
    def __str__(self):
        return str(self.anyo)+'-'+str(self.anyo+1)
    
#datos de los equipos
class Equipo(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    fundacion = models.PositiveSmallIntegerField(default=0)
    estadio = models.CharField(max_length=30)
    aforo = models.PositiveIntegerField(default=0)
    direccion = models.TextField()
    
    def __str__(self):
        return self.nombre
    
#datos de las jornadas
class Jornada(models.Model):
    numero = models.PositiveSmallIntegerField()
    fecha = models.CharField(max_length=20)
    temporada = models.ForeignKey(Temporada,on_delete=models.CASCADE)
    
    def __str__(self):
        return "Temporada:" + str(self.temporada) + " -  Jornada:" + str(self.numero)
    
    class Meta:
        unique_together = ('temporada','numero')
        
#datos de los partidos 
class Partido(models.Model):
    jornada = models.ForeignKey(Jornada,on_delete=models.CASCADE)
    # el atributo related_name indica el nombre del campo que se creará en la tabla Equipo (por defecto partido_set)
    # aquí es necesario especificar nombres porque hay dos relaciones con la tabla Equipo 
    local = models.ForeignKey(Equipo, related_name='partido_local', on_delete=models.CASCADE)
    visitante = models.ForeignKey(Equipo,related_name='partido_visitante', on_delete=models.CASCADE)
    goles_local = models.PositiveSmallIntegerField()
    goles_visitante = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.local.nombre + " - " + self.visitante.nombre
    
    class Meta:
        unique_together = ('jornada','local','visitante')
