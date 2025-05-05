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

PAGINAS = 2  #número de páginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_datos()
        
def extraer_peliculas():
    lista=[]
    
    for p in range(1,PAGINAS+1):
        url="https://www.elseptimoarte.net/estrenos/"+str(p)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f,"lxml")      
        
        lista_link_peliculas = s.find("ul", class_="elements").find_all("li")
        for link_pelicula in lista_link_peliculas:
            link = "https://www.elseptimoarte.net/"+link_pelicula.a['href']
            f = urllib.request.urlopen(link)
            s = BeautifulSoup(f, "lxml")
            datos = s.find("main", class_="informativo").find("section",class_="highlight").div.dl
            titulo_original = datos.find("dt",string="Título original").find_next_sibling("dd").string.strip()
            #si no tiene título se pone el título original
            if (datos.find("dt",string="Título")):
                titulo = datos.find("dt",string="Título").find_next_sibling("dd").string.strip()
            else:
                titulo = titulo_original      
            pais = "".join(datos.find("dt",string="País").find_next_sibling("dd").stripped_strings)
            fecha = datetime.strptime(datos.find("dt",string="Estreno en España").find_next_sibling("dd").string.strip(), '%d/%m/%Y')
            
            generos_director = s.find("div",id="datos_pelicula")
            generos = "".join(generos_director.find("p",class_="categorias").stripped_strings)
            director = "".join(generos_director.find("p",class_="director").stripped_strings)   

            sinopsis = "".join(s.find("div", class_="info").stripped_strings) if s.find("div", class_="info") else "Sin sinopsis"
            print((titulo,titulo_original,fecha,pais,generos,director,sinopsis,link))                     
            lista.append((titulo,titulo_original,fecha,pais,generos,director,sinopsis,link))
    print("Done")    
    return lista


def imprimir_lista(cursor):
    v = Toplevel()
    v.title("Películas")
    
    # Frame to contain the listbox and both scrollbars
    frame = Frame(v)
    frame.pack(fill=BOTH, expand=True)
    
    # Vertical scrollbar
    sc_v = Scrollbar(frame)
    sc_v.pack(side=RIGHT, fill=Y)
    
    # Horizontal scrollbar
    sc_h = Scrollbar(frame, orient=HORIZONTAL)
    sc_h.pack(side=BOTTOM, fill=X)
    
    # Listbox with both scrollbars
    lb = Listbox(frame, width=150, yscrollcommand=sc_v.set, xscrollcommand=sc_h.set)
    
    for row in cursor:
        lb.insert(END, "Título: " + row['titulo'])
        lb.insert(END, "Título original: " + row['titulo_original'])
        lb.insert(END, "Fecha de estreno: " + row['fecha'].strftime('%d/%m/%Y'))
        lb.insert(END, "País: " + row['pais'])
        lb.insert(END, "Géneros: " + row['generos'])
        lb.insert(END, "Director: " + row['director'])
        lb.insert(END, "Sinopsis: " + row['sinopsis'])
        lb.insert(END, "Enlace: " + row['link'])
        lb.insert(END, "\n\n")
    
    lb.pack(side=LEFT, fill=BOTH, expand=True)
    
    # Configure the scrollbars
    sc_v.config(command=lb.yview)
    sc_h.config(command=lb.xview)

 
def almacenar_datos():
    #define el esquema de la información
    schem = Schema(titulo=TEXT(stored=True),titulo_original=TEXT(stored=True),fecha=DATETIME(stored=True),pais=KEYWORD(stored=True,commas=True),
                   generos=KEYWORD(stored=True,commas=True),director=KEYWORD(stored=True,commas=True),sinopsis=TEXT(stored=True),link=TEXT(stored=True))
    
    #eliminamos el directorio del índice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el índice
    ix = create_in("Index", schema=schem)
    #creamos un writer para poder añadir documentos al indice
    writer = ix.writer()
    i=0
    lista=extraer_peliculas()
    for j in lista:
        #añade cada juego de la lista al índice
        writer.add_document(titulo=str(j[0]), titulo_original=str(j[1]), fecha=j[2], pais=str(j[3]), generos=str(j[4]), director=str(j[5])
                            , sinopsis=str(j[6]), link=str(j[7]))   
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " juegos")          

 
# permite buscar los juegos por una "temática"
def buscar_titulo_sinopsis():
    def mostrar_lista(event):    
        with ix.searcher() as searcher:
            entrada = str(en.get().lower())
            #se busca como una frase porque hay temáticas con varias palabras
            query = MultifieldParser(["titulo","sinopsis"], ix.schema).parse('"'+entrada+'"')
            results = searcher.search(query,limit=10)
            imprimir_lista(results)
    
    
    v = Toplevel()
    v.title("Búsqueda por Título o Sinopsis")
    l = Label(v, text="Introduzca el título o la sinopsis a buscar:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    en = Entry(v, width=50)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)


def buscar_genero():
    def mostrar_lista(event):    
        with ix.searcher() as searcher:
            entrada = str(en.get())
            #se busca como una frase porque hay temáticas con varias palabras
            query = QueryParser("generos", ix.schema).parse('"'+entrada+'"')
            results = searcher.search(query,limit=20)
            imprimir_lista(results)
    
    
    v = Toplevel()
    v.title("Búsqueda por Género")
    l = Label(v, text="Seleccione género a buscar:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    with ix.searcher() as searcher:
        #lista de todas las temáticas disponibles en el campo de temáticas
        lista_generos = [i.decode('utf-8') for i in searcher.lexicon('generos')]
    
    en = Spinbox(v, values=lista_generos, state="readonly")
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)


 
# permite buscar frases en los "detalles" de los juegos 
def buscar_detalles():
    def mostrar_lista(event):
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            query = QueryParser("detalles", ix.schema).parse('"'+str(en.get())+'"')
            results = searcher.search(query,limit=10) #sólo devuelve los 10 primeros
            imprimir_lista(results)
    
    v = Toplevel()
    v.title("Búsqueda por Detalles")
    l = Label(v, text="Introduzca la frase a buscar:")
    l.pack(side=LEFT)
    en = Entry(v, width=75)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
        

# permite buscar juegos hasta un precio
def buscar_fechas():
    def mostrar_lista(event):
        if not re.match('^\d{8} \d{8}$', en.get()):
            messagebox.showinfo("ERROR", "Formato incorrecto (AAAAMMDD.AAAAMMDD)")
            return
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            fecha1 = en.get().split(" ")[0]
            fecha2 = en.get().split(" ")[1]
            query = QueryParser("fecha", ix.schema).parse('['+fecha1 +' TO '+fecha2+']')
            results = searcher.search(query,limit=None) 
            imprimir_lista(results)
    
    v = Toplevel()
    v.title("Búsqueda por Fecha")
    l = Label(v, text="Introduzca el rango:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)

# permite buscar juegos para un determinado número de jugadores
def buscar_jugadores():
    def mostrar_lista(event):
        if not re.match('\d+', en.get().strip()):
            messagebox.showinfo("ERROR", "Formato incorrecto (dd)")
            return
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            query = QueryParser("jugadores", ix.schema).parse(str(en.get().strip()))
            results = searcher.search(query,limit=None)
            imprimir_lista(results)
    
    v = Toplevel()
    v.title("Búsqueda por Jugadores")
    l = Label(v, text="Introduzca el número de jugadores:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)


def ventana_principal():       
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Título / Sinopsis", command=buscar_titulo_sinopsis)
    buscarmenu.add_command(label="Género", command=buscar_genero)
    buscarmenu.add_command(label="Fechas", command=buscar_fechas)
    buscarmenu.add_command(label="Jugadores", command=buscar_jugadores)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    ventana_principal()