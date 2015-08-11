# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui
from sys import platform as _platform

class HenonSettings(QtGui.QDialog):
    def __init__(self, _parent):
        super(QtGui.QDialog, self).__init__(_parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = _parent
        
        self.setWindowTitle(self.tr("Available settings"))
        vbox = QtGui.QVBoxLayout() # vbox for all elements in scroll area

        henon_map = "<b>H\xe9non map</b><br>"
        henon_map += "x[n+1] = 1 - a * x[n]^2 + y[n]<br>"
        henon_map += "y[n+1] = b * x[n]"

        hbox = QtGui.QHBoxLayout()           
        spec = QtGui.QLabel(henon_map)
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()       
        spec = QtGui.QLabel("<b>H\xe9non parameter settings<b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox.addLayout(hbox)        
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Parameter a")
        self.hena_double = QtGui.QDoubleSpinBox()
        self.hena_double.setAccelerated(True)
        self.hena_double.setMaximum(3.0)
        self.hena_double.setMinimum(-3.0)
        self.hena_double.setValue(self.parent.hena)
        self.hena_double.setSingleStep(0.01)
        self.hena_double.setToolTip("H\xe9non parameter a")             
        hbox.addWidget(self.hena_double) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)          

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Parameter b")
        self.henb_double = QtGui.QDoubleSpinBox()
        self.henb_double.setAccelerated(True)
        self.henb_double.setMaximum(3.0)
        self.henb_double.setMinimum(-3.0)
        self.henb_double.setValue(self.parent.henb)
        self.henb_double.setSingleStep(0.01)        
        self.henb_double.setToolTip("H\xe9non parameter b")             
        hbox.addWidget(self.henb_double) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox) 

        """
        hbox = QtGui.QHBoxLayout()           
        spec = QtGui.QLabel("<b>Animation settings</b><br>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox.addLayout(hbox)  
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Animation range")
        hena_boolean = QtGui.QCheckBox()
        hena_boolean.setChecked(True)
        #hena_boolean.setObjectName(i)
        #if i + "_desc" in curr_params:
        #    self.booleans[-1].setToolTip(curr_params[i + "_desc"])               
        hbox.addWidget(hena_boolean)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)
        """

        ### Widget for scrollable area ###        
        groupbox = QtGui.QGroupBox()
        groupbox.setLayout(vbox)
        
        scroll = QtGui.QScrollArea()       
        scroll.setWidget(groupbox)
        scroll.setWidgetResizable(True)
        
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(scroll)

        ### Buttonbox for ok or cancel ###
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtGui.QBoxLayout.RightToLeft)

        layout.addWidget(buttonbox)
        self.setMinimumWidth(1024)

    def read(self):

        self.parent.hena = self.hena_double.value()
        self.parent.henb = self.henb_double.value()
        
        self.parent.statusBar().showMessage(self.tr("Parameter settings updated"), 1000)
        self.accept()