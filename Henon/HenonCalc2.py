# -*- coding: utf-8 -*-
from PyQt5 import QtCore
import pyopencl as cl
import multiprocessing as mp # for thread-safe memory sharing
#from datetime import datetime #DEBUG
import numpy as np
from time import sleep

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QObject.__init__(self)

class HenonCalc2(QtCore.QObject):
    # Starts up worker threads for Henon calculations and then waits for stop signal
    # Implementation uses OpenCL for multithreaded calculation

    def __init__(self, _params, _context, _command_queue, _mem_flags, _program):
        QtCore.QObject.__init__(self)
        
#        print "[HenonCalc2] Initialization" #DEBUG
        self.context = _context
        self.command_queue = _command_queue
        self.mem_flags = _mem_flags
        self.program = _program

        self.quit_signal = Signal()
        
        self.hena = _params['hena']
        self.henb = _params['henb']
        self.xleft = _params['xleft']
        self.ytop = _params['ytop']
        self.xright = _params['xright']
        self.ybottom = _params['ybottom']
        self.window_width = _params['window_width']
        self.window_height = _params['window_height']
        self.global_work_size = _params['global_work_size']
        self.max_iter = _params['max_iter']
        self.plot_interval = _params['plot_interval']
        self.drop_iter = _params['drop_iter']
        self.hena_mid = _params['hena_mid']
        self.hena_range = _params['hena_range']        
        self.hena_increment = _params['hena_increment']
        self.hena_anim = _params['hena_anim']
        self.henb_mid = _params['henb_mid']
        self.henb_range = _params['henb_range']        
        self.henb_increment = _params['henb_increment']
        self.henb_anim = _params['henb_anim']
        self.max_iter_anim = _params['max_iter_anim']
        self.plot_interval_anim = _params['plot_interval_anim']        
        self.animation_running = _params['animation_running']

        self.xratio = self.window_width/(self.xright-self.xleft)
        self.yratio = self.window_height/(self.ytop-self.ybottom)

        self.interval_flag = mp.Value('b', False) # Boolean for sending interval signal
        self.stop_signal = mp.Value('b', False) # Boolean for sending stop signal

        # empty array that will be copied to OpenCL kernel for processing
        self.cl_arr = np.zeros((self.window_height*self.window_width), dtype=np.uint16)
        
        self.received_stop_signal = False            
        self.workers_started = False     
                     
    def run(self):

        if (self.workers_started): # fix strange problem where run command is started twice by QThread
            return

        self.workers_started = True

#        print "[HenonCalc2] Starting workers" #DEBUG

        # ensures dtype and c-type contiguous, but does not seem to be necessary
        #self.cl_arr = np.require(self.cl_arr, np.uint16, 'C') 

#        start_time = datetime.now() #DEBUG

        iter_count = 0

        xratio = self.window_width/(self.xright-self.xleft)
        yratio = self.window_height/(self.ytop-self.ybottom)

        if self.animation_running:
            hena_max = round(self.hena_mid + 0.5*self.hena_range,3)
            henb_max = round(self.henb_mid + 0.5*self.henb_range,3)
            self.plot_interval = self.plot_interval_anim
            self.max_iter = self.max_iter_anim
            
        # random x,y values in (-0.1,0.1) range for each GPU thread
        # opencl-float2 does not exist in current pyopencl version, but complex does
        # so we'll use that for now to pass along x,y values
        xx = ((np.random.random_sample(self.global_work_size)-0.5)/5)
        yy = ((np.random.random_sample(self.global_work_size)-0.5)/5) * 1j
        queue = xx+yy
        first_run = True

        int_params = np.array([self.plot_interval,self.drop_iter,self.window_height,self.window_width],dtype=np.uint32) #np.uint64
        float_params = np.array([self.hena,self.henb,self.xleft,self.ybottom,xratio,yratio],dtype=np.float64)

        while not self.received_stop_signal:
    
            # allocate memory for buffers and copy contents
            int_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=int_params)    
            float_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=float_params)
            queue_buffer = cl.Buffer(self.context, self.mem_flags.READ_WRITE | self.mem_flags.COPY_HOST_PTR, hostbuf=queue)
            cl_arr_buffer = cl.Buffer(self.context, self.mem_flags.WRITE_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=self.cl_arr)

            # run calculations
            self.program.henon(self.command_queue, queue.shape, None, queue_buffer, cl_arr_buffer,\
                                int_params_buffer, float_params_buffer)

            iter_count += self.plot_interval
             
            if not self.animation_running:                  
                # copy calculation results from buffer memory
                cl.enqueue_copy(self.command_queue, self.cl_arr, cl_arr_buffer).wait() 
                
                self.interval_flag.value = True                
#                print "[HenonCalc2] Sent signal to HenonUpdate" #DEBUG

                if first_run: # set drop_iter to zero after first calculation run
                    int_params = np.array([self.plot_interval,0,self.window_height,self.window_width],dtype=np.uint32)            
                    first_run = False
            else:
                # copy calculation results from buffer memory
                cl.enqueue_copy(self.command_queue, self.cl_arr, cl_arr_buffer).wait()

                self.interval_flag.value = True
#                print "[HenonCalc2] Sent signal to HenonUpdate" #DEBUG
                
                while not self.received_stop_signal: # wait until previous data was updated on screen
                    if self.interval_flag.value:
#                        print "[HenonCalc2] Waiting for signal from HenonUpdate" #DEBUG
                        sleep(0.01)
                    else:
                        break

                if (iter_count >= self.max_iter): # do not erase if last frame
                    break
                    
                self.cl_arr[:] = 0
                
                if self.hena_anim:
                    new_hena = round(self.hena + self.hena_increment,3)
                    if new_hena <= hena_max:
                        self.hena = new_hena

                if self.henb_anim:
                    new_henb = round(self.henb + self.henb_increment,3)
                    if new_henb <= henb_max:
                       self.henb = new_henb                
                
                float_params = np.array([self.hena,self.henb,self.xleft,self.ybottom,xratio,yratio],dtype=np.float64)

            # copy x,y values from buffer memory to re-use as queue
            cl.enqueue_copy(self.command_queue, queue, queue_buffer).wait()

            if (iter_count >= self.max_iter):
                break

        self.stop_signal.value = True 
        self.quit_signal.sig.emit() # stop thread
        
#        delta = datetime.now() - start_time #DEBUG                        
#        print "[HenonCalc2] Workers have stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG 
                    
    def stop(self):                      
#        print "[HenonCalc2] Received stop signal" #DEBUG
        self.received_stop_signal = True