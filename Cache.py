# -*- coding: utf-8 -*-

class Cache():
    # Crear constructor
    def __init__(self, maxSize):
        self.paginas = {}
        self.maxSize = maxSize
    
    def __len__(self):
        return len(self.paginas)
    
    def __contains__(self, nombre):
        return self.paginas.has_key(nombre)
    
    def __getitem__(self, nombre):
        return self.paginas[nombre]
    
    def __setitem__(self, nombre, pagina):
        self.agregarPagina(nombre, pagina)
    
    def __iter__(self):
        return self.paginas.__iter__()
    
    def size(self):
        # Devolver el tamano acutal
        return len(self.paginas)
    
    def eliminarPaginaMasAntigua(self):
        # Revisar que cache no este vacia
        if len(self) > 0:
            self.paginas.popitem()
    
    def buscarPagina(self, nombre):
        # Buscar el nombre de la pagina
        return self.__contains__(nombre)
    
    def agregarPagina(self, nombre, pagina):
        # Revisar que la pagina no sea duplicada
        if self.buscarPagina(nombre):
            return
        
        # Revisar si se ha llegado al limite de paginas
        if len(self) >= self.maxSize:
            self.eliminarPaginaMasAntigua()
        
        # Agregar la pagina actual
        self.paginas[nombre] = pagina
