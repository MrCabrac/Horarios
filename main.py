# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 18:52:01 2020

@author: Steven
"""

########################################NOTAS########################################
#   - Los cambios desde un cuadro de diálogo interactivo solo se realizan al presionar OK !!!
#   - Eliminar los archivos entre opciones y no la carpeta
#
#####################################################################################
#   subjects_list: LISTA DE TODAS LAS MATERIAS con su semestre
#####################################################################################
import os
import sys
import shutil
import pandas as pd
from PyQt5 import uic, QtWidgets, QtCore, Qt, QtGui
from PyQt5.QtCore import QThreadPool, QEventLoop, QTimer
from PyQt5.QtWidgets import (QApplication, QDialog, QPushButton, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QHeaderView, QMenu,
                             QActionGroup, QAction, QMessageBox, QInputDialog, QWidget,
                             QFileDialog)

from PyQt5.QtGui import QPainter, QColor, QFont
import numpy.core._methods
import numpy.lib.format
import numpy as np
import re

qtCreatorFile = "main.ui" # Nombre del archivo de la interface gráfica.
qtReadExcelfile = "readExcel.ui" # Nombre del archivo de la interface gráfica.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
Read_Excel_Window, QtBaseClass = uic.loadUiType(qtReadExcelfile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Horarios")

        self.schedule_view_select.setEnabled(False)
        #Tabla 1 ----------------
        self.teachers_table.setColumnCount(3)# Establecer el número de columnas
        self.teachers_table.setAlternatingRowColors(True)# Dibujar el fondo usando colores alternados
        self.teachers_table.verticalHeader().setVisible(False)# Ocultar encabezado vertical
        self.teachers_table.horizontalHeader().setVisible(False)# Ocultar encabezado vertical
        self.teachers_table.horizontalHeader().setStretchLastSection(True)
        self.teachers_table.setWordWrap(False)# Establecer el ajuste de palabras del texto
        self.teachers_table.setSortingEnabled(False)# Deshabilitar clasificación
        self.teachers_table.clicked.connect(self.select_teacher)
        for indice, ancho in enumerate((180, 45, 45), start=0):
            self.teachers_table.setColumnWidth(indice, ancho)
        #Tabla 2 ----------------
        self.week_table.setColumnCount(6)# Establecer el número de columnas
        self.week_table.setDragDropOverwriteMode(False)# Deshabilitar el comportamiento de arrastrar y soltar
        self.week_table.setRowCount(15)# Establecer el número de filas
        self.week_table.setAlternatingRowColors(True)# Dibujar el fondo usando colores alternados
        self.week_table.setHorizontalHeaderLabels(("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.week_table.setVerticalHeaderLabels(("6-7","7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.week_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Deshabilitar edición
        self.week_table.setWordWrap(False)# Establecer el ajuste de palabras del texto
        self.week_table.setSortingEnabled(False)# Deshabilitar clasificación
        self.week_table.clicked.connect(self.edit_data_table)
        #self.week_table.itemDoubleClicked.connect(self.edit_data_table)
        for indice, ancho in enumerate((100, 100, 100, 100, 100, 100), start=0):
            self.week_table.setColumnWidth(indice, ancho)

        #Botones
        self.add_subject.clicked.connect(self.add_subject_to_list)
        self.del_subject.clicked.connect(self.delete_subject_to_list)
        self.subject_list.itemClicked.connect(self.item_click)
        self.save_table_button.clicked.connect(self.save_data_table)
        self.crearOpciones.clicked.connect(self.make_options)
        self.cargarResultados.clicked.connect(self.schedule_to_tableview)
        #--------
        self.actionSalir.triggered.connect(self.close)
        self.actionConfigurar_profesores.triggered.connect(self.teacher_filter)
        self.actionD_as.triggered.connect(self.day_filter)
        self.actionA_adir.triggered.connect(self.add_teacher)
        self.actionRemover.triggered.connect(self.del_teacher)
        self.actionA_adir_asignaturas.triggered.connect(self.add_asignatura_window)
        self.actionEliminar_asignatura.triggered.connect(self.del_asignatura)
        self.actionA_adir_grupo_a_asignatura.triggered.connect(self.add_group_window)
        self.actionA_adir_grupo_a_asignatura.setStatusTip("Añadir un grupo de clase para la asignatura seleccionada.") ##################################
        self.actionA_adir_grupo_a_asignatura.setEnabled(False)
        self.actionEliminar_grupo.triggered.connect(self.del_group)
        self.actionEliminar_grupo.setEnabled(False)
        self.actionCargar_archivo.triggered.connect(self.automaticLoad)
        #---
        self.schedule_view_select.valueChanged.connect(self.view_schedule)
        #Listas
        self.teachers_name_list = list()
        if not os.path.exists('teacher_list.npy'):
            np.save('teacher_list.npy', self.teachers_name_list) #si no existe, crea algo vacio
        self.teachers_name_list = np.load('teacher_list.npy').tolist()

        ##Cargar la lista de todas las materias
        self.list_of_all_subjects = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], }
        if not os.path.exists('subjects_list.npy'):
            np.save('subjects_list.npy', self.list_of_all_subjects)#si no existe, crea algo vacio
        self.list_of_all_subjects = np.load('subjects_list.npy', allow_pickle=True).item()

        self.load_groups_file()
        '''
        self.teachers = {"Análisis numérico": [[self.teachers_name_list[0], "GR01", "2.1C"],
                                               [self.teachers_name_list[1], "GR03", "2.1C"],
                                               [self.teachers_name_list[2], "GR04", "2.1C"],
                                               [self.teachers_name_list[1], "GR05", "2.1C"],
                                               [self.teachers_name_list[2], "GR06", "2.1C"],
                                               [self.teachers_name_list[2], "GR07", "2.1C"],
                                               ["none", "none", "none"]],
                         "Dinámica": [[self.teachers_name_list[3], "GR01", "2.5C"],
                                      ["none", "none", "none"]],
                         "Física de campos": [[self.teachers_name_list[4], "GR01", "2.4B"],
                                              [self.teachers_name_list[6], "GR02", "2.4B"],
                                              [self.teachers_name_list[7], "GR04", "2.3B"],
                                              [self.teachers_name_list[7], "GR05", "2.5B-2.3B"],
                                              [self.teachers_name_list[5], "GR06", "2.2B"],
                                              ["none", "none", "none"]],
                         "Mecánica de materiales":[[self.teachers_name_list[8], "GR01", "3.5C"],
                                                   [self.teachers_name_list[9], "GR02", "2.1B"],
                                                   [self.teachers_name_list[10], "GR03", "2.1C-2.4C"],
                                                   ["none", "none", "none"]],
                         "Probabilidad y estadística":[[self.teachers_name_list[11], "GR01", "2.5B"],
                                                       [self.teachers_name_list[11], "GR02", "2.5B"],
                                                       [self.teachers_name_list[12], "GR03", "2.5B"],
                                                       [self.teachers_name_list[12], "GR04", "2.5B"],
                                                       [self.teachers_name_list[11], "GR05", "2.5B"],
                                                       [self.teachers_name_list[13], "GR06", "2.5B-2.4B"],
                                                       ["none", "none", "none"]],
                         "Modelos y simulación":[[self.teachers_name_list[14], "GR01", "3.5B"],
                                                 [self.teachers_name_list[14], "GR02", "3.5B"],
                                                 [self.teachers_name_list[14], "GR03", "3.5B"],
                                                 [self.teachers_name_list[15], "GR04", "3.5B"],
                                                 [self.teachers_name_list[15], "GR05", "3.5B"],
                                                 [self.teachers_name_list[15], "GR06", "3.5B"],
                                                 [self.teachers_name_list[16], "GR07", "3.5B"],
                                                 [self.teachers_name_list[16], "GR08", "3.5B"],
                                                 [self.teachers_name_list[17], "GR09", "3.5B"],
                                                 [self.teachers_name_list[18], "GR10", "3.5B"],
                                                 ["none", "none", "none"]],
                         "Economía general":[[self.teachers_name_list[19], "GR01", "2.2C"],
                                             [self.teachers_name_list[20], "GR02", "3.5C - 2.4B"],
                                             [self.teachers_name_list[20], "GR03", "2.5C"],
                                             [self.teachers_name_list[21], "GR05", "2.6C"],
                                             ["none", "none", "none"]],
                         "Proyecto de ingeniería II":[["G", "GR01", "2.2C"],
                                                      ["none", "none", "none"]],
                         "Administración general":[["H", "GR01", ""],
                                                   ["A", "GR03", "none"],
                                                   ["B", "GR04", "none"],
                                                   ["C", "GR05", "none"],
                                                   ["D", "GR06", "none"],
                                                   ["E", "GR07", "none"],
                                                   ["F -ingles-", "GR08", "none"],
                                                   ["none", "none", "none"]]}
         '''
        self.subject_list_self = list()
        self.show_subjects_list()
        self.colors2 = {"r":[205, 175, 84, 72, 244, 235, 153, 229, 46, 175],
                        "g":[97, 122, 153, 201, 208, 152, 163, 110, 134, 96],
                        "b":[85, 197, 199, 176, 63, 78, 164, 232, 193, 26]}

        self.colors = [[169, 50, 38], [165, 105, 189], [41, 128, 185], [26, 188, 156], [130, 224, 170],
                       [244, 208, 63], [230, 126, 34], [149, 165, 166], [93, 109, 126], [155, 255, 1],
                       [88, 214, 141], [187, 143, 206], [248, 196, 113], [35, 155, 86], [202, 178, 61],
                       [169, 50, 38], [165, 105, 189], [41, 128, 185], [26, 188, 156], [130, 224, 170],#r
                       [244, 208, 63], [230, 126, 34], [149, 165, 166], [93, 109, 126], [155, 255, 1],#r
                       [88, 214, 141], [187, 143, 206], [248, 196, 113], [35, 155, 86], [202, 178, 61],#r
                       [88, 214, 141], [187, 143, 206], [248, 196, 113]]#reutilizados
        #Matrices
        #Aux variables
        self.subject = "none"
        self.week_space_selected_row = "none"
        self.week_space_selected_column = "none"
        #Path variables
        self.save_schedule_path = "horarios"
        #Filter variables
        self.filter_teachers_excluded = list()
        self.academic_days = 6
        self.maxSignatures = 9

#_________________________________________________________________________________________
#Métodos
    def load_groups_file(self):
        self.teachers = dict()
        if not os.path.exists("groups.npy"):
            np.save('groups.npy', self.teachers)#si no existe, crea algo vacio
            print("Creando nuevo archivo de Groups.npy")
        self.teachers = np.load('groups.npy', allow_pickle=True).item()
        return self.teachers

    def select_teacher(self, item):
        teacher = self.teachers_table.item(item.row(), 0).text()
        group = self.teachers_table.item(item.row(), 1).text()
        room = self.teachers_table.item(item.row(), 2).text()
        self.statusBar().showMessage("Profesor: {} // Grupo: {} // Aula {}".format(teacher, group, room))
        if self.week_space_selected_row != "none":
            if group != "none":
                self.week_table.setItem(self.week_space_selected_row, self.week_space_selected_column, QTableWidgetItem(group)) #asignar el grupo seleccionado desde la lista de profesores
                try:
                    self.week_table.item(self.week_space_selected_row, self.week_space_selected_column).setBackground(QtGui.QColor(self.colors[item.row()][0], self.colors[item.row()][1], self.colors[item.row()][2])) #pintar el cuadro
                except Exception as error:
                    print("En colores: ", error)
                horario_loaded = np.load("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject)) #cargar el horario para modificarlo
                horario_loaded[self.week_space_selected_row][self.week_space_selected_column] = int(group[-2:])
                np.save("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject), horario_loaded) #guardar el horario 0
            else:
                self.week_table.setItem(self.week_space_selected_row, self.week_space_selected_column, QTableWidgetItem(0))
                horario_loaded = np.load("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject)) #cargar el horario para modificarlo
                horario_loaded[self.week_space_selected_row][self.week_space_selected_column] = 0
                np.save("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject), horario_loaded) #guardar el horario 0

    def edit_data_table(self, item):
        #revisar si hay clases
        if self.teachers.get(self.subject):
            self.week_space_selected_row = item.row()
            self.week_space_selected_column = item.column()
        else:
            self.week_space_selected_row = "none"
            self.week_space_selected_column = "none"
        data = ""
        try:
            data = self.week_table.item(item.row(), item.column()).text() #warning
            #print(type(data), "*", data, "*")
        except AttributeError:
            pass
        #print("item clicked: ", self.week_space_selected_row, self.week_space_selected_column)
        if self.subject != "none" and data != "":
            try:
                for clase in self.teachers.get(self.subject):
                    if data in clase:
                        teacher = clase[0]
                        group = clase[1]
                        room = clase[2]
                        self.statusBar().showMessage("Profesor: {} // Grupo: {} // Aula {}".format(teacher, group, room))
            except TypeError:
                self.statusBar().showMessage("No hay profesores para {}". format(self.subject))
        if data == "":
            self.statusBar().showMessage("Profesor: {} // Grupo: {} // Aula {}".format("none", "none", "none"))

    def save_data_table(self):
        #print("funciona, cambiar elementos a: ", self.subject, item.row())
        if self.subject != "none":
            horario_loaded = np.load("horarios/{}.npy".format(self.subject)) #cargar el horario
            print(horario_loaded)
        print(self.subject, "no hay elementos para guardar")
        '''
        if item.text() != horario_loaded[item.row()][item.column()]:
            horario_loaded[item.row()][item.column()] = item.text()[-2:] #escribe el cambio
            #print(item.text()[-2:])
            np.save("horarios/{}".format(self.subject), horario_loaded)
            try:
                self.week_table.item(item.row, item.column).setBackground(QtGui.QColor(self.teachers_colors.get("r")[int(item.text)], self.teachers_colors.get("g")[int(item.text())], self.teachers_colors.get("b")[int(item.text())]))
            except:
                pass
        '''

    def add_subject_to_list(self):
        item, ok = QInputDialog.getItem(self, "Añadir una asignatura", "Semestre...", list(map(str, list(self.list_of_all_subjects.keys()))), 0, False)
        if ok:
            subjects = self.list_of_all_subjects.get(int(item))
            msg = Qt.QMessageBox()
            msg.setText("Asignatura...")
            msg.setWindowTitle("Añadir una asignatura")
            #lista de asignaturas
            listview = Qt.QListView() #crear listview
            listview.setFixedSize(300, 200) #set size
            listview.setEditTriggers(QAbstractItemView.NoEditTriggers) #no se puede editar la lista
            self.model = Qt.QStandardItemModel()
            for element in subjects:
                item = Qt.QStandardItem(element)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                item.setCheckable(True)
                if element in self.subject_list_self:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                self.model.appendRow(item)
            listview.setModel(self.model)
            self.model.itemChanged.connect(self.add_subject_to_list_complement) #al marcar o desmarcar la casilla
            #aditional_buttons
            #select_all = QPushButton()
            #select_all.setText("Seleccionar todo")
            #select_all.clicked.connect(self.select_all_list_signatures)
            #layout
            l = msg.layout() #crear un layout
            l.addWidget(listview, 3, 1, 1, 3)
            #l.addWidget(select_all, 4, 1, 1, 3)
            #botones
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            aux_subject_list_self = self.subject_list_self.copy()
            retval = msg.exec_()
            if retval == QMessageBox.Cancel:
                self.subject_list_self = aux_subject_list_self
                self.show_subjects_list()
                del aux_subject_list_self

    def add_subject_to_list_complement(self, item):
        if item.checkState() == 2:
            self.subject_list_self.append(item.text()) #añadir asignatura seleccionada a la lista
            self.show_subjects_list() #mostrar la lista de asignaturas añadidas
        else:
            if item.text() in self.subject_list_self: #si ya esta marcada
                self.subject_list_self.remove(item.text()) #remover asignatura de la lista
                self.show_subjects_list() #mostrar la lista de asignaturas añadidas

#    def select_all_list_signatures(self):
#        print("seleccionar todo")
#        #item.setCheckState(QtCore.Qt.Checked)
#        print(self.model.selectedIndexes())

    def delete_subject_to_list(self):
        try:
            self.actionA_adir_grupo_a_asignatura.setEnabled(False)
            self.actionEliminar_grupo.setEnabled(False)
            item = self.subject_list.takeItem(self.subject_list.currentRow())
            self.subject_list_self.remove(item.text())
            self.week_table.clear() #limpiar tabla
            self.teachers_table.clear() #limpiar tabla
            self.week_table.setHorizontalHeaderLabels(("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
            self.week_table.setVerticalHeaderLabels(("6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
            self.teachers_table.setColumnCount(0)# Establecer el número de columnas
            self.teachers_table.setRowCount(0)# Establecer el número de columnas
            #print(self.subject_list_self)
            self.week_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Deshabilitar edición
            self.subject_name.setText("None")
            self.period_name.setText("None")
        except AttributeError:
            self.statusBar().showMessage("No hay elementos para eliminar.")

    def show_subjects_list(self):
        self.subject_list.clear()
        for element in self.subject_list_self:
            item = Qt.QListWidgetItem(element)
            self.subject_list.addItem(item)

    def item_click(self, item):
        self.load_groups_file()
        self.actionEliminar_grupo.setEnabled(True)
        self.actionA_adir_grupo_a_asignatura.setEnabled(True)
        #self.week_table.setEditTriggers(QAbstractItemView.AllEditTriggers) # Habilitar edición
        self.subject = item.text() #item seleccionado
        self.period_selected = self.search_period(self.subject) #obtener el semestre
        self.statusBar().showMessage("Horario en: {}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject))
        if not os.path.exists("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject)): #si no existe el archivo horario de la asignatura
            default = np.zeros((15, 6), dtype=np.int) #crear un array
            #Crear carpeta
            if not os.path.exists("{}/{}".format(self.save_schedule_path, self.subject)):
                os.mkdir("{}/{}".format(self.save_schedule_path, self.subject))
            np.save("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject), default) #guardar el horario 0
        horario_loaded = np.load("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject)) #abrir el horario
        #poner datos en la tabla
        list_of_groups = list()
        if self.teachers.get(self.subject): #si la lista de clases NO está vacia
            for clase in self.teachers.get(self.subject):
                list_of_groups.append(clase[1])
            for row in range(0, self.week_table.rowCount()):
                for column in range(0, self.week_table.columnCount()):
                    data = horario_loaded[row][column]
                    #modificar el dato
                    if data == int(0):
                        self.week_table.setItem(row, column, QTableWidgetItem(0)) #mostrar en la tabla lo que tiene el array
                    else:
                        if len(str(data)) == 1:
                            data = "0"+str(data)
                        self.week_table.setItem(row, column, QTableWidgetItem("GR"+str(data))) #mostrar en la tabla lo que tiene el array
                        index = list_of_groups.index("GR"+str(data)) ##Error al haber un grupo en la tabla que no esta en la de profesores
                        try:
                            self.week_table.item(row, column).setBackground(QtGui.QColor(self.colors[index][0], self.colors[index][1], self.colors[index][2])) #pintar el cuadro
                        except Exception as error:
                            print("En color background tabla_week: ", error)
                        try:
                            for clase in self.teachers.get(self.subject):
                                if data in clase:
                                    #print(data)
                                    #teacher = clase[0]
                                    group = clase[1]
                                    print(group)
                                    #room = clase[2]
                        except TypeError:
                            self.statusBar().showMessage("No hay profesores para {}".format(self.subject))
        else:
            self.statusBar().showMessage("No hay clases para {}".format(self.subject))
            self.week_table.clear() #limpiar tabla
            self.teachers_table.clear() #limpiar tabla
            self.week_table.setHorizontalHeaderLabels(("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
            self.week_table.setVerticalHeaderLabels(("6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"))# Establecer las etiquetas de encabezado horizontal usando etiquetas

        self.subject_name.setText(self.subject) #mostrar el nombre
        self.period_name.setText(str(self.period_selected)) #mostrar el semestre
        try:
            number_of_teachers = len(self.teachers.get(self.subject))
            self.teachers_table.setColumnCount(3)
            self.teachers_table.setRowCount(number_of_teachers)# Establecer el número de filas
            #llenar la tabla
            for row in range(len(self.teachers.get(self.subject))): #por cada profesor de la asignatura seleccionada
                for column in range(len(self.teachers.get(self.subject)[row])):
                    self.teachers_table.setItem(row, column, QTableWidgetItem(self.teachers.get(self.subject)[row][column]))
                    teacher = self.teachers_table.item(row, 0).text()
                    if teacher != "none":
                        self.teachers_table.item(row, column).setBackground(QtGui.QColor(self.colors[row][0], self.colors[row][1], self.colors[row][2]))
        except TypeError:
            self.teachers_table.setColumnCount(3)
            self.teachers_table.setRowCount(1)
            self.teachers_table.setItem(0, 0, QTableWidgetItem("None"))
            self.teachers_table.setItem(0, 1, QTableWidgetItem("None"))
            self.teachers_table.setItem(0, 2, QTableWidgetItem("None"))
#_________________________________________________________________________________________
#Parte 2 - crear opciones

    def make_options(self):
        #crear diccionario con todos los grupos de cada asignatura
        all_data = {}
        buttonReply = QMessageBox.question(self, 'Atención', "Desea continuar??", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            if len(self.subject_list_self) > 1:
                #cargar todas las asignaturas
                for subject in self.subject_list_self:
                    subject_schedule_loaded = np.load("{}/{}/{}.npy".format(self.save_schedule_path, subject, subject)) #cargar el horario para modificarlo
                    groups = self.get_groups(subject_schedule_loaded)
                    #buscar semestre y ubicacion en lista
                    for periodo in self.list_of_all_subjects:
                        for asignatura in self.list_of_all_subjects[periodo]:
                            if asignatura == subject:
                                position = self.list_of_all_subjects[periodo].index(subject)
                                semestre = periodo
                                #print(subject, semestre, position)
                    for cont in range(len(groups)):
                        group = groups[cont]
                        #guardar cada grupo en la misma carpeta de la asignatura
                        np.save("{}/{}/{}.npy".format(self.save_schedule_path, subject, "horario"+str(np.max(group))), group) #guardar el horario 0
                        #Asignar al grupo un codigo unico para identificar, guardado en all_data
                        number_group = np.max(group)
                        group = group//np.max(group)
                        group = group * int(str(number_group)+str(semestre)+str(position))
                        groups[cont] = group
                    all_data[subject] = groups
                #print(all_data)
                #crear las combinaciones
                #print(self.subject_list_self)
                schedules = list()
                check_column = 0
                ###___
                self.combinate_schedules(all_data)
            else:
                self.statusBar().showMessage("No hay suficientes elementos para combinar.")
        else:
            pass
            #print('No clicked.')

    def get_groups(self, array): #recibe la asignatura
        groups = list()
        for cont in range(1, np.max(array)+1):
            array_copy = array.copy() #forzar la copia
            array_copy[array_copy != cont] = 0
            if np.any(array_copy):
                groups.append(array_copy)
        return groups

    def compatible(self, array1, array2):
        new_array = array1*array2
        response = not np.any(new_array)
        return response

    def combinate_schedules(self, all_data):
        schedules = list()
        check_column = 0
        while check_column+1 < len(self.subject_list_self):
            #print(check_column)
            #print(self.subject_list_self[check_column])
            for group in all_data.get(self.subject_list_self[check_column]):
                for group2 in all_data.get(self.subject_list_self[check_column+1]):
                    if self.compatible(group, group2): #si se pueden combinar
                        schedules.append(group+group2)
            #print(schedules)
            all_data[self.subject_list_self[check_column+1]] = schedules
            schedules = list()
            check_column += 1
        final_schedules = all_data.get(self.subject_list_self[-1:][0])
        self.save_schedules(final_schedules)

    def save_schedules(self, schedules_list):
        if os.path.exists("{}/opciones".format(self.save_schedule_path)):
            shutil.rmtree("{}/opciones".format(self.save_schedule_path), ignore_errors=True)
            os.mkdir("{}/opciones".format(self.save_schedule_path))
        else:
            os.mkdir("{}/opciones".format(self.save_schedule_path))
        QMessageBox.information(self, "Informacion", "Se crearon {} horarios.".format(len(schedules_list)))
        for cont in range(len(schedules_list)):
            np.save("{}/opciones/{}.npy".format(self.save_schedule_path, "opcion"+str(cont)), schedules_list[cont]) #guardar el horario 0

    def schedule_to_tableview(self):
        self.files = list() #una lista path de los horarios seleccionados
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        self.files, _ = QFileDialog.getOpenFileNames(self, "Abrir horarios", "{}/opciones".format(self.save_schedule_path), "Python Files (*.npy)", options=options)
        files_passed = list()
        if self.files:
            #verificar cada horario para ver si se puede pasar a visualizacion
            for cont in range(len(self.files)): #por cada horario seleccionado
                default_loaded = np.load(self.files[cont])
                number_rows, number_columns = default_loaded.shape
                present_teachers = list()
                academic_days = self.get_info_from_schedule(default_loaded)
                for row in range(number_rows):
                    for column in range(number_columns):
                        code = str(default_loaded[row, column])
                        if len(code) >= 3: #interpretacion del codigo con grupo, semestre, posicion
                            propiedades = self.get_info_from_code(code)
                            #print(propiedades)
                            if not propiedades[3] in present_teachers:
                                present_teachers.append(propiedades[3])
                schedule_check = True
                if academic_days <= self.academic_days: #si está entre los días escogidos
                    schedule_check = schedule_check * True
                    for teacher in self.filter_teachers_excluded:
                    #print(teacher)
                        if teacher in present_teachers:
                            #print("Este horario no pasa")
                            schedule_check = schedule_check * False
                            break
                        else:
                            #print("Este horario si pasa")
                            schedule_check * True
                            #if not self.files[cont] in files_passed:
                             #   files_passed.append(self.files[cont])
                else:
                    schedule_check = schedule_check * False
                if schedule_check:
                    #print("Horario pasó")
                    if not self.files[cont] in files_passed:
                        files_passed.append(self.files[cont])
            self.files = files_passed
            self.week_table.clear() #limpiar tabla
            self.week_table.setHorizontalHeaderLabels(("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
            self.week_table.setVerticalHeaderLabels(("6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
            if len(self.files) == 0:
                #self.statusBar().showMessage("No hay horarios para mostrar debido a los filtros.")
                QMessageBox.warning(self, "Advertencia", "No hay horarios disponibles debido a los filtros.")
            else:
                self.view_schedule()

    def get_info_from_schedule(self, schedule):
        #Obtener los dias ocupados de la semana
        suma_y = schedule.sum(axis = 0)
        academicDays = 6-np.count_nonzero(suma_y == 0)
        return academicDays

    def get_info_from_code(self, code):
        position = int(code[-1])
        if int(code[-2]) == 0:
            semestre = int(code[-3:-1])
            grupo = int(code[:-3])
        else:
            grupo = int(code[:-2])
            semestre = int(code[-2])
        asignatura = self.list_of_all_subjects[semestre][position]
        clases = self.teachers[asignatura]
        profesor = "none"
        #tomar el profesor de la asignatura
        for clase in clases:
            if not clase[1] == "none":
                if int(clase[1][-2:]) == grupo:
                    profesor = clase[0]
        return [grupo, semestre, asignatura, profesor]

    def view_schedule(self):
        self.schedule_view_select.setEnabled(True) #habilitar el combobox
        self.week_table.clear() #limpiar tabla
        self.week_table.setHorizontalHeaderLabels(("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.week_table.setVerticalHeaderLabels(("6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"))# Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.schedule_view_select.setRange(1, len(self.files))
        schedule_number = self.schedule_view_select.value()-1
        self.statusBar().showMessage("Horario seleccionado #{} de {} horarios cargados. File: {}".format(schedule_number+1, len(self.files), self.files[schedule_number].split("/")[-1]))
        #cargar un horario
        default_loaded = np.load(self.files[schedule_number]) #cargar el horario numero (eleccion de usuario)
        #mostrar en la tabla de semana
        number_rows, number_columns = default_loaded.shape
        for row in range(number_rows):
            for column in range(number_columns):
                code = str(default_loaded[row, column])
                if len(code) >= 3: #interpretacion del codigo con grupo, semestre, posicion
                    propiedades = self.get_info_from_code(code)
                    grupo, asignatura, profesor = propiedades[0], propiedades[2], propiedades[3]
                    self.week_table.setItem(row, column, QTableWidgetItem("GR0{} // {} // {}".format(grupo, asignatura, profesor))) #mostrar en la tabla lo que tiene el array
                    self.week_table.item(row, column).setToolTip("GR0{} // {} // {}".format(grupo, asignatura, profesor))
                    try:
                        self.week_table.item(row, column).setBackground(QtGui.QColor(self.colors[self.teachers_name_list.index(profesor)][0], self.colors[self.teachers_name_list.index(profesor)][1], self.colors[self.teachers_name_list.index(profesor)][2])) #pintar el cuadro#self.teachers_name_list
                    except Exception as error:
                        pass
                        #print("Profesor {} no registrado // ".format(profesor), error)

    def teacher_filter(self):
        msg = Qt.QMessageBox()
        msg.setText("Excluir un profesor")
        msg.setWindowTitle("Filtro de profesores")
        listview = Qt.QListView() #crear listview
        listview.setFixedSize(300, 200) #set size
        listview.setEditTriggers(QAbstractItemView.NoEditTriggers) #no se puede editar la lista
        self.model2 = Qt.QStandardItemModel()
        #self.teachers_name_list.sort() #ordenar la lista ##no habilitar se voltea todo :|
        for element in self.teachers_name_list:
            item = Qt.QStandardItem(element)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setCheckable(True)
            if element in self.filter_teachers_excluded:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            #item.setCheckState(QtCore.Qt.Checked)
            self.model2.appendRow(item)
        listview.setModel(self.model2)
        self.model2.itemChanged.connect(self.teacher_filter_complement) #al marcar o desmarcar casilla
        l = msg.layout() #crear un layout
        l.addWidget(listview, 3, 1, 1, 3)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        aux_filter_teachers_excluded = self.filter_teachers_excluded.copy() ##CURIOSAMENTE se estaban editando las 2 a la vez
        retval = msg.exec_()
        if retval == QMessageBox.Cancel: #si presiona el boton de cancelar
            self.filter_teachers_excluded = aux_filter_teachers_excluded

    def teacher_filter_complement(self, item):
        if item.checkState() == 2:
            #print("esta en 2")
            self.filter_teachers_excluded.append(item.text())
            #print(len(self.teachers_name_list), len(self.filter_teachers_excluded))
        else:
            #print("esta en 1")
            self.filter_teachers_excluded.remove(item.text())
            #print(len(self.teachers_name_list), len(self.filter_teachers_excluded))

    def day_filter(self):
        item, ok = QInputDialog.getInt(self, "Selección", "<b>Actual:</b> {}<br><br>Seleccione el número de días académicos:".format(self.academic_days), self.academic_days, 1, 6, 1)
        if ok:
            self.academic_days = item
            #print(self.academic_days)

    def add_teacher(self):
        text, okPressed = QInputDialog.getText(self, "Añadir profesor", "Nombre del profesor:")
        text_copy = self.text_modify(text)
        check = True
        if okPressed and text != '':
            buttonReply = QMessageBox.question(self, 'Atención', "Desea continuar??<br><br>Nombre ingresado: <b>{}</b>".format(text), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                for teacher in self.teachers_name_list:
                    teacher_copy = self.text_modify(teacher)
                    if text_copy == teacher_copy:
                        check = check * False
                    else:
                        check = check * True
                if check:
                    #añadir profesor al archivo
                    self.teachers_name_list.append(text.lower().title())
                    self.statusBar().showMessage("{} añadido con éxito.".format(text.lower().title()))
                    np.save('teacher_list.npy', self.teachers_name_list)
                else:
                    self.statusBar().showMessage("{} ya se encuentra listado.".format(text))

    def del_teacher(self):
        items = self.teachers_name_list
        items.sort()
        item, ok = QInputDialog.getItem(self, "Eliminar profesor", "Seleccione un profesor:", items, 0, False)
        if ok and item:
            #eliminar el profesor
            self.teachers_name_list.remove(item)
            np.save('teacher_list.npy', self.teachers_name_list)
            self.statusBar().showMessage("{} se ha removido del listado.".format(item))

    def text_modify(self, text):
        if type(text) == str:
            text = text.lower().strip()
            a, b = 'áéíóúü', 'aeiouu'
            trans = str.maketrans(a, b)
            response = text.translate(trans)
        else:
            response = "nan"
        return response

    def add_asignatura_window(self):
        msg = Qt.QMessageBox()
        msg.setWindowTitle("Nombre de la asignatura")
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        #Labels
        label_semestre = Qt.QLabel()
        label_name = Qt.QLabel()
        label_semestre.setText("Semestre:")
        label_name.setText("Nombre:")
        #Widgets
        select_time = Qt.QComboBox() #crear combobox
        select_time.addItems(list(map(str, list(self.list_of_all_subjects.keys()))))
        select_time.setFixedSize(40, 20)
        input_subject = Qt.QLineEdit() #crear campo de entrada de texto
        input_subject.setFixedSize(150, 20)
        #Layout
        l = msg.layout() #crear un layout
        l.addWidget(label_semestre, 0, 0, 1, 1)         #añadir widgets al layout
        l.addWidget(label_name, 1, 0, 1, 1)
        l.addWidget(select_time, 0, 1, 1, 1) ##row, column, size_row, size_column
        l.addWidget(input_subject, 1, 1, 1, 1)
        retval = msg.exec_()
        if QMessageBox.Ok and input_subject.text() != '':
            buttonReply = QMessageBox.question(self, 'Atención', "Desea continuar??<br><br>Semeste ingresado: <b>{}</b><br>Nombre ingresado: <b>{}</b>".format(select_time.currentText(), input_subject.text()), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                ##anade la asignatura
                try:
                    self.add_asignatura(int(select_time.currentText()), self.text_modify(input_subject.text()))
                except Exception as error:
                    QMessageBox.warning(self, "Advertencia", "{}".format(str(error)))
            else:
                self.statusBar().showMessage("{} no ha sido agregado.".format(input_subject.text().lower().capitalize()))

    def add_asignatura(self, semestre, nombre):
        print("*** Add asignatura ***")
        present_subjects = self.list_of_all_subjects[semestre]
        check = True
        for subject in present_subjects:
            if self.text_modify(nombre) in self.text_modify(subject):
                check = check * False
            else:
                check = check * True
        if check:
            if len(self.list_of_all_subjects[semestre]) < self.maxSignatures:#si hay <10 asignaturas
                present_subjects.append(nombre.lower().capitalize())#añadir asignatura
                self.list_of_all_subjects[semestre] = present_subjects
                np.save('subjects_list.npy', self.list_of_all_subjects)
            else:
                ##Error de maximas asignaturas
                raise Exception("Ha llegado al máximo de asignaturas por semestre ({})".format(self.maxSignatures))
        else:
            raise Exception("{} ya esta presente en la lista.".format(nombre.lower().capitalize()))

    def del_asignatura(self):
        number, ok = QInputDialog.getItem(self, "Eliminar asignatura", "Semestre", list(map(str, list(self.list_of_all_subjects.keys()))), 0, False)
        if ok and len(self.list_of_all_subjects[int(number)]) > 0:
            present_subjects = self.list_of_all_subjects[int(number)]
            item, ok = QInputDialog.getItem(self, "Eliminar asignatura", "Asignatura", present_subjects, 0, False)
            if ok:
                present_subjects.remove(item)
                self.list_of_all_subjects[int(number)] = present_subjects
                np.save('subjects_list.npy', self.list_of_all_subjects)
        else:
            if len(self.list_of_all_subjects[int(number)]) == 0:
                self.statusBar().showMessage("No hay asignaturas registradas en el semestre {}.".format(number))
            if not ok:
                self.statusBar().showMessage("Eliminar asignatura cancelado.")

    def add_group_window(self):
        msg = Qt.QMessageBox()
        msg.setWindowTitle("Agregar grupo")
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        #Labels
        label_profesor = Qt.QLabel()
        label_grupo = Qt.QLabel()
        label_aula = Qt.QLabel()
        label_profesor.setText("Profesor:")
        label_grupo.setText("Grupo:")
        label_aula.setText("Aula:")
        #widgets
        select_teacher = Qt.QComboBox() #crear combobox
        select_teacher.addItems(self.teachers_name_list)
        select_teacher.setFixedSize(200, 20)
        select_group = Qt.QSpinBox()
        select_group.setFixedSize(40, 20)
        select_group.setMinimum(1)
        input_room = Qt.QLineEdit() #crear campo de entrada de texto
        input_room.setFixedSize(50, 20)
        #Layout
        l = msg.layout()
        l.addWidget(label_profesor, 0, 0)
        l.addWidget(label_grupo, 0, 1)
        l.addWidget(label_aula, 0, 2)
        l.addWidget(select_teacher, 1, 0) ##row, column, rowspan, columnspan
        l.addWidget(select_group, 1, 1)
        l.addWidget(input_room, 1, 2)
        retval = msg.exec_()

        if retval == QMessageBox.Ok:
            buttonReply = QMessageBox.question(self, 'Atención',
                                               "Desea continuar??<br><br>Profesor: <b>{}</b><br>Grupo: <b>{}</b><br>Aula: <b>{}</b>".format(select_teacher.currentText(),
                                                                                      select_group.value(), input_room.text()))
            if buttonReply == QMessageBox.Yes:
                try:
                    self.add_group(self.subject, select_teacher.currentText(), select_group.value(), input_room.text())
                    self.teachers = np.load('groups.npy').item()
                except Exception as error:
                    QMessageBox.warning(self, "Advertencia", str(error))

    #            print("Semestre {} // Asignatura {}".format(self.period_selected, self.subject))
#                if self.subject in self.teachers.keys():#si la asignatura existe
#                    print("La asignatura ya está agregada")
#                else:
#                    print("Agregar asignatura")
#                    self.teachers[self.subject] = [["none", "none", "none"]]
#                #añadir el grupo a la asignatura
#                grupos = self.teachers[self.subject]
#                #print(grupos)
#                if len(str(select_group.value())) > 1:
#                    group = "GR" + str(select_group.value())
#                else:
#                    group = "GR0" + str(select_group.value())
#                #actualizar tabla lista
#                grupos.insert(-1, [select_teacher.currentText(), group, input_room.text()])
#                self.teachers[self.subject] = grupos
#                np.save('groups.npy', self.teachers)#si no existe, crea algo vacio

    def add_group(self, materia, teacher, group, place):
        print("*** add_group ***")
        teachers = self.load_groups_file()
        self.load_groups_file()
        if materia in teachers.keys():#si la asignatura existe
                print("La asignatura ya está agregada")
        else:
            teachers[materia] = [["none", "none", "none"]]
        #añadir el grupo a la asignatura
        grupos = teachers[materia]
        if len(str(group)) > 1:
            group = "GR" + str(group)
        else:
            group = "GR0" + str(group)
        #Verificar si el grupo ya existe
        for grupo in grupos:
            if not group in grupo:
                grupos.insert(-1, [teacher, group, place])
                teachers[materia.capitalize()] = grupos
                np.save('groups.npy', teachers)#si no existe, crea algo vacio
                break
            else:
                raise Exception("El grupo ya existe.")
                break

    def del_group(self):
        present_groups = list()
        grupos = list(self.teachers[self.subject])
        for grupo in grupos:
            if grupo[1].lower() != "none":
                present_groups.append(grupo[1])
        item, ok = QInputDialog.getItem(self, "Eliminar grupo", "Cual grupo desea eliminar:", present_groups, 0, False)
        if ok:
            #esta seguro?
            for grupo in grupos:
                if grupo[1] == item:
                    grupos.remove(grupo)
                    ##toca eliminar el grupo de los horarios
                    horario = np.load("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject)) #abrir el horario
                    positions_to_reset = np.argwhere(horario == int(grupo[1][-2:]))
                    for position_del in positions_to_reset:
                        horario[position_del[0], position_del[1]] = 0
                    np.save("{}/{}/{}.npy".format(self.save_schedule_path, self.subject, self.subject), horario)#si no existe, crea algo vacio
                    #actualizar las 2 tablas
                    send_item = Qt.QListWidgetItem(self.subject)
                    self.item_click(send_item)
            self.teachers[self.subject] = grupos
            np.save('groups.npy', self.teachers)

    def search_period(self, find):
        response = "None"
        values = list(self.list_of_all_subjects.values())
        for semestre in values:
            for subject in semestre:
                if subject == find:
                    response = values.index(semestre)+1
                    break
        return response

    def automaticLoad(self):
        self.SW = DisplayWindow()
        self.SW.show()

#        import pandas as pd
#        options = QFileDialog.Options()
#        options |= QFileDialog.DontUseNativeDialog
#        excelFile_patch, _ = QFileDialog.getOpenFileName(self, "Abrir horarios", "", "Excel Files (*.xlsx)", options=options)
#        print(excelFile_patch)
#        QMessageBox.information(self, "Informacion", "Procesando archivo")
#        for semestre in range(3, 11):
#            try:
#                dataFrame = pd.read_excel(excelFile_patch, sheet_name = str(semestre))
#                semana = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
#                row = 0
#                signatures = list()
#                horarios = list()
#                for row in range(dataFrame.shape[0]):
#                    data = list()
#                    counter_row = 0
#                    counter_column = 0
#                    for column in dataFrame.iloc[row]:
#                        if self.text_modify(column) == self.text_modify(semana[counter_row]):
#                            data.append(self.text_modify(column))
#                            counter_row += 1
#                        if self.text_modify(column) == self.text_modify(semana[-1]):
#                            break
#                        counter_column += 1
#                
#                    if data == semana:
##                        print("Se detecta una isla", row, counter_column)
#                        signatures.append(self.getSignature(dataFrame.iloc[row-1][0]))
#                #        print("Materia estimanada:", dataframe.iloc[row-1][0])
#                        horarios.append(dataFrame.iloc[row:row+17, 1:counter_column+1])
#                #        print(dataframe.iloc[row:row+17, 0:counter_column+1])
#                print("AutomaticLoad > ", "Semestre:", semestre, " > ", signatures)
#            except Exception as error:
#                print("AutomaticLoad - Error > ", error)
    
    def getSignature(self, text):
        response = text
        try:
            response = text.split("-", 1)[0]
        except Exception as error:
            print(error)
        try:
            response = response.split("(")[0]
        except Exception as error:
            print(error)
        return self.text_modify(response.strip())

class DisplayWindow(QtWidgets.QMainWindow, Read_Excel_Window):
    def __init__(self):
        super(DisplayWindow, self).__init__()
        QtWidgets.QMainWindow.__init__(self)
        Read_Excel_Window.__init__(self)
        self.setupUi(self)

        self.setWindowTitle("Cargar archivo")

        self.excelFile_patch = ""
        self.loadBtn.clicked.connect(self.loadFile)
        self.processBtn.clicked.connect(self.processFile)
        self.filePatchEdit.setEnabled(False)
        self.fileRead = False


    def loadFile(self):
        self.fileRead = False
        self.loadBtn.setEnabled(False)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.excelFile_patch, _ = QFileDialog.getOpenFileName(self, "Abrir archivo Excel", "", "Excel Files (*.xlsx)", options=options)
        self.filePatchEdit.setText(self.excelFile_patch)
        self.loadBtn.setEnabled(True)
        if self.excelFile_patch:
            self.processBtn.setEnabled(True)
        else:
            self.processBtn.setEnabled(False)

    def processFile(self):
        global window
        semestres_list = list()
        self.code = "none"
        self.semestre = 1
        self.semestres = list()
        self.processBtn.setEnabled(False)
        self.loadBtn.setEnabled(False)
        self.excelFile_patch = self.filePatchEdit.displayText()
        self.logView.appendPlainText("- Abriendo archivo: {}".format(self.excelFile_patch))
        QApplication.processEvents()
        exit_reason = 0
        for semestre in range(1, 11):
            try:
                self.dataFrame = pd.read_excel(self.excelFile_patch, sheet_name = str(semestre)) #leer un semestre
                self.semestres.append(semestre)
                semestres_list.append(self.dataFrame)
                
                semana = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
                row = 0
                signatures = list()
                horarios = list()
                for row in range(self.dataFrame.shape[0]):
                    self.progressBar_2.setMaximum(self.dataFrame.shape[0])
                    self.progressBar_2.setValue(row)
                    data = list()
                    counter_row = 0
                    counter_column = 0
                    for column in self.dataFrame.iloc[row]:
                        if window.text_modify(column) == window.text_modify(semana[counter_row]):
                            data.append(window.text_modify(column))
                            counter_row += 1
                        if window.text_modify(column) == window.text_modify(semana[-1]): #si llega al sábado ROMPE
                            break
                        counter_column += 1
                    if data == semana: # si detecta un horario
                        asignatura = window.getSignature(self.dataFrame.iloc[row-1][0])
                        signatures.append(asignatura) # lista de asignaturas
                        horario = self.dataFrame.iloc[row:row+16, 1:counter_column+1]
                        horarios.append(horario)
                        try:
                            ##Intentar añadir esa asignatura
                            window.add_asignatura(semestre, signatures[-1])
                            self.logView.appendPlainText("- {} ha sido añadido a la lista | Semestre: {}".format(signatures[-1], semestre))
                        except Exception as error:
                            self.logView.appendPlainText("- {}".format(error))
                            QApplication.processEvents()

                        ##Añadir el horario de esa asignatura
                        horario, grupos = self.informacionHorario(horario)
                        ##Añadir los grupos
                        for grupo in grupos:
                            window.add_group(signatures[-1].capitalize(), "no disponible", grupo, "")
                            self.logView.appendPlainText("-- Grupo {} añadido.".format(grupo))
                        #Añadir los horarios
                        if not os.path.exists("horarios/{}".format(asignatura.capitalize())):
                            self.logView.appendPlainText("- Creado: horarios/{}".format(asignatura.capitalize()))
                            os.mkdir("horarios/{}".format(asignatura.capitalize()))
                        np.save("horarios/{}/{}.npy".format(asignatura.capitalize(), asignatura.capitalize()), horario)

                    self.progressBar_2.setValue(row)
                print("AutomaticLoad > ", "Semestre:", semestre, " > ", signatures)

            except Exception as error:
                if "[Errno 13] Permission denied:" in str(error):
                    self.logView.appendPlainText("- {} | Es posible que otro programa esté usando el archivo.".format(error))
                    QApplication.processEvents()
                    exit_reason = 1
                    break
                else:
                    print(error)

            self.progressBar.setValue(semestre)
            QApplication.processEvents()
        if self.semestres:
            self.logView.appendPlainText("- Semestres cargados: {}".format(self.semestres))
            QApplication.processEvents()
        else:
            if exit_reason == 0:
                self.logView.appendPlainText("- Archivo inválido")
                self.loadBtn.setEnabled(True)
                QApplication.processEvents()
        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)
        self.logView.appendPlainText("- Terminado.")
        self.loadBtn.setEnabled(True)

    def informacionHorario(self, horario):
        print("*** AddHorario ***")
        ##Obtener el array
        horatio = list()
        save = False
        neededGroups = list()
        for row in range(1, horario.shape[0]):
            horatio.append(list(horario.iloc[row]))
            newRowList = list() #lista nueva para guardar los grupos
            for group in list(horario.iloc[row]):
                if type(group) == str:
                    number = re.findall(r'\d\d', group)
                    if number:
                        number = int(number[0])
                        save = True
                    else:
                        number = re.findall(r'\d', group)
                        if number:
                            number = int(number[0])
                            save = True
                        else:
                            #Espacio en blanco o grupo sin número
                            if group.strip():
                                number = 1
                                save = True
                            else: #si es espacio en blanco
                                newRowList.append(0)
                                save = False
    #                        self.logView.appendPlainText("!!! Hay errores con el formato del archivo, por favor, revíselo. ({}) Debería de tener un número identificable.".format(group))
                    if save:
                        newRowList.append(number)
                        neededGroups.append(number)
                else:
                    newRowList.append(0)
            horatio[row-1] = newRowList
        horatio = np.array(horatio)
        neededGroups = list(set(neededGroups))
        return horatio, neededGroups

if __name__ == "__main__":
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
