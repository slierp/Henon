# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from datetime import datetime
import numpy as np

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

class HenonUpdate(QtCore.QObject):

    def __init__(self, _interval_flags, _stop_signal, _thread_count, _mp_arr, _params, _window_representation):
        QtCore.QObject.__init__(self)
        
#        print "[HenonUpdate] Initialization" #DEBUG

        self.signal = Signal()
        self.quit_signal = Signal()
        self.interval_flags = _interval_flags
        self.stop_signal = _stop_signal
        self.thread_count = _thread_count
        self.mp_arr = _mp_arr
        self.params = _params
        self.window_representation = _window_representation
        self.window_width = self.params['window_width']
        self.window_height = self.params['window_height']
        self.time_prev = datetime.now()
        
        self.updates_started = False        
                
    def run(self):

        if (self.updates_started): # fix strange problem where run command is started twice by QThread
            return

#        print "[HenonUpdate] Starting screen updates" #DEBUG
        
        self.updates_started = True
        
        while True:          
            
            self.wait_for_interval()

            if self.stop_signal.value:
#                print "[HenonUpdate] Received stop signal" #DEBUG
                self.quit_signal.sig.emit()
                return            
            
            self.interval_flags[:] = [False]*self.thread_count
            
            delta = datetime.now() - self.time_prev
            
            if (delta.microseconds < 2e5): # do not try redraw screen too fast
#                print "[HenonUpdate] Skipping a screen update as it is too soon" #DEBUG
                continue

#            print "[HenonUpdate] Copying results and sending screen re-draw signal" #DEBUG
           
            #with self.mp_arr.get_lock():
            arr = np.frombuffer(self.mp_arr.get_obj(), dtype=np.bool) # get calculation result
            arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
            arr = arr.T # height/width are switched around by default
            self.window_representation[arr == True] = 0xFFFFFFFF # add newly calculated pixels            
    
#            print "[HenonUpdate] Pixels in screen window: " + str(self.window_width*self.window_height) #DEBUG
#            print "[HenonUpdate] Pixels in copied array: " + str(np.count_nonzero(arr)) #DEBUG 
#            print "[HenonUpdate] Pixels in window array: " + str(np.count_nonzero(self.window_representation)) #DEBUG

#            print "[HenonUpdate] Sending signal after " + str(delta.microseconds) + " microseconds" #DEBUG
            self.signal.sig.emit()
            self.time_prev = datetime.now() 

    def wait_for_interval(self):

        while True:
            if all(i for i in self.interval_flags) or self.stop_signal.value:
                return