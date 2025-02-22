import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import dateutil.parser
import re

def abrir_url(url,file):
    try:
        urllib.request.urlretrieve(url,file)
        return file
    except:
        print  ("Error al conectarse a la página")
        return None

def extraer_datos():
    fichero="noticias"
    if abrir_url("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",fichero):
        with open(fichero, "r", encoding="utf-8") as f:
            s = f.read()

        titulos = re.findall(r"<title>(.*)</title>", s)[1:]
        links = re.findall(r"<link>(.*)</link>", s)[1:]
        fechas = re.findall(r"<pubDate>(.*)</pubDate>", s)

        resultado = []
        for titulo, link, fecha in zip(titulos, links, fechas):
            resultado.append([titulo, link, fecha])

        return resultado

'''
Método para crear una base de datos sqlite a partir de los datos extraídos de las noticias
'''
def almacenar_bd():
    conn = sqlite3.connect('noticias.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS NOTICIAS")   
    conn.execute('''CREATE TABLE NOTICIAS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       TITULO           TEXT    NOT NULL,
       LINK           TEXT    NOT NULL,
       FECHA        DATE NOT NULL);''')
    l = extraer_datos()
    for i in l:
        conn.execute("""INSERT INTO NOTICIAS (TITULO, LINK, FECHA) VALUES (?,?,?)""",(i[0],i[1],i[2]))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM NOTICIAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

'''
Método para seleccionar el título, link y fecha de las noticias almacenadas en la base de datos
'''
def listar_bd():
    conn = sqlite3.connect('noticias.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT TITULO, LINK, FECHA FROM NOTICIAS")
    imprimir_etiqueta(cursor)
    conn.close()
    
'''
Métodos para imprimir en una ventana los datos de las noticias almacenadas en la base de datos
'''    
def imprimir_etiqueta(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y) # scrollbar a la derecha y que se expanda en el eje Y
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0]) # END para que se añada al final del ListBox
        lb.insert(END,row[1])
        lb.insert(END,row[2])
        lb.insert(END,'')
    lb.pack(side = LEFT, fill = BOTH) # Hace que la listbox se ponga a la izquierda y se expanda en ambos ejes
    sc.config(command = lb.yview) # Asocia la scrollbar con la listbox
    
def imprimir_etiqueta_1(cursor,fecha):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        if dateutil.parser.parse(fecha,dayfirst=True).date() == dateutil.parser.parse(row[2]).date():
            lb.insert(END,row[0])
            lb.insert(END,row[1])
            lb.insert(END,row[2])
            lb.insert(END,'')
    lb.pack(side = LEFT, fill = BOTH)
    sc.config(command = lb.yview)

'''
Métodos para buscar noticias por mes y por día
''' 
def buscar_mes_bd():
    def listar_busqueda(event): # Hay que poner event aunque no se use
        conn = sqlite3.connect('noticias.db')
        conn.text_factory = str
        s = "%"+en.get()+"%" # Se añaden los % para que busque en cualquier posición, es decir, si en = 5, 
                             # busca en todos los meses que contengan un 5. Si no ponemos los %, buscaría solo en el mes 5
        cursor = conn.execute("""SELECT TITULO, LINK, FECHA FROM NOTICIAS WHERE FECHA LIKE ?""",(s,))
        imprimir_etiqueta(cursor)
        conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Introduzca el mes (Xxx): ")
    lb.pack(side = LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda) # Cuando se pulse Enter se ejecuta la función listar_busqueda
    en.pack(side = LEFT)
  
def buscar_dia_bd():
    def listar_busqueda(event):
        conn = sqlite3.connect('noticias.db')
        conn.text_factory = str 
        cursor = conn.execute("""SELECT TITULO,LINK,FECHA FROM NOTICIAS""") 
        imprimir_etiqueta_1(cursor,en.get())
        conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Introduzca la fecha (dd/mm/aaaa): ")
    lb.pack(side = LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side = LEFT)
        
'''
Creación de la ventana principal
'''
def ventana_principal():
    top = Tk()
    almacenar = Button(top, text="Almacenar", command = almacenar_bd)
    almacenar.pack(side = LEFT)
    listar = Button(top, text="Listar", command = listar_bd)
    listar.pack(side = LEFT)
    Buscar = Button(top, text="Busca Mes", command = buscar_mes_bd)
    Buscar.pack(side = LEFT)
    Buscar = Button(top, text="Busca Día", command = buscar_dia_bd)
    Buscar.pack(side = LEFT)
    top.mainloop() # Sirve para que la ventana no se cierre tras ejecutar el programa MUY IMPORTANTE
    

if __name__ == "__main__":
    ventana_principal()

