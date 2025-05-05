#encoding:utf-8
from principal.models import Temporada, Equipo, Jornada, Partido
from django.shortcuts import render, get_object_or_404
from principal import populateDB


def cargar(request):
    if populateDB.populateDatabase():
        tem = Temporada.objects.all().count()
        equ = Equipo.objects.all().count()
        jor = Jornada.objects.all().count()
        par = Partido.objects.all().count()
        informacion="Datos cargados correctamente\n" + "Temporadas: " + str(tem) + " ; " + "Jornadas: " + str(jor) + " ; " + "Partidos: " + str(par) + " ; " + "Equipos: " + str(equ)
    else:
        informacion="ERROR en la carga de datos"    
    return render(request, 'carga.html', {'inf':informacion})

#muestra los títulos de las recetas que están registradas
def inicio(request):
    temporadas=Temporada.objects.all()
    return render(request,'inicio.html', {'temporadas':temporadas})

#muestra el nombre de los equipos almacenados (con un enlace a detalle de cada uno)
def lista_equipos(request):
    equipos=Equipo.objects.all()
    return render(request,'equipos.html', {'datos':equipos})

#muestra detalles de un equipo (nombre, fundación, estadio, aforo y dirección)
def detalle_equipo(request, id_equipo):
    equipo = get_object_or_404(Equipo, pk=id_equipo)
    return render(request,'equipo.html',{'equipo':equipo})

#muestra los cinco estadios con más aforo (nombre equipo, estadio y aforo)
def estadios_mayores(request):
    equipos = Equipo.objects.all().order_by('-aforo')[:5]
    return render(request,'estadios_mayores.html',{'equipos':equipos})

#muestra los resultados de la última temporada, agrupados por jornadas
def ultima_temporada(request):
    ultima = Temporada.objects.all().order_by('-anyo')[0]
    partidos = Partido.objects.filter(jornada__temporada=ultima)
    return render(request,'ultima_temporada.html',{'partidos':partidos , 'anyo':ultima.anyo})

