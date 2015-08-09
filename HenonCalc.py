# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from time import sleep
from random import uniform
from multiprocessing import Process, Array, cpu_count
import numpy as np
import numpy.ma as ma

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

class HenonCalc(QtCore.QObject):

    def __init__(self, _parent, _window_representation, _params):
        QtCore.QObject.__init__(self)
        
        self.parent = _parent
        self.window_representation = _window_representation
        self.params = _params
        self.stop_signal = False
        self.signal = Signal()
        
        self.xleft = self.params['xleft']
        self.ytop = self.params['ytop']
        self.xright = self.params['xright']
        self.ybottom = self.params['ybottom']
        self.hena = self.params['hena']
        self.henb = self.params['henb']

        self.fast_calc = self.params['fast_calc']
        self.window_width = len(self.window_representation)
        self.window_height = len(self.window_representation[0])
        self.xratio = self.window_width/(self.xright-self.xleft) # ratio screenwidth to valuewidth
        self.yratio = self.window_height/(self.ytop-self.ybottom)        
        self.drawn_pixels = 0

    @QtCore.pyqtSlot()               
    def run(self):        
        
        self.parent.statusBar().showMessage(self.tr("Calculating..."))        

        mp_arr = Array('b', self.window_width*self.window_height) # shared array containing booleans for each pixel

        process_list = []
        for i in range(cpu_count()):
            process_list.append(Process(target=self.calc, args=([mp_arr]))) # independent process
            process_list[i].start()
        
        for i in range(cpu_count()): # finish all calculations before continuing
            process_list[i].join()
        
        arr = np.frombuffer(mp_arr.get_obj(), dtype=np.bool) # get calculation result
        arr = arr.reshape((self.window_height,self.window_width))
        arr = arr.T
        self.window_representation[arr == True] = 0xFFFFFFFF # add newly calculated pixels

        self.parent.statusBar().showMessage(self.tr("Ready"))
        
    def calc(self,array):
        
        henx = uniform(-0.1,0.1) # generate random starting points
        heny = uniform(-0.1,0.1)

        for i in range(10): # prevent drawing first iterations
            henxtemp = 1-(self.hena*henx*henx) + heny
            heny = self.henb * henx
            henx = henxtemp

        max_pixels = int(0.1 * self.window_width * self.window_height / cpu_count())

        while True:
                    
            if self.stop_signal:
                break
        
            henxtemp = 1-(self.hena*henx*henx) + heny
            heny = self.henb * henx
            henx = henxtemp
            x_draw = int((henx-self.xleft) * self.xratio)
            y_draw = int((heny-self.ybottom) * self.yratio)
            
            if (0 < x_draw < self.window_width) and (0 < y_draw < self.window_height):
                array[(y_draw*self.window_width) + x_draw] = True                
                self.drawn_pixels += 1
                
                if self.drawn_pixels >= max_pixels:
                    break                
        