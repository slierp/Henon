# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from time import sleep

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

class HenonUpdate(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)
        
        self.signal = Signal()
                
    def run(self):
        while True:
            self.signal.sig.emit()
            sleep(0.2)