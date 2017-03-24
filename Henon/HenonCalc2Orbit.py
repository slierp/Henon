# -*- coding: utf-8 -*-
from PyQt5 import QtCore
import pyopencl as cl
import multiprocessing as mp # for thread-safe memory sharing
import numpy as np

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QObject.__init__(self)

class HenonCalc2Orbit(QtCore.QObject):
    # Starts up worker threads for Henon calculations and then waits for stop signal
    # Implementation uses OpenCL for multithreaded calculation

    def __init__(self, _params, _context, _command_queue, _mem_flags, _program):
        QtCore.QObject.__init__(self)
        
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
        self.max_iter_orbit = _params['max_iter_orbit']
        self.plot_interval_orbit = _params['plot_interval_orbit']        
        self.drop_iter = _params['drop_iter']
        self.orbit_parameter = _params['orbit_parameter'] 
        self.orbit_coordinate = _params['orbit_coordinate']

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

        iter_count = 0

        xratio = self.window_width/(self.xright-self.xleft)
        yratio = self.window_height/(self.ytop-self.ybottom)
            
        # random x,y values in (-0.1,0.1) range for each thread
        # one thread per pixel along screen width
        xx = ((np.random.random_sample(self.window_width)-0.5)/5)
        yy = ((np.random.random_sample(self.window_width)-0.5)/5) * 1j
        queue = xx+yy

        int_params = np.array([self.plot_interval_orbit,self.drop_iter,self.window_height,self.window_width,self.orbit_parameter,self.orbit_coordinate],dtype=np.uint32)
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

            iter_count += self.plot_interval_orbit
                           
            # copy calculation results from buffer memory
            cl.enqueue_copy(self.command_queue, self.cl_arr, cl_arr_buffer).wait() 
            
            self.interval_flag.value = True

            # copy x,y values from buffer memory to re-use as queue
            cl.enqueue_copy(self.command_queue, queue, queue_buffer).wait()

            if (iter_count >= self.max_iter_orbit):
                break

        self.stop_signal.value = True 
        self.quit_signal.sig.emit() # stop thread
                    
    def stop(self):
        self.received_stop_signal = True