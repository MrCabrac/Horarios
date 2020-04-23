# -*- coding: utf-8 -*-
"""
Creado en Sun Sep 30 12:20:10 2018

@autor: Steven's
"""

def about_qt():
    about_qt_text = '''<h3>About Qt</h3><p>This program uses Qt version 5.6.2.</p>
                       <p>Qt is a C++ toolkit for cross-platform application development.</p>
                       <p>Qt provides single-source portability across all major desktop operating
                       systems. It is also available for embedded Linux and other embedded and
                       mobile operating systems.</p>
                       <p>Qt is available under three different licensing options designed to 
                       accommodate the needs of our various users.</p>
                       <p>Qt licensed under our commercial license agreement is appropriate 
                       for development of proprietary/commercial software where you do not 
                       want to share any source code with third parties or otherwise cannot 
                       comply with the terms of the GNU LGPL version 3 or GNU LGPL version 2.1.</p>
                       <p>Qt licensed under the GNU LGPL version 3 is appropriate for the 
                       development of Qt applications provided you can comply with the terms and
                       conditions of the GNU LGPL version 3.</p>
                       <p>Qt licensed under the GNU LGLP version 3 is appropriate for the 
                       development of Qt applications provided you can comply whit the terms and
                       conditions of the GNU LGPL version 3.</p>
                       <p>Qt licensed under the GNU LGLP version 2.1 is appropriate for the 
                       development of Qt applications provided you can comply whit the terms and
                       conditions of the GNU LGPL version 2.1.</p>
                       <p>Please see <a href="http://qt.io/licensing">qt.io/licensing</a>
                       for an overview of Qt licensing.</p>
                       <p>Copyright (C) 2016 The Qt Company Ltd and other contributors.</p>
                       <p>Qt and the Qt logo are trademarks of the Qt Company Ltd.</p>
                       <p>Qt is the Qt Company Ltd product developed as an open source project.<br>
                       See <a href="http://qt.io/">qt.io</a>
                       for more information.</p>'''
    return about_qt_text

def how_use():
    how_to_use = '''<h3>Como usar E-Race</h3>
                       <p>Conecte todo el hardware (Arduino y sensores).</p>
                       <p>Inicie el programa.</p>
                       <p>Puede cambiar el nombre de los equipos haciendo doble click sobre la
                       casilla.</p>
                       <p>En la caja de arduino, haga click en <b>Refresh</b> para visualizar los
                       puertos disponibles y seleccione el correcto.</p>
                       <p>Cuando esté listo, haga click en <b>Comenzar</b> y espere los marcadores
                       en el monitor.</p>
                       <p>Puede hacer un máximo de 4 carreras, al final, presione <b>Total</b> 
                       para ver el tiempo resultante de todas las pruebas para cada competidor.</p>
                       <p>Para exportar el archivo con los resultados, use <b>'Ctrl + E'</b> o
                       haga click en <b>Exportar</b> desde 'File', el archivo estará en el directorio
                       del programa.</p>
                       <p>Para comenzar de nuevo haga click en <b>Reset Todo</b>, esto limpiará
                       los marcadores y el historial.</p>
                       <p><b>Inicio rápido</b> se usa cuando no quiere esperar un comienzo manual.</p>'''
    return how_to_use

def about_program():
    about_program = '''<h3>About E-Race</h3>
                       <p>Record competition times and save in data sheet.</p>
                       <p>Created by Brayan Martínez</p>
                       <p>Python 3.6.3 64bits, Qt 5.6.2, PyQt 5.6.2 on Windows</p>'''
    return about_program

if __name__ == "__main__":
    print("About")

about_qt()
about_program()
