# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore, QtGui
import HenonResources
from HenonUpdate import HenonUpdate
from HenonWidget import HenonWidget
from HenonCalc import HenonCalc
from HenonHelp import HenonHelp
from HenonSettings import HenonSettings
from multiprocessing import cpu_count
from math import log
from copy import deepcopy

"""
TODO

Add setting for plot_interval
One thread for animations of the whole attractor in a,b space

"""

class MainGui(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        
        super(MainGui, self).__init__(parent)
        
        self.setWindowTitle(self.tr("H\xe9non explorer")) #u'\xe9'

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
        
        # general settings
        self.hena = 1.4
        self.henb = 0.3
        self.xleft = -1.5
        self.ytop = 0.4
        self.xright = 1.5
        self.ybottom = -0.4
        self.thread_count = cpu_count()
        self.plot_interval = int(200000/self.thread_count)
        self.max_iter = 1
        self.iter_auto_mode = True
        self.full_screen = False
        self.first_run = True
        
        # animation settings
        self.hena_mid = 0.75
        self.hena_range = 1.0
        self.hena_increment = 0.05
        self.hena_anim = False
        self.henb_mid = -0.05
        self.henb_range = 0.7
        self.henb_increment = 0.05
        self.henb_anim = False
        self.animation_running = False
        
        # run default animation
        #self.iter_auto_mode = False
        #self.max_iter = 50000
        #self.plot_interval = 50000
        #self.henb_anim = True
        
        self.qt_thread0 = QtCore.QThread(self) # Separate Qt thread for generating regular update signals        
        self.qt_thread1 = QtCore.QThread(self) # Separate Qt thread for generating screen pixels              

    def on_about(self):
        msg = self.tr("H\xe9non explorer\n\n- Author: Ronald Naber\n- License: Public domain")
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
      
        self.Henon_widget.updateGL()
            
        if self.animation_running:
            self.Henon_widget.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))
            self.animate()            

    def wait_thread_end(self, thread):
        
        while True:            
            if thread.isRunning():
                thread.quit()
            else:
                return

    def initialize_calculation(self):
        
        # make sure threads have finished
        self.wait_thread_end(self.qt_thread0)
        self.wait_thread_end(self.qt_thread1)          
        
        if self.first_run:
            self.first_run = False

        if self.iter_auto_mode: 
            # set default maximum number of iterations
            # heavily optimized formula for calculating required number of iterations
            # as a function of the number of screen pixels and the x,y space represented by it
            area = (self.xright - self.xleft) * (self.ytop - self.ybottom)        
            self.max_iter = int(0.5 * abs(log(area)**2/log(2.4)**2) *  self.Henon_widget.window_width * self.Henon_widget.window_height / self.thread_count)
            self.plot_interval = int(200000/self.thread_count)
#            print "[MainGui] Plot area: " + str(area) #DEBUG
            
        if self.plot_interval > self.max_iter: # sanity check
            self.plot_interval = self.max_iter
        
        if (not self.max_iter): # sanity check
            self.max_iter = 1
        
#        print "[MainGui] Window width: " + str(self.Henon_widget.window_width) #DEBUG
#        print "[MainGui] Window height: " + str(self.Henon_widget.window_height) #DEBUG
#        print "[MainGui] Thread count: " + str(self.thread_count) #DEBUG            
#        print "[MainGui] Maximum iterations: " + str(self.max_iter) #DEBUG
#        print "[MainGui] Plot interval for iterations: " + str(self.plot_interval) #DEBUG
        
        # set widget plot area
        self.Henon_widget.xleft = self.xleft
        self.Henon_widget.ytop = self.ytop
        self.Henon_widget.xright = self.xright
        self.Henon_widget.ybottom = self.ybottom
        
        params = {} # put parameters in dict for easy transfer to calculation thread
        params['hena'] = self.hena
        params['henb'] = self.henb
        params['xleft'] = self.xleft
        params['ytop'] = self.ytop
        params['xright'] = self.xright
        params['ybottom'] = self.ybottom
        params['window_width'] = self.Henon_widget.window_width
        params['window_height'] = self.Henon_widget.window_height
        params['thread_count'] = self.thread_count
        params['max_iter'] = self.max_iter
        params['plot_interval'] = self.plot_interval

        # Henon_calc will start workers and wait for stop signal
        self.Henon_calc = HenonCalc(params)
        
        # Henon_updateWill will wait for worker signals and then send screen update signals
        self.Henon_update = HenonUpdate(self.Henon_calc.interval_flags, self.Henon_calc.stop_signal,\
            deepcopy(self.thread_count), self.Henon_calc.mp_arr, deepcopy(params), self.Henon_widget.window_representation)        
        
        self.Henon_update.moveToThread(self.qt_thread0) # Move updater to separate thread
        self.Henon_calc.moveToThread(self.qt_thread1)        
        
        # connecting like this appears crucial to make the thread run independently
        # and prevent GUI freeze
        if not self.animation_running:
            self.qt_thread0.started.connect(self.Henon_update.run)
        else:
            self.qt_thread0.started.connect(self.Henon_update.run_anim)
        self.qt_thread1.started.connect(self.Henon_calc.run)
        
        self.Henon_update.signal.sig.connect(self.update_screen) # Get signal for screen updates
        self.Henon_update.quit_signal.sig.connect(self.qt_thread0.quit) # Quit thread when finished
        self.Henon_calc.quit_signal.sig.connect(self.qt_thread1.quit) # Quit thread when finished
        
        self.qt_thread0.start()
        self.qt_thread1.start()     

    def initialize_animation(self):
        
        if self.first_run:
            return
        
