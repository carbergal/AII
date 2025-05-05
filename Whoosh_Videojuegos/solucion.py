#encoding:utf-8

from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
import whoosh
import whoosh.fields
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID, DATETIME
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import DateRange

PAGINAS = 1  #número de páginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def format_month(month_name):
    months = {
        'enero': '01',
        'febrero': '02',
        'marzo': '03',
        'abril': '04',
        'mayo': '05',
        'junio': '06',
        'julio': '07',
        'agosto': '08',
        'septiembre': '09',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12'
    }
    return months.get(month_name.lower(), '01')

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_datos()
        
def extraer_juegos():
    lista=[]
    
    
    url="https://vandal.elespanol.com/rankings/videojuegos"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f,"lxml")      
    
    l = s.find_all("table", class_= "table transparente tablasinbordes")
    
    for i in l:
        tr = i.find_all("tr")
        
        datos1 = tr[-2].find_all("td")
        puesto = "".join(datos1[0].find("div", class_="tcenter").stripped_strings)
        print(puesto)
        titulo = datos1[1].find("a").string.strip()
        plataforma = datos1[1].find("span").string.strip()
        link ="https://vandal.elespanol.com"+ datos1[1].find("a")['href']
        
        descripcion = tr[-1].find_all("td")[1].p.stripped_strings
        descripcion = " ".join(list(descripcion))

        f2 = urllib.request.urlopen(link)
        j = BeautifulSoup(f2,"lxml")
        fecha = j.find_all("div",class_="fichatecnica")[1]
        fecha = fecha.find("b").stripped_strings
        fecha = " ".join(list(fecha)).split(":")[1].strip()

        if(fecha != fecha.split(" ")[0]):
            dia = "01"
            mes = format_month(fecha.split(" ")[0])
            año = fecha.split(" ")[1]
            fecha = dia + "/" + mes + "/" + año

        fecha = datetime.strptime(fecha, '%d/%m/%Y')
        print((puesto,titulo,plataforma,descripcion,fecha))

        lista.append((puesto,titulo,plataforma,descripcion,fecha))


    return lista
    


