# -*- coding: utf-8 -*-
from __future__ import division
from PyQt5 import QtCore
from random import uniform
import multiprocessing as mp
import numpy as np
import ctypes

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QObject.__init__(self)

class HenonCalcOrbit(QtCore.QObject):
    # Starts up worker threads for Henon calculations and then waits for stop signal

    def __init__(self, _settings):
        QtCore.QObject.__init__(self)
        
        self.settings = _settings
        self.signal = Signal()
        self.quit_signal = Signal()
        
        self.window_width = self.settings['window_width']
        self.window_height = self.settings['window_height']
        self.thread_count = self.settings['thread_count']

        # shared array containing booleans for each pixel
        # content is a flattened array so it needs to be deflattened later on
        # RawArray implementation allows for copying local numpy array, which gives
        # speed-up, but may give stability issues as well
        self.mp_arr = mp.RawArray(ctypes.c_byte, self.window_width*self.window_height)

        self.interval_flags = mp.Array('b', self.thread_count) # Have worker tell us when a piece work is finished
        self.interval_flags[:] = [False]*self.thread_count

        self.stop_signal = mp.Array('b', self.thread_count) # Booleans for sending stop signal
        self.stop_signal[:] = [False]*self.thread_count

        shared_tuple = self.mp_arr, self.interval_flags, self.stop_signal

        self.worker_list = []
        for i in range(self.thread_count):
            self.worker_list.append(WorkerProcess(args=([i, self.settings, shared_tuple]))) # independent process
            
        self.workers_started = False
                     
    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

        for i in range(self.thread_count):            
            self.worker_list[i].start()
            
        self.workers_started = True
                    
    def stop(self):
                      
        self.stop_signal.value = True # send signal to HenonUpdate

        for i in range(self.thread_count):
            # shut down workers if alive
            if self.worker_list[i].is_alive():
                self.worker_list[i].shutdown()
            
        self.quit_signal.sig.emit() # stop thread
        
class WorkerProcess(mp.Process):
    # Subclass Process instead of calling function allows for nice exiting
    # using mp.Event and exit.set(); having a separate worker and thread is also
    # less transparent

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        mp.Process.__init__(self)
        self.exit = mp.Event()
        
        self.run_number = args[0]           
        
        settings = args[1]
        self.hena = settings['hena']
        self.henb = settings['henb']
        self.xleft = settings['xleft']
        self.ytop = settings['ytop']
        self.xright = settings['xright']
        self.ybottom = settings['ybottom']
        self.window_width = settings['window_width']
        self.window_height = settings['window_height']
        self.drop_iter = settings['drop_iter']
        self.max_iter_orbit = settings['max_iter_orbit']
        self.orbit_parameter = settings['orbit_parameter']
        self.orbit_coordinate = settings['orbit_coordinate']
        self.thread_count = settings['thread_count']

        self.xratio = self.window_width/(self.xright-self.xleft)
        self.yratio = self.window_height/(self.ytop-self.ybottom)
            
        self.mp_arr, self.interval_flags, self.stop_signal = args[2]

    def shutdown(self):
        self.exit.set()

    def run(self):
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        # make local array for storing pixel during each iteration        
        # manipulating local array instead of multiprocessing array is a bit faster
        # subsequent data copying step takes almost no time
        local_array = np.zeros(len(self.mp_arr),dtype=ctypes.c_byte)
        
        # make local copies of variables to increase speed            
        xratio = self.xratio
        ybottom = self.ybottom
        yratio = self.yratio
        drop_iter = self.drop_iter
        max_iter = self.max_iter_orbit
        window_width = self.window_width
        window_height = self.window_height
        run_number = self.run_number
        thread_count = self.thread_count 
        x_draw = run_number
        orbit_parameter = self.orbit_parameter
        orbit_coordinate = self.orbit_coordinate

        if orbit_parameter:
            hena = self.xleft
            hena += run_number/xratio
            henb = self.henb            
        else:
            hena = self.hena
            henb = self.xleft
            henb += run_number/xratio

        while not self.exit.is_set():

            try:            
                for i in range(drop_iter): # prevent drawing first iterations
                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
            except OverflowError: # if x,y results move towards infinity
                henx = uniform(-0.1,0.1)
                heny = uniform(-0.1,0.1)
                
                x_draw += thread_count
            
                if orbit_parameter:
                    hena += thread_count/xratio
                else:
                    henb += thread_count/xratio
                
                if (x_draw >= window_width):
                    break
            
                continue
            
            # no plot interval as we only calculate #threads pixels at a time
            # no try/except because we only allow working a,b ranges
            for i in range(max_iter): # changed xrange to range for Python3 conversion
                henx, heny = 1 + heny - (hena*(henx**2)), henb * henx            
                if orbit_coordinate:
                    y_draw = int((heny-ybottom) * yratio)
                else:
                    y_draw = int((henx-ybottom) * yratio)
                    
                if (0 < y_draw < window_height):                  
                    local_array[(window_height-y_draw)*window_width + x_draw] = True
            
            x_draw += thread_count
            
            if orbit_parameter:
                hena += thread_count/xratio
            else:
                henb += thread_count/xratio
            
            if (x_draw >= window_width):
                break           

        # 'bitwise or' on local array and multiprocessing array
        np.frombuffer(self.mp_arr, dtype=ctypes.c_byte)[local_array == True] = True
        
        self.interval_flags[run_number] = True # send message to HenonUpdate to show end result 
        self.stop_signal[run_number] = True # sends message to HenonUpdate to stop because max_iter reached