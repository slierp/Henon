# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
import pyopencl as cl
#from datetime import datetime #DEBUG
import numpy as np
from random import uniform

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
        
        self.signal = Signal()
        self.interval_signal = Signal() # for HenonUpdate2
        self.stop_signal = Signal() # for HenonUpdate2
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

        self.xratio = self.window_width/(self.xright-self.xleft)
        self.yratio = self.window_height/(self.ytop-self.ybottom)

        self.interval_flag = False # Have worker tell us when a piece work is finished

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

        # random x,y values in (-0.1,0.1) range for each GPU thread
        # opencl-float2 does not exist in current pyopencl version, but complex does
        # so we'll use that for now to pass along x,y values
        xx = ((np.random.random_sample(self.global_work_size)-0.5)/5)
        yy = ((np.random.random_sample(self.global_work_size)-0.5)/5) * 1j
        queue = xx+yy
        first_run = True

        int_params = np.array([self.plot_interval,self.drop_iter,self.window_height,self.window_width],dtype=np.uint32) #np.uint64
        float_params = np.array([self.hena,self.henb,self.xleft,self.ybottom,xratio,yratio],dtype=np.float64)

        while True:
    
            # allocate memory for buffers and copy contents
            int_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=int_params)    
            float_params_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=float_params)
            queue_buffer = cl.Buffer(self.context, self.mem_flags.READ_WRITE | self.mem_flags.COPY_HOST_PTR, hostbuf=queue)
            cl_arr_buffer = cl.Buffer(self.context, self.mem_flags.WRITE_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=self.cl_arr)

            # run GPU calculations
            self.program.henon(self.command_queue, queue.shape, None, queue_buffer, cl_arr_buffer,\
                                int_params_buffer, float_params_buffer)
                                
            # copy calculation results from buffer memory
            cl.enqueue_copy(self.command_queue, self.cl_arr, cl_arr_buffer).wait()

#            print "[HenonCalc2] Pixels in copied array: " + str(np.count_nonzero(self.cl_arr)) #DEBUG

            # copy x,y values from buffer memory to re-use as queue
            cl.enqueue_copy(self.command_queue, queue, queue_buffer).wait()

            if first_run: # set drop_iter to zero after first calculation run
                int_params = np.array([self.plot_interval,0,self.window_height,self.window_width],dtype=np.uint32)            
                first_run = False                
            
            self.interval_signal.sig.emit() # sends message to HenonUpdate to do update
            
            iter_count += self.plot_interval

            if (iter_count >= self.max_iter) or self.received_stop_signal:
                break

        self.stop_signal.sig.emit() # sends message to HenonUpdate to stop
        self.quit_signal.sig.emit() # stop thread
        
#        delta = datetime.now() - start_time #DEBUG                        
#        print "[HenonCalc2] Workers have stopped after " + str(round(delta.seconds + delta.microseconds/1e6,2)) + " seconds" #DEBUG 
                    
    def stop(self):
                      
#        print "[HenonCalc2] Received stop signal" #DEBUG
        self.received_stop_signal = True