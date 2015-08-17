# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from datetime import datetime
import numpy as np

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)    

class HenonUpdate(QtCore.QObject):
    # waits for signals from worker threads; once all are received it copies the results into
    # window_representation and sends a signal to trigger a screen re-draw

    def __init__(self, _interval_flags, _stop_signal, _thread_count, _mp_arr, _window_representation, _window_width, _window_height, _enlarge_rare_pixels):
        QtCore.QObject.__init__(self)
        
#        print "[HenonUpdate] Initialization" #DEBUG

        self.signal = Signal()
        self.quit_signal = Signal()
        
        self.interval_flags = _interval_flags
        self.stop_signal = _stop_signal
        self.thread_count = _thread_count
        self.mp_arr = _mp_arr
        self.window_representation = _window_representation
        self.window_width = _window_width
        self.window_height = _window_height
        self.enlarge_rare_pixels = _enlarge_rare_pixels
        self.time_prev = datetime.now()
        
        self.updates_started = False        
                
    def run(self):

        if (self.updates_started): # fix strange problem where run command is started twice by QThread
            return

#        print "[HenonUpdate] Ready for screen updates" #DEBUG
        
        self.updates_started = True

        # make copies for speed improvement        
        window_width = self.window_width
        window_height = self.window_height            
        enlarge_rare_pixels = self.enlarge_rare_pixels
        
        while True:          

            if self.stop_signal.value:
#                print "[HenonUpdate] Received stop signal" #DEBUG
                self.quit_signal.sig.emit()
                return
            
            self.wait_for_interval()            
            
            self.interval_flags[:] = [False]*self.thread_count
            
            delta = datetime.now() - self.time_prev
            
            if (delta.microseconds < 1e4): # do not try to redraw screen faster than necessary; can freeze up GUI
#                print "[HenonUpdate] Skipping a screen update as it is too soon" #DEBUG
                continue

#            print "[HenonUpdate] Copying results and sending screen re-draw signal" #DEBUG
           
            arr = np.frombuffer(self.mp_arr, dtype=np.bool) # get calculation result
            arr = arr.reshape((window_height,window_width)) # deflatten array
            
            if enlarge_rare_pixels:
                # enlarge pixels if there are very few of them
                pixel_number = np.count_nonzero(arr)
                if (pixel_number < 17) and (pixel_number > 0):
                    arr = np.bitwise_or(arr,np.roll(arr,1,0))
                    arr = np.bitwise_or(arr,np.roll(arr,-1,0))
                    arr = np.bitwise_or(arr,np.roll(arr,1,1))
                    arr = np.bitwise_or(arr,np.roll(arr,-1,1)) 
                
            self.window_representation[arr == True] = 255 # add newly calculated pixels
    
#            print "[HenonUpdate] Pixels in screen window: " + str(self.window_width*self.window_height) #DEBUG
#            print "[HenonUpdate] Pixels in copied array: " + str(np.count_nonzero(arr)) #DEBUG 
#            print "[HenonUpdate] Pixels in window array: " + str(np.count_nonzero(self.window_representation)) #DEBUG

#            print "[HenonUpdate] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG
            self.signal.sig.emit()
            self.time_prev = datetime.now() 

    def run_anim(self):
        
#        print "[HenonUpdate] Ready for animation screen update" #DEBUG

        if (self.updates_started): # fix strange problem where run command is started twice by QThread
            return
        
        self.updates_started = True
            
        while True:
            if all(i for i in self.interval_flags):
                break

#        print "[HenonUpdate] Animation screen update" #DEBUG
        
        arr = np.frombuffer(self.mp_arr, dtype=np.bool) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
        
        if self.enlarge_rare_pixels:
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = np.bitwise_or(arr,np.roll(arr,1,0))
                arr = np.bitwise_or(arr,np.roll(arr,-1,0))
                arr = np.bitwise_or(arr,np.roll(arr,1,1))
                arr = np.bitwise_or(arr,np.roll(arr,-1,1)) 
            
        self.window_representation[arr == True] = 255 # add newly calculated pixels            
    
        self.signal.sig.emit()
        self.quit_signal.sig.emit()        

    def wait_for_interval(self):

        while True:
            if all(i for i in self.interval_flags) or self.stop_signal.value:
                return