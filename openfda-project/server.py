import http.server
import socketserver
import http.client
import json
import urllib.parse

PORT = 8000

#Importamos los módulos necesarios y definimos el puerto

# noinspection PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker
class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    #Definimos "do_Get" para atender las peticiones del cliente
    def do_GET(self):

        #La clase "responses" nos servirá para enviar los headers necesarios en funcion de si la petición no se puede procesar,
        #si se trata de acceder a un sitio sin identificación o si se ejecuta /redirect
        class responses(HTTPRequestHandler):
            def response200(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                return

            def response404(self):
                self.send_response(404, "Not Found")
                self.send_error(404, "SEARCH NOT FOUND", "READ BELOW")
                return

            def response401(self):
                self.send_response(401, "Unauthorized")
                self.send_header('WWW-Authenticate', 'Basic realm="Secure Area"')
                self.end_headers()
                return

            def response302(self):
                self.send_response(302, "Redirect")
                self.send_header('Location', '/')
                self.end_headers()
                return

        #parsed_path analizará la url introducida en cada momento dividiendola en distintos parámetros

        parsed_path = urllib.parse.urlparse(self.path)

#-----------------------------------------------------------------------------------------------------------------------
        #En la clase OpendFDAHTML se define el HTML básico de los mensajes que enviaremos al cliente aunque luego puedan ser
        #modificados

        class OpenFDAHTML(responses):

            def message(self):
                with open("index.html","r" ) as plot:
                    mesage = plot.read()
                return mesage

            def message2(self):
                with open("index2.html", "r") as plot2:
                    mesage2 = plot2.read()
                return mesage2
            def message3(self):
                mesage3 = """<!doctype html>
                                   <html>
                                       <body style='background-color: white'>
                                       </body>
                                   </html>"""
                return mesage3
            def message4(self):
                mesage4 = """<!doctype html>
                                   <html>
                                       <body style='background-color: white'>
                                       </body>
                                   </html>"""
                return mesage4
        message = OpenFDAHTML.message(self)
        message2 = OpenFDAHTML.message2(self)
        message3 = OpenFDAHTML.message3(self)

#-----------------------------------------------------------------------------------------------------------------------

        #La clase OpenFDAParser define los métodos para comunicarse con la API de OpenFda y obtener la información requerida
        #por el cliente
        class OpenFDAParser(OpenFDAHTML):

            #index() se encargará de las peticiones de search (Ej: searchDrug)
            def index(self, search, name):

                conn = http.client.HTTPSConnection("api.fda.gov")

                #Si el usuario no ha definido el parámetro limit lo definimos como "limit=10"
                if "limit" in parsed_path.query:
                    if "searchDrug" in parsed_path.path:
                        params = str(parsed_path.query).split("&")
                    else:
                        #Queremos que params tenga una lista con la busqueda en [0] y limit en [1], si el usuario en lugar de
                        #"openfda.manufacturer_name" introduce "company=" lo sustituimos para hacer la petición a la Api
                        params = str(parsed_path.query).split("&")
                        params[0] = "openfda.manufacturer_name:{}".format(str(parsed_path.query)[8:str(parsed_path.query).find("&")])

                else:
                    params = [parsed_path.query, "limit=10"]


                #La siguiente petición nos servirá para obtener el número total de resultados para nuestra búsqueda
                conn.request("GET","/drug/label.json?search={}".format(params[0]))

                r1 = conn.getresponse()

                print(r1.status, r1.reason)

                label_raw = r1.read().decode("utf-8")

                conn.close()

                label = json.loads(label_raw)

                message3 = OpenFDAHTML.message3(self)


                try:
                    #La siguiente linea sirve para asegurarse de que el parámetro "limit" introducido es numérico
                    int(str(params[1])[6:])
                    try:
                        #El numero total de resultados se guardan en "count"
                        count = label['meta']['results']['total']

                        #No se pueden mostrar más de 100 resultados
                        if count < 100 or int(params[1][6:]) < 100:

                            #Obtenemos las busquedas con el "limit" correspondiente
                            conn.request("GET", "/drug/label.json?search={}&{}".format(params[0], params[1]))

                            r2 = conn.getresponse()

                            print(r2.status, r2.reason)

                            label_raw2 = r2.read().decode("utf-8")

                            conn.close()

                            label2 = json.loads(label_raw2)

                            #Al llamar al método hemos definido name como título de la página y search como búsqueda
                            message3 += "<h1 align=\"center\">{}</h1>".format(name)

                            message3 += "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>" + "<HR>"

                            if search == "active_ingredient":
                                enum = 0
                                message3 += "<ul>"
                                message3 += "<h4 align=right> Showing {} results of {} </h4>".format(params[1][6:], count)
                                for result in label2["results"]:
                                    enum += 1
                                    try:
                                        #obtenemos el nombre de las compañias y el id para mayor información
                                        id = result['id']
                                        companyname = result["openfda"]["manufacturer_name"][0]
                                        message3 += "<li>{}. <b>Company Name:</b> {} || <b>Id:</b> {} </li>".format(enum, companyname, id)
                                        message3 += "<br>"
                                    except:
                                        id = result['id']
                                        message3 += "<li>{}. <b>Company Name:</b> {} || <b>Id:</b> {} </li>".format(enum, "No name available", id)
                                        message3 += "<br>"

                            else:
                                enum2 = 0
                                message3 += "<ul>"
                                message3 += "<h4 align=right> Showing {} results of {}</h4>".format(params[1][6:], count)
                                for result in label2["results"]:
                                    enum2 += 1
                                    try:
                                        #En este caso nombre de los fármacos e id
                                        drugname = result["openfda"]["generic_name"][0]
                                        id = result['id']
                                        message3 += "<li>{}. <b>Drug Name:</b> {} || <b>Id:</b> {} </li>".format(enum2, drugname, id)
                                        message3 += "<br>"
                                    except:
                                        id = result['id']
                                        message3 += "<li>{}. <b>Drug Name:</b> {} || <b>Id:</b> {} </li>".format(enum2, "No name available", id)
                                        message3 += "<br>"
                            message3 += "</ul>"

                            #Una vez ejecutada la petición mandamos la cabecera "200 OK"
                            responses.response200(self)
                            self.wfile.write(bytes(message3, "utf8"))

                        #Para los fallos enviamos la cabecera "404 Not Found"
                        else:
                            message3 += "<HR>" + "<h2 align = \"center\">Error 404----> Termino poco especifico (Mas de 100 resultados)</h2>" \
                                        + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                            responses.response404(self)
                            self.wfile.write(bytes(message3, "utf8"))
                    except:
                        message3 += "<HR>" + "<h2 align = \"center\">Error 404----> No hay resultados disponibles para su busqueda</h2>" \
                                    + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"

                        responses.response404(self)
                        self.wfile.write(bytes(message3, "utf8"))
                    return
                except:
                    message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es correcta</h2>" \
                                + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message3, "utf8"))
                    return



            #index2() sirve para obtener la información de la Api y listar los datos obtenidos (Ej: listDrugs)
            def index2(self, name2, field1 , field2):

                params2 = [parsed_path.query]

                conn = http.client.HTTPSConnection("api.fda.gov")

                conn.request("GET", "/drug/label.json?{}".format(params2[0]))

                r3 = conn.getresponse()

                print(r3.status, r3.reason)

                label_raw3 = r3.read().decode("utf-8")

                conn.close()

                label3 = json.loads(label_raw3)
                enum = 0
                message4 = OpenFDAHTML.message4(self)

                try:
                    #De igual forma comprobamos que "limit" sea numérico y menor que 100
                    int(str(params2[0])[6:])
                    if int(str(params2[0])[6:]) < 100:
                        message4 = "<h1 align = \"center\">{}</h1>".format(name2)
                        message4 += "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>" + "<HR>"
                        message4 += "<ul>"
                        for list3 in label3['results']:
                            enum += 1
                            #En este caso "field1" y "field2" son parámetros que nos indican la ruta dentro del Json de
                            #los Warnings, los nombres de fármacos y los nombres de empresas
                            if field1 != "":
                                try:
                                    element = list3[field1][field2][0]
                                    message4 += "<li>{}. {}</li>".format(enum, element)
                                    message4 += "<br>"
                                except:
                                    message4 += "<li>{}. {}</li>".format(enum, "Desconocida")
                                    message4 += "<br>"
                            else:
                                try:
                                    #Si "field1" esta vacio significa que estamos buscando Warnings, que no están dentro de
                                    #openfda en el Json
                                    element = list3[field2][0]
                                    message4 += "<li>{}. {}</li>".format(enum, element)
                                    message4 += "<br>"
                                except:
                                    message4 += "<li>{}. {}</li>".format(enum, "Desconocida")
                                    message4 += "<br>"

                        message4 += "</ul>"
                        responses.response200(self)
                        self.wfile.write(bytes(message4, "utf8"))
                    else:
                        message4 += "<HR>" + "<h2 align = \"center\">Error 404----> Termino poco especifico (Mas de 100 resultados)</h2>" \
                                    + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                        responses.response404(self)
                        self.wfile.write(bytes(message4, "utf8"))
                except:
                    message4 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es correcta</h2>"
                    message4 += "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message4, "utf8"))

                return



# ----------------------------------------------------------------------------------------------------------------------
        #OpenFDAClient define los metodos para enviar el mensaje solicitado al cliente
        class OpenFDAClient(OpenFDAParser):
            def search1(self):
                responses.response200(self)
                self.wfile.write(bytes(message, "utf8"))
            def search2(self):
                responses.response200(self)
                self.wfile.write(bytes(message2, "utf8"))
            def search3(self):
                responses.response200(self)
                self.wfile.write(bytes(message3, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------

        #Si en la url se pide la página principal o la de Api More Info se manda la siguiente respuesta:
        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            OpenFDAClient.search1(self)
        elif parsed_path.path == "/index2.html":
            OpenFDAClient.search2(self)

#-----------------------------------------------------------------------------------------------------------------------

        elif parsed_path.path == "/searchDrug":
            if parsed_path.query == "":
                #Si no se han introducido campos para iniciar la búsqueda se muestra el formulario correspondiente
                message += "<form method=\"get\"> " \
                           "<div>Drug Name<input type = \"text\" name = \"active_ingredient\"></div>" \
                           "<div>Limit<input type = \"text\" name = \"limit\"<\div><div class=\"button\">" \
                           "<button type=\"submit\">Send your message</button></div></form>"
                OpenFDAClient.search1(self)
            else:
                #Nos aseguramos de que el campo introducido es correcto
                if "active_ingredient" in parsed_path.query:
                    OpenFDAParser.index(self, "active_ingredient", "ETIQUETAS DE LOS MEDICAMENTOS")
                else:
                    message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es " \
                                         "correcta, revise los parametros</h2>" \
                                + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message3, "utf8"))


        elif parsed_path.path == "/searchCompany":
            if parsed_path.query == "":
                message += "<form method=\"get\"" \
                           "> Company Name<input type = \"text\" name = \"openfda.manufacturer_name\">" \
                           "<div>Limit<input type = \"text\" name = \"limit\"<\div><div class=\"button\">" \
                           "<button type=\"submit\">Send your message</button></div></form>"
                OpenFDAClient.search1(self)
            else:
                #En este caso "company" también nos sirve como campo
                if "openfda.manufacturer_name" in parsed_path.query or "company" in parsed_path.query:
                    OpenFDAParser.index(self, "openfda.manufacturer_name", "ETIQUETAS DE LOS MEDICAMENTOS DE LA EMPRESA")

                else:
                    message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es " \
                                         "correcta, revise los parametros</h2>" \
                                + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message3, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------

        elif parsed_path.path == "/listDrugs":
            if parsed_path.query == "":
                message += "<form method=\"get\"" \
                           "<div>Limit<input type = \"text\" name = \"limit\"<\div><div class=\"button\">" \
                           "<button type=\"submit\">Send your message</button></div></form>"
                OpenFDAClient.search1(self)
            else:
                #Para ejecutar un listado de productos debe estar presente el campo "limit"
                if "limit" in parsed_path.query:
                    OpenFDAParser.index2(self, "LISTA DE FARMACOS", "openfda", "generic_name")
                else:
                    message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es " \
                                         "correcta, revise los parametros</h2>" \
                                + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message3, "utf8"))
        elif parsed_path.path == "/listCompanies":
            if parsed_path.query == "":
                message += "<form method=\"get\"" \
                           "<div>Limit<input type = \"text\" name = \"limit\"<\div><div class=\"button\">" \
                           "<button type=\"submit\">Send your message</button></div></form>"
                OpenFDAClient.search1(self)
            else:
                if "limit" in parsed_path.query:
                    OpenFDAParser.index2(self, "LISTA DE EMPRESAS", "openfda", "manufacturer_name")
                else:
                    message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es " \
                                         "correcta, revise los parametros</h2>" \
                                + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message3, "utf8"))

        elif parsed_path.path == "/listWarnings":
            if parsed_path.query == "":
                message += "<form method=\"get\"" \
                           "<div>Limit<input type = \"text\" name = \"limit\"<\div><div class=\"button\">" \
                           "<button type=\"submit\">Send your message</button></div></form>"
                OpenFDAClient.search1(self)
            else:
                if "limit" in parsed_path.query:
                    OpenFDAParser.index2(self, "LISTA DE ADVERTENCIAS", "", "warnings")
                else:
                    message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es " \
                                         "correcta, revise los parametros</h2>" \
                                + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
                    responses.response404(self)
                    self.wfile.write(bytes(message3, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------
        #Si el cliente trata de acceder a /secret se pedirá una clave de autentificación y se redireccionará a una página
        #de error
        elif parsed_path.path == "/secret":
            responses.response401(self)
            message3 += "<HR>" + "<h2 align = \"center\">Error 401----> Error de autenficacion, pagina no disponible </h2>" \
                        + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
            self.wfile.write(bytes(message3, "utf8"))

        #En /redirect se nos redireccionará a la página principal desde cualquier punto de la web
        elif parsed_path.path == "/redirect":
            responses.response302(self)


#-----------------------------------------------------------------------------------------------------------------------

        #En caso de que la dirección introducida no este comprendida entre las que puede procesar el código se lanzará
        #un error
        else:
            message3 += "<HR>" + "<h2 align = \"center\">Error 404----> La direccion introducida no es correcta, " \
                                 "revise los parametros de busqueda</h2>" \
                            + "<h2 align=\"center\"><a href=\"index.html\">Navegacion intraweb</a></h2>"
            responses.response404(self)
            self.wfile.write(bytes(message3, "utf8"))


        print("File served!")
        return


socketserver.TCPServer.allow_reuse_address = True



# Establecemos como manejador nuestra propia clase
Handler = HTTPRequestHandler

#Configuramos el socket del servidor, para esperar conexiones de clientes
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