def imprimir_lista(cursor):
    v = Toplevel()
    v.title("Videojuegos")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row['titulo'])
        lb.insert(END,"    Puesto: "+ str(row['puesto']))
        lb.insert(END,"    Título: "+ row['titulo'])
        lb.insert(END,"    Plataforma: "+ row['plataforma'])
        lb.insert(END,"    Fecha: "+ row['fecha'].strftime('%d/%m/%Y'))
        lb.insert(END,"    Descripción: "+ row['descripcion'])
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

 
def almacenar_datos():
    #define el esquema de la información
    # puesto,titulo,plataforma,descripcion,fecha
    schem = Schema(puesto=NUMERIC(stored=True,numtype=int,unique=True), titulo=TEXT(stored=True), plataforma=TEXT(stored=True), descripcion=TEXT(stored=True), fecha=DATETIME(stored=True))
    
    #eliminamos el directorio del índice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el índice
    ix = create_in("Index", schema=schem)
    #creamos un writer para poder añadir documentos al indice
    writer = ix.writer()
    i=0
    lista=extraer_juegos()
    for j in lista:
        #añade cada juego de la lista al índice
        writer.add_document(puesto=int(str(j[0])), titulo=str(j[1]), plataforma=str(j[2]), descripcion=str(j[3]), fecha=j[4])
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " juegos")          

 
def buscar_titulo_descripcion():
    def mostrar_lista(event):    
        with ix.searcher() as searcher:
            entrada = str(en.get().lower())

            query = MultifieldParser(["titulo","descripcion"], ix.schema).parse('"'+entrada+'"')
            results = searcher.search(query,limit=None)
            imprimir_lista(results)
    
    
    v = Toplevel()
    v.title("Búsqueda por Título o Descripción")
    l = Label(v, text="Introduzca el título o la descripción a buscar:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    en = Entry(v, width=50)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)


def buscar_fecha():
    def mostrar_lista(event):
        if not re.match('^\d{2}-\d{2}-\d{4}$', en.get()):
            messagebox.showinfo("ERROR", "Formato incorrecto (dd-mm-aaaa)")
            return
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            day, month, year = en.get().split('-')
            fecha_datetime = datetime(int(year), int(month), int(day))
            query = DateRange("fecha", None, fecha_datetime)
            results = searcher.search(query,limit=None) 
            imprimir_lista(results)
    
    v = Toplevel()
    v.title("Búsqueda por Fecha")
    l = Label(v, text="Introduzca la fecha límite:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
 
def buscar_plataforma():
    def mostrar_lista(event):    
        with ix.searcher() as searcher:
            entrada = str(en.get())
            #se busca como una frase porque hay temáticas con varias palabras
            query = QueryParser("plataforma", ix.schema).parse('"'+entrada+'"')
            results = searcher.search(query,limit=None)
            imprimir_lista(results)
    
    
    v = Toplevel()
    v.title("Búsqueda por Plataforma")
    l = Label(v, text="Seleccione plataforma a buscar:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    with ix.searcher() as searcher:
        #lista de todas las temáticas disponibles en el campo de temáticas
        lista_generos = [i.decode('utf-8') for i in searcher.lexicon('plataforma')]
    
    en = Spinbox(v, values=lista_generos, state="readonly")
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
        





def modificar_descripcion():
    def modificar():
    #Comprobamos el formato de la entrada
        if not re.match("^([1-9]|[1-9][0-9]|100)$", en.get().strip()):
            messagebox.showinfo("Error", "Formato incorrecto. Debe ser un número entre 1 y 100")
            return
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            #Se crea la Query según la entrada dada, dentro de título y con el esquema
            query = QueryParser("puesto", ix.schema).parse(en.get())
            results = searcher.search(query, limit=None)
            #Se crea una ventana con título de un tamaño prefijado
            

            r=results[0]

            writer = ix.writer()
        
            writer.update_document(puesto=r['puesto'], titulo=r['titulo'], plataforma=r['plataforma'], descripcion=en1.get(), fecha=r['fecha'])
            writer.commit()

        with ix.searcher() as searcher:
            #Se crea la Query según la entrada dada, dentro de título y con el esquema
            query = QueryParser("puesto", ix.schema).parse(en.get())
            results = searcher.search(query, limit=None)
            r = results[0]
            #Se crea una ventana con título de un tamaño prefijado    
            v = Toplevel()
            v.title("Videojuego Modificado")
            v.geometry('800x150')
            #Se crea scroll vertical en el margen derecho
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            #Se crea un espacio de listado
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            
            lb.insert(END,r['titulo'])
            lb.insert(END,"    Puesto: "+ str(r['puesto']))
            lb.insert(END,"    Título: "+ r['titulo'])
            lb.insert(END,"    Plataforma: "+ r['plataforma'])
            lb.insert(END,"    Fecha: "+ r['fecha'].strftime('%d/%m/%Y'))
            lb.insert(END,"    Descripción: "+ r['descripcion'])
            lb.insert(END,"\n\n")



    #Se crea ventana con título
    v = Toplevel()
    v.title("Modificar Descripción")
    #Etiqueta para la barra de búsqueda y barra
    l = Label(v, text="Introduzca Puesto Videojuego:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.pack(side=LEFT)
    #Etiqueta para la barra de búsqueda y barra
    l1 = Label(v, text="Introduzca Nueva Descripción:")
    l1.pack(side=LEFT)
    en1 = Entry(v)
    en1.pack(side=LEFT)
    #Botón que introduce los datos
    bt = Button(v, text='Modificar', command=modificar)
    bt.pack(side=LEFT)


def ventana_principal():       
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=almacenar_datos)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Plataforma", command=buscar_plataforma)
    buscarmenu.add_command(label="Título / Descripción", command=buscar_titulo_descripcion)
    buscarmenu.add_command(label="Fecha", command=buscar_fecha)
    buscarmenu.add_command(label="Modificar", command=modificar_descripcion)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    ventana_principal()