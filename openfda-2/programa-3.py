import http.client
import json

conn = http.client.HTTPSConnection("api.fda.gov")

#Nuestro cliente pide todos los archivos del servidor en los que el acido acetilsalicílico se encuentra como ingrediente
#activo. El parametro "count" nos devuelve un json con todos los términos que aparecen en el apartado "active_ingredient"
#y las veces que lo hacen

conn.request("GET", "/drug/label.json?search=active_ingredient:acetylsalicylic&count=active_ingredient")

r1 = conn.getresponse()

print(r1.status, r1.reason)

label_raw = r1.read().decode("utf-8")

conn.close()

label = json.loads(label_raw)

iterlabel = label["results"]
count = 0
#Con el siguiente bucle obtenemos el número de archivos que tienen como ingrediente activo el ácido
for dic in iterlabel:
    if dic["term"] == "acetylsalicylic":
        count = dic["count"]


#Volvemos a hacer que el cliente realice una petición con el volumen correspondiente al número de archivos que queremos
conn.request("GET", "/drug/label.json?search=active_ingredient:acetylsalicylic&limit={}".format(count))

r2 = conn.getresponse()

label_raw2 = r2.read().decode("utf-8")
conn.close()

label2 = json.loads(label_raw2)

iterlabel2 = label2["results"]

#Imprimimos por pantalla el nombre del fabricante de todos los medicamentos obtenidos del servidor
for e in iterlabel2:
    try:
        print("-" + str(e["openfda"]["manufacturer_name"]))
    except KeyError:
        print("- No hay datos del fabricante")
