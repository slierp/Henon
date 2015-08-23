# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
import pyopencl as cl
import numpy as np

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QObject.__init__(self)

class HenonCalc2(QtCore.QObject):
    # Starts up worker threads for Henon calculations and then waits for stop signal
    # Implementation uses OpenCL for multithreaded calculation

    def __init__(self, _window_representation, _params, _context, _command_queue, _mem_flags, _program):
        QtCore.QObject.__init__(self)
        
#        print "[HenonCalc2] Initialization" #DEBUG
        self.window_representation = _window_representation
        self.context = _context
        self.command_queue = _command_queue
        self.mem_flags = _mem_flags
        self.program = _program
        
        self.signal = Signal()
        self.interval_signal = Signal() # for HenonUpdate2
        self.stop_signal = Signal() # for HenonUpdate2
        self.quit_signal = Signal()
        
        self.xleft = _params['xleft']
        self.ytop = _params['ytop']
        self.xright = _params['xright']
        self.ybottom = _params['ybottom']
        self.window_width = _params['window_width']
        self.window_height = _params['window_height']
        self.thread_count = _params['thread_count']
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

        maxiter=100       
        thread_count = 100
        # random x,y values in (-0.1,0.1) range for each GPU thread
        # opencl-float2 does not exist in current pyopencl version, but complex does
        # so we'll use that for now to pass along x,y values
        xx = ((np.random.random_sample(thread_count)-0.5)/5)
        yy = ((np.random.random_sample(thread_count)-0.5)/5) * 1j
        queue = np.ravel(xx+yy[:, np.newaxis]).astype(np.complex64)

        # allocate memory for buffers and copy queue into buffer
        queue_buffer = cl.Buffer(self.context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR, hostbuf=queue)
        cl_arr_buffer = cl.Buffer(self.context, self.mem_flags.WRITE_ONLY, self.cl_arr.nbytes)
        
        # fill window memory buffer with zeroes
        cl.enqueue_copy(self.command_queue, cl_arr_buffer, self.cl_arr).wait()

        # run GPU calculations
        self.program.henon(self.command_queue, queue.shape, None, queue_buffer, np.uint16(maxiter),\
                           cl_arr_buffer, np.uint16(self.drop_iter), np.uint16(self.window_height),\
                           np.uint16(self.window_width))
    
        # copy calculation results from buffer memory
        cl.enqueue_copy(self.command_queue, self.cl_arr, cl_arr_buffer).wait()

        #self.interval_signal.sig.emit() # sends message to HenonUpdate to do update
        self.stop_signal.sig.emit() # sends message to HenonUpdate to do stop
        self.quit_signal.sig.emit() # stop thread
        
#        print "[HenonCalc2] Workers finished" #DEBUG
                    
    def stop(self):
                      
#        print "[HenonCalc2] Received stop signal" #DEBUG
        self.received_stop_signal = True