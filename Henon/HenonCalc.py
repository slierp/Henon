# -*- coding: utf-8 -*-
from PyQt5 import QtCore
import multiprocessing as mp
#from datetime import datetime
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
        self.array = mp.RawArray(ctypes.c_bool, window_width*window_height)
        
        self.interval_flags = mp.Array('b', self.thread_count) # Have worker tell us when a piece work is finished
        self.interval_flags[:] = [False]*self.thread_count

        self.stop_signal = mp.Array('b', self.thread_count) # Booleans for sending stop signal
        self.stop_signal[:] = [False]*self.thread_count
            
        self.workers_started = False
                     
    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

        #print("[" + self.name + "] Starting workers")

        shared_tuple = self.array, self.interval_flags, self.stop_signal
        self.worker_list = []
        for i in range(self.thread_count):
            
            if not self.orbit_mode:
                w = WorkerProcess(args=([i, self.settings, shared_tuple]))
            else:
                w = WorkerProcessOrbit(args=([i, self.settings, shared_tuple]))
                
            self.worker_list.append(w)
            
            try:
                w.start()
            except:
                pass
           
        self.workers_started = True

        self.exec_() # start thread
    
    @QtCore.pyqtSlot()              
    def stop(self):
                      
        #print("[" + self.name + "] Received stop signal")

        if self.workers_started:
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
        self.array, self.interval_flags, self.stop_signal = args[2]
        self.randomizer = np.random.default_rng()        
        #print("[" + self.name + "] Worker " + str(self.run_number) + " initialization")        

    def shutdown(self):
        #print("[" + self.name + "] Worker " + str(self.run_number) + " shutdown initiated")
        self.exit.set()

    def fixed_points(self,a,b,point):
        
        a0 = pow(1-b,2)/4
        
        if a > a0:      
            x0 = (1/(2*a))*(-(1-b) + pow(pow(1-b,2) + 4*a,0.5))
            y0= b*x0
            x1 = (1/(2*a))*(-(1-b) - pow(pow(1-b,2) + 4*a,0.5))
            y1= b*x1
        else:
            x0 = y0 = x1 = y0 = 0
       
        if not point:
            return x0,y0
        else:
            return x1,y1

    def run(self):
        
        #start_time = datetime.now()
        #print("[" + self.name + "] Worker " + str(self.run_number) + " has started")

        iter_count = 0

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
        initial_conditions_multiplier = self.settings['initial_conditions_multiplier']
        initial_conditions_additive = self.settings['initial_conditions_additive']

        animation_running = self.settings['animation_running']
        xratio = window_width/(xright-xleft)
        yratio = window_height/(ytop-ybottom)

        henx = (((self.randomizer.random()-0.5)/5) + initial_conditions_additive) * initial_conditions_multiplier # generate random starting points
        heny = (((self.randomizer.random()-0.5)/5) + initial_conditions_additive) * initial_conditions_multiplier
        #henx,heny = self.fixed_points(hena,henb,0)

        run_number = self.run_number

        if animation_running:
            hena_start = self.settings['hena_start']            
            hena_stop = self.settings['hena_stop']
            hena_increment = self.settings['hena_increment']
            hena_anim = self.settings['hena_anim']
            henb_start = self.settings['henb_start']
            henb_stop = self.settings['henb_stop']
            henb_increment = self.settings['henb_increment']
            henb_anim = self.settings['henb_anim']
            plot_interval = self.settings['plot_interval_anim']
            max_iter = self.settings['max_iter_anim']
            empty_array = mp.RawArray(ctypes.c_bool, window_width*window_height) # needed for emptying self.array
            empty_array[:] = [False]*window_width*window_height            

            if hena_anim:
                hena = hena_start
                
            if henb_anim:
                henb = henb_start

            if hena_stop < hena_start:
                hena_increment = - hena_increment

            if henb_stop < henb_start:
                henb_increment = - henb_increment

        # make local array for storing pixel during each iteration
        local_array = np.zeros(window_width*window_height,dtype=np.bool)
        
        while not self.exit.is_set():
 
            try:            
                for _ in repeat(None, drop_iter): # prevent drawing first iterations
                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
                    #henx, heny = heny,  -0.2*henx + (2.75*heny) - pow(heny,3) # Duffing
                    #henx, heny = pow(henx,2)-pow(heny,2)+(0.9*henx)+(-0.6013*heny),\
                    #    (2*henx*heny)+(2.0*henx)+(0.5*heny) # Tinkerbell                        
            except: # if x,y results move towards infinity
                #print("[" + self.name + "] Worker " + str(self.run_number) + " overflow")
                pass

            try:
                for _ in repeat(None, plot_interval):

                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
                    #henx, heny = heny,  -0.2*henx + (2.75*heny) - pow(heny,3) # Duffing
                    #henx, heny = pow(henx,2)-pow(heny,2)+(0.9*henx)+(-0.6013*heny),\
                    #    (2*henx*heny)+(2.0*henx)+(0.5*heny) # Tinkerbell                      
                    #if (0 < x_draw < window_width) and (0 < y_draw < window_height):
                    if (xleft < henx < xright) and (ybottom < heny < ytop):                        
                        # draw pixel if it is inside the current display area
                        #x_draw = int(round((henx-xleft) * xratio)) # adding rounding here is slightly more correct
                        x_draw = int((henx-xleft) * xratio) # but takes considerably more time
                        y_draw = int((heny-ybottom) * yratio) 

                        #local_array[(y_draw*window_width) + x_draw] = True # for bottom-left origin
                        
                        # for top-left origin
                        # +0 is there in case of common bug in drawing method that returns invalid window width;
                        # in combination with array flattening such bugs give very distorted images                    
                        local_array[(window_height-y_draw)*(window_width+0) + x_draw] = True
            except: # OverFlowError
                #print("[WorkerProcess] Worker " + str(run_number) + " overflow")
                pass
                
            iter_count += plot_interval
            
            # 'bitwise or' on local array and multiprocessing array when plot_interval is reached
            if not animation_running:
                # add newly calculated pixels that this worker generatedy
                #np.frombuffer(self.array, dtype=ctypes.c_byte)[local_array == True] = True                
                np.frombuffer(self.array, dtype=ctypes.c_bool)[local_array == True] = True
                # indicate to HenonUpdate that we have some new pixels to draw
                self.interval_flags[run_number] = True                
            else:

                while not self.exit.is_set(): # wait until previous data was updated
                    sleep(0.01)
                    if not self.interval_flags[run_number]:
                        break

                if (run_number == 0): # empty current array and copy new data if you are worker 0
                    ctypes.memmove(self.array, empty_array, window_width*window_height)
                    np.frombuffer(self.array, dtype=ctypes.c_bool)[local_array == True] = True
                    self.interval_flags[run_number] = True
                else:
                    while not self.exit.is_set(): # wait until worker 0 is finished 
                        sleep(0.01)
                        if self.interval_flags[0]:
                            np.frombuffer(self.array, dtype=ctypes.c_bool)[local_array == True] = True
                            self.interval_flags[run_number] = True
                            break           

                if hena_anim:                    
                    new_hena = np.round(hena + hena_increment,4)
                    
                    if hena_stop >= hena_start and new_hena <= hena_stop:
                        hena = new_hena
                    elif hena_stop <= hena_start and new_hena >= hena_stop:
                        hena = new_hena                        

                if henb_anim:
                    new_henb = np.round(henb + henb_increment,4)
                    
                    if henb_stop >= henb_start and new_henb <= henb_stop:
                        henb = new_henb
                    elif henb_stop <= henb_start and new_henb >= henb_stop:
                        henb = new_henb
                
                local_array.fill(False)
            
            if (iter_count >= max_iter):
                break
                    
        self.interval_flags[run_number] = True # send message to HenonUpdate to show end result 
        self.stop_signal[run_number] = True # sends message to HenonUpdate to stop because max_iter reached
        
        #delta = datetime.now() - start_time
        #print("[" + self.name + "] Worker " + str(run_number) + " has stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds")        
        #print("[" + self.name + "] Worker " + str(run_number) + " has stopped")
        
class WorkerProcessOrbit(WorkerProcess):    

    def run(self):
        
        self.name= "WorkerProcessOrbit"
        
        #print("[" + self.name + "] Worker " + str(self.run_number) + " has started")

        iter_count = 0
        
        # make local copies of variables to increase speed
        hena = self.settings['hena']
        henb = self.settings['henb']
        xleft = self.settings['xleft']
        xright = self.settings['xright']
        ybottom = self.settings['ybottom']
        ytop = self.settings['ytop']
        plot_interval = self.settings['plot_interval_orbit']
        max_iter = self.settings['max_iter_orbit']
        window_width = self.settings['window_width']
        window_height = self.settings['window_height']
        drop_iter = self.settings['drop_iter']
        thread_count = self.settings['thread_count']
        orbit_parameter = self.settings['orbit_parameter']
        orbit_coordinate = self.settings['orbit_coordinate']
        animation_running = self.settings['animation_running'] 
        initial_conditions_multiplier = self.settings['initial_conditions_multiplier']        
        initial_conditions_additive = self.settings['initial_conditions_additive']
        
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

        if animation_running:
            hena_start = self.settings['hena_start']            
            hena_stop = self.settings['hena_stop']
            hena_increment = self.settings['hena_increment']
            hena_anim = self.settings['hena_anim']
            henb_start = self.settings['henb_start']
            henb_stop = self.settings['henb_stop']
            henb_increment = self.settings['henb_increment']
            henb_anim = self.settings['henb_anim']
            max_iter = self.settings['max_iter_anim']
            #empty_array = mp.RawArray(ctypes.c_byte, window_width*window_height) # needed for emptying self.array
            empty_array = mp.RawArray(ctypes.c_bool, window_width*window_height) # needed for emptying self.array
            empty_array[:] = [False]*window_width*window_height

            if hena_anim:
                hena = hena_start
                
            if henb_anim:
                henb = henb_start

            if orbit_parameter:
                hena = xleft
            else:
                henb = xleft
                
            if hena_stop < hena_start:
                hena_increment = - hena_increment

            if henb_stop < henb_start:
                henb_increment = - henb_increment

        # make local array for storing pixel during each iteration        
        #local_array = mp.RawArray(ctypes.c_bool, window_width*window_height)
        local_array = np.zeros(window_width*window_height,dtype=np.bool)

        henx_start = (((self.randomizer.random()-0.5)/5) + initial_conditions_additive) * initial_conditions_multiplier # generate random starting points
        heny_start = (((self.randomizer.random()-0.5)/5) + initial_conditions_additive) * initial_conditions_multiplier
        #henx_start,heny_start = self.fixed_points(hena,henb,0)        
        henx,heny = henx_start,heny_start

        while not self.exit.is_set():

            try:
                for _ in repeat(None, drop_iter): # prevent drawing first iterations
                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx
                    #henx, heny = heny,  -0.2*henx + (2.75*heny) - pow(heny,3) # Duffing
                    #henx, heny = pow(henx,2)-pow(heny,2)+(0.9*henx)+(-0.6013*heny),\
                    #    (2*henx*heny)+(2.0*henx)+(0.5*heny) # Tinkerbell                     
            except: #OverFlowError          
                pass
            
            try:
                for _ in repeat(None, plot_interval):             
                    henx, heny = 1 + heny - (hena*(henx**2)), henb * henx 
                    #henx, heny = heny,  -0.2*henx + (2.75*heny) - pow(heny,3) # Duffing
                    #henx, heny = pow(henx,2)-pow(heny,2)+(0.9*henx)+(-0.6013*heny),\
                    #   (2*henx*heny)+(2.0*henx)+(0.5*heny) # Tinkerbell                     
                    if orbit_coordinate:
                        #y_draw = int(round((heny-ybottom) * yratio)) # adding rounding here is slightly more correct
                        y_draw = int((heny-ybottom) * yratio)
                    else:
                        #y_draw = int(round((henx-ybottom) * yratio))
                        y_draw = int((henx-ybottom) * yratio)
                        
                    if (0 < y_draw < window_height):                  
                        local_array[(window_height-y_draw)*window_width + x_draw] = True                     
            except: #OverFlowError
                pass
            
            x_draw += thread_count
            
            if orbit_parameter:
                hena += thread_count/xratio
            else:
                henb += thread_count/xratio
            
            if (x_draw >= window_width):
                
                if not animation_running:
                    # 'bitwise or' on local array and multiprocessing array
                    np.frombuffer(self.array, dtype=ctypes.c_bool)[local_array == True] = True
                    
                    # indicate to HenonUpdate that we have some new pixels to draw
                    self.interval_flags[run_number] = True
                    
                    iter_count += plot_interval
                    x_draw = run_number 

                    henx,heny = henx_start,heny_start
                    
                    if orbit_parameter:
                        hena = xleft
                        hena += run_number/xratio           
                    else:
                        henb = xleft
                        henb += run_number/xratio                

                else:

                    while not self.exit.is_set(): # wait until previous data was updated
                        sleep(0.01)
                        if not self.interval_flags[run_number]:
                            break

                    if (run_number == 0): # empty current array and copy new data if you are worker 0
                        ctypes.memmove(self.array, empty_array, window_width*window_height)
                        np.frombuffer(self.array, dtype=ctypes.c_bool)[local_array == True] = True
                        self.interval_flags[run_number] = True
                    else:
                        while not self.exit.is_set(): # wait until worker 0 is finished 
                            sleep(0.01)
                            if self.interval_flags[0]:
                                np.frombuffer(self.array, dtype=ctypes.c_bool)[local_array == True] = True
                                self.interval_flags[run_number] = True
                                break
                                       
                    iter_count += plot_interval
                    x_draw = run_number                                       

                    henx,heny = henx_start,heny_start

                    if orbit_parameter:
                        hena = xleft
                        hena += run_number/xratio

                        new_henb = np.round(henb + henb_increment,4)
                        
                        if henb_stop >= henb_start and new_henb <= henb_stop:
                            henb = new_henb
                        elif henb_stop <= henb_start and new_henb >= henb_stop:
                            henb = new_henb                   
                    else:
                        henb = xleft
                        henb += run_number/xratio

                        new_hena = np.round(hena + hena_increment,4)
                    
                        if hena_stop >= hena_start and new_hena <= hena_stop:
                            hena = new_hena
                        elif hena_stop <= hena_start and new_hena >= hena_stop:
                            hena = new_hena
                    
                    local_array.fill(False)
            
            if (iter_count >= max_iter):
                break
        
        self.interval_flags[run_number] = True # send message to HenonUpdate to show end result 
        self.stop_signal[run_number] = True # sends message to HenonUpdate to stop because max_iter reached        
        #print("[" + self.name + "] Worker " + str(run_number) + " has stopped")