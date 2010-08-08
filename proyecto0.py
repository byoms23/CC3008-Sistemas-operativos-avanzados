# -*- coding: utf-8 -*-
import socket, io
from time import gmtime, strftime

mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
mySocket.bind ( ( 'localhost', 2727 ) )
mySocket.listen ( 1 )

while True:
  channel, details = mySocket.accept()
  print 'We have opened a connection with', details
  solicitud = channel.recv ( 100 )
  
  print solicitud
  
  log = open('request.log', 'a')
  log.write("Conexion con: " + str(details) + '\n')
  
  # Revisar que la solicitud sea valida
  if not solicitud.startswith('GET'):
    log.write('Solicitud denegada: ' + str(solicitud) + '\n' )
    log.write('\n')
    log.close()
    continue
  
  # Crear log
  log.write('Solicitud aceptada: ' + str(solicitud) + '\n' )
  log.write('\n')
  log.close()
  
  # Crear pagina de respuesta
  pagina = ""
  fichero = open('archivo.html', 'r')
  for linea in fichero:
    pagina += linea
  fichero.close() 

  channel.send ( '''
HTTP/1.1 200 OK
Server: byWS/0.1 (Unix) (FreeBSD/BSD)
Date: ''' + strftime("%a, %d %b %Y %H:%M:%S ", gmtime()) + '''
Content-Type: text/html
Content-Length: ''' + str(len(pagina)) + '\n\n' + pagina)
  
  channel.close()
   
   
"""
CODE: SELECT ALL   EXPAND VIEW
hostname="fbsdgw.marbosoft.org"
#this is my real ADSL router
defaultrouter="192.168.0.1"      

Marco
ifconfig_em0="DHCP"
ifconfig_em1="inet 172.16.1.1netmask 255.255.255.0"
ifconfig_em2="inet 172.16.2.1netmask 255.255.255.0"
gateway_enable="YES"


This is first "client"'s rc.conf:

CODE: SELECT ALL   EXPAND VIEW
hostname="fbsdnw11.marbosoft.org"
ifconfig_em0="inet 172.16.1.2netmask 255.255.255.0"
defaultrouter="fbsdgw"
"""