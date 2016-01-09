# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from datetime import datetime
import numpy as np

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)    

class StringSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class HenonUpdate(QtCore.QObject):
    # HenonUpdate implementation for multiprocessing
    # waits for signals from worker threads; once all are received it copies the results into
    # window_representation and sends a signal to trigger a screen re-draw

    def __init__(self, _settings, _interval_flags, _stop_signal, _mp_arr, _window_representation):       
        QtCore.QObject.__init__(self)
        
#        print "[HenonUpdate] Initialization" #DEBUG

        self.signal = Signal()
        self.quit_signal = Signal()
        self.benchmark_signal = StringSignal()        
        
        self.interval_flags = _interval_flags
        self.stop_signal = _stop_signal
        self.thread_count = _settings['thread_count']
        self.mp_arr = _mp_arr
        self.window_representation = _window_representation
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

#        print "[HenonUpdate] Ready for screen updates" #DEBUG
        
        self.updates_started = True

        # timer for checking updates
        # needs to be declared here and not in initialization
        # because QTimer requires a QThread, which HenonUpdate is moved into after init
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_for_update)
        
        self.check_for_update()

    def check_for_update(self):
       
        if all(i for i in self.interval_flags): # perform update
            self.perform_update()
            self.interval_flags[:] = [False]*self.thread_count # reset for new signal        
        elif self.stop_signal.value: # quit updates
            self.perform_update()
            if self.benchmark:
                delta = datetime.now() - self.time_start
                self.benchmark_signal.sig.emit(str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
            
            self.quit_signal.sig.emit()            
            return
        
        # call itself again in some time
        if self.animation_running:
            time_delay = max([25,self.animation_delay])
            self.timer.start(time_delay)
        else:
            self.timer.start(25)

    def perform_update(self):

#        print "[HenonUpdate] Copying results and sending screen re-draw signal" #DEBUG
       
        arr = np.frombuffer(self.mp_arr, dtype=np.bool) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
        
        if self.enlarge_rare_pixels:
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1)
 
        if self.animation_running:
            self.window_representation[:] = 0
           
        self.window_representation[arr == True] = 255 # add newly calculated pixels

#        print "[HenonUpdate] Pixels in screen window: " + str(self.window_width*self.window_height) #DEBUG
#        print "[HenonUpdate] Pixels in copied array: " + str(np.count_nonzero(arr)) #DEBUG 
#        print "[HenonUpdate] Pixels in window array: " + str(np.count_nonzero(self.window_representation)) #DEBUG

#        delta = datetime.now() - self.time_prev #DEBUG
#        print "[HenonUpdate] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG
        self.signal.sig.emit()       