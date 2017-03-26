# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from random import uniform
import multiprocessing as mp
#from datetime import datetime #DEBUG
import numpy as np
import ctypes
from time import sleep
from itertools import repeat

class HenonCalc(QtCore.QThread):    
    # Starts up worker threads for Henon calculations and then waits for stop signal
    # Not strictly necessary to make a separate thread, but it is required for HenonCalc2
    # so for compatibility it is a separate thread

    def __init__(self, _settings):
        QtCore.QThread.__init__(self)
        self.name= "HenonCalc"
        
        #print("[" + self.name + "] Initialization")
        self.settings = _settings
        
        window_width = self.settings['window_width']
        window_height = self.settings['window_height']
        
        self.thread_count = self.settings['thread_count']        
        self.orbit_mode = self.settings['orbit_mode']

        # shared array containing booleans for each pixel
        # content is a flattened array so it needs to be deflattened later on
        # RawArray implementation allows for copying local numpy array, which gives
        # speed-up, but may give stability issues as well
        self.mp_arr = mp.RawArray(ctypes.c_byte, window_width*window_height)

        self.interval_flags = mp.Array('b', self.thread_count) # Have worker tell us when a piece work is finished
        self.interval_flags[:] = [False]*self.thread_count

        self.stop_signal = mp.Array('b', self.thread_count) # Booleans for sending stop signal
        self.stop_signal[:] = [False]*self.thread_count
            
        self.workers_started = False
                     
    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

        #print("[" + self.name + "] Starting workers")

        shared_tuple = self.mp_arr, self.interval_flags, self.stop_signal
        self.worker_list = []
        for i in range(self.thread_count):
            if not self.orbit_mode:
                w = WorkerProcess(args=([i, self.settings, shared_tuple]))
            else:
                w = WorkerProcessOrbit(args=([i, self.settings, shared_tuple]))
            self.worker_list.append(w)
            w.start()
           
        self.workers_started = True

        self.exec_() # start thread
    
    @QtCore.pyqtSlot()              
    def stop(self):
                      
        #print("[" + self.name + "] Received stop signal")

        [worker.shutdown() for worker in self.worker_list] # shut down workers

        self.stop_signal.value = [True]*self.thread_count # stop updates
        
        self.quit() # stop thread
        
