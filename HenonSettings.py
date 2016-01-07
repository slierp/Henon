# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui, QtCore
from sys import platform as _platform
from multiprocessing import cpu_count

try: # check if PyOpenCL is present as it is optional
    import pyopencl as cl
except ImportError:
    pass

class HenonSettings(QtGui.QDialog):
    # Generates a settings dialog    
    
    def __init__(self, _parent):
        super(QtGui.QDialog, self).__init__(_parent)
        
        self.parent = _parent
        
        self.setWindowTitle(self.tr("Settings"))

        tabwidget = QtGui.QTabWidget()
        
        ### Tab general ###
        vbox_tab_general = QtGui.QVBoxLayout() 

        hbox = QtGui.QHBoxLayout()       
        spec = QtGui.QLabel("<b>H\xe9non parameter settings<b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox_tab_general.addLayout(hbox)        
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Parameter 'a'")
        self.hena = QtGui.QDoubleSpinBox()
        self.hena.setDecimals(3)
        self.hena.setAccelerated(True)
        self.hena.setMaximum(3.0)
        self.hena.setMinimum(-3.0)
        self.hena.setValue(self.parent.hena)
        self.hena.setSingleStep(0.01)          
        hbox.addWidget(self.hena) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox_tab_general.addLayout(hbox)          

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Parameter 'b'")
        self.henb = QtGui.QDoubleSpinBox()
        self.henb.setDecimals(3)
        self.henb.setAccelerated(True)
        self.henb.setMaximum(3.0)
        self.henb.setMinimum(-3.0)
        self.henb.setValue(self.parent.henb)
        self.henb.setSingleStep(0.01)                  
        hbox.addWidget(self.henb) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()       
        spec = QtGui.QLabel("<b>View settings<b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox_tab_general.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Area width")
        self.area_width = QtGui.QDoubleSpinBox()
        self.area_width.setDecimals(6)
        self.area_width.setAccelerated(True)
        self.area_width.setMaximum(10.0)
        self.area_width.setMinimum(0.0001)
        self.area_width.setValue(self.parent.xright - self.parent.xleft)
        self.area_width.setSingleStep(0.01)             
        hbox.addWidget(self.area_width) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Area height")
        self.area_height = QtGui.QDoubleSpinBox()
        self.area_height.setDecimals(6)
        self.area_height.setAccelerated(True)
        self.area_height.setMaximum(10.0)
        self.area_height.setMinimum(0.0001)
        self.area_height.setValue(self.parent.ytop - self.parent.ybottom)
        self.area_height.setSingleStep(0.01)            
        hbox.addWidget(self.area_height) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Left edge location")
        self.xleft = QtGui.QDoubleSpinBox()
        self.xleft.setDecimals(6)
        self.xleft.setAccelerated(True)
        self.xleft.setMaximum(2.0)
        self.xleft.setMinimum(-2.0)
        self.xleft.setValue(self.parent.xleft)
        self.xleft.setSingleStep(0.01)             
        hbox.addWidget(self.xleft) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox) 
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Bottom edge location")
        self.ybottom = QtGui.QDoubleSpinBox()
        self.ybottom.setDecimals(6)
        self.ybottom.setAccelerated(True)
        self.ybottom.setMaximum(1.0)
        self.ybottom.setMinimum(-1.0)
        self.ybottom.setValue(self.parent.ybottom)
        self.ybottom.setSingleStep(0.01)            
        hbox.addWidget(self.ybottom) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Enlarge rare pixels")
        self.enlarge_rare_pixels = QtGui.QCheckBox()
        self.enlarge_rare_pixels.setChecked(self.parent.enlarge_rare_pixels)
        description.mouseReleaseEvent = self.switch_enlarge_rare_pixels
        hbox.addWidget(self.enlarge_rare_pixels)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)        

        hbox = QtGui.QHBoxLayout()           
        spec = QtGui.QLabel("<b>Calculation settings</b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox_tab_general.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Max iterations")
        self.max_iter = QtGui.QSpinBox()
        self.max_iter.setAccelerated(True)
        self.max_iter.setMaximum(999999999)
        self.max_iter.setMinimum(1)
        self.max_iter.setValue(self.parent.max_iter)
        self.max_iter.setSingleStep(1000)
        self.max_iter.setDisabled(self.parent.iter_auto_mode)
        hbox.addWidget(self.max_iter) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Plot interval")
        self.plot_interval = QtGui.QSpinBox()
        self.plot_interval.setAccelerated(True)
        self.plot_interval.setMaximum(999999999)
        self.plot_interval.setMinimum(1)
        self.plot_interval.setValue(self.parent.plot_interval)
        self.plot_interval.setSingleStep(1000)
        self.plot_interval.setDisabled(self.parent.iter_auto_mode)
        hbox.addWidget(self.plot_interval) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)         

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Auto-mode")
        self.iter_auto_mode = QtGui.QCheckBox()
        self.iter_auto_mode.setChecked(self.parent.iter_auto_mode)
        self.iter_auto_mode.mouseReleaseEvent = self.switch_iter_auto_mode
        description.mouseReleaseEvent = self.switch_iter_auto_mode
        hbox.addWidget(self.iter_auto_mode)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_general.addLayout(hbox)

        vbox_tab_general.addStretch(1)
        generic_widget_general = QtGui.QWidget()
        generic_widget_general.setLayout(vbox_tab_general)
        tabwidget.addTab(generic_widget_general, QtCore.QString("General"))

        ### Tab animation ###
        vbox_tab_animation = QtGui.QVBoxLayout()
        
        hbox = QtGui.QHBoxLayout()           
        spec = QtGui.QLabel("<b>Animation settings</b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox_tab_animation.addLayout(hbox)  
                
        vbox_anim_left = QtGui.QVBoxLayout()
        vbox_anim_right = QtGui.QVBoxLayout()
        
        vbox_anim_left.addWidget(QtGui.QLabel("Parameter 'a'"))
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Mid-point")
        self.hena_mid = QtGui.QDoubleSpinBox()
        self.hena_mid.setDecimals(3)
        self.hena_mid.setAccelerated(True)
        self.hena_mid.setMaximum(3.0)
        self.hena_mid.setMinimum(-3.0)
        self.hena_mid.setValue(self.parent.hena_mid)
        self.hena_mid.setSingleStep(0.01)          
        hbox.addWidget(self.hena_mid) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Range")
        self.hena_range = QtGui.QDoubleSpinBox()
        self.hena_range.setDecimals(3)
        self.hena_range.setAccelerated(True)
        self.hena_range.setMaximum(3.0)
        self.hena_range.setMinimum(0.01)
        self.hena_range.setValue(self.parent.hena_range)
        self.hena_range.setSingleStep(0.01)           
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
        hbox.addWidget(self.hena_increment) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Animate")
        self.hena_anim = QtGui.QCheckBox()
        self.hena_anim.setChecked(self.parent.hena_anim)
        description.mouseReleaseEvent = self.switch_hena_anim
        hbox.addWidget(self.hena_anim)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox)        

        vbox_anim_right.addWidget(QtGui.QLabel("Parameter 'b'"))

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Mid-point")
        self.henb_mid = QtGui.QDoubleSpinBox()
        self.henb_mid.setDecimals(3)
        self.henb_mid.setAccelerated(True)
        self.henb_mid.setMaximum(3.0)
        self.henb_mid.setMinimum(-3.0)
        self.henb_mid.setValue(self.parent.henb_mid)
        self.henb_mid.setSingleStep(0.01)            
        hbox.addWidget(self.henb_mid) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Range")
        self.henb_range = QtGui.QDoubleSpinBox()
        self.henb_range.setDecimals(3)
        self.henb_range.setAccelerated(True)
        self.henb_range.setMaximum(3.0)
        self.henb_range.setMinimum(-3.0)
        self.henb_range.setValue(self.parent.henb_range)
        self.henb_range.setSingleStep(0.01)          
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
        hbox.addWidget(self.henb_increment) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox) 

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Animate")
        self.henb_anim = QtGui.QCheckBox()
        self.henb_anim.setChecked(self.parent.henb_anim)
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
        vbox_tab_animation.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Animation time delay [ms]")
        self.animation_delay = QtGui.QSpinBox()
        self.animation_delay.setAccelerated(True)
        self.animation_delay.setMaximum(999)
        self.animation_delay.setMinimum(50)
        self.animation_delay.setValue(self.parent.animation_delay)
        self.animation_delay.setSingleStep(10)
        hbox.addWidget(self.animation_delay) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_animation.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()           
        spec = QtGui.QLabel("<b>Calculation settings</b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox_tab_animation.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Max iterations")
        self.max_iter_anim = QtGui.QSpinBox()
        self.max_iter_anim.setAccelerated(True)
        self.max_iter_anim.setMaximum(999999999)
        self.max_iter_anim.setMinimum(1)
        self.max_iter_anim.setValue(self.parent.max_iter_anim)
        self.max_iter_anim.setSingleStep(1000)
        hbox.addWidget(self.max_iter_anim) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_animation.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Plot interval")
        self.plot_interval_anim = QtGui.QSpinBox()
        self.plot_interval_anim.setAccelerated(True)
        self.plot_interval_anim.setMaximum(999999999)
        self.plot_interval_anim.setMinimum(1)
        self.plot_interval_anim.setValue(self.parent.plot_interval_anim)
        self.plot_interval_anim.setSingleStep(1000)
        hbox.addWidget(self.plot_interval_anim) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_animation.addLayout(hbox)
        
        vbox_tab_animation.addStretch(1)
        generic_widget_animation = QtGui.QWidget()
        generic_widget_animation.setLayout(vbox_tab_animation)
        tabwidget.addTab(generic_widget_animation, QtCore.QString("Animation"))

        ### Tab calculation ###
        vbox_tab_calculation = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()       
        spec = QtGui.QLabel("<b>Calculation settings<b>")
        hbox.addWidget(spec)
        hbox.addStretch(1)
        vbox_tab_calculation.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Drop iterations")
        self.drop_iter = QtGui.QSpinBox()
        self.drop_iter.setAccelerated(True)
        self.drop_iter.setMaximum(9999)
        self.drop_iter.setMinimum(0)
        self.drop_iter.setValue(self.parent.drop_iter)
        self.drop_iter.setSingleStep(1)            
        hbox.addWidget(self.drop_iter) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_calculation.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Thread count")
        self.thread_count = QtGui.QSpinBox()
        self.thread_count.setAccelerated(True)
        if (not self.parent.opencl_enabled):
            self.thread_count.setMaximum(cpu_count())
        else:
            self.thread_count.setMaximum(9999)
        self.thread_count.setMinimum(1)
        self.thread_count.setValue(self.parent.thread_count)
        self.thread_count.setSingleStep(1)
        self.thread_count.setDisabled(self.parent.opencl_enabled)            
        hbox.addWidget(self.thread_count) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_calculation.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        description = QtGui.QLabel("Enable OpenCL")
        self.opencl_enabled = QtGui.QCheckBox()
        self.opencl_enabled.setDisabled(not self.parent.module_opencl_present)
        description.setDisabled(not self.parent.module_opencl_present)
        self.opencl_enabled.setChecked(self.parent.opencl_enabled)
        self.opencl_enabled.mouseReleaseEvent = self.switch_opencl_enabled
        description.mouseReleaseEvent = self.switch_opencl_enabled
        hbox.addWidget(self.opencl_enabled)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_tab_calculation.addLayout(hbox)

        if self.parent.module_opencl_present:

            self.scroll_area = QtGui.QScrollArea()
            self.scroll_area.setDisabled(not self.opencl_enabled.isChecked())
            checkbox_widget = QtGui.QWidget()
            checkbox_vbox = QtGui.QVBoxLayout()            
            
            self.devices_cb = []

            num = 0
            for platform in cl.get_platforms():
                platform_name = QtGui.QLabel("Platform: " + platform.name)
                checkbox_vbox.addWidget(platform_name)
                for device in platform.get_devices():
                    self.devices_cb.append(QtGui.QRadioButton(device.name))
                    self.devices_cb[num].setMinimumWidth(400) # prevent obscured text
                    checkbox_vbox.addWidget(self.devices_cb[num])
                    if num == self.parent.device_selection:
                        self.devices_cb[num].setChecked(True)                     
                    num += 1

            checkbox_widget.setLayout(checkbox_vbox)
            self.scroll_area.setWidget(checkbox_widget)
            vbox_tab_calculation.addWidget(self.scroll_area)

        vbox_tab_calculation.addStretch(1)
        generic_widget_calculation = QtGui.QWidget()
        generic_widget_calculation.setLayout(vbox_tab_calculation)
        tabwidget.addTab(generic_widget_calculation, QtCore.QString("Calculation"))
        
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(tabwidget)

        ### Buttonbox for ok or cancel ###
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtGui.QBoxLayout.RightToLeft)

        layout.addWidget(buttonbox)
        self.setMinimumWidth(512)

    def switch_enlarge_rare_pixels(self, event):
        # function for making QLabel near checkbox clickable
        self.enlarge_rare_pixels.setChecked(not self.enlarge_rare_pixels.isChecked())

    def switch_opencl_enabled(self, event):
        # function for making QLabel near checkbox clickable
        self.opencl_enabled.setChecked(not self.opencl_enabled.isChecked())
        self.scroll_area.setDisabled(not self.opencl_enabled.isChecked())
        self.thread_count.setDisabled(self.opencl_enabled.isChecked())

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

        ### General settings ###
        self.parent.hena = self.hena.value()
        self.parent.henb = self.henb.value()
        self.parent.xleft = self.xleft.value()
        self.parent.xright = self.xleft.value() + self.area_width.value()
        self.parent.ybottom = self.ybottom.value()
        self.parent.ytop = self.ybottom.value() + self.area_height.value()
        self.parent.enlarge_rare_pixels = self.enlarge_rare_pixels.isChecked()

        if not self.iter_auto_mode.isChecked():
            # only read it if auto mode is turned off
            self.parent.max_iter = self.max_iter.value()
            self.parent.plot_interval = self.plot_interval.value()

        self.parent.iter_auto_mode = self.iter_auto_mode.isChecked()
        
        ### Animation settings ###
        self.parent.hena_mid = self.hena_mid.value()
        self.parent.hena_range = self.hena_range.value()
        self.parent.hena_increment = self.hena_increment.value()
        self.parent.hena_anim = self.hena_anim.isChecked()
        
        self.parent.henb_mid = self.henb_mid.value()
        self.parent.henb_range = self.henb_range.value()
        self.parent.henb_increment = self.henb_increment.value()
        self.parent.henb_anim = self.henb_anim.isChecked()

        self.parent.max_iter_anim = self.max_iter_anim.value()
        self.parent.plot_interval_anim = self.plot_interval_anim.value()        
        self.parent.animation_delay = self.animation_delay.value()

        ### Calculation settings ###
        self.parent.drop_iter = self.drop_iter.value()
        
        if self.parent.module_opencl_present and not self.opencl_enabled.isChecked():
            self.parent.thread_count = self.thread_count.value()            

        if self.parent.module_opencl_present:
            self.parent.opencl_enabled = self.opencl_enabled.isChecked()            
            
            for i in range(len(self.devices_cb)):
                if self.devices_cb[i].isChecked():
                    self.parent.device_selection = i
        
            if self.opencl_enabled.isChecked():
                self.parent.initialize_opencl()
        
        self.parent.statusBar().showMessage(self.tr("Parameter settings updated; press R to re-draw"), 3000)
        self.accept()