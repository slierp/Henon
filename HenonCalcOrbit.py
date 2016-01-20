# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from random import uniform
import multiprocessing as mp
#from datetime import datetime #DEBUG
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
        
#        print "[HenonCalc] Initialization" #DEBUG
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

        self.stop_signal = mp.Value('b', False) # Boolean for sending stop signal

        shared_tuple = self.mp_arr, self.interval_flags, self.stop_signal

        self.worker_list = []
        for i in range(self.thread_count):
            self.worker_list.append(WorkerProcess(args=([i, self.settings, shared_tuple]))) # independent process
            
        self.workers_started = False
                     
    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

#        print "[HenonCalc] Starting workers" #DEBUG

        for i in range(self.thread_count):            
            self.worker_list[i].start()
            
        self.workers_started = True
                    
    def stop(self):
                      
#        print "[HenonCalc] Received stop signal" #DEBUG
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

        self.xratio = self.window_width/(self.xright-self.xleft)
        self.yratio = self.window_height/(self.ytop-self.ybottom)
            
        self.mp_arr, self.interval_flags, self.stop_signal = args[2]

    def shutdown(self):
#        print "[WorkerProcess] Worker " + str(self.run_number) + " shutdown initiated" #DEBUG
        self.exit.set()

    def drop_iterations(self,hena,henb,henx,heny):        
        try:            
            for i in range(self.drop_iter): # prevent drawing first iterations
                henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
            return henx,heny
        except OverflowError: # if x,y results move towards infinity
#            print "[WorkerProcess] Worker " + str(self.run_number) + " overflow" #DEBUG                
            return uniform(-0.1,0.1),uniform(-0.1,0.1)

    def run(self):
        
#        start_time = datetime.now() #DEBUG

#        print "[WorkerProcess] Worker " + str(self.run_number) + " has started" #DEBUG
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        # make local array for storing pixel during each iteration        
        # manipulating local array instead of multiprocessing array is a bit faster
        # subsequent data copying step takes almost no time
        local_array = np.zeros(len(self.mp_arr),dtype=ctypes.c_byte)
        
        # make local copies of variables to increase speed
        if self.orbit_parameter:
            hena = self.xleft
            henb = self.henb            
        else:
            hena = self.hena
            henb = self.xleft
            
        xratio = self.xratio
        ybottom = self.ybottom
        yratio = self.yratio
        drop_iter = self.drop_iter
        max_iter = self.max_iter_orbit
        window_width = self.window_width
        window_height = self.window_height
        run_number = self.run_number
        x_draw = 0

        while not self.exit.is_set():

            for i in xrange(max_iter):                
                try:            
                    for i in range(drop_iter): # prevent drawing first iterations
                        henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
                except OverflowError: # if x,y results move towards infinity
                    break                  
                
                try:
                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx            
                    y_draw = int((heny-ybottom) * yratio)
                    if (0 < y_draw < window_height):                  
                        local_array[(window_height-y_draw)*(window_width+0) + x_draw] = True
                except:
                    break

            # 'bitwise or' on local array and multiprocessing array
            np.frombuffer(self.mp_arr, dtype=ctypes.c_byte)[local_array == True] = True
            self.interval_flags[run_number] = True
            
            x_draw += 1
            hena += 1/xratio
            
            if (x_draw >= window_width):
                break
            
        # send message to HenonUpdate to show end result
        # in animation mode HenonUpdate will stop based only on interval_flags since there will be
        # only frame to draw
        self.interval_flags[run_number] = True 
        
        if (run_number == 0):
            self.stop_signal.value = True # sends message to HenonUpdate to stop because max_iter reached
        
#        delta = datetime.now() - start_time #DEBUG             
                        
#        print "[WorkerProcess] Worker " + str(run_number) + " has stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG        