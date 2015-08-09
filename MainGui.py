# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore, QtGui
import HenonResources
from HenonWidget import HenonWidget
from HenonUpdate import HenonUpdate
from HenonCalc import HenonCalc

"""
TODO

Multiple threads for enhanced zooming
One thread for animations of the whole attractor in a,b space

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
        
        self.qt_thread0 = QtCore.QThread(self) # Separate Qt thread for generating regular update signals
        self.update_instance = HenonUpdate() # Will generate screen update signals
        self.update_instance.moveToThread(self.qt_thread0) # Move updater to separate thread
        self.update_instance.signal.sig.connect(self.update_screen) # Get signal for screen updates      
        self.qt_thread0.started.connect(self.update_instance.run) # Start updates when thread is started          
        self.qt_thread0.start()
        
        self.hena = 1.4
        self.henb = 0.3
        self.stop_signal = False
        self.fast_calc = False

    def on_about(self):
        msg = self.tr("Henon explorer\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)

    def keyPressEvent(self, e):
            
        if e.key() == QtCore.Qt.Key_Space:
            self.give_stop_signal()
            self.Henon_widget.reset_scale()
            self.statusBar().showMessage(self.tr("Resetting view..."))
        elif e.key() == QtCore.Qt.Key_Escape:
            self.give_stop_signal()
            self.statusBar().showMessage(self.tr("Sending stop signal..."))

    def give_stop_signal(self):
        self.Henon_calc.stop_signal = True                

    @QtCore.pyqtSlot()
    def update_screen(self):
        self.Henon_widget.updateGL()

    def initialize_calculation(self):
        
        params0 = {} # put parameters in dict for easy transfer to calculation thread
        params0['hena'] = self.hena
        params0['henb'] = self.henb
        params0['xleft'] = self.Henon_widget.xleft
        params0['ytop'] = self.Henon_widget.ytop
        params0['xright'] = self.Henon_widget.xright
        params0['ybottom'] = self.Henon_widget.ybottom
        params0['fast_calc'] = self.fast_calc
            
        self.Henon_calc = HenonCalc(self,self.Henon_widget.window_representation, params0) # Will generate screen pixels
        self.Henon_calc.run()

    def create_main_frame(self):
        
        self.Henon_widget = HenonWidget(self)
        vbox = QtGui.QVBoxLayout()        
        vbox.addWidget(self.Henon_widget)

        main_frame = QtGui.QWidget()                                                         
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

        self.status_text = QtGui.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr(""))

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
