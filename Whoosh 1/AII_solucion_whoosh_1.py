import os
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from tkinter import *
from tkinter import messagebox

# Dictionary to store email-name pairs
agenda={}
# Directory paths
dirdocs="Whoosh 1\Docs\Correos"      # Path to email documents
dirindex="Whoosh 1\Index"            # Path to the search index
dirage="Whoosh 1\Docs\Agenda"        # Path to the agenda file

# Creates a search index from documents in dirdocs directory
# The index is created in the dirindex directory
def crea_index():
    # Inner function to load and index documents
    def carga():
        # Define the schema for the index
        sch = Schema(remitente=TEXT(stored=True), destinatarios=KEYWORD(stored=True), fecha=DATETIME(stored=True), 
                     asunto=TEXT(stored=True), contenido=TEXT(stored=True,phrase=False), nombrefichero=ID(stored=True))
        # Create the index
        ix = create_in(dirindex, schema=sch)
        writer = ix.writer()
        # Process each document in the directory
        for docname in os.listdir(dirdocs):
            if not os.path.isdir(dirdocs+docname):
                add_doc(writer, dirdocs, docname)                  
        writer.commit()
        messagebox.showinfo("INDICE CREADO", "Se han cargado " + str(ix.reader().doc_count()) + " documentos")
    
    # Check if documents directory exists
    if not os.path.exists(dirdocs):
        messagebox.showerror("ERROR", "No existe el directorio de documentos " + dirdocs)
    else:
        # Create index directory if it doesn't exist
        if not os.path.exists(dirindex):
            os.mkdir(dirindex)
    # Check if index is empty, ask for reindexing if not
    if not len(os.listdir(dirindex))==0:
        respuesta = messagebox.askyesno("Confirmar","Indice no vacío. Desea reindexar?") 
        if respuesta:
            carga()           
    else:
        carga()
        
# Function to search in subject or body of emails        
def asunto_o_cuerpo():
    # Inner function to handle the search when Enter is pressed
    def listar_asunto_o_cuerpo(event):
            ix=open_dir(dirindex)   
            with ix.searcher() as searcher:
                # Create a query that searches in both subject and content fields
                myquery = MultifieldParser(["asunto","contenido"], ix.schema).parse(str(entry.get()))
                results = searcher.search(myquery)
                listar(results)
            
    # Create input dialog
    v = Toplevel()
    label = Label(v, text="Introduzca consulta sobre asunto o contenido: ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar_asunto_o_cuerpo)
    entry.pack(side=LEFT)
    
# Function to search for emails after a specific date        
def posteriores_a_fecha():  
    # Inner function to handle the date search when Enter is pressed
    def listar_fecha(event):
            # Create a range query from the input date to the maximum possible date
            myquery='{'+ str(entry.get()) + ' TO]'
            ix=open_dir(dirindex)   
            try:
                with ix.searcher() as searcher:
                    query = QueryParser("fecha", ix.schema).parse(myquery)
                    results = searcher.search(query)
                    listar(results)
            except:
                messagebox.showerror("ERROR", "Formato de fecha incorrecto")
            
    # Create input dialog for date
    v = Toplevel()
    label = Label(v, text="Introduzca la fecha (AAAAMMDD): ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar_fecha)
    entry.pack(side=LEFT)
              
# Function to search for potential spam emails
def spam():
    # Inner function to handle spam search when Enter is pressed
    def listar_spam(event):
        ix=open_dir(dirindex)   
        with ix.searcher() as searcher:
            # Use OrGroup to match any of the specified spam words
            query = QueryParser("asunto", ix.schema,group=qparser.OrGroup).parse(str(entry.get()))
            results = searcher.search(query)
            
            # Create a window to display results with only specific information
            v1 = Toplevel()
            sc = Scrollbar(v1)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v1, width=100, yscrollcommand=sc.set)
            for row in results:
                s = 'FICHERO: ' + row['nombrefichero']
                lb.insert(END, s)
                s = 'REMITENTE: ' + agenda[row['remitente']]
                lb.insert(END, s)
                lb.insert(END, "-------------------------------")       
            lb.pack(side=LEFT, fill=BOTH)
            sc.config(command=lb.yview)        
    
    # Create input dialog for spam keywords
    v = Toplevel()
    label = Label(v, text="Introduzca palabras spam: ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar_spam)
    entry.pack(side=LEFT)           

# Function to add a document to the index
def add_doc(writer, path, docname):
    try:
        # Open and read document content
        fileobj=open(path+'\\'+docname, "r")
        rte=fileobj.readline().strip()        # Sender
        dtos=fileobj.readline().strip()       # Recipients
        f=fileobj.readline().strip()          # Date string
        dat=datetime.strptime(f,'%Y%m%d')     # Convert to datetime
        ast=fileobj.readline().strip()        # Subject
        ctdo=fileobj.read()                   # Body content
        fileobj.close()           
        
        # Add document to the index
        writer.add_document(remitente=rte, destinatarios=dtos, fecha=dat, asunto=ast, contenido=ctdo, nombrefichero=docname)
    
    except:
        messagebox.showerror("ERROR", "Error: No se ha podido añadir el documento "+path+'\\'+docname)

# Load the email-to-name mapping from agenda file
def crea_agenda():
    try:
        fileobj=open(dirage+'\\'+"agenda.txt", "r")
        email=fileobj.readline()
        # Read pairs of lines (email and name)
        while email:
            nombre=fileobj.readline()
            agenda[email.strip()]=nombre.strip()
            email=fileobj.readline()
    except:
        messagebox.showerror("ERROR", "No se ha podido crear la agenda. Compruebe que existe el fichero "+dirage+'\\'+"agenda.txt")
           
# Function to load both the index and agenda
def cargar():
    crea_index()
    crea_agenda()
    
# Display search results in a scrollable list
def listar(results):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    # Add each result to the listbox
    for row in results:
        s = 'REMITENTE: ' + row['remitente']
        lb.insert(END, s)       
        s = "DESTINATARIOS: " + row['destinatarios']
        lb.insert(END, s)
        s = "FECHA: " + row['fecha'].strftime('%d-%m-%Y')
        lb.insert(END, s)
        s = "ASUNTO: " + row['asunto']
        lb.insert(END, s)
        s = "CUERPO: " + row['contenido']
        lb.insert(END, s)
        lb.insert(END,"------------------------------------------------------------------------\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

# Create the main application window and menu
def ventana_principal():
    # Function to list all documents in the index
    def listar_todo():
        ix=open_dir(dirindex)
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            listar(results) 
    
    raiz = Tk()

    menu = Menu(raiz)

    # DATA menu
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar_todo)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    # SEARCH menu
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Asunto o Cuerpo", command=asunto_o_cuerpo)
    menubuscar.add_command(label="Posteriores a una Fecha", command=posteriores_a_fecha)
    menubuscar.add_command(label="Spam", command=spam)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()

# Entry point of the program
if __name__ == "__main__":
    ventana_principal()