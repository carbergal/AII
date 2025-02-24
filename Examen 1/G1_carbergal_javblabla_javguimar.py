'''
Miembros del grupo:
- Carlos Berenguer Galea (carbergal)
- Javier Blanquero Blanco (javblabla)
- Javier Guijarro Marín (javguimar)
'''



from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
# lineas para evitar error SSL

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context



def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_bd()

def almacenar_bd():

    #Creamos la tabla en la base de datos
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS JUEGO")
    conn.execute('''CREATE TABLE JUEGO
       (TITULO            TEXT NOT NULL,
        PORCENTAJE    TEXT,
        PRECIO         REAL,
        TEMATICAS      TEXT,
        COMPLEJIDAD   TEXT);''')

    
    f = urllib.request.urlopen("https://zacatrus.es/juegos-de-mesa.html")
    s = BeautifulSoup(f, "lxml")
    lista_link_juegos = s.find("ol", class_=["products","list","items","product-items"]).find_all("li")

    for link_juego in lista_link_juegos:
        f = urllib.request.urlopen(link_juego.a['href'])
        s = BeautifulSoup(f, "lxml")

        #Titulo, porcentaje y precio los sacamos de una parte de la pagina
        datos = s.find("div", class_="product-info-main")

        titulo = datos.find("h1", class_="page-title").find("span", class_="base").string.strip()

        porcentaje_span = s.find("span", itemprop="ratingValue")
        porcentaje = porcentaje_span.get_text(strip=True) if porcentaje_span else "Desconocida"

        precio = datos.find("div", class_=["price-box","price-final_price"]).span.span.find("span", class_="price").string.strip()

        #Tematicas y complejidad los sacamos de otra parte de la pagina
        datos2 = s.find("div", class_=["data", "table","additional-attributes"])

        tematicas_element = datos2.find("div", class_=["col","data"], attrs={"data-th":"Temática"})
        if tematicas_element:
            tematicas = tematicas_element.get_text(strip=True)
        else:
            tematicas = "Desconocida"

        complejidad_element = datos2.find("div", class_=["col","data"], attrs={"data-th":"Complejidad"})
        if complejidad_element:
            complejidad = complejidad_element.get_text(strip=True)
        else:
            complejidad = "Desconocida"
       
        precio_convertido = precio.split("\xa0€")[0]

        #Insertamos los valores en la tabla
        conn.execute("""INSERT INTO JUEGO (TITULO, PORCENTAJE, PRECIO, TEMATICAS, COMPLEJIDAD) VALUES (?,?,?,?,?)""",
                     (titulo,porcentaje, float(precio_convertido.replace(',','.')), tematicas, complejidad))
    conn.commit()

    #Mostramos el conteo de datos
    cursor = conn.execute("SELECT COUNT(*) FROM JUEGO")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def buscar_por_tematica():
    def listar(event):
            conn = sqlite3.connect('juegos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT TITULO, TEMATICAS, COMPLEJIDAD FROM JUEGO where TEMATICAS LIKE '%" + str(entry.get())+"%'")
            conn.close
            listar_2(cursor)
    
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT TEMATICAS FROM JUEGO")
    
    #Sacamos el conjunto de tematicas para el spinbox
    tematicas=set()
    for i in cursor:
        tematicas_juego = i[0].split(",")
        for tematica in tematicas_juego:
            tematicas.add(tematica.strip())

    v = Toplevel()
    label = Label(v, text="Seleccione temática: ")
    label.pack(side=LEFT)
    entry = Spinbox(v, values=list(tematicas), state='readonly')
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)
    
    conn.close()

def buscar_por_complejidad():
    def listar(event):
            conn = sqlite3.connect('juegos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT TITULO, TEMATICAS, COMPLEJIDAD FROM JUEGO where COMPLEJIDAD like '%" + str(entry.get())+"%'")
            conn.close
            listar_2(cursor)
    
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT COMPLEJIDAD FROM JUEGO")
    
    #Sacamos el conjunto de complejidades para el spinbox
    complejidades=set()
    for i in cursor:
        complejidades.add(i)

    v = Toplevel()
    label = Label(v, text="Seleccione complejidad: ")
    label.pack(side=LEFT)
    entry = Spinbox(v, values=list(complejidades), state='readonly')
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)
    
    conn.close()
    
    
def listar_juegos(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'TÍTULO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = "     PORC. POSITIVOS: " + str(row[1]) + ' | PRECIO: ' + str(row[2]) + ' | TEMÁTICA/S: ' + row[3]  + ' | COMPLEJIDAD: ' + row[4] 
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

#Funcion listar2 para la parte de buscar 
def listar_2(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'TÍTULO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = "     TEMÁTICAS: " + str(row[1]) +  ' | COMPLEJIDAD: ' + row[2] 
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def ventana_principal():
    def listar():
            conn = sqlite3.connect('juegos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT TITULO, PORCENTAJE, PRECIO, TEMATICAS, COMPLEJIDAD FROM JUEGO")
            conn.close
            listar_juegos(cursor)

    def listar_mejores():
            conn = sqlite3.connect('juegos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT TITULO, PORCENTAJE, PRECIO, TEMATICAS, COMPLEJIDAD FROM JUEGO where PORCENTAJE >= 90 AND PORCENTAJE NOT like '%"+"Desconocida"+"%'")
            conn.close
            listar_juegos(cursor)
            
    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos",menu=menudatos)

    menulistar = Menu(menu, tearoff=0)
    menulistar.add_command(label="Juegos", command=listar)
    menulistar.add_command(label="Mejores juegos", command=listar_mejores)
    menu.add_cascade(label="Listar",menu=menulistar)


    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Juegos por temática", command=buscar_por_tematica)
    menubuscar.add_command(label="Juegos por complejidad", command=buscar_por_complejidad)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()

