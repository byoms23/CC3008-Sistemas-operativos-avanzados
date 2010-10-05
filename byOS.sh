#!/bin/sh
case "$1" in
    start)
        # codigo para iniciar el demonio/programa
        python webServer.py start
    ;;
    stop)
        # codigo para parar el demonio/programa
        python webServer.py stop
    ;;
    restart)
        # codigo para reiniciar el demonio/programa
        python webServer.py restart
    ;;
        # imprimir error
esac
