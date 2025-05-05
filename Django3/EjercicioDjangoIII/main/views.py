#encoding:utf-8
from main.models import Usuario, Puntuacion, Pelicula
from main.populateDB import populate
from main.forms import  UsuarioBusquedaForm, PeliculaBusquedaYearForm
from django.shortcuts import render
from django.db.models import Avg, Count
from django.http.response import HttpResponseRedirect
from django.conf import settings


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required



#Funcion de acceso restringido que carga los datos en la BD  
@login_required(login_url='/ingresar')
def populateDatabase(request):
    populate()
    logout(request)  # se hace logout para obligar a login cada vez que se vaya a poblar la BD
    return HttpResponseRedirect('/index.html')


def mostrar_ocupaciones(request):
    usuarios= Usuario.objects.all().order_by('ocupacion')
    return render(request, 'ocupacion_usuarios.html',{'usuarios':usuarios, 'STATIC_URL':settings.STATIC_URL})

# el parámetro pag es para indicar la página que queremos mostrar (paginador uikit). Cada página es de 10 películas
def mostrar_mejores_peliculas(request,pag):
    if pag > 5:
        pag = 5
    else:
        if pag < 1:
            pag = 1
    #peliculas con más de 100 puntuaciones
    peliculas = Pelicula.objects.annotate(avg_rating=Avg('puntuacion__puntuacion'),num_rating=Count('puntuacion__puntuacion')).filter(num_rating__gt=100).order_by('-avg_rating')[(pag-1)*10:pag*10]
    return render(request, 'mejores_peliculas.html', {'peliculas':peliculas, 'pagina':pag, 'STATIC_URL':settings.STATIC_URL})


def mostrar_peliculas_year(request):
    formulario = PeliculaBusquedaYearForm()
    peliculas = None
    anyo = None
    
    if request.method=='POST':
        formulario = PeliculaBusquedaYearForm(request.POST)
        
        if formulario.is_valid():
            anyo=formulario.cleaned_data['year']
            peliculas = Pelicula.objects.filter(fechaEstreno__year=anyo)
    
    return render(request, 'busqueda_peliculas.html', {'formulario':formulario, 'peliculas':peliculas, 'anyo':anyo, 'STATIC_URL':settings.STATIC_URL})


def mostrar_puntuaciones_usuario(request):
    formulario = UsuarioBusquedaForm()
    puntuaciones = None
    idusuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idusuario = formulario.cleaned_data['idUsuario']
            puntuaciones = Puntuacion.objects.filter(idUsuario = Usuario.objects.get(pk=idusuario))
            
    return render(request, 'puntuaciones_usuario.html', {'formulario':formulario, 'puntuaciones':puntuaciones, 'idusuario':idusuario, 'STATIC_URL':settings.STATIC_URL})


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})


def ingresar(request):
    if request.user.is_authenticated:
        return(HttpResponseRedirect('/populate'))
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/populate'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})


