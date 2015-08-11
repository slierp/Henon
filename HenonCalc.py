# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from random import uniform
from multiprocessing import Process, Array, Value, cpu_count
import numpy as np
from math import log, isinf, isnan

class HenonCalc(QtCore.QObject):

    def __init__(self, _window_representation, _params):
        QtCore.QObject.__init__(self)
        
        self.window_representation = _window_representation
        self.params = _params
        
        self.xleft = self.params['xleft']
        self.ytop = self.params['ytop']
        self.xright = self.params['xright']
        self.ybottom = self.params['ybottom']
        self.hena = self.params['hena']
        self.henb = self.params['henb']

        self.window_width = len(self.window_representation)
        self.window_height = len(self.window_representation[0])
        self.xratio = self.window_width/(self.xright-self.xleft) # ratio screenwidth to valuewidth
        self.yratio = self.window_height/(self.ytop-self.ybottom)

        self.cpu_number = cpu_count() # determines number of worker threads

        # distribute work into separate tasks in order to enable GUI responsiveness
        # for smaller areas we need more tasks and correspondingly lower thresholds
        area = (self.xright - self.xleft) * (self.ytop - self.ybottom)
        
        # heavily optimized formula for calculating required number of iterations
        # as a function of the number of screen pixels and the x,y space represented
        # by it
        self.iter_threshold = int(2 * abs(int(log(area)**2/log(2.4)**2)) *  self.window_width * self.window_height / self.cpu_number) 
        
#        print "Iteration threshold: " + str(self.iter_threshold) #DEBUG      
                     
    def run(self):

        # shared array containing booleans for each pixel
        # content is a flattened array so it needs to be deflattened later on
        self.mp_arr = Array('b', self.window_width*self.window_height)

        self.stop_signal = Value('b', False) # Boolean for sending stop signal

        self.worker_list = []
        for i in range(self.cpu_number):
            self.worker_list.append(Process(target=self.worker, args=([i, self.mp_arr, self.stop_signal]))) # independent process
            self.worker_list[i].start()                 

    def read_array(self):                    
            
#        print "Copying results and sending screen re-draw signal" #DEBUG
       
        #with self.mp_arr.get_lock():
        arr = np.frombuffer(self.mp_arr.get_obj(), dtype=np.bool) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width)) # deflatten array
        arr = arr.T # height/width are switched around by default
        self.window_representation[arr == True] = 0xFFFFFFFF # add newly calculated pixels            

#        print "Pixels in screen window: " + str(self.window_width*self.window_height) #DEBUG
#        print "Pixels in copied array: " + str(np.count_nonzero(arr)) #DEBUG 
#        print "Pixels in window array: " + str(np.count_nonzero(self.window_representation)) #DEBUG
        
    def worker(self, run_number, array, stop_signal):      

#        print "-- Worker " + str(run_number) + " has started --" #DEBUG
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        for i in range(10): # prevent drawing first iterations
            henxtemp = 1-self.hena*(henx**2) + heny
            heny = self.henb * henx
            henx = henxtemp

        iter_count = 0

        while True:             
        
            henxtemp = 1-(self.hena*henx*henx) + heny
            heny = self.henb * henx
            henx = henxtemp
            x_draw = (henx-self.xleft) * self.xratio
            y_draw = (heny-self.ybottom) * self.yratio
            
            if (not isinf(x_draw)) and (not isinf(y_draw)) and (not isnan(x_draw)) and (not isnan(y_draw)):                
                # do not convert to int unless the number is finite
                if (0 < int(x_draw) < self.window_width) and (0 < int(y_draw) < self.window_height):
                    # draw pixel if it is inside the current display area
                    array[(int(y_draw)*self.window_width) + int(x_draw)] = True
                                        
            iter_count += 1
            
            if (iter_count >= self.iter_threshold) or (stop_signal.value):
                 break
                        
#        print "-- Worker " + str(run_number) + " has stopped --" #DEBUG
                    
    def stop(self):
              
        # send signal to stop workers
        self.stop_signal.value = True