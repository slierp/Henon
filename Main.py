# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui
from MainGui import MainGui
import sys
import HenonResources
import multiprocessing as mp

if __name__ == "__main__":
    mp.freeze_support() # needed for Windows support
    app = QtGui.QApplication.instance()
    if not app:
        # if no other PyQt program is running (such as the IDE) create a new instance
        app = QtGui.QApplication(sys.argv)       
        
    app.setStyle("windows")
    
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print "Henon explorer"
            print "Options:"
            print "--h, --help  : Help message"
            exit()
        
    window = MainGui()
    window.show()
    app.exec_()
