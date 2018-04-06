import http.server
import socketserver
import http.client
import json
import urllib.parse

PORT = 8000

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        #Aqui llamamos a nuestro cliente para que extraiga información sobre los medicamentos

        conn = http.client.HTTPSConnection("api.fda.gov")

        conn.request("GET", "/drug/label.json?limit=10", None, )

        r1 = conn.getresponse()

        print(r1.status, r1.reason)

        label_raw = r1.read().decode("utf-8")
        conn.close()

        label_raw2 = json.loads(label_raw)["results"]

#-----------------------------------------------------------------------------------------------------------------------

        #Gracias al módulo urllib.parse podemos analizar la url de nuestra página dividiéndola en segmentos que utilizaremos
        #más adelante

        parsed_path = urllib.parse.urlparse(self.path)

#-----------------------------------------------------------------------------------------------------------------------
        #Aquí comienza la respuesta del servidor ante la petición GET del cliente
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        #Expresamos el mensaje que luego será enviado por el servidor al cliente, en este caso será en lenguaje html
        #lo que será traducido en una página web para el cliente
        message = """<!doctype html>
        <html>
           <body style='background-color: white'>
             <h1>LISTA DE MEDICAMENTOS</h1>
           </body>
        </html>"""

        #En el bucle "for" se itera sobre el json obtenido por nuestro cliente y se añade al mensaje anterior el nombre
        #de cada medicamento que aparece en el archivo en forma de lista
        for e in range(10):
            try:
                label = label_raw2[e]["openfda"]
                message += "<li>{}</li>".format(str(e + 1) + ". " + str(label["generic_name"][0]))
            #"Except" por si algún medicamento aparece sin nombre
            except KeyError:
                message += "<li>{}</li>".format((str(e + 1) + ". " + "No name available"))
        #Enlazamos a la página principal otra página que definiremos más adelante con la etiqueta completa de todos los
        #medicamentos para más información del cliente
        message += "<a href=\"index.html\">click here for more info</a>"

        #-------------------------------------------------------------------------------------------#

        #Otro mensaje que el servidor enviará con otra pagina en la que guardamos la información de las etiquetas mediante
        #un bucle "for"
        message2 = """<!doctype html>
                               <html>
                                  <body style='background-color: white'>
                                  </body>
                               </html>"""

        for x in range(10):
            try:
                message2 += "<p>{}<p>".format(str(x + 1) + ". " + str(label_raw2[x]["openfda"]["generic_name"][0]) + " --->  " + str(label_raw2[x]))
            except KeyError:
                message2 += "<p>{}<p>".format(str(x + 1) + ". " + "No name available" + " --->  " + str(label_raw2[x]))

#-----------------------------------------------------------------------------------------------------------------------
        #En el segmento "path" está el archivo al que accede el cliente mediante el enlace anterior, ahí el servidor
        #enviará la página con las etiquetas
        if parsed_path.path == "/index.html":
            self.wfile.write(bytes(message2, "utf8"))
        else:
            self.wfile.write(bytes(message, "utf8"))
        print("File served!")
        return


# ----------------------------------
# El servidor comienza a aqui
# ----------------------------------
# Establecemos como manejador nuestra propia clase
Handler = HTTPRequestHandler

# -- Configurar el socket del servidor, para esperar conexiones de clientes
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)

    # Entrar en el bucle principal
    # Las peticiones se atienden desde nuestro manejador
    # Cada vez que se ocurra un "GET" se invoca al metodo do_GET de
    # nuestro manejador
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Interrumpido por el usuario")

print("")
print("Servidor parado")