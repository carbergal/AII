import os, ssl
from tkinter import Tk, Menu, messagebox
from bs4 import BeautifulSoup
import urllib.request
import lxml
import sqlite3




if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context 


def abrir_url(url,file):
    try:
        urllib.request.urlretrieve(url,file)
        return file
    except:
        print  ("Error al conectarse a la página")
        return None


def extraer_datos():
    fichero="vinos"
    resultado = []
    if abrir_url("https://www.vinissimus.com/es/vinos/tinto/?cursor=0",fichero):
        with open(fichero, "r", encoding="utf-8") as f:
            s = f.read()

        soup = BeautifulSoup(s, 'lxml')
        vinos = soup.find_all('div', class_='product-list-item')

        for vino in vinos:
            nombre = vino.find("div", class_="details").a.h2.text
            precio = vino.find("p", class_="price").text.strip()
            denominacion = vino.find("div", class_="details").find("div", class_="region").text.strip()
            bodega = vino.find("div", class_="details").find("div", class_="cellar-name").text.strip()
            uvas = vino.find("div", class_="details").find("div", class_="tags").find_all("span")
            uvas = [uva.string.replace("/", " ").strip() for uva in uvas]
            tipos = ""
            for uva in uvas:
                tipos += uva + ", "
            resultado.append([nombre, precio, denominacion,bodega,tipos])
    
    if abrir_url("https://www.vinissimus.com/es/vinos/tinto/?cursor=36",fichero):
        with open(fichero, "r", encoding="utf-8") as f:
            s = f.read()

        soup = BeautifulSoup(s, 'lxml')
        vinos = soup.find_all('div', class_='product-list-item')
      
        for vino in vinos:
            nombre = vino.find("div", class_="details").a.h2.text
            precio = vino.find("p", class_="price").text.strip()
            denominacion = vino.find("div", class_="details").find("div", class_="region").text.strip()
            bodega = vino.find("div", class_="details").find("div", class_="cellar-name").text.strip()
            uvas = vino.find("div", class_="details").find("div", class_="tags").find_all("span")
            uvas = [uva.string.replace("/", " ").strip() for uva in uvas]
            tipos = ""
            for uva in uvas:
                tipos += uva + ", "
            resultado.append([nombre, precio, denominacion,bodega,tipos])
    
    if abrir_url("https://www.vinissimus.com/es/vinos/tinto/?cursor=72",fichero):
        with open(fichero, "r", encoding="utf-8") as f:
            s = f.read()

        soup = BeautifulSoup(s, 'lxml')
        vinos = soup.find_all('div', class_='product-list-item')
        for vino in vinos:
            nombre = vino.find("div", class_="details").a.h2.text
            precio = vino.find("p", class_="price").text.strip()
            denominacion = vino.find("div", class_="details").find("div", class_="region").text.strip()
            bodega = vino.find("div", class_="details").find("div", class_="cellar-name").text.strip()
            uvas = vino.find("div", class_="details").find("div", class_="tags").find_all("span")
            
            uvas = [uva.string.replace("/", " ").strip() for uva in uvas]
            tipos = ""
            for uva in uvas:
                tipos += uva + ", "

            resultado.append([nombre, precio, denominacion,bodega,tipos])
    return resultado



def cargar():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS VINOS")   
    conn.execute('''CREATE TABLE VINOS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       NOMBRE           TEXT    NOT NULL,
       PRECIO           DOUBLE    NOT NULL,
       DENOMINACION        TEXT NOT NULL,
       BODEGA           TEXT NOT NULL,
       UVAS             TEXT NOT NULL);''')
    l = extraer_datos()
    for i in l:
        conn.execute("""INSERT INTO VINOS (NOMBRE, PRECIO, DENOMINACION, BODEGA, UVAS) VALUES (?,?,?,?,?)""",(i[0],i[1],i[2],i[3],i[4]))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM VINOS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()




raiz = Tk()

menu = Menu(raiz)

# DATOS
menudatos = Menu(menu, tearoff=0)
menudatos.add_command(label="Cargar", command=cargar)
# menudatos.add_command(label="Listar", command=listar_todos)
menudatos.add_command(label="Salir", command=raiz.quit)
menu.add_cascade(label="Datos", menu=menudatos)

# BUSCAR
menubuscar = Menu(menu, tearoff=0)
# menubuscar.add_command(label="Denominación", command=buscar_por_denominacion)
# menubuscar.add_command(label="Precio", command=buscar_por_precio)
# menubuscar.add_command(label="Uvas", command=buscar_por_uvas)
menu.add_cascade(label="Buscar", menu=menubuscar)

raiz.config(menu=menu)

raiz.mainloop()