#        print "[MainGui] Starting animation" #DEBUG        
        
        self.stop_calculation()
        
        if (not self.hena_anim) and (not self.henb_anim):
            # cannot animate if no variables are selected for animation
            return

        if (self.hena_anim):
            self.hena = self.hena_mid - 0.5*self.hena_range

        if (self.henb_anim):
            self.henb = self.henb_mid - 0.5*self.henb_range

        self.animation_running = True
        
        self.update_screen()
        
    def animate(self):       
        
        if (self.hena_anim):                
            if (self.hena < (self.hena_mid + 0.5*self.hena_range)):
                self.hena += self.hena_increment
                self.statusBar().showMessage("a = " + str(self.hena))                   
            else:
                self.animation_running = False                
                return
                
        if (self.henb_anim):
            if (self.henb < (self.henb_mid + 0.5*self.henb_range)):
                self.henb += self.henb_increment
                self.statusBar().showMessage("b = " + str(self.henb))
            else:
                self.animation_running = False                
                return 

    def reset_view(self):
        self.stop_calculation()        
        self.statusBar().showMessage(self.tr("Resetting view..."), 1000)
        self.xleft = -1.5
        self.ytop = 0.4
        self.xright = 1.5
        self.ybottom = -0.4
        self.Henon_widget.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))

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
        self.Henon_widget.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))

    def stop_calculation(self):
        self.Henon_calc.stop()

    def stop_user_command(self):
        self.statusBar().showMessage(self.tr("Sending stop signal..."), 1000)
        self.stop_calculation()       

    def closeEvent(self, event):
        # call stop function in order to terminate calculation processes
        # processes will continue after window close otherwise
        self.stop_calculation()

    def open_help_dialog(self):
        help_dialog = HenonHelp(self)
        help_dialog.setModal(True)
        help_dialog.show()        

    def open_settings_dialog(self):
        if self.animation_running:
            # prevent user from changing settings during animation
            return
            
        settings_dialog = HenonSettings(self)
        settings_dialog.setModal(True)
        settings_dialog.show() 

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

        tip = self.tr("Change settings")        
        settings_action = QtGui.QAction(self.tr("Settings"), self)
        settings_action.setIcon(QtGui.QIcon(":gear.png"))
        settings_action.triggered.connect(self.open_settings_dialog)        
        settings_action.setToolTip(tip)
        settings_action.setStatusTip(tip)
        settings_action.setShortcut('S')

        tip = self.tr("Animate")        
        animate_action = QtGui.QAction(self.tr("Animate"), self)
        animate_action.setIcon(QtGui.QIcon(":play.png"))
        animate_action.triggered.connect(self.initialize_animation)        
        animate_action.setToolTip(tip)
        animate_action.setStatusTip(tip)
        animate_action.setShortcut('A')

        tip = self.tr("Re-draw screen")        
        start_action = QtGui.QAction(self.tr("Re-draw"), self)
        start_action.setIcon(QtGui.QIcon(":redo.png"))
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
        
        self.run_menu.addAction(settings_action)
        self.run_menu.addAction(animate_action)
        self.run_menu.addAction(start_action)
        self.run_menu.addAction(stop_action)
        self.run_menu.addAction(quit_action)

        self.view_menu = self.menuBar().addMenu(self.tr("View"))

        tip = self.tr("Reset view")        
        reset_action = QtGui.QAction(self.tr("Reset view"), self)
        reset_action.setIcon(QtGui.QIcon(":revert.png"))
        reset_action.triggered.connect(self.reset_view)         
        reset_action.setToolTip(tip)
        reset_action.setStatusTip(tip)
        reset_action.setShortcut('F5')

        tip = self.tr("Toggle full-screen")        
        fullscreen_action = QtGui.QAction(self.tr("Full-screen"), self)
        fullscreen_action.setIcon(QtGui.QIcon(":expand.png"))
        fullscreen_action.triggered.connect(self.toggle_full_screen)         
        fullscreen_action.setToolTip(tip)
        fullscreen_action.setStatusTip(tip)
        fullscreen_action.setShortcut('F')

        self.view_menu.addAction(reset_action)
        self.view_menu.addAction(fullscreen_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("Help information")        
        help_action = QtGui.QAction(self.tr("Help..."), self)
        help_action.setIcon(QtGui.QIcon(":help.png"))
        help_action.triggered.connect(self.open_help_dialog)         
        help_action.setToolTip(tip)
        help_action.setStatusTip(tip)
        help_action.setShortcut('H')

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(help_action)
        self.help_menu.addAction(about_action)
