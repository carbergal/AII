from main.models import Usuario, Ocupacion, Puntuacion, Pelicula, Categoria
from datetime import datetime

path = "data"

def populate():
    populateOccupations()
    populateGenres()
    u=populateUsers()
    m=populateMovies()
    populateRatings(u,m)  #USAMOS LOS DICCIONARIOS DE USUARIOS Y PELICULAS PARA ACELERAR LA CARGA EN PUNTUACIONES

def populateOccupations():
    print("Loading occupations...")
    Ocupacion.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\u.occupation", "r")
    for line in fileobj.readlines():
        lista.append(Ocupacion(nombre=str(line.strip())))
    fileobj.close()
    Ocupacion.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    print("Occupations inserted: " + str(Ocupacion.objects.count()))
    print("---------------------------------------------------------")


def populateGenres():
    print("Loading Movie Genres...")
    Categoria.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\u.genre", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        if len(rip) != 2:
            continue
        lista.append(Categoria(idCategoria=rip[1], nombre=rip[0]))
    fileobj.close()
    Categoria.objects.bulk_create(lista)
    
    print("Genres inserted: " + str(Categoria.objects.count()))
    print("---------------------------------------------------------")


def populateUsers():
    print("Loading users...")
    Usuario.objects.all().delete()
    
    lista=[]
    dict={} # diccionario de los usuarios {idusuario:objeto_usuario}
    fileobj=open(path+"\\u.user", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        if len(rip) != 5:
            continue
        u=Usuario(idUsuario=rip[0], edad=rip[1], sexo=rip[2], ocupacion=Ocupacion.objects.get(nombre=rip[3]), codigoPostal=rip[4])
        lista.append(u)
        dict[rip[0]]=u
    fileobj.close()
    Usuario.objects.bulk_create(lista)
    
    print("Users inserted: " + str(Usuario.objects.count()))
    print("---------------------------------------------------------")
    return(dict)

def populateMovies():
    print("Loading movies...")
    Pelicula.objects.all().delete()
    
    lista_peliculas =[]  # lista de peliculas
    dict_categorias={}  #  diccionario de categorias de cada pelicula (idPelicula y lista de categorias)
    fileobj=open(path+"\\u.item", "r")
    for line in fileobj.readlines():
        rip = line.strip().split('|')
        
        date = None if len(rip[2]) == 0 else datetime.strptime(rip[2], '%d-%b-%Y')
        lista_peliculas.append(Pelicula(idPelicula=rip[0], titulo=rip[1], fechaEstreno=date, imdbUrl=rip[4]))
        
        lista_aux=[]
        for i in range(5, len(rip)):
            if rip [i] == '1':
                lista_aux.append(Categoria.objects.get(pk = (i-5)))
        dict_categorias[rip[0]]=lista_aux
    fileobj.close()    
    Pelicula.objects.bulk_create(lista_peliculas)

    dict={} # diccionario de las pel�culas {idpelicula:objeto_pelicula}
    for pelicula in Pelicula.objects.all():
        #aqu� se a�aden las categorias a cada pel�cula
        pelicula.categorias.set(dict_categorias[pelicula.idPelicula])
        dict[pelicula.idPelicula]=pelicula
    
    print("Movies inserted: " + str(Pelicula.objects.count()))
    print("---------------------------------------------------------")
    return(dict)

def populateRatings(u,m):
    # usamos los diccionarios de usuarios y pel�culas para acelerar la creaci�n de las puntuaciones
    # evitando tener que acceder a las tablas de Usuario y Pelicula
    print("Loading ratings...")
    Puntuacion.objects.all().delete()

    lista=[]
    fileobj=open(path+"\\u.data", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('\t')
        lista.append(Puntuacion(idUsuario=u[rip[0]], idPelicula=m[rip[1]], puntuacion=rip[2]))
    fileobj.close()
    Puntuacion.objects.bulk_create(lista)
    print("Ratings inserted: " + str(Puntuacion.objects.count()))
    print("---------------------------------------------------------")


    

