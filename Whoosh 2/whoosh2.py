import os
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from tkinter import *
from tkinter import messagebox
import urllib.request
from bs4 import BeautifulSoup
from whoosh.fields import NUMERIC

# Dictionary to store email-name pairs
agenda={}
# Directory paths
dirdocs="Whoosh 1\Docs\Correos"      # Path to email documents
dirindex="Whoosh 2\Index"            # Path to the search index
dirage="Whoosh 1\Docs\Agenda"        # Path to the agenda file

# Creates a search index from documents in dirdocs directory
# The index is created in the dirindex directory
def crea_index():
    # Inner function to load and index documents
    def carga():
        # Define the schema for the index
        sch = Schema(titulo=TEXT(stored=True), precio=NUMERIC(stored=True, numtype = float), tematicas=KEYWORD(stored=True, commas=True), complejidad=TEXT(stored=True), num_jugadores=KEYWORD(stored=True), detalles=TEXT(stored=True))
        # Create the index
        ix = create_in(dirindex, schema=sch)
        writer = ix.writer()
        f = urllib.request.urlopen("https://zacatrus.es/juegos-de-mesa.html")
        s = BeautifulSoup(f, "lxml")
        lista_link_juegos = s.find("ol", class_=["products","list","items","product-items"]).find_all("li")

        for link_juego in lista_link_juegos:
            f = urllib.request.urlopen(link_juego.a['href'])
            s = BeautifulSoup(f, "lxml")

            #Titulo, porcentaje y precio los sacamos de una parte de la pagina
            datos = s.find("div", class_="product-info-main")

            titulo = datos.find("h1", class_="page-title").find("span", class_="base").string.strip()


            precio = datos.find("div", class_=["price-box","price-final_price"]).span.span.find("span", class_="price").string.strip()

            #Tematicas y complejidad los sacamos de otra parte de la pagina
            datos2 = s.find("div", class_=["data", "table","additional-attributes"])
            
            num_jugadores_element = datos2.find("div",class_=["col","data"], attrs={"data-th":"Núm. jugadores"})
            num_jugadores = num_jugadores_element.get_text(strip=True) if num_jugadores_element else []

            tematicas_element = datos2.find("div", class_=["col","data"], attrs={"data-th":"Temática"})
            if tematicas_element:
                tematicas = tematicas_element.get_text(strip=True)
                print(tematicas)
            else:
                tematicas = "Desconocida"
                print(tematicas)

            complejidad_element = datos2.find("div", class_=["col","data"], attrs={"data-th":"Complejidad"})
            if complejidad_element:
                complejidad = complejidad_element.get_text(strip=True)
            else:
                complejidad = "Desconocida"
        
            precio_convertido = precio.split("\xa0€")[0]

            detalles_element = s.find("div", class_=["product","info","detailed"]).p
            if detalles_element:
                detalles = detalles_element.get_text(strip=True)
            else:
                detalles = "Desconocida"


            writer.add_document(titulo=titulo, precio = float(precio_convertido.replace(",",".")), tematicas=tematicas, complejidad=complejidad, num_jugadores=num_jugadores, detalles=detalles)
        writer.commit()
        messagebox.showinfo("INDICE CREADO", "Se han cargado " + str(ix.reader().doc_count()) + " documentos")
    
    # Check if documents directory exists
        # Create index directory if it doesn't exist
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    # Check if index is empty, ask for reindexing if not
    if len(os.listdir(dirindex))!=0:
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

           
# Function to load both the index and agenda
def cargar():
    crea_index()
    
def list_to_str(data):
    """
    Converts a list or string to a formatted string.
    If data is already a string, returns it as is.
    If data is a list, joins the elements with commas.
    
    Args:
        data: List or string to convert
        
    Returns:
        String representation of the input data
    """
    if isinstance(data, list):
        return ", ".join(data)
    return str(data)


# Display search results in a scrollable list
def listar(results):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    # Add each result to the listbox
    for row in results:
        s = 'TITULO: ' + row['titulo']
        lb.insert(END, s)       
        s = "PRECIO: " + str(row['precio'])
        lb.insert(END, s)
        s = "TEMATICAS: " + row['tematicas']
        lb.insert(END, s)
        s = "COMPLEJIDAD: " + row['complejidad']
        lb.insert(END, s)
        s = "NUM_JUGADORES: " + list_to_str(row['num_jugadores'])
        lb.insert(END, s)
        s = "DETALLES: " + row['detalles']
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