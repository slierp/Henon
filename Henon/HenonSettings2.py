# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class HenonSettings2(QtWidgets.QDialog):
    # Generates a settings dialog    
    
    def __init__(self, _parent):
        super(QtWidgets.QDialog, self).__init__(_parent)
        
        self.parent = _parent
        
        self.setWindowTitle(self.tr("Settings"))
        
        ### Tab general ###

        group_henon_parameter = QtWidgets.QGroupBox("Scale of x and y axes")
        vbox = QtWidgets.QVBoxLayout()       

        if not self.parent.orbit_mode:
            xleft_str = "lowest x value on x-axis"
            xright_str = "highest x value on x-axis"
            xleft_min = xright_min = -10
            xleft_max = xright_max = 10            
            ybottom_str = "lowest y value on y-axis"
            ytop_str = "highest y value on y-axis"

        else:            
            if self.parent.orbit_parameter: # parameter a
                xleft_min = xright_min = -4
                xleft_max = xright_max = 4           
                xleft_str = "lowest 'a' value on x-axis"
                xright_str = "highest 'a' value on x-axis"
            else:
                xleft_min = xright_min = -2
                xleft_max = xright_max = 2                
                xleft_str = "lowest 'b' value on x-axis"
                xright_str = "highest 'b' value on x-axis"
        
            if self.parent.orbit_coordinate: # y-coordinate
                ybottom_str = "lowest y value on y-axis"
                ytop_str = "highest y value on y-axis"
            else:
                ybottom_str = "lowest x value on y-axis"
                ytop_str = "highest x value on y-axis"

        ybottom_min = ytop_min = -10
        ybottom_max = ytop_max = 10       
            
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel(xleft_str)
        self.xleft = QtWidgets.QDoubleSpinBox()
        self.xleft.setDecimals(4)
        self.xleft.setAccelerated(True)
        self.xleft.setMaximum(xleft_max)
        self.xleft.setMinimum(xleft_min)
        self.xleft.setValue(self.parent.xleft)
        self.xleft.setSingleStep(0.01)          
        hbox.addWidget(self.xleft) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)          

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel(xright_str)
        self.xright = QtWidgets.QDoubleSpinBox()
        self.xright.setDecimals(4)
        self.xright.setAccelerated(True)
        self.xright.setMaximum(xright_max)
        self.xright.setMinimum(xright_min)
        self.xright.setValue(self.parent.xright)
        self.xright.setSingleStep(0.01)
        self.xright.valueChanged.connect(self.xrightchange)          
        hbox.addWidget(self.xright) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel(ybottom_str)
        self.ybottom = QtWidgets.QDoubleSpinBox()
        self.ybottom.setDecimals(4)
        self.ybottom.setAccelerated(True)
        self.ybottom.setMaximum(ybottom_max)
        self.ybottom.setMinimum(ybottom_min)
        self.ybottom.setValue(self.parent.ybottom)
        self.ybottom.setSingleStep(0.01)          
        hbox.addWidget(self.ybottom) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel(ytop_str)
        self.ytop = QtWidgets.QDoubleSpinBox()
        self.ytop.setDecimals(4)
        self.ytop.setAccelerated(True)
        self.ytop.setMaximum(ytop_max)
        self.ytop.setMinimum(ytop_min)
        self.ytop.setValue(self.parent.ytop)
        self.ytop.setSingleStep(0.01)
        self.ytop.valueChanged.connect(self.ytopchange)          
        hbox.addWidget(self.ytop) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)        

        group_henon_parameter.setLayout(vbox)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(group_henon_parameter)

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft)

        layout.addWidget(buttonbox)
        self.setMinimumWidth(512)

    def xrightchange(self, event):
        if self.xright.value() < (self.xleft.value()+0.01):
            self.xright.setValue(self.xleft.value()+0.01)

    def ytopchange(self, event):
        if self.ytop.value() < (self.ybottom.value()+0.01):
            self.ytop.setValue(self.ybottom.value()+0.01)

    def read(self):

        self.parent.xleft = self.xleft.value()
        self.parent.xright = self.xright.value()
        self.parent.ybottom = self.ybottom.value()
        self.parent.ytop = self.ytop.value()
        
        # trigger resize event to force implementation of super-sampling setting
        self.parent.Henon_widget.trigger_resizeEvent()

        self.parent.statusBar().showMessage(self.tr("x,y scale settings updated"), 1000)
        self.accept()