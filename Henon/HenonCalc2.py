# -*- coding: utf-8 -*-
from PyQt5 import QtCore
import pyopencl as cl
import multiprocessing as mp # for thread-safe memory sharing
#from datetime import datetime
import numpy as np
import ctypes
from time import sleep

class HenonCalc2(QtCore.QThread):  
    # Starts up worker threads for Henon calculations and then waits for stop signal
    # Implementation uses OpenCL for multithreaded calculation

    def __init__(self, _settings, _context, _command_queue, _mem_flags, _program):
        QtCore.QThread.__init__(self)
        self.name= "HenonCalc2"
        
        #print("[" + self.name + "] Initialization")
        self.context = _context
        self.command_queue = _command_queue
        self.mem_flags = _mem_flags
        self.program = _program
        self.settings = _settings
        
        self.orbit_mode = self.settings['orbit_mode']

        window_width = self.settings['window_width']
        window_height = self.settings['window_height']

        self.interval_flags = mp.Value('b', False) # Boolean for sending interval signal
        self.stop_signal = mp.Value('b', False) # Boolean for sending stop signal

        # empty array that will be copied to OpenCL kernel for processing
        #self.array = np.zeros((self.window_height*self.window_width), dtype=np.uint16)
        #self.array = mp.RawArray('H', window_width*window_height)
        self.array = mp.RawArray(ctypes.c_bool, window_width*window_height)
                   
        self.workers_started = False     

    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

        #print("[" + self.name + "] Starting workers")

        shared_tuple = self.context, self.command_queue, self.mem_flags, self.program, self.array, self.interval_flags, self.stop_signal

        if not self.orbit_mode:
            self.worker = WorkerProcess(args=([self.settings, shared_tuple]))
        else:
            self.worker = WorkerProcessOrbit(args=([self.settings, shared_tuple]))

        self.worker.start()

        self.workers_started = True

        self.exec_() # start thread

    @QtCore.pyqtSlot()
    def stop(self):                      
        #print("[" + self.name + "] Received stop signal")
        self.received_stop_signal = True
        if self.workers_started:
            self.worker.shutdown()
        self.quit() # stop thread


class WorkerProcess(QtCore.QThread):
    # Subclass Process instead of calling function allows for nice exiting
    # using mp.Event and exit.set(); having a separate worker and thread is also
    # less transparent                     

    def __init__(self, args=()):
        QtCore.QThread.__init__(self)
        self.name= "WorkerProcess"
        self.exit = mp.Event()       
        self.settings = args[0]            
        self.context, self.command_queue, self.mem_flags, self.program, self.array, self.interval_flags, self.stop_signal = args[1]
        self.randomizer = np.random.default_rng()        
        #print("[" + self.name + "] Worker " + str(self.run_number) + " initialization")

    def shutdown(self):
        #print("[" + self.name + "] Worker " + str(self.run_number) + " shutdown initiated")
        self.exit.set()

    def run(self):
        QtCore.QTimer.singleShot(0, self.run_calculation)
        self.exec_()

    def run_calculation(self):

        hena = self.settings['hena']
        henb = self.settings['henb']
        xleft = self.settings['xleft']
        ytop = self.settings['ytop']
        xright = self.settings['xright']
        ybottom = self.settings['ybottom']
        global_work_size = pow(2,self.settings['global_work_size'])
        max_iter = self.settings['max_iter']
        plot_interval = self.settings['plot_interval']
        drop_iter = self.settings['drop_iter']       
        animation_running = self.settings['animation_running']
        window_width = self.settings['window_width']
        window_height = self.settings['window_height']        
        
        # ensures dtype and c-type contiguous, but does not seem to be necessary
        #self.array = np.require(self.array, np.uint16, 'C') 

        #start_time = datetime.now()

        iter_count = 0

        xratio = window_width/(xright-xleft)
        yratio = window_height/(ytop-ybottom)

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
            plot_interval = self.settings['plot_interval_anim']
            #empty_array = mp.RawArray('H', 2*window_width*window_height) # needed for emptying self.array
            empty_array = mp.RawArray(ctypes.c_bool, window_width*window_height) # needed for emptying self.array
            
            if hena_anim:
                hena = hena_start
                
            if henb_anim:
                henb = henb_start                                     
                
            if hena_stop < hena_start:
                hena_increment = - hena_increment

            if henb_stop < henb_start:
                henb_increment = - henb_increment                
            
        # random x,y values in (-0.1,0.1) range for each GPU thread
        # opencl-float2 does not exist in current pyopencl version, but complex does
        # so we'll use that for now to pass along x,y values
        #xx = ((np.random.random_sample(global_work_size)-0.5)/5)
        xx = ((self.randomizer.random(global_work_size)-0.5)/5)
        #yy = ((np.random.random_sample(global_work_size)-0.5)/5) * 1j
        yy = ((self.randomizer.random(global_work_size)-0.5)/5) * 1j
        queue = xx+yy
        first_run = True

        local_array = mp.RawArray(ctypes.c_bool, window_width*window_height)
        int_params = np.array([plot_interval,drop_iter,window_height,window_width],dtype=np.uint32)
        float_params = np.array([hena,henb,xleft,ybottom,xratio,yratio],dtype=np.float64)

        while not self.exit.is_set():
    
            # allocate memory for buffers and copy contents
            int_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=int_params)    
            float_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=float_params)
            queue_buffer = cl.Buffer(self.context, self.mem_flags.READ_WRITE | self.mem_flags.COPY_HOST_PTR, hostbuf=queue)
            array_buffer = cl.Buffer(self.context, self.mem_flags.WRITE_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=local_array) #self.array)

            # run calculations
            self.program.henon(self.command_queue, queue.shape, None, queue_buffer, array_buffer,\
                                int_params_buffer, float_params_buffer)

            iter_count += plot_interval
             
            if not animation_running:                  
                # copy calculation results from buffer memory
                cl.enqueue_copy(self.command_queue, self.array, array_buffer).wait() 
                
                self.interval_flags.value = True                
                #print("[" + self.name + "] Sent signal to HenonUpdate")

                if first_run: # set drop_iter to zero after first calculation run
                    int_params = np.array([plot_interval,0,window_height,window_width],dtype=np.uint32)            
                    first_run = False
            else:
                if not first_run:
                    first_run = False
                    while not self.exit.is_set(): # wait until previous data was updated on screen
                        if self.interval_flags.value:
                            #print("[" + self.name + "] Waiting for signal from HenonUpdate")
                            sleep(0.01)
                        else:
                            break                
                
                # copy calculation results from buffer memory
                cl.enqueue_copy(self.command_queue, self.array, array_buffer).wait()

                self.interval_flags.value = True
                #print("[" + self.name + "] Sent signal to HenonUpdate")

                if (iter_count >= max_iter): # do not erase if last frame
                    break

                # erase image array for next animation frame
                #ctypes.memmove(self.array, empty_array, window_width*window_height)                             
                ctypes.memmove(local_array, empty_array, window_width*window_height)                 

                if hena_anim:
                    hena = np.round(hena + hena_increment,4)              

                if henb_anim:
                    henb = np.round(henb + henb_increment,4)
                
                float_params = np.array([hena,henb,xleft,ybottom,xratio,yratio],dtype=np.float64)

            # copy x,y values from buffer memory to re-use as queue
            cl.enqueue_copy(self.command_queue, queue, queue_buffer).wait()

            if (iter_count >= max_iter):
                break
        
        #delta = datetime.now() - start_time                       
        #print "[HenonCalc2] Workers have stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds"

        self.stop_signal.value = True
        self.quit()
        
class WorkerProcessOrbit(WorkerProcess):

    def run(self):
        self.name= "WorkerProcessOrbit"
        QtCore.QTimer.singleShot(0, self.run_calculation)
        self.exec_()

    def run_calculation(self):
        
        hena = self.settings['hena']
        henb = self.settings['henb']
        xleft = self.settings['xleft']
        ytop = self.settings['ytop']
        xright = self.settings['xright']
        ybottom = self.settings['ybottom']
        drop_iter = self.settings['drop_iter']
        orbit_parameter = self.settings['orbit_parameter'] 
        orbit_coordinate = self.settings['orbit_coordinate']
        plot_interval_orbit = self.settings['plot_interval_orbit']
        max_iter_orbit = self.settings['max_iter_orbit']
        animation_running = self.settings['animation_running']
        window_width = self.settings['window_width']
        window_height = self.settings['window_height']
        orbit_multiplier = pow(2,self.settings['orbit_multiplier'])      
    
        iter_count = 0

        xratio = window_width/(xright-xleft)
        yratio = window_height/(ytop-ybottom)

        if animation_running:
            hena_start = self.settings['hena_start']
            hena_stop = self.settings['hena_stop']        
            hena_increment = self.settings['hena_increment']
            hena_anim = self.settings['hena_anim']
            henb_start = self.settings['henb_start']
            henb_stop = self.settings['henb_stop']        
            henb_increment = self.settings['henb_increment']
            henb_anim = self.settings['henb_anim']
            max_iter_orbit = self.settings['max_iter_anim']
            #empty_array = mp.RawArray('H', 2*window_width*window_height) # needed for emptying self.array
            empty_array = mp.RawArray(ctypes.c_bool, window_width*window_height) # needed for emptying self.array
            first_run = True
            
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
            
        # random x,y values in (-0.1,0.1) range for each thread
        # one thread per pixel along screen width
        xx = ((self.randomizer.random(window_width*orbit_multiplier)-0.5)/5)     
        #xx = np.full(window_width,0.01)
        yy = ((self.randomizer.random(window_width*orbit_multiplier)-0.5)/5) * 1j           
        #yy = np.full(window_width,0.01j)
        queue = xx+yy
        
        local_array = mp.RawArray(ctypes.c_bool, window_width*window_height)
        #int_params = np.array([plot_interval_orbit,drop_iter,window_height,window_width,orbit_parameter,orbit_coordinate],dtype=np.uint32)
        int_params = np.array([plot_interval_orbit,drop_iter,window_height,window_width,orbit_parameter,orbit_coordinate,orbit_multiplier],dtype=np.uint32)        
        float_params = np.array([hena,henb,xleft,ybottom,xratio,yratio],dtype=np.float64)

        while not self.exit.is_set():
    
            # allocate memory for buffers and copy contents
            int_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=int_params)    
            float_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=float_params)
            queue_buffer = cl.Buffer(self.context, self.mem_flags.READ_WRITE | self.mem_flags.COPY_HOST_PTR, hostbuf=queue)
            array_buffer = cl.Buffer(self.context, self.mem_flags.WRITE_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=local_array) #self.array)

            # run calculations
            self.program.henon(self.command_queue, queue.shape, None, queue_buffer, array_buffer,\
                                int_params_buffer, float_params_buffer)

            iter_count += plot_interval_orbit
    
            if not animation_running:
                # copy calculation results from buffer memory
                cl.enqueue_copy(self.command_queue, self.array, array_buffer).wait() 
                
                self.interval_flags.value = True
            else:
                if not first_run:
                    first_run = False
                    while not self.exit.is_set(): # wait until previous data was updated on screen
                        if self.interval_flags.value:
                            #print("[" + self.name + "] Waiting for signal from HenonUpdate")
                            sleep(0.01)
                        else:
                            break
                    
                # copy calculation results from buffer memory
                cl.enqueue_copy(self.command_queue, self.array, array_buffer).wait()

                self.interval_flags.value = True
                #print("[" + self.name + "] Sent signal to HenonUpdate")
                
                if (iter_count >= max_iter_orbit): # do not erase if last frame
                    break

                # erase image array for next animation frame
                #ctypes.memmove(self.array, empty_array, window_width*window_height)                
                ctypes.memmove(local_array, empty_array, window_width*window_height)                             

                if orbit_parameter:
                    henb = np.round(henb + henb_increment,4)                  
                else:                    
                    hena = np.round(hena + hena_increment,4) 
                    
                float_params = np.array([hena,henb,xleft,ybottom,xratio,yratio],dtype=np.float64)

            # copy x,y values from buffer memory to re-use as queue
            cl.enqueue_copy(self.command_queue, queue, queue_buffer).wait()

            if (iter_count >= max_iter_orbit):
                break

        self.stop_signal.value = True
        self.quit()