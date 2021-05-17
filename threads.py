# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 13:04:41 2020

@author: Steven
"""

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time

class Worker(QRunnable):
    '''
    Worker thread
    '''

    @pyqtSlot()
    def run(self):
        '''
        Your code goes in this function
        '''
        print("Thread start") 
        time.sleep(5)
        print("Thread complete")

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.counter = 0

        layout = QVBoxLayout()
    
        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)

        c = QPushButton("?")
        c.pressed.connect(self.change_message)

        layout.addWidget(self.l)
        layout.addWidget(b)

        layout.addWidget(c)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
    def change_message(self):
        self.message = "OH NO"
    
    def oh_no(self):
        worker = Worker()
        self.threadpool.start(worker)

    def ahre(self):
        print("Thread start") 
        time.sleep(5)
        print("Thread complete")


app = QApplication([])
window = MainWindow()
app.exec_()