#encoding:utf-8
from tkinter import *
from tkinter import messagebox
import os
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME
from whoosh.qparser import MultifieldParser
from datetime import datetime
from whoosh.qparser import QueryParser


def get_schema_correo():
    return Schema(remitente=TEXT(stored=True), destinatarios=KEYWORD(stored=True), fecha=DATETIME(stored=True),
                  asunto=TEXT(stored=True), contenido=TEXT(stored=True))


def get_schema_agenda():
    return Schema(email=TEXT(stored=True), nombre=TEXT(stored=True))


def add_doc_mail(dir_mails, dir_index):
    ix = create_in(dir_index, schema=get_schema_correo())
    writer = ix.writer()
    i = 0
    for docname in os.listdir(dir_mails):
        if not os.path.isdir(dir_mails+docname):
            fileobj = open(dir_mails + '/' + docname, "r")
            rte = fileobj.readline().strip()
            dtos = fileobj.readline().strip()
            f = fileobj.readline().strip()
            fcha = datetime.strptime(f, '%Y%m%d')
            ast = fileobj.readline().strip()
            ctdo = fileobj.read()
            fileobj.close()
            writer.add_document(remitente=rte, destinatarios=dtos, fecha=fcha, asunto=ast, contenido=ctdo)
            i+=1
    writer.commit()
    return i


def add_doc_contact(dir_contacts, dir_index):
    iy = create_in(dir_index, schema=get_schema_agenda())
    writer = iy.writer()
    z = 0
    for docname in os.listdir(dir_contacts):
        if not os.path.isdir(dir_contacts+docname):
            with open(dir_contacts + '/' + docname, "r") as f:
                lineas = f.readlines()
                i = 0
                while i < (len(lineas)):
                    ml = lineas[i].strip()
                    nme = lineas[i + 1].strip()
                    i = i + 2
                    writer.add_document(email=ml, nombre=nme)
                    z = z + 1
    writer.commit()
    return z


def index(dir_mails, dir_contacts, dir_index):
    if not os.path.exists(dir_mails):
        print ("Error: no existe el directorio de correos: " + dir_mails)
        if not os.path.exists(dir_contacts):
            print("Error: no existe el directorio de contactos: " + dir_contacts)
    else:
        if not os.path.exists(dir_index + str(1)):
            os.mkdir(dir_index + str(1))
        if not os.path.exists(dir_index + str(2)):
            os.mkdir(dir_index + str(2))

    i = add_doc_mail(dir_mails, dir_index + str(1))
    z = add_doc_contact(dir_contacts, dir_index + str(2))

    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " correos y " + str(z) + " contactos")


def search(types, text, dir_index, to_save):
    res = []
    ix = open_dir(dir_index)
    with ix.searcher() as searcher:
        if len(types) == 1 and types[0] == 'fecha':
            myquery = '{' + text + 'TO]'
            q = QueryParser("fecha", ix.schema).parse(myquery)
        else:
            qp = MultifieldParser(types, ix.schema)
            q = qp.parse(text)
        results = searcher.search(q)
        for r in results:
            aux = []
            for element in to_save:
                aux.append(r[element])
            res.append(aux)
        return res

    
def apartado_a(dir_index):
    def mostrar_lista(event):
        lb.delete(0,END)   #borra toda la lista
        busqueda1 = search(["asunto", "contenido"], str(en.get()), dir_index + str(1), ["destinatarios", "asunto"])
        for elemento in busqueda1:
            correos = elemento[0].split(" ")
            for correo in correos:
                nombres = search(["email"], str(correo), dir_index + str(2), ["nombre"])
                i = 1
                for nombre in nombres:
                    lb.insert(END, "Nombre (" + str(i) + "): " + str(nombre[0]))
                    i = i + 1
                lb.insert(END, "Asunto del correo: " + elemento[1])
                lb.insert(END, " ")

    v = Toplevel()
    v.title("Busqueda por asunto y remitente")
    f =Frame(v)
    f.pack(side=TOP)
    l = Label(f, text=" Introduzca el texto a buscar:")
    l.pack(side=LEFT)
    en = Entry(f)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, yscrollcommand=sc.set)
    lb.pack(side=BOTTOM, fill = BOTH)
    sc.config(command = lb.yview)


def apartado_b(dir_index):
    def mostrar_lista(event):
        lb.delete(0,END)   #borra toda la lista
        busqueda1 = search(["fecha"], str(en.get()), dir_index + str(1), ["remitente", "destinatarios", "asunto"])
        for elemento in busqueda1:
            correos = elemento[0].split(" ")
            for correo in correos:
                nombres = search(["email"], str(correo), dir_index + str(2), ["nombre"])
                i = 1
                for nombre in nombres:
                    lb.insert(END, "Nombre (" + str(i) + "): " + str(nombre[0]))
                    i = i + 1
                lb.insert(END, "remitente")
        lb.insert(END, " ")

    v = Toplevel()
    v.title("Busqueda por asunto y remitente")
    f =Frame(v)
    f.pack(side=TOP)
    l = Label(f, text=" Introduzca el texto a buscar:")
    l.pack(side=LEFT)
    en = Entry(f)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, yscrollcommand=sc.set)
    lb.pack(side=BOTTOM, fill = BOTH)
    sc.config(command = lb.yview)
    
def ventana_principal():
    dir_mails = "Whoosh 1\Docs\Correos"
    dir_contacts = "Whoosh 1\Docs\Agenda"
    dir_index = "Whoosh 1\Index"
    top = Tk()
    indexar = Button(top, text="Indexar", command = lambda: index(dir_mails, dir_contacts, dir_index))
    indexar.pack(side = TOP)
    Buscar1= Button(top, text="Búsqueda por asunto o contenido", command = lambda: apartado_a(dir_index))
    Buscar1.pack(side = TOP)
    Buscar2 = Button(top, text="Buscar correos posteriores a una fecha (YYYYMMDD)", command = lambda: apartado_b(dir_index))
    Buscar2.pack(side = TOP)
    top.mainloop()


if __name__ == '__main__':
    ventana_principal()