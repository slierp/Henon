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

class HenonUpdate(QtCore.QThread):
    # HenonUpdate implementation for multiprocessing
    # waits for signals from worker threads; once all are received it copies the results into
    # window_representation and sends a signal to trigger a screen re-draw

    def __init__(self, _settings, _interval_flags, _stop_signal, _array, _window_representation):
        QtCore.QThread.__init__(self)
        self.name = "HenonUpdate"
        
        #print("[" + self.name + "] Initialization")

        self.signal = Signal()
        self.updates_stopped = StringSignal()
        
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
        self.screen_update = False
        self.stop = False
                
    def run(self):

        if (self.updates_started): # fix strange problem where run command is started twice by QThread
            return

        #print("[" + self.name + "] Ready to receive screen updates")
       
        self.updates_started = True
        
        QtCore.QTimer.singleShot(100, self.check_for_update)

        self.exec_() # start thread                  

    def check_for_update(self): # wait for multiprocessing workers
        
        if not self.opencl_enabled:
            quit_signal = all(i for i in self.stop_signal)
        else:
            quit_signal = self.stop_signal.value                 
                
        if quit_signal: # quit updates
            #print("[" + self.name + "] Received stop signal")
            self.stop = True
            self.perform_update()
            
            result = ""
            if self.benchmark:
                delta = datetime.now() - self.time_start
                result = str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds"
            
            self.animation_running = False

            self.updates_stopped.sig.emit(result)                
            self.quit() # stop thread
            return

        if not self.opencl_enabled:
            interval_signal = all(i for i in self.interval_flags)
        else:
            interval_signal = self.interval_flags.value
        
        if interval_signal:
            #print("[" + self.name + "] Received interval signal")
            self.perform_update()
                   
            if self.animation_running:                                  
                QtCore.QTimer.singleShot(self.animation_delay, self.check_for_update)
            
            return
        
        if not self.stop:
            QtCore.QTimer.singleShot(100, self.check_for_update)

    def perform_update(self):

        #print("[" + self.name + "] Copying results and sending screen re-draw signal")
       
        arr = np.frombuffer(self.array, dtype=np.byte) # get calculation result

        if not self.stop:
            if not self.opencl_enabled:
                self.interval_flags[:] = [False]*self.thread_count # restart all workers 
            else:                
                self.interval_flags.value = False # restart all workers               
        
        arr = arr.reshape((self.window_height,self.window_width))
        arr = arr*255
        
        if self.enlarge_rare_pixels:
            arr = arr.reshape((self.window_height,self.window_width)) # deflatten array            
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1)

        if self.animation_running:
            np.copyto(self.window_representation,arr)
        else: 
            self.window_representation[arr == 255] = 255

        ##print("[" + self.name + "] Pixels in screen window: " + str(self.window_width*self.window_height))
        ##print("[" + self.name + "] Pixels in copied array: " + str(np.count_nonzero(arr))) 
        ##print("[" + self.name + "] Pixels in window array: " + str(np.count_nonzero(self.window_representation)))

        #delta = datetime.now() - self.time_prev
        ##print("[" + self.name + "] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")

        self.screen_update = False
        self.signal.sig.emit()        
        
        if not self.stop:
            self.wait_for_screen_update

    @QtCore.pyqtSlot()        
    def screen_update_finished(self):
        #print("[" + self.name + "] Screen update finished signal received")
        self.screen_update = True

    def wait_for_screen_update(self):
        
            if self.screen_update:                 
                self.check_for_update
                
            QtCore.QTimer.singleShot(100, self.wait_for_screen_update)
     