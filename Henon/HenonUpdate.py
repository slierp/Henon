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
        self.screen_update = False
        self.stop = False
                
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

    def check_for_update(self): # wait for multiprocessing workers
        
        #for i in range(self.thread_count): # check incoming signals
        #    print(self.interval_flags[i],end='')            
        #    print(" ")
        
        if all(i for i in self.stop_signal): # quit updates
            #print("[" + self.name + "] Received stop signal")
            self.stop = True
            self.perform_update()
            
            if self.benchmark:
                delta = datetime.now() - self.time_start
                self.benchmark_signal.sig.emit(str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
            
            if self.animation_running:
                self.animation_running = False
                self.quit_signal.sig.emit() # stop animation
                
            self.quit() # stop thread
            return
        
        if all(i for i in self.interval_flags):
            #print("[" + self.name + "] Received interval signal")
            self.perform_update()
                   
            if self.animation_running:                                  
                QtCore.QTimer.singleShot(self.animation_delay, self.check_for_update)
            
            return
        
        if not self.stop:
            QtCore.QTimer.singleShot(100, self.check_for_update)
        
    def check_for_update2(self): # wait for opencl workers
        
        if self.stop_signal.value: # quit updates
            #print("[" + self.name + "] Received stop signal")
            self.stop = True
            self.perform_update2()            

            if self.benchmark:
                delta = datetime.now() - self.time_start
                self.benchmark_signal.sig.emit(str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")
            
            if self.animation_running:
                self.animation_running = False                
                self.quit_signal.sig.emit() # stop animation
                
            self.quit() # stop thread
            return
        
        if self.interval_flags.value:
            #print("[" + self.name + "] Received interval signal")
            self.perform_update2()
        
            if self.animation_running:                                  
                QtCore.QTimer.singleShot(self.animation_delay, self.check_for_update2)
                
            return

        if not self.stop:            
            QtCore.QTimer.singleShot(100, self.check_for_update2)        

    def perform_update(self): # for multiprocessing

        #print("[" + self.name + "] Copying results and sending screen re-draw signal")
       
        arr = np.frombuffer(self.array, dtype=np.bool) # get calculation result
        
        if not self.stop:
            self.interval_flags[:] = [False]*self.thread_count # restart all workers 
        
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
        
        if self.enlarge_rare_pixels:
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1)
 
        #if self.animation_running:
        #    self.window_representation[:] = 0
           
        #self.window_representation[arr == True] = True # 200 # add newly calculated pixels

        if self.animation_running:
            np.copyto(self.window_representation,arr)
        else:
            #self.window_representation += arr # add newly calculated pixels        
            #self.window_representation[arr == True] = True # 200 # add newly calculated pixels   
            np.logical_or(self.window_representation,arr,self.window_representation)

        ##print("[" + self.name + "] Pixels in screen window: " + str(self.window_width*self.window_height))
        ##print("[" + self.name + "] Pixels in copied array: " + str(np.count_nonzero(arr))) 
        ##print("[" + self.name + "] Pixels in window array: " + str(np.count_nonzero(self.window_representation)))

        #delta = datetime.now() - self.time_prev
        ##print("[" + self.name + "] Sending signal after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")

        self.screen_update = False
        self.signal.sig.emit()        
        
        if not self.stop:
            self.wait_for_screen_update
        
    def perform_update2(self): # for opencl
        
        #print("[" + self.name + "] Copying results and sending screen re-draw signal")

        #arr = np.frombuffer(self.array, dtype=np.uint16) # get calculation result        
        arr = np.frombuffer(self.array, dtype=np.bool) # get calculation result
        
        if not self.stop:
            self.interval_flags.value = False # reset for new signal        
            
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array                         
        
        if self.enlarge_rare_pixels:
            # enlarge pixels if there are very few of them
            pixel_number = np.count_nonzero(arr)
            if (pixel_number < 17) and (pixel_number > 0):
                arr = arr + np.roll(arr,1,0) + np.roll(arr,-1,0) + np.roll(arr,1,1) + np.roll(arr,-1,1)
 
        if self.animation_running:
            np.copyto(self.window_representation,arr)
        else:
            #self.window_representation += arr # add newly calculated pixels        
            #self.window_representation[arr == True] = True # 200 # add newly calculated pixels        
            np.logical_or(self.window_representation,arr,self.window_representation)

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
                if not self.opencl_enabled:                   
                    self.check_for_update
                else:
                    self.check_for_update2
                return
                
            QtCore.QTimer.singleShot(100, self.wait_for_screen_update)
     