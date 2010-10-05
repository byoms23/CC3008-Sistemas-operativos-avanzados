# -*- coding: utf-8 -*-

import io, threading, time, sys
from time import gmtime, strftime

class Hilo(threading.Thread):
    
    name = ""
    
    def __init__(self, nombre, cola, cache, users, rootFolder, logFile, scripPath):
        threading.Thread.__init__(self)
        self.setName(nombre)
        self.cola = cola
        self.usuarios = users
        self.rootFolder = rootFolder
        self.logFile = logFile
        self.cache = cache
        self.canal = None
        self.detalles = None
        self.disk = None
        self.log = None
        self.scriptPath = scripPath
        
    def __str__(self):
        return str(self.getName())
    
    def run(self):
        while True:
            # Limpiar datos
            self.disk = None
            self.log = None
            
            # Revisar cola y esperar hasta que existan
            self.canal, self.detalles = self.cola.get(True)
            
            # Recibir y procesar mensaje
            self.recibirMensaje(self.canal, self.detalles)
            
            # Terminar ejecucion actual
            self.terminar(self.canal, self.log)
    
    
    def recibirMensaje(self, canal, detalles):
        # Recibir la solicitud
        solicitud = canal.recv ( 10000 )
        #solicitud = None
        #canal.recv_into ( solicitud )

        
        # Informar que se está utilizando
        #print "Descripción hilo: ", self
        #print len(solicitud)
        #print solicitud
        
        # Inicio de log
        logText = 'Date: ' + strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()) + '\n'
        logText += 'IP: ' + detalles[0] + '\n'
        
        # Crear parametros de retorno
        solicitud =  solicitud.split()
        link = ''
        returnCode = ''
        disk = ''
        pagina = ''
        # Revisar que la solicitud sea valida
        if solicitud[0] != 'GET':
            # TODODONE Enviar mensaje de error
            returnCode = '405 Method Not Allowed\nAllow: GET'
            pagina = self.abrirRecurso('error/405.html')
            disk = '"Error 405"'
        else:
            # TODODONE Obtener enlace pedido
            link = solicitud[1]
            
            # Revisar si el link a punta a '*/'
            if link[-1]  == '/':
                link = link + 'index.html'
            # Revisar si el link empieza con '/'
            if link[0] == '/':
                link = link [1:]
            # Agregar el folder inicial
            #~ print link
            
            # Buscar recurso solicitado
            returnCode, disk, pagina = self.buscarRecurso(link, solicitud)
            
        # Crear codigo de envio
        contenido = '''
Content-Type: text/html
Content-Length: ''' + str(len(pagina)) + '\n\n' + pagina
        code = 'HTTP/1.1 ' + returnCode + '''
Server: byWS/0.2.1 (Unix) (FreeBSD/BSD)
Date: ''' + strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()) + contenido
        
        # Enviar codigo solicitado
        canal.send (code)
        
        # Registrar cambios en el log
        logText += 'URL requested:'  + link + '\n'
        logText += 'Sended code: """' + code +'\n"""\n'
        logText += 'Transfered bytes: ' + str(len(code)) + '\n'
        logText += 'From ' + disk + '.\n'
        logText += "Executed in thread '" + str(self) + "'.\n\n"
        log = open(self.scriptPath + self.logFile, 'a')
        log.write(logText)
        log.close()
        
        # Guardar el resultado de la operacion
        self.disk = disk
        self.log = log
    
    def terminar(self, canal, log):
        # Cerrar conexion
        canal.close()
        
        # Terminar la tarea
        self.cola.task_done()

    
    def buscarRecurso(self, link, solicitud):
        returnCode, disk, pagina = '200 OK', '', ''
        try:
            # Revisar cache
            pagina = self.cache[link]
            
            # Reportar que se ha encontrado en cache
            disk = "cache"
        except KeyError as x:
            try:
                # Crear pagina de respuesta
                pagina = self.abrirRecurso(link, fatherPath=self.rootFolder)
                
                # Reportar que se ha tomado de disco
                disk = 'disk'
                
                # Guardar pagina en cache
                self.cache[link] = pagina
                
            except IOError as ioerror:
                # TODODONE Enviar mensaje de error porque no existe el recurso
                returnCode = '404 Not Found'
                pagina = self.abrirRecurso('error/404.html')
                disk = '"Error 404"'
                
        try:
            # Autentificar
            self.autentificar(link, solicitud)
        except AccesoNoAutorizado as aut:
            # TODO Enviar mensaje de error porque no tiene permiso para ver la pagina
            returnCode = '401 Authorization Required\nWWW-Authenticate: Basic realm="Secure Area"'
            pagina = self.abrirRecurso('error/401.html')
            disk = '"Error 401"'
        
        # Devolver datos encontrados
        return returnCode, disk, pagina

    def abrirRecurso(self, path, fatherPath=None):
        # Agregar path
        if not fatherPath:
            fatherPath = self.scriptPath
        
        
        # Abrir recurso
        fichero = open(fatherPath + path, 'r')
        
        # Recorrer recurso
        pagina = ''
        for linea in fichero:
            pagina += linea
        
        # Cerrar recurso
        fichero.close()
        
        # Devolver resultado
        return pagina
    
    def autentificar(self, link, solicitud):
        # Revisar si es un archivo seguro
        if not link.endswith('.htmls'):
            return
        
        # Revisar si tiene parametros de autentificacion
        if "Authorization:" in solicitud:
            i = solicitud.index("Authorization:")
            # Revisar que la solicitud sea valida
            if solicitud[i+1] == "Basic":
                # Descifrar la cadena de identificacion
                identificador = solicitud[i+2].decode("base64").split(":")
                usuario = identificador[0]
                password = identificador[1]
                
                #~ print usuario, ": '",password, "'" 
                try:
                    passTemp = self.usuarios[usuario]
                    if passTemp != password:
                        # Tirar exception por acceso no autorizado
                        raise AccesoNoAutorizado(link)

                except KeyError:
                    # Tirar exception por acceso no autorizado
                    raise AccesoNoAutorizado(link)
            else:
                # Tirar exception por acceso no autorizado
                raise AccesoNoAutorizado(link)
        else:
            # Tirar exception por acceso no autorizado
            raise AccesoNoAutorizado(link)

import exceptions
class AccesoNoAutorizado(exceptions.Exception):
    def __init__(self, pageName):
        self.message='"'+pageName+'" requiere autentificacion.'
        
