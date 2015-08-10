# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore, QtGui
import HenonResources
from HenonUpdate import HenonUpdate
from HenonWidget import HenonWidget
from HenonCalc import HenonCalc

"""
TODO

Implement help file
Implement dialog for setting a,b values
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
        
        self.hena = 1.4
        self.henb = 0.3
        self.full_screen = False
        
        self.qt_thread0 = QtCore.QThread(self) # Separate Qt thread for generating regular update signals
        self.update_instance = HenonUpdate() # Will generate screen update signals
        self.update_instance.moveToThread(self.qt_thread0) # Move updater to separate thread
        self.update_instance.signal.sig.connect(self.update_screen) # Get signal for screen updates      
        self.qt_thread0.started.connect(self.update_instance.run) # Start updates when thread is started          
        self.qt_thread0.start()
        
        self.qt_thread1 = QtCore.QThread(self) # Separate Qt thread for generating screen pixels        

    def on_about(self):
        msg = self.tr("Henon explorer\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)

    def keyPressEvent(self, e):
        if (e.key() == QtCore.Qt.Key_Space):
            # reset view with F5 or space
            self.reset_view()              
        elif (e.key() == QtCore.Qt.Key_Escape):
            # exit full-screen mode with escape button or stop calculation
            if (self.full_screen):                
                self.toggle_full_screen()
            else:
                self.stop_user_command()             

    @QtCore.pyqtSlot()
    def update_screen(self):
        
        if self.qt_thread1.isRunning():
            self.Henon_calc.read_array()
            self.Henon_widget.updateGL()

    def initialize_calculation(self):
        
        params = {} # put parameters in dict for easy transfer to calculation thread
        params['hena'] = self.hena
        params['henb'] = self.henb
        params['xleft'] = self.Henon_widget.xleft
        params['ytop'] = self.Henon_widget.ytop
        params['xright'] = self.Henon_widget.xright
        params['ybottom'] = self.Henon_widget.ybottom

        self.Henon_calc = HenonCalc(self.Henon_widget.window_representation, params) # Will generate screen pixels
        self.Henon_calc.moveToThread(self.qt_thread1) # Move to separate thread

        self.qt_thread1.start()
        self.qt_thread1.setPriority(QtCore.QThread.IdlePriority) # try to increase GUI responsiveness
        
        # qthread is started twice for unknown reasons, so perform run command separately
        # do not connect to qthread started signal
        self.Henon_calc.run()

    def reset_view(self):
        self.stop_calculation()        
        self.statusBar().showMessage(self.tr("Resetting view..."), 1000)            
        self.Henon_widget.reset_scale()

    def toggle_full_screen(self):
        self.stop_calculation()
        
        if not self.full_screen: # toggle full screen mode
            self.showFullScreen()
            self.full_screen = True
            self.statusBar().showMessage(self.tr("Press escape to exit full screen"), 1000)             
        else:
            self.showNormal()
            self.full_screen = False
        return            

    def restart_calculation(self):
        self.stop_calculation()        
        self.statusBar().showMessage(self.tr("Restarting..."), 1000)
        self.Henon_widget.restart()

    def stop_calculation(self):    
        self.Henon_calc.stop()     

    def stop_user_command(self):
        self.statusBar().showMessage(self.tr("Sending stop signal..."), 1000)
        self.stop_calculation()       

    def closeEvent(self, event):
        # call stop function in order to terminate calculation processes
        # processes will continue after window close otherwise
        self.stop_calculation()

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
        self.run_menu = self.menuBar().addMenu(self.tr("Run"))      

        tip = self.tr("Re-start")        
        start_action = QtGui.QAction(self.tr("Re-start"), self)
        start_action.setIcon(QtGui.QIcon(":play.png"))
        start_action.triggered.connect(self.restart_calculation)        
        start_action.setToolTip(tip)
        start_action.setStatusTip(tip)
        start_action.setShortcut('R')

        tip = self.tr("Stop")        
        stop_action = QtGui.QAction(self.tr("Stop"), self)
        stop_action.setIcon(QtGui.QIcon(":stop.png"))
        stop_action.triggered.connect(self.stop_user_command)        
        stop_action.setToolTip(tip)
        stop_action.setStatusTip(tip)
        stop_action.setShortcut('X')

        tip = self.tr("Quit")        
        quit_action = QtGui.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)        
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Q')
        
        self.run_menu.addAction(start_action)
        self.run_menu.addAction(stop_action)
        self.run_menu.addAction(quit_action)

        self.view_menu = self.menuBar().addMenu(self.tr("View"))

        tip = self.tr("Reset view")        
        reset_action = QtGui.QAction(self.tr("Reset view"), self)
        reset_action.triggered.connect(self.reset_view)         
        reset_action.setToolTip(tip)
        reset_action.setStatusTip(tip)
        reset_action.setShortcut('F5')

        tip = self.tr("Toggle full-screen")        
        fullscreen_action = QtGui.QAction(self.tr("Full-screen"), self)
        fullscreen_action.triggered.connect(self.toggle_full_screen)         
        fullscreen_action.setToolTip(tip)
        fullscreen_action.setStatusTip(tip)
        fullscreen_action.setShortcut('F')

        self.view_menu.addAction(reset_action)
        self.view_menu.addAction(fullscreen_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(about_action)