class WorkerProcess(mp.Process):
    # Subclass Process instead of calling function allows for nice exiting
    # using mp.Event and exit.set(); having a separate worker and thread is also
    # less transparent

    def __init__(self, args=()):
        mp.Process.__init__(self)
        self.name= "WorkerProcess"
        self.exit = mp.Event()        
        self.run_number = args[0]        
        self.settings = args[1]            
        self.mp_arr, self.interval_flags, self.stop_signal = args[2]
        #print("[" + self.name + "] Worker " + str(self.run_number) + " initialization")        

    def shutdown(self):
        #print("[" + self.name + "] Worker " + str(self.run_number) + " shutdown initiated")
        self.exit.set()

    def drop_iterations(self,drop_iter,hena,henb,henx,heny):        
        try:            
            for _ in repeat(None, drop_iter): # prevent drawing first iterations
                henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
            return henx,heny
        except OverflowError: # if x,y results move towards infinity
            #print("[" + self.name + "] Worker " + str(self.run_number) + " overflow")                
            return uniform(-0.1,0.1),uniform(-0.1,0.1)

    def run(self):
        
        #start_time = datetime.now() #DEBUG
        #print("[" + self.name + "] Worker " + str(self.run_number) + " has started")
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        iter_count = 0

        # make local array for storing pixel during each iteration        
        # manipulating local array instead of multiprocessing array is a bit faster
        # subsequent data copying step takes almost no time
        local_array = np.zeros(len(self.mp_arr),dtype=ctypes.c_byte)
        empty_array = np.zeros(len(self.mp_arr),dtype=ctypes.c_byte)
        
        # make local copies of variables to increase speed
        hena = self.settings['hena']
        henb = self.settings['henb']
        xleft = self.settings['xleft']
        xright = self.settings['xright']
        ybottom = self.settings['ybottom']
        ytop = self.settings['ytop']
        plot_interval = self.settings['plot_interval']
        max_iter = self.settings['max_iter']
        window_width = self.settings['window_width']
        window_height = self.settings['window_height']
        drop_iter = self.settings['drop_iter']       

        animation_running = self.settings['animation_running']
        xratio = window_width/(xright-xleft)
        yratio = window_height/(ytop-ybottom)

        run_number = self.run_number

        if animation_running:
            hena_increment = self.settings['hena_increment']
            hena_anim = self.settings['hena_anim']
            henb_increment = self.settings['henb_increment']
            henb_anim = self.settings['henb_anim']
            hena_max = round(self.hena_mid + 0.5*self.hena_range,3)
            henb_max = round(self.henb_mid + 0.5*self.henb_range,3)
            plot_interval = self.settings['plot_interval_anim']
            max_iter = self.settings['max_iter_anim']

        henx,heny = self.drop_iterations(drop_iter,hena,henb,henx,heny)

        if not henx or not heny:
            return

        while not self.exit.is_set():

            for _ in repeat(None, plot_interval):
                try:
                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx            

                    #if (0 < x_draw < window_width) and (0 < y_draw < window_height):
                    if (xleft < henx < xright) and (ybottom < heny < ytop):                        
                        # draw pixel if it is inside the current display area
                        x_draw = int((henx-xleft) * xratio) # adding rounding here is slightly more correct
                        y_draw = int((heny-ybottom) * yratio) # but takes considerably more time

                        #local_array[(y_draw*window_width) + x_draw] = True # for bottom-left origin
                        
                        # for top-left origin
                        # +0 is there in case of common bug in drawing method that returns invalid window width;
                        # in combination with array flattening such bugs give very distorted images                    
                        local_array[(window_height-y_draw)*(window_width+0) + x_draw] = True
                except:
                    #print("[WorkerProcess] Worker " + str(run_number) + " overflow") #DEBUG
                    pass
                
            iter_count += plot_interval
            
            # 'bitwise or' on local array and multiprocessing array when plot_interval is reached
            if not animation_running:
                # add newly calculated pixels that this worker generatedy
                np.frombuffer(self.mp_arr, dtype=ctypes.c_byte)[local_array == True] = True
                # indicate to HenonUpdate that we have some new pixels to draw
                self.interval_flags[run_number] = True                
            else:
                while not self.exit.is_set(): # wait until previous data was updated
                    if self.interval_flags[run_number]:
                        sleep(0.01)
                    else:
                        break

                if (run_number == 0): # empty current array
                    ctypes.memmove(self.mp_arr, empty_array.data[:], len(empty_array.data))
                else: # allow some time for worker 0 to empty array
                    sleep(0.01)
                
                np.frombuffer(self.mp_arr, dtype=ctypes.c_byte)[local_array == True] = True
                self.interval_flags[run_number] = True
                
                if iter_count >= max_iter:
                    pass

                if hena_anim:
                    new_hena = round(hena + hena_increment,3)
                    if new_hena <= hena_max:
                        hena = new_hena

                if henb_anim:
                    new_henb = round(henb + henb_increment,3)
                    if new_henb <= henb_max:
                       henb = new_henb
                
                henx,heny = self.drop_iterations(hena,henb,henx,heny)
                
                local_array = np.zeros(len(local_array),dtype=ctypes.c_byte)
            
            if (iter_count >= max_iter):
                break
                    
        self.interval_flags[run_number] = True # send message to HenonUpdate to show end result 
        self.stop_signal[run_number] = True # sends message to HenonUpdate to stop because max_iter reached
        
        #delta = datetime.now() - start_time #DEBUG
        #print("[" + self.name + "] Worker " + str(run_number) + " has stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds") #DEBUG        
        #print("[" + self.name + "] Worker " + str(run_number) + " has stopped")
        
class WorkerProcessOrbit(WorkerProcess):    

    def run(self):
        
        self.name= "WorkerProcessOrbit"
        
        #print("[" + self.name + "] Worker " + str(self.run_number) + " has started")
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        # make local array for storing pixel during each iteration        
        # manipulating local array instead of multiprocessing array is a bit faster
        # subsequent data copying step takes almost no time
        local_array = np.zeros(len(self.mp_arr),dtype=ctypes.c_byte)
        
        # make local copies of variables to increase speed
        hena = self.settings['hena']
        henb = self.settings['henb']
        xleft = self.settings['xleft']
        xright = self.settings['xright']
        ybottom = self.settings['ybottom']
        ytop = self.settings['ytop']
        max_iter = self.settings['max_iter_orbit']
        window_width = self.settings['window_width']
        window_height = self.settings['window_height']
        drop_iter = self.settings['drop_iter']
        thread_count = self.settings['thread_count']
        orbit_parameter = self.settings['orbit_parameter']
        orbit_coordinate = self.settings['orbit_coordinate']
        
        xratio = window_width/(xright-xleft)
        yratio = window_height/(ytop-ybottom)

        run_number = self.run_number
        x_draw = run_number

        if orbit_parameter:
            hena = xleft
            hena += run_number/xratio           
        else:
            henb = xleft
            henb += run_number/xratio

        while not self.exit.is_set():

            try:
                for _ in repeat(None, drop_iter): # prevent drawing first iterations
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
            for _ in repeat(None, max_iter):
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
        #print("[" + self.name + "] Worker " + str(run_number) + " has stopped")