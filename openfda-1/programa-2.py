import http.client
import json

conn = http.client.HTTPSConnection("api.fda.gov")

#En este caso para obtener diez objetos cualquiera de la url debemos especificar los parámetros de busqueda

#Estableciendo limit en 10 obtendremos 10 json de objetos cualquiera de toda la página ya que no hemos especificado
#el parámetro search

conn.request("GET", "/drug/label.json?limit=10", None, )

r1 = conn.getresponse()

print(r1.status, r1.reason)

label_raw = r1.read().decode("utf-8")

conn.close()

#Iteramos sobre las posiciones de los diccionarios con la información de cada objeto y obtenemos su id
for i in range (10):
    label = json.loads(label_raw)["results"][i]
    print ("El identificador del objeto", i+1, "es: " + str(label["id"]) + "\n")
    

