# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui
from sys import platform as _platform
from multiprocessing import cpu_count

class HenonSettings(QtGui.QDialog):
    def __init__(self, _parent):
        super(QtGui.QDialog, self).__init__(_parent)
        
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
        description = QtGui.QLabel("Parameter 'a'")
        self.hena = QtGui.QDoubleSpinBox()
        self.hena.setAccelerated(True)
        self.hena.setMaximum(3.0)
        self.hena.setMinimum(-3.0)
        self.hena.setValue(self.parent.hena)
        self.hena.setSingleStep(0.01)
        self.hena.setToolTip("H\xe9non parameter 'a'")             
        hbox.addWidget(self.hena) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)          

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Parameter 'b'")
        self.henb = QtGui.QDoubleSpinBox()
        self.henb.setAccelerated(True)
        self.henb.setMaximum(3.0)
        self.henb.setMinimum(-3.0)
        self.henb.setValue(self.parent.henb)
        self.henb.setSingleStep(0.01)        
        self.henb.setToolTip("H\xe9non parameter 'b'")             
        hbox.addWidget(self.henb) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()       
        spec = QtGui.QLabel("<b>Calculation settings<b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Thread count")
        self.thread_count = QtGui.QSpinBox()
        self.thread_count.setAccelerated(True)
        self.thread_count.setMaximum(cpu_count())
        self.thread_count.setMinimum(1)
        self.thread_count.setValue(self.parent.thread_count)
        self.thread_count.setSingleStep(1)
        self.thread_count.setToolTip("Thread count")             
        hbox.addWidget(self.thread_count) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Max iterations")
        self.max_iter = QtGui.QSpinBox()
        self.max_iter.setAccelerated(True)
        self.max_iter.setMaximum(999999999)
        self.max_iter.setMinimum(1)
        self.max_iter.setValue(self.parent.max_iter)
        self.max_iter.setSingleStep(1000)
        self.max_iter.setToolTip("Max iterations")
        self.max_iter.setDisabled(self.parent.iter_auto_mode)
        hbox.addWidget(self.max_iter) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Plot interval")
        self.plot_interval = QtGui.QSpinBox()
        self.plot_interval.setAccelerated(True)
        self.plot_interval.setMaximum(999999999)
        self.plot_interval.setMinimum(1)
        self.plot_interval.setValue(self.parent.plot_interval)
        self.plot_interval.setSingleStep(1000)
        self.plot_interval.setToolTip("Plot interval")
        self.plot_interval.setDisabled(self.parent.iter_auto_mode)
        hbox.addWidget(self.plot_interval) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)         

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Auto-mode")
        self.iter_auto_mode = QtGui.QCheckBox()
        self.iter_auto_mode.setChecked(self.parent.iter_auto_mode)
        self.iter_auto_mode.mouseReleaseEvent = self.switch_iter_auto_mode
        self.iter_auto_mode.setToolTip("Auto-mode")
        description.mouseReleaseEvent = self.switch_iter_auto_mode
        hbox.addWidget(self.iter_auto_mode)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()           
        spec = QtGui.QLabel("<b>Animation settings</b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox.addLayout(hbox)  
                
        vbox_anim_left = QtGui.QVBoxLayout()
        vbox_anim_right = QtGui.QVBoxLayout()
        
        vbox_anim_left.addWidget(QtGui.QLabel("Parameter 'a'"))
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Mid-point")
        self.hena_mid = QtGui.QDoubleSpinBox()
        self.hena_mid.setAccelerated(True)
        self.hena_mid.setMaximum(3.0)
        self.hena_mid.setMinimum(-3.0)
        self.hena_mid.setValue(self.parent.hena_mid)
        self.hena_mid.setSingleStep(0.01)
        self.hena_mid.setToolTip("H\xe9non parameter 'a' mid-point")             
        hbox.addWidget(self.hena_mid) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Range")
        self.hena_range = QtGui.QDoubleSpinBox()
        self.hena_range.setAccelerated(True)
        self.hena_range.setMaximum(3.0)
        self.hena_range.setMinimum(0.01)
        self.hena_range.setValue(self.parent.hena_range)
        self.hena_range.setSingleStep(0.01)
        self.hena_range.setToolTip("H\xe9non parameter 'a' range")             
        hbox.addWidget(self.hena_range) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Increment")
        self.hena_increment = QtGui.QDoubleSpinBox()
        self.hena_increment.setAccelerated(True)
        self.hena_increment.setDecimals(3)
        self.hena_increment.setMaximum(0.5)
        self.hena_increment.setMinimum(0.001)
        self.hena_increment.setValue(self.parent.hena_increment)
        self.hena_increment.setSingleStep(0.001)
        self.hena_increment.setToolTip("H\xe9non parameter 'a' increment")             
        hbox.addWidget(self.hena_increment) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Animate")
        self.hena_anim = QtGui.QCheckBox()
        self.hena_anim.setChecked(self.parent.hena_anim)
        self.hena_anim.setToolTip("Animate parameter 'a'")
        description.mouseReleaseEvent = self.switch_hena_anim
        hbox.addWidget(self.hena_anim)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox)        

        vbox_anim_right.addWidget(QtGui.QLabel("Parameter 'b'"))

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Mid-point")
        self.henb_mid = QtGui.QDoubleSpinBox()
        self.henb_mid.setAccelerated(True)
        self.henb_mid.setMaximum(3.0)
        self.henb_mid.setMinimum(-3.0)
        self.henb_mid.setValue(self.parent.henb_mid)
        self.henb_mid.setSingleStep(0.01)
        self.henb_mid.setToolTip("H\xe9non parameter 'b' mid-point")             
        hbox.addWidget(self.henb_mid) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Range")
        self.henb_range = QtGui.QDoubleSpinBox()
        self.henb_range.setAccelerated(True)
        self.henb_range.setMaximum(3.0)
        self.henb_range.setMinimum(-3.0)
        self.henb_range.setValue(self.parent.henb_range)
        self.henb_range.setSingleStep(0.01)
        self.henb_range.setToolTip("H\xe9non parameter 'b' range")             
        hbox.addWidget(self.henb_range) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Increment")
        self.henb_increment = QtGui.QDoubleSpinBox()
        self.henb_increment.setAccelerated(True)
        self.henb_increment.setDecimals(3)
        self.henb_increment.setMaximum(0.5)
        self.henb_increment.setMinimum(0.001)
        self.henb_increment.setValue(self.parent.henb_increment)
        self.henb_increment.setSingleStep(0.001)
        self.henb_increment.setToolTip("H\xe9non parameter 'b' increment")             
        hbox.addWidget(self.henb_increment) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Animate")
        self.henb_anim = QtGui.QCheckBox()
        self.henb_anim.setChecked(self.parent.henb_anim)
        self.henb_anim.setToolTip("Animate parameter 'b'")
        description.mouseReleaseEvent = self.switch_henb_anim
        hbox.addWidget(self.henb_anim)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox_anim_left)
        hbox.addSpacing(10)      
        hbox.addLayout(vbox_anim_right)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

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
        self.setMinimumWidth(512)

    def switch_iter_auto_mode(self, event):
        # function for making QLabel near checkbox clickable
        self.iter_auto_mode.setChecked(not self.iter_auto_mode.isChecked())
        self.max_iter.setDisabled(self.iter_auto_mode.isChecked())
        self.plot_interval.setDisabled(self.iter_auto_mode.isChecked())
        
    def switch_hena_anim(self, event):
        # function for making QLabel near checkbox clickable
        self.hena_anim.setChecked(not self.hena_anim.isChecked())

    def switch_henb_anim(self, event):
        # function for making QLabel near checkbox clickable
        self.henb_anim.setChecked(not self.henb_anim.isChecked())

    def read(self):

        self.parent.hena = self.hena.value()
        self.parent.henb = self.henb.value()
        
        if not self.iter_auto_mode.isChecked():
            # only read it if auto mode is turned off
            self.parent.max_iter = self.max_iter.value()
            self.parent.plot_interval = self.plot_interval.value()
        
        self.parent.iter_auto_mode = self.iter_auto_mode.isChecked()
        self.parent.thread_count = self.thread_count.value()
        
        self.parent.hena_mid = self.hena_mid.value()
        self.parent.hena_range = self.hena_range.value()
        self.parent.hena_increment = self.hena_increment.value()
        self.parent.hena_anim = self.hena_anim.isChecked()
        
        self.parent.henb_mid = self.henb_mid.value()
        self.parent.henb_range = self.henb_range.value()
        self.parent.henb_increment = self.henb_increment.value()
        self.parent.henb_anim = self.henb_anim.isChecked()
        
        self.parent.statusBar().showMessage(self.tr("Parameter settings updated"), 1000)
        self.accept()