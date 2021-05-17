# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 18:52:01 2020

@author: Steven
"""

import numpy as np
from PyQt5 import uic, QtWidgets, QtCore, Qt, QtGui
from PyQt5.QtWidgets import (QApplication, QDialog, QPushButton, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QHeaderView, QMenu,
                             QActionGroup, QAction, QMessageBox, QInputDialog, QWidget,
                             QFileDialog)

from PyQt5.QtGui import QPainter, QColor, QFont
import sys
import random
from tempfile import TemporaryFile
import os
import shutil
import cv2
import numpy as np

import pandas as pd
try:
    dataframe = pd.read_excel("Excel2.xlsx", sheet_name = "6")
except Exception as error:
    print("Error", error)

#print(dataframe)
print(dataframe.columns[0])

#la idea es capturar islas

def readable(text):
    if type(text) == str:
        text = text.lower().strip()
        a, b = 'áéíóúü', 'aeiouu'
        trans = str.maketrans(a, b)
        response = text.translate(trans)
    else:
        response = "NaN"
    return response

def getSignature(text):
    response = text
    try:
        response = text.split("-", 1)[0]
    except Exception as error:
        print(error)
#    print(response)
    try:
        response = response.split("(")[0]
    except Exception as error:
        print(error)
    return readable(response)

semana = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
row = 0
signatures = list()
horarios = list()
for row in range(dataframe.shape[0]):
    data = list()
    counter_row = 0
    counter_column = 0
    for column in dataframe.iloc[row]:
        if readable(column) == readable(semana[counter_row]):
            data.append(readable(column))
            counter_row += 1
        if readable(column) == readable(semana[-1]):
            break
        counter_column += 1
    if data == semana:
        print(counter_row, counter_column)
        print("Se detecta una isla", row, counter_column)
        signatures.append(getSignature(dataframe.iloc[row-1][0]))
#        print("Materia estimanada:", dataframe.iloc[row-1][0])
        horarios.append(dataframe.iloc[row:row+16, 1:counter_column+1])
#        print(dataframe.iloc[row:row+17, 0:counter_column+1])

print(signatures)
print(horarios)


#subjects_list: LISTA DE TODAS LAS MATERIAS
horario = np.load("horarios/Iot/Iot.npy")
#horario = np.load("groups.npy")
print(horario.shape)

import re
horatio = list()
neededGroups = list()
for horario in horarios:
    horario = horarios[-1]
    print(horario.shape[0])
    for row in range(1, horario.shape[0]):
        horatio.append(list(horario.iloc[row]))
        newRowList = list() #lista nueva para guardar los grupos
        for group in list(horario.iloc[row]):
            if type(group) == str:
                if group.strip():
                    try:
                        number = re.findall(r'\d\d', group)[0]
                    except Exception:
                        number = re.findall(r'\d', group)[0]
                    finally:
                        newRowList.append(int(number))
                        neededGroups.append(int(number))
                else:
                    newRowList.append(0)
            else:
                newRowList.append(0)
        horatio[row-1] = newRowList
    break
horatio = np.array(horatio)
neededGroups = list(set(neededGroups))
print(horatio.shape)
print(neededGroups)


try:
    li = []
    li[0]
    print(1)
except Exception:
    li2 = []
    li2[0]
    print(2)
finally:
    print(3)