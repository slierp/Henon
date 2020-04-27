# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from datetime import datetime
import numpy as np
from time import sleep

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)    

class StringSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class HenonUpdate(QtCore.QThread):
    # HenonUpdate implementation for multiprocessing
    # waits for signals from worker threads; once all are received it copies the results into
    # window_representation and sends a signal to trigger a screen re-draw

    def __init__(self, _settings, _interval_flags, _stop_signal, _array, _window_representation):
        QtCore.QThread.__init__(self)
        self.name = "HenonUpdate"
        
        #print("[" + self.name + "] Initialization")

        self.signal = Signal()
        self.quit_signal = Signal()
        self.benchmark_signal = StringSignal()
        
        self.opencl_enabled = _settings['opencl_enabled']        
        self.interval_flags = _interval_flags
        self.stop_signal = _stop_signal
        self.thread_count = _settings['thread_count']
        self.array = _array
        self.window_representation = _window_representation
        self.window_width = _settings['window_width']
        self.window_height = _settings['window_height']
        self.enlarge_rare_pixels = _settings['enlarge_rare_pixels']
        self.benchmark = _settings['benchmark']
        self.animation_running = _settings['animation_running']
        self.animation_delay = _settings['animation_delay']
        #self.time_prev = datetime.now()

        if self.benchmark:
            self.time_start = datetime.now()
        
        self.updates_started = False        
                
    def run(self):

        if (self.updates_started): # fix strange problem where run command is started twice by QThread
            return

        #print("[" + self.name + "] Ready to receive screen updates")
       
        self.updates_started = True
        
        if not self.opencl_enabled:
            QtCore.QTimer.singleShot(100, self.check_for_update)
        else:
            QtCore.QTimer.singleShot(100, self.check_for_update2)

        self.exec_() # start thread        

    def check_for_update(self): # for multiprocessing
        
        #for i in range(self.thread_count): # check incoming signals
        #    #print(self.interval_flags[i],end='')            
        ##print(" ")
        
        if all(i for i in self.stop_signal): # quit updates
            #print("[" + self.name + "] Received stop signal")
            self.perform_update()            
            if self.benchmark:
                delta = datetime.now() - self.time_start
                self.benchmark_signal.sig.emit(str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
            
            if self.animation_running:
                self.quit_signal.sig.emit() # stop animation
                
            self.quit() # stop thread
            return
        
        if all(i for i in self.interval_flags):
            #print("[" + self.name + "] Received interval signal")
            self.perform_update()
                    
            if not self.animation_running:                            
                # call itself regularly
                self.interval_flags[:] = [False]*self.thread_count # restart all workers
                QtCore.QTimer.singleShot(100, self.check_for_update)
                return        
            else:                
                self.interval_flags[0] = False # give worker 0 a head-start            
                while True: # wait until worker 0 emptied the array and copied new data
                    if not self.interval_flags[0]:
                        sleep(0.01)
                    else:
                        break
                
                if self.thread_count:
                    self.interval_flags[1:] = [False]*(self.thread_count-1) # restart all other workers                
                    
                QtCore.QTimer.singleShot(self.animation_delay, self.check_for_update)
                return
    
        QtCore.QTimer.singleShot(100, self.check_for_update)
        
    def check_for_update2(self): # for opencl
        
        if self.stop_signal.value: # quit updates
            #print("[" + self.name + "] Received stop signal")
            self.perform_update2()            
            if self.benchmark:
                delta = datetime.now() - self.time_start
                self.benchmark_signal.sig.emit(str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
            
            if self.animation_running:
                self.quit_signal.sig.emit() # stop animation
                
            self.quit() # stop thread
            return
        
        if self.interval_flags.value:
            #print("[" + self.name + "] Received interval signal")
            self.perform_update2()
            self.interval_flags.value = False # reset for new signal
        
            if not self.animation_running:                            
                # call itself regularly
                QtCore.QTimer.singleShot(100, self.check_for_update2)
                return        
            else:
                QtCore.QTimer.singleShot(self.animation_delay, self.check_for_update2)
                return
    
        QtCore.QTimer.singleShot(100, self.check_for_update2)        

    def perform_update(self): # for multiprocessing

        #print("[" + self.name + "] Copying results and sending screen re-draw signal")
       
        arr = np.frombuffer(self.array, dtype=np.bool) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
        
        if self.enlarge_rare_pixels:
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1)
 
        if self.animation_running:
            self.window_representation[:] = 0
           
        self.window_representation[arr == True] = 200 # add newly calculated pixels

        ##print("[" + self.name + "] Pixels in screen window: " + str(self.window_width*self.window_height))
        ##print("[" + self.name + "] Pixels in copied array: " + str(np.count_nonzero(arr))) 
        ##print("[" + self.name + "] Pixels in window array: " + str(np.count_nonzero(self.window_representation)))

        #delta = datetime.now() - self.time_prev
        ##print("[" + self.name + "] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
        self.signal.sig.emit()
        
    def perform_update2(self): # for opencl
        
        #print("[" + self.name + "] Copying results and sending screen re-draw signal")
        
        arr = np.frombuffer(self.array, dtype=np.uint16) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array                         
        
        if self.enlarge_rare_pixels:
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1)
 
        if self.animation_running:
            self.window_representation[:] = 0
           
        self.window_representation[arr == 255] = 200 # add newly calculated pixels

        ##print("[" + self.name + "] Pixels in screen window: " + str(self.window_width*self.window_height))
        ##print("[" + self.name + "] Pixels in copied array: " + str(np.count_nonzero(arr))) 
        ##print("[" + self.name + "] Pixels in window array: " + str(np.count_nonzero(self.window_representation)))

        #delta = datetime.now() - self.time_prev
        ##print("[" + self.name + "] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
        self.signal.sig.emit()         