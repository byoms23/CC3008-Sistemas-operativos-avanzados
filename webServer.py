# -*- coding: utf-8 -*-

# Crear utilitarios (importar modulos) propios
import Cache, Hilo
from daemon import Daemon
# Crear utilitarios (importar modulos) del sistema
import xml.dom.minidom, io, socket, Queue, sys, os
from xml.dom.minidom import Node

class byOS(Daemon):
    def run(self):
        
        # Verficar el archivo de configuracion
        script = sys.path[0] + "/"
        doc = xml.dom.minidom.parse(script + "configuration.xml")
        port, poolSize, cacheSize, rootFolder, logFile, users = '','','','', '', {}
        # Cargar configuraciones
        for node in doc.getElementsByTagName("port"):
            port = int(node.getAttribute("value"))
        for node in doc.getElementsByTagName("poolSize"):
            poolSize = int(node.getAttribute("value"))
        for node in doc.getElementsByTagName("cacheSize"):
            cacheSize = int(node.getAttribute("value"))
        for node in doc.getElementsByTagName("rootFolder"):
            rootFolder = node.getAttribute("value")
        for node in doc.getElementsByTagName("logFile"):
            logFile = node.getAttribute("value")
        for node in doc.getElementsByTagName("users"):
            for user in node.getElementsByTagName("user"):
                users[user.getAttribute("name")] = user.getAttribute("password")

        # Crear socket para escuchar en el puerto 80
        miSocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        miSocket.bind ( ( 'localhost', port ) )
        miSocket.listen ( 1 )

        # Crear la cola donde se encontraran todas las conexiones abiertas
        cola = Queue.Queue()

        # Crear cache (para guardar paginas)
        cache = Cache.Cache(cacheSize)

        # Crear pool the threads
        hilos = []
        for i in range(poolSize):
            h = Hilo.Hilo("Hilo ("+str(i+1)+")", 
                cola, cache, users, rootFolder, logFile, script)
            hilos += [h]
            h.start()

        # Hilo de ejecucion principal
        while True:
            # Esperar conexion en el socket
            canal, detalles = miSocket.accept()

            # Colocar conexion en la cola
            cola.put((canal, detalles))


if __name__ == "__main__":
    daemon = byOS('/tmp/byOS.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
