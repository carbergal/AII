import re
from datetime import datetime

with open("fichero1", encoding="utf-8") as f:
    s = f.read()



def transform_date(date_str):
    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    return date_obj.strftime('%d/%m/%Y')

titulos = re.findall(r'<title>(.+)</title>', s)[1:]
links = re.findall(r'<link>(.+)</link>', s)[1:]
fechas = re.findall(r'<pubDate>(.+)</pubDate>', s)
    

mes = input("Introduce un mes para filtrar las noticias: ")


dia = input("Introduce un día para filtrar las noticias: ")


for i in range(len(titulos)):
    fechas[i] = transform_date(fechas[i])
    if fechas[i].split("/")[1] == mes and fechas[i].split("/")[0] == dia:
        print(f"Título: {titulos[i]} \nLink: {links[i]} \nFecha: {fechas[i]}\n")

