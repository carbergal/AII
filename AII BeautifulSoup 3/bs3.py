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

    conn = sqlite3.connect('partidos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS PARTIDOS")
    conn.execute('''CREATE TABLE PARTIDOS
       (LOCAL            TEXT NOT NULL,
        VISITANTE    TEXT        ,
        GOLES_LOCAL      INTEGER,
        GOLES_VISITANTE            INTEGER,
        LINK        TEXT,
        JORNADA         INTEGER          
);''')

    
    f = urllib.request.urlopen("http://resultados.as.com/resultados/futbol/primera/2021_2022/calendario/")
    s = BeautifulSoup(f, "lxml")
    lista_jornadas = s.findAll("div", class_="resultados")
    for jornada in lista_jornadas:
        local = jornada.findAll("td", class_="col-equipo-local")
        visitante = jornada.findAll("td", class_="col-equipo-visitante")
        resultado = jornada.findAll("td", class_="col-resultado")
        link = jornada.findAll("td", class_="col-resultado")
        num_jornada = int(jornada.find("h2",class_="tit-modulo").find("a").string.strip().split(" ")[1])
        for i in range(len(local)):
            local[i] = local[i].find("span", class_="nombre-equipo").string.strip()
            visitante[i] = visitante[i].find("span", class_="nombre-equipo").string.strip()
            resultado[i] = resultado[i].find("a").string.strip()
            goles_local = int(resultado[i][0])
            goles_visitante = int(resultado[i][-1])
            link[i] = link[i].find("a",class_="resultado")['href']


            conn.execute("""INSERT INTO PARTIDOS (LOCAL, VISITANTE, GOLES_LOCAL, GOLES_VISITANTE, LINK, JORNADA) VALUES (?,?,?,?,?,?)""",
                     (local[i],visitante[i],goles_local,goles_visitante,link[i],num_jornada))
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM PARTIDOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close

def listar_partidos(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)

    num_jornada = 0
    for row in cursor:
        if row[4] != num_jornada:
            num_jornada = row[4]
            s = 'Jornada ' + str(row[4])
            lb.insert(END, s)
            lb.insert(END, "------------------------------------------------------------------------")
        s =str(row[0]) + " " + str(row[2]) + "-" + str(row[3]) + " " + row[1]
        lb.insert(END, s)
        lb.insert(END,"\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def buscar_por_jornada():  
    def listar(event):
            conn = sqlite3.connect('partidos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT LOCAL, VISITANTE, GOLES_LOCAL, GOLES_VISITANTE, JORNADA FROM PARTIDOS WHERE JORNADA == " + str(entry.get()))
            conn.close
            listar_partidos(cursor)
    ventana = Toplevel()
    label = Label(ventana, text="Introduzca jornada a buscar ")
    label.pack(side=LEFT)
    entry = Entry(ventana)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)


def estadisticas_jornada():  
    def listar(event):
            conn = sqlite3.connect('partidos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT GOLES_LOCAL, GOLES_VISITANTE, JORNADA FROM PARTIDOS WHERE JORNADA == " + str(entry.get()))
            conn.close
            listar_estadisticas(cursor)
    ventana = Toplevel()
    label = Label(ventana, text="Introduzca jornada a buscar ")
    label.pack(side=LEFT)
    entry = Entry(ventana)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

def listar_estadisticas(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)

    vic_local = 0
    vic_visitante = 0
    empates = 0
    goles_total = 0
    for row in cursor:
        goles_total += row[0] + row[1]
        if(row[0] > row[1]):
            vic_local += 1
        elif(row[0] < row[1]):
            vic_visitante += 1
        else:
            empates += 1

    s = 'GOLES TOTAL JORNADA: ' + str(goles_total)
    lb.insert(END, s)
    lb.insert(END, "\n")
    s = 'VICTORIAS LOCAL: ' + str(vic_local)
    lb.insert(END, s)
    lb.insert(END, "VICTORIAS VISITANTE: " + str(vic_visitante))
    lb.insert(END, "EMPATES: " + str(empates))
    lb.insert(END, "\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)




def ventana_principal():
    def listar():
        conn = sqlite3.connect('partidos.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT LOCAL, VISITANTE, GOLES_LOCAL, GOLES_VISITANTE, JORNADA FROM PARTIDOS")
        conn.close
        listar_partidos(cursor)
    
    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Jornada", command=buscar_por_jornada)
    menubuscar.add_command(label="Estadisticas", command=estadisticas_jornada)
    # menubuscar.add_command(label="Géneros", command=buscar_por_genero)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()
