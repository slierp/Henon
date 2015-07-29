# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore, QtGui
import HenonResources
from Henon import Henon

"""
TODO

Create multiple threads using multiprocessing:
Have Henon iterator calculation fill up an array that represents window
Have OpenGL draw the array to the screen from time to time

"""

class MainGui(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        
        super(MainGui, self).__init__(parent)
        
        self.setWindowTitle(self.tr("Henon explorer"))

        ### Set initial geometry and center the window on the screen ###
        self.resize(1024, 576)
        frameGm = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())        
        
        ### Set default font size ###
        self.setStyleSheet('font-size: 12pt;') 
        
        self.create_menu()
        self.create_main_frame()       

    def on_about(self):
        msg = self.tr("Henon explorer\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)

    def keyPressEvent(self, e):
            
        if e.key() == QtCore.Qt.Key_Space:
            self.Henon_widget.reset_scale()

    def create_main_frame(self):           
        
        vbox = QtGui.QVBoxLayout()
        self.Henon_widget = Henon()
        vbox.addWidget(self.Henon_widget)

        main_frame = QtGui.QWidget()                                                         
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

        self.status_text = QtGui.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr("Ready"))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))      

        tip = self.tr("Quit")        
        quit_action = QtGui.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)        
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')
        
        self.file_menu.addAction(quit_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(about_action)
