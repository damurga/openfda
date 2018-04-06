import http.client
import json

conn = http.client.HTTPSConnection("api.fda.gov")

conn.request("GET", "/drug/label.json", None, )

r1 = conn.getresponse()

print(r1.status, r1.reason)

label_raw = r1.read().decode("utf-8")

conn.close()

label = json.loads(label_raw)["results"][0]

#Imprimimos por pantalla los datos que nos piden a partir del json obtenido por la petición del cliente
print("Los datos obtenidos del producto se muestran a continuación:" + "\n"*2 + "- Identificador(id):", str(label["id"]))
print("- Proposito del producto:", ",".join(label["purpose"]))
print("- Nombre del fabricante:", str(label["openfda"]["manufacturer_name"][0]))
