

import re
import urllib.request
import os.path

'''
Método para extraer las noticias de un fichero, buscando datos concretos con expresiones regulares
'''
def extraer_lista(file):
    with open(file, "r", encoding="utf-8") as f:
        s = f.read()

    titulos = re.findall(r"<title>(.*)<\/title>", s)[1:]
    links = re.findall(r"<link>(.*)<\/link>", s)[1:]
    fechas = re.findall(r"<pubDate>(.*)<\/pubDate>", s)

    resultado = []
    for titulo, link, fecha in zip(titulos, links, fechas):
        resultado.append([titulo, link, fecha])

    return resultado

'''
Método para imprimir la lista de noticias
'''
def imprimir_lista(l):
    for t in l:
        print ("Título:", str(t[0]))
        print ("Link:", t[1])
        f=formatear_fecha(t[2])
        print ("Fecha: {0:2s}/{1:2s}/{2:4s}\n".format(f[0],f[1],f[2]))
 

'''
Método para abrir una url y guardar el contenido en un fichero
'''
def abrir_url(url,file):
    try:
        if os.path.exists(file):
            recarga = input("La página ya ha sido cargada. Desea recargarla (s/n)?")
            if recarga == "s":
                urllib.request.urlretrieve(url,file)
        else:
            urllib.request.urlretrieve(url,file)
        return file
    except:
        print  ("Error al conectarse a la página")
        return None


'''
Método para buscar noticias por fecha
'''
def buscar_fecha(l):
    mes = input("Introduzca el mes (mm):")
    dia = input("Introduzca el dia (dd):")
    print()
    enc=False
    for t in l:
        f =formatear_fecha(t[2])
        if mes == f[1] and dia == f[0]:
            print ("Título:", str(t[0]))
            print ("Link:", t[1])
            print ("Fecha: {0:2s}/{1:2s}/{2:4s}\n".format(f[0],f[1],f[2]))
            enc = True
    if not enc:
        print ("No hay noticias para ese mes")
        
'''
Método para formatear el mes de la fecha
'''        
def formatear_fecha(s):
    meses={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    fecha = re.search(r'.*(\d\d)\s*(.{3})\s*(\d{4}).*', s)
    l = list(fecha.groups())
    l[1] = meses[l[1]]
    return tuple(l)

if __name__ == "__main__":
    fichero="noticias"
    if abrir_url("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",fichero):
        l=extraer_lista(fichero)
    if l:
        imprimir_lista(l)
        buscar_fecha(l)
