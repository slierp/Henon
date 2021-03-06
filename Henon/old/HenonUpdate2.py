# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from datetime import datetime
import numpy as np

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)    

class StringSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class HenonUpdate2(QtCore.QObject):
    # waits for signals from worker threads; once received it copies the results into
    # window_representation and sends a signal to trigger a screen re-draw

    def __init__(self,  _settings, _interval_flag, _stop_signal, _cl_arr, _window_representation):    
        QtCore.QObject.__init__(self)
        
#        print "[HenonUpdate2] Initialization" #DEBUG

        self.signal = Signal() # for screen updates
        self.quit_signal = Signal()
        self.benchmark_signal = StringSignal()

        self.interval_flag = _interval_flag
        self.stop_signal = _stop_signal        
        self.cl_arr = _cl_arr        
        self.window_representation = _window_representation
        self.thread_count = _settings['thread_count']
        self.window_width = _settings['window_width']
        self.window_height = _settings['window_height']        
        self.enlarge_rare_pixels = _settings['enlarge_rare_pixels']
        self.benchmark = _settings['benchmark']
        self.animation_running = _settings['animation_running']
        self.animation_delay = _settings['animation_delay']        
#        self.time_prev = datetime.now() #DEBUG

        if self.benchmark:
            self.time_start = datetime.now()
        
        self.updates_started = False       

    def run(self):

        if (self.updates_started): # fix strange problem where run command is started twice by QThread
            return

#        print "[HenonUpdate2] Ready for screen updates" #DEBUG
        
        self.updates_started = True

        # timer for checking updates
        # needs to be declared here and not in initialization
        # because QTimer requires a QThread, which HenonUpdate is moved into after init
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_for_update)
        
        self.check_for_update()

    def check_for_update(self):
        
        if self.interval_flag.value: # perform update
            self.perform_update()
            self.interval_flag.value = False
#            print "[HenonUpdate2] Sent signal to HenonCalc" #DEBUG            
            
            if self.animation_running:
                self.timer.start(self.animation_delay)
                return
        elif self.stop_signal.value: # quit updates        
            self.perform_update() # draw final result

            if self.benchmark:
                delta = datetime.now() - self.time_start
                self.benchmark_signal.sig.emit(str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
            
            self.quit_signal.sig.emit()
            return
        
        # call itself again in some time
        self.timer.start(10)
#        print "[HenonUpdate2] Waiting for signal from HenonCalc" #DEBUG

    def perform_update(self):

#        print "[HenonUpdate2] Copying results and sending screen re-draw signal" #DEBUG
       
        arr = np.frombuffer(self.cl_arr, dtype=np.uint16) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
        
        if self.enlarge_rare_pixels:
#            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1) 

        if self.animation_running: # clear screen if animation running
            self.window_representation[:] = 0

        self.window_representation[arr == 255] = 255 # add newly calculated pixels

#        print "[HenonUpdate2] Pixels in screen window: " + str(self.window_width*self.window_height) #DEBUG
#        print "[HenonUpdate2] Pixels in copied array: " + str(np.count_nonzero(arr)) #DEBUG 
#        print "[HenonUpdate2] Pixels in window array: " + str(np.count_nonzero(self.window_representation)) #DEBUG

#        delta = datetime.now() - self.time_prev #DEBUG
#        print "[HenonUpdate2] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG
        self.signal.sig.emit() # Signal for MainGui to update screen     