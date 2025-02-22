from tkinter import Tk, Button, Toplevel, Label, Listbox, END, LEFT, BOTH, Entry
import sqlite3
import re

conn = sqlite3.connect('noticias.db')
cursor = conn.cursor()

def crear_bd():

    cursor.execute('DROP TABLE IF EXISTS news')
    cursor.execute('''
        CREATE TABLE news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            fecha DATE,
            link TEXT
        )
    ''')

    with open ("fichero1", encoding="utf-8") as f:
        s = f.read()

    titulos = re.findall(r'<title>(.+)<\/title>', s)[1:]
    links = re.findall(r'<link>(.+)<\/link>', s)[1:]
    fechas = re.findall(r'<pubDate>(.+)<\/pubDate>', s)

    for i in range(len(titulos)):
        cursor.execute('''
            INSERT INTO news (titulo, fecha, link)
            VALUES (?, ?, ?)
        ''', (titulos[i], fechas[i], links[i]))

    conn.commit()


def listar():
    cursor.execute('SELECT * FROM news')
    v = Toplevel()
    lb = Listbox(v,width=200, height=30)
    for row in cursor.fetchall():
        for i in range(3):
            lb.insert(END, row[i+1])
        lb.insert(END, " ")
    lb.pack(side=LEFT, fill=BOTH)

def formatear_mes(mes):
    pass


def buscar_mes(event, entry):
    try:
        mes = int(entry.get())
        if mes < 1 or mes > 12:
            raise ValueError
        else:
            # Add code to handle valid month input
            cursor.execute('SELECT * FROM news WHERE fecha LIKE "%/{}%"'.formatear_mes(mes))
            v = Toplevel()
            lb = Listbox(v, width=200, height=30)
            for row in cursor.fetchall():
                for i in range(3):
                    lb.insert(END, row[i+1])
                lb.insert(END, " ")
            lb.pack(side=LEFT, fill=BOTH)

    except ValueError:
        nueva_ventana = Toplevel()
        nueva_ventana.title("Error")
        Label(nueva_ventana, text="Introduzca un mes válido", padx=20, pady=20).pack()


def mostrar_ventana(mensaje):
    nueva_ventana = Toplevel()
    nueva_ventana.title("tk")
    Label(nueva_ventana, text=mensaje, padx=20, pady=20).pack()

def funcion1():
    crear_bd()
    mostrar_ventana("BD creada correctamente")

def funcion2():
    listar()
    # mostrar_ventana("Botón 2 presionado")

def funcion3():
    root= Tk()
    root.title("tk")
    Label(root, text="Introduzca el mes (Xxx)").pack()
    entry = Entry(root)
    entry.bind("<Return>", lambda event: buscar_mes(event, entry))
    entry.pack()

def funcion4():
    mostrar_ventana("Introduzca la fecha (dd/mm/aaaa)")

root = Tk()
root.title("Tk")

btn1 = Button(root, text="Almacenar", command=funcion1)
btn1.pack(side="left", padx=5, pady=10)

btn2 = Button(root, text="Listar", command=funcion2)
btn2.pack(side="left", padx=5, pady=10)

btn3 = Button(root, text="Buscar Mes", command=funcion3)
btn3.pack(side="left", padx=5, pady=10)

btn4 = Button(root, text="Buscar Día", command=funcion4)
btn4.pack(side="left", padx=5, pady=10)

root.mainloop()



