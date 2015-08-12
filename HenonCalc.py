# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from random import uniform
from multiprocessing import Process, Array, RawArray, Value
from math import isinf, isnan
#from datetime import datetime #DEBUG
import numpy as np
import ctypes

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QObject.__init__(self)                

class HenonCalc(QtCore.QObject):

    def __init__(self, _params):
        QtCore.QObject.__init__(self)
        
#        print "[HenonCalc] Initialization" #DEBUG
        self.params = _params
        self.signal = Signal()
        self.quit_signal = Signal()
        
        self.xleft = self.params['xleft']
        self.ytop = self.params['ytop']
        self.xright = self.params['xright']
        self.ybottom = self.params['ybottom']
        self.hena = self.params['hena']
        self.henb = self.params['henb']
        self.window_width = self.params['window_width']
        self.window_height = self.params['window_height']
        self.thread_count = self.params['thread_count']
        self.max_iter = self.params['max_iter']
        self.plot_interval = self.params['plot_interval']

        self.xratio = self.window_width/(self.xright-self.xleft)
        self.yratio = self.window_height/(self.ytop-self.ybottom)

        # shared array containing booleans for each pixel
        # content is a flattened array so it needs to be deflattened later on
        # RawArray implementation allows for copying local numpy array, which gives
        # speed-up, but may give stability issues as well
        self.mp_arr = RawArray(ctypes.c_byte, self.window_width*self.window_height)
        #self.mp_arr = Array('b', self.window_width*self.window_height)

        self.interval_flags = Array('b', self.thread_count) # Have worker tell us when a piece work is finished

        self.stop_signal = Value('b', False) # Boolean for sending stop signal

        self.worker_list = []
        for i in range(self.thread_count):
            self.worker_list.append(Process(target=self.worker, args=([i, self.mp_arr, self.interval_flags, self.stop_signal]))) # independent process
            
        self.workers_started = False
                     
    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

#        print "[HenonCalc] Starting workers" #DEBUG

        for i in range(self.thread_count):
            self.worker_list[i].start()
            
        self.workers_started = True            
        
    def worker(self, run_number, array, interval_flags, stop_signal):      

#        start_time = datetime.now() #DEBUG

#        print "[HenonCalc] Worker " + str(run_number) + " has started" #DEBUG
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        for i in range(10): # prevent drawing first iterations
            henxtemp = 1-self.hena*(henx**2) + heny
            heny = self.henb * henx
            henx = henxtemp

        iter_count = 0

        # make local array for storing pixel during each iteration        
        # manipulating local array instead of multiprocessing array is a bit faster
        # subsequent data copying step takes almost no time
        local_array = np.zeros(len(array),dtype=ctypes.c_byte)
        
        # make local copies of variables to increase speed
        hena = self.hena
        henb = self.henb
        xleft = self.xleft
        xratio = self.xratio
        ybottom = self.ybottom
        yratio = self.yratio
        plot_interval = self.plot_interval
        max_iter = self.max_iter
        window_width = self.window_width
        window_height = self.window_height

        while True:             

            try:
                henxtemp = float(1-(hena*henx**2) + heny)
                heny = float(henb * henx)
                henx = henxtemp
                x_draw = (henx-xleft) * xratio
                y_draw = (heny-ybottom) * yratio
            except OverflowError:
#                print "[HenonCalc] Worker " + str(run_number) + " overflow" #DEBUG                
                break
            
            if (not isinf(x_draw)) and (not isinf(y_draw)) and (not isnan(x_draw)) and (not isnan(y_draw)):                
                # do not convert to int unless the number is finite
                if (0 < int(x_draw) < window_width) and (0 < int(y_draw) < window_height):
                    # draw pixel if it is inside the current display area
                    #array[(int(y_draw)*self.window_width) + int(x_draw)] = True
                    local_array[(int(y_draw)*window_width) + int(x_draw)] = True
                                        
            iter_count += 1
            
            if iter_count % plot_interval == 0:
                # copy local array to multiprocessing array when plot_interval is reached
                arr = np.frombuffer(array, dtype=ctypes.c_byte) # get current array in numpy format
                new_arr = np.bitwise_or(arr, local_array) # add newly calculated pixels
                ctypes.memmove(array, new_arr.data[:], len(new_arr.data)) # copy result into shared array   
                # indicate to HenonUpdate that we have some new pixels to draw
                interval_flags[run_number] = True               
            
            if (iter_count >= max_iter):
                if (run_number == 0):
                    # sends message to HenonUpdate to stop when max_iter reached
                    self.stop_signal.value = True
                break
            
            if iter_count % 1000 == 0:
                # do not check stop_signal too often
                # quickly limits iteration time
                if (stop_signal.value):
                    break

        interval_flags[run_number] = True # send message to HenonUpdate to show end result
                        
#        delta = datetime.now() - start_time #DEBUG             
                        
#        print "[HenonCalc] Worker " + str(run_number) + " has stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG
                    
    def stop(self):
                      
#        print "[HenonCalc] Received stop signal" #DEBUG
        self.stop_signal.value = True # send signal to stop workers

        for i in range(self.thread_count):
            # terminate worker threads if alive
            # prevents some issues with remaining threads after program has exited
            if self.worker_list[i].is_alive():
                self.worker_list[i].join()
                self.worker_list[i].terminate()
#                print "[HenonCalc] Worker " + str(i) + " terminated" #DEBUG
            
        self.quit_signal.sig.emit() # stop thread