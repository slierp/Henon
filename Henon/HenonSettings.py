# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform
from multiprocessing import cpu_count

try: # check if PyOpenCL is present as it is optional
    import pyopencl as cl
except ImportError:
    pass

class HenonSettings(QtWidgets.QDialog):
    # Generates a settings dialog    
    
    def __init__(self, _parent):
        super(QtWidgets.QDialog, self).__init__(_parent)
        
        self.parent = _parent
        
        self.setWindowTitle(self.tr("Settings"))

        tabwidget = QtWidgets.QTabWidget()
        
        ### Tab general ###
        vbox_tab_general = QtWidgets.QVBoxLayout() 

        group_henon_parameter = QtWidgets.QGroupBox("H\xe9non parameter settings")
        vbox = QtWidgets.QVBoxLayout()       
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Parameter 'a'")
        self.hena = QtWidgets.QDoubleSpinBox()
        self.hena.setDecimals(4)
        self.hena.setAccelerated(True)
        self.hena.setMaximum(2.0)
        self.hena.setMinimum(-2.0)
        self.hena.setValue(self.parent.hena)
        self.hena.setSingleStep(0.01)          
        hbox.addWidget(self.hena) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)          

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Parameter 'b'")
        self.henb = QtWidgets.QDoubleSpinBox()
        self.henb.setDecimals(4)
        self.henb.setAccelerated(True)
        self.henb.setMaximum(2.0)
        self.henb.setMinimum(-2.0)
        self.henb.setValue(self.parent.henb)
        self.henb.setSingleStep(0.01)                  
        hbox.addWidget(self.henb) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox) 

        group_henon_parameter.setLayout(vbox)        
        vbox_tab_general.addWidget(group_henon_parameter)

        group_henon_iter = QtWidgets.QGroupBox("Number of iterations")
        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Auto-mode")
        self.iter_auto_mode = QtWidgets.QCheckBox()
        self.iter_auto_mode.setChecked(self.parent.iter_auto_mode)
        self.iter_auto_mode.mouseReleaseEvent = self.switch_iter_auto_mode
        description.mouseReleaseEvent = self.switch_iter_auto_mode
        hbox.addWidget(self.iter_auto_mode)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Max iterations per thread")
        self.max_iter = QtWidgets.QSpinBox()
        self.max_iter.setAccelerated(True)
        self.max_iter.setMaximum(999999999)
        self.max_iter.setMinimum(1)
        self.max_iter.setValue(self.parent.max_iter)
        self.max_iter.setSingleStep(1000)
        self.max_iter.setDisabled(self.parent.iter_auto_mode)
        hbox.addWidget(self.max_iter) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Plot interval per thread")
        self.plot_interval = QtWidgets.QSpinBox()
        self.plot_interval.setAccelerated(True)
        self.plot_interval.setMaximum(999999999)
        self.plot_interval.setMinimum(1)
        self.plot_interval.setValue(self.parent.plot_interval)
        self.plot_interval.setSingleStep(1000)
        self.plot_interval.setDisabled(self.parent.iter_auto_mode)
        hbox.addWidget(self.plot_interval) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)         

        group_henon_iter.setLayout(vbox)        
        vbox_tab_general.addWidget(group_henon_iter)

        group_henon_appear = QtWidgets.QGroupBox("Appearance")
        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Pixel color")        
        self.color_combobox = QtWidgets.QComboBox(self)
        for i in self.parent.color_options:
            self.color_combobox.addItem(i)               
        self.color_combobox.setCurrentIndex(self.parent.color)
        hbox.addWidget(self.color_combobox) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Supersampling")        
        self.sampling_combobox = QtWidgets.QComboBox(self)
        for i in self.parent.super_sampling_options:
            self.sampling_combobox.addItem(i)               
        self.sampling_combobox.setCurrentIndex(self.parent.super_sampling)
        hbox.addWidget(self.sampling_combobox) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        #hbox = QtWidgets.QHBoxLayout()
        #description = QtWidgets.QLabel("Image resize method")        
        #self.resize_method_combobox = QtWidgets.QComboBox(self)
        #for i in self.parent.resize_method_options:
        #    self.resize_method_combobox.addItem(i)               
        #self.resize_method_combobox.setCurrentIndex(self.parent.resize_method)
        #hbox.addWidget(self.resize_method_combobox) 
        #hbox.addWidget(description)
        #hbox.addStretch(1)                
        #vbox.addLayout(hbox)

        group_henon_appear.setLayout(vbox)        
        vbox_tab_general.addWidget(group_henon_appear)

        vbox_tab_general.addStretch(1)
        generic_widget_general = QtWidgets.QWidget()
        generic_widget_general.setLayout(vbox_tab_general)
        tabwidget.addTab(generic_widget_general, "General")

        ### Orbit map tab ###
        vbox_tab_orbit = QtWidgets.QVBoxLayout()  

        group_parameter = QtWidgets.QGroupBox("Parameter selection for x-axis")
        vbox = QtWidgets.QVBoxLayout()

        self.orbit_parameter_a = QtWidgets.QRadioButton("Parameter 'a'")
        self.orbit_parameter_a.setChecked(self.parent.orbit_parameter)       
        vbox.addWidget(self.orbit_parameter_a)

        self.orbit_parameter_b = QtWidgets.QRadioButton("Parameter 'b'")
        self.orbit_parameter_b.setChecked(not self.parent.orbit_parameter)      
        vbox.addWidget(self.orbit_parameter_b)

        group_parameter.setLayout(vbox)        
        vbox_tab_orbit.addWidget(group_parameter)
        
        group_coordinate = QtWidgets.QGroupBox("Coordinate selection for y-axis")
        vbox = QtWidgets.QVBoxLayout()

        self.orbit_coordinate_x = QtWidgets.QRadioButton("x-coordinate")
        self.orbit_coordinate_x.setChecked(not self.parent.orbit_coordinate)
        vbox.addWidget(self.orbit_coordinate_x)              

        self.orbit_coordinate_y = QtWidgets.QRadioButton("y-coordinate")
        self.orbit_coordinate_y.setChecked(self.parent.orbit_coordinate)
        vbox.addWidget(self.orbit_coordinate_y)

        group_coordinate.setLayout(vbox)        
        vbox_tab_orbit.addWidget(group_coordinate)

        group_orbit_iter = QtWidgets.QGroupBox("Number of iterations")
        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Auto-mode")
        self.iter_auto_mode_orbit = QtWidgets.QCheckBox()
        self.iter_auto_mode_orbit.setChecked(self.parent.iter_auto_mode_orbit)
        self.iter_auto_mode_orbit.mouseReleaseEvent = self.switch_iter_auto_mode_orbit
        description.mouseReleaseEvent = self.switch_iter_auto_mode_orbit
        hbox.addWidget(self.iter_auto_mode_orbit)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Max iterations per pixel along screen width")
        self.max_iter_orbit = QtWidgets.QSpinBox()
        self.max_iter_orbit.setAccelerated(True)
        self.max_iter_orbit.setMaximum(99999)
        self.max_iter_orbit.setMinimum(1)
        self.max_iter_orbit.setValue(self.parent.max_iter_orbit)
        self.max_iter_orbit.setSingleStep(100)
        self.max_iter_orbit.setDisabled(self.parent.iter_auto_mode_orbit)
        hbox.addWidget(self.max_iter_orbit) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Plot interval per pixel along screen width")
        self.plot_interval_orbit = QtWidgets.QSpinBox()
        self.plot_interval_orbit.setAccelerated(True)
        self.plot_interval_orbit.setMaximum(99999)
        self.plot_interval_orbit.setMinimum(1)
        self.plot_interval_orbit.setValue(self.parent.plot_interval_orbit)
        self.plot_interval_orbit.setSingleStep(100)
        self.plot_interval_orbit.setDisabled(self.parent.iter_auto_mode_orbit)
        hbox.addWidget(self.plot_interval_orbit) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        group_orbit_iter.setLayout(vbox)        
        vbox_tab_orbit.addWidget(group_orbit_iter)

        vbox_tab_orbit.addStretch(1)
        generic_widget_animation = QtWidgets.QWidget()
        generic_widget_animation.setLayout(vbox_tab_orbit)
        tabwidget.addTab(generic_widget_animation, "Orbit map")

        ### Tab animation ###
        vbox_tab_animation = QtWidgets.QVBoxLayout()

        group_henon_anim = QtWidgets.QGroupBox("H\xe9non parameter animation settings")
        vbox = QtWidgets.QVBoxLayout() 
                
        vbox_anim_left = QtWidgets.QVBoxLayout()
        vbox_anim_right = QtWidgets.QVBoxLayout()
        
        vbox_anim_left.addWidget(QtWidgets.QLabel("Parameter 'a'"))
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Start")
        self.hena_start = QtWidgets.QDoubleSpinBox()
        self.hena_start.setDecimals(4)
        self.hena_start.setAccelerated(True)
        self.hena_start.setMaximum(2.0)
        self.hena_start.setMinimum(-2.0)
        self.hena_start.setValue(self.parent.hena_start)
        self.hena_start.setSingleStep(0.01)          
        hbox.addWidget(self.hena_start) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Stop")
        self.hena_stop = QtWidgets.QDoubleSpinBox()
        self.hena_stop.setDecimals(4)
        self.hena_stop.setAccelerated(True)
        self.hena_stop.setMaximum(2.0)
        self.hena_stop.setMinimum(-2.0)
        self.hena_stop.setValue(self.parent.hena_stop)
        self.hena_stop.setSingleStep(0.01)           
        hbox.addWidget(self.hena_stop) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox) 

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Increment")
        self.hena_increment = QtWidgets.QDoubleSpinBox()
        self.hena_increment.setAccelerated(True)
        self.hena_increment.setDecimals(4)
        self.hena_increment.setMaximum(0.5)
        self.hena_increment.setMinimum(0.0001)
        self.hena_increment.setValue(self.parent.hena_increment)
        self.hena_increment.setSingleStep(0.0001)          
        hbox.addWidget(self.hena_increment) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox) 

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Animate")
        self.hena_anim = QtWidgets.QCheckBox()
        self.hena_anim.setChecked(self.parent.hena_anim)
        description.mouseReleaseEvent = self.switch_hena_anim
        hbox.addWidget(self.hena_anim)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_left.addLayout(hbox)        

        vbox_anim_right.addWidget(QtWidgets.QLabel("Parameter 'b'"))

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Start")
        self.henb_start = QtWidgets.QDoubleSpinBox()
        self.henb_start.setDecimals(4)
        self.henb_start.setAccelerated(True)
        self.henb_start.setMaximum(2.0)
        self.henb_start.setMinimum(-2.0)
        self.henb_start.setValue(self.parent.henb_start)
        self.henb_start.setSingleStep(0.01)            
        hbox.addWidget(self.henb_start) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Stop")
        self.henb_stop = QtWidgets.QDoubleSpinBox()
        self.henb_stop.setDecimals(4)
        self.henb_stop.setAccelerated(True)
        self.henb_stop.setMaximum(2.0)
        self.henb_stop.setMinimum(-2.0)
        self.henb_stop.setValue(self.parent.henb_stop)
        self.henb_stop.setSingleStep(0.01)          
        hbox.addWidget(self.henb_stop) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox) 

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Increment")
        self.henb_increment = QtWidgets.QDoubleSpinBox()
        self.henb_increment.setAccelerated(True)
        self.henb_increment.setDecimals(4)
        self.henb_increment.setMaximum(0.5)
        self.henb_increment.setMinimum(0.0001)
        self.henb_increment.setValue(self.parent.henb_increment)
        self.henb_increment.setSingleStep(0.0001)           
        hbox.addWidget(self.henb_increment) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox) 

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Animate")
        self.henb_anim = QtWidgets.QCheckBox()
        self.henb_anim.setChecked(self.parent.henb_anim)
        description.mouseReleaseEvent = self.switch_henb_anim
        hbox.addWidget(self.henb_anim)
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox_anim_right.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox_anim_left)
        hbox.addSpacing(10)      
        hbox.addLayout(vbox_anim_right)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        group_henon_anim.setLayout(vbox)        
        vbox_tab_animation.addWidget(group_henon_anim)

        group_henon_anim_iter = QtWidgets.QGroupBox("Iteration settings for each frame")
        vbox = QtWidgets.QVBoxLayout() 

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Number of iterations (not for orbit mode)")
        self.plot_interval_anim = QtWidgets.QSpinBox()
        self.plot_interval_anim.setAccelerated(True)
        self.plot_interval_anim.setMaximum(99999)
        self.plot_interval_anim.setMinimum(1)
        self.plot_interval_anim.setValue(self.parent.plot_interval_anim)
        self.plot_interval_anim.setSingleStep(1000)
        hbox.addWidget(self.plot_interval_anim) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Animation time delay [ms]")
        self.animation_delay = QtWidgets.QSpinBox()
        self.animation_delay.setAccelerated(True)
        self.animation_delay.setMaximum(999)
        self.animation_delay.setMinimum(20)
        self.animation_delay.setValue(self.parent.animation_delay)
        self.animation_delay.setSingleStep(10)
        hbox.addWidget(self.animation_delay) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        #hbox = QtWidgets.QHBoxLayout()
        #description = QtWidgets.QLabel("Enlarge rare pixels")
        #self.enlarge_rare_pixels = QtWidgets.QCheckBox()
        #self.enlarge_rare_pixels.setChecked(self.parent.enlarge_rare_pixels)
        #description.mouseReleaseEvent = self.switch_enlarge_rare_pixels
        #hbox.addWidget(self.enlarge_rare_pixels)
        #hbox.addWidget(description)
        #hbox.addStretch(1)                
        #vbox.addLayout(hbox)

        group_henon_anim_iter.setLayout(vbox)        
        vbox_tab_animation.addWidget(group_henon_anim_iter)
        
        vbox_tab_animation.addStretch(1)
        generic_widget_animation = QtWidgets.QWidget()
        generic_widget_animation.setLayout(vbox_tab_animation)
        tabwidget.addTab(generic_widget_animation, "Animation")

        ### Tab calculation ###      
        
        vbox_tab_calculation = QtWidgets.QVBoxLayout()

        group_init = QtWidgets.QGroupBox("Initial conditions")
        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Drop iterations")
        self.drop_iter = QtWidgets.QSpinBox()
        self.drop_iter.setAccelerated(True)
        self.drop_iter.setMaximum(99999)
        self.drop_iter.setMinimum(0)
        self.drop_iter.setValue(self.parent.drop_iter)
        self.drop_iter.setSingleStep(100)            
        hbox.addWidget(self.drop_iter) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)     

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("x[0],y[0] additive (n + random(-0.1,0.1))")
        self.initial_conditions_additive = QtWidgets.QDoubleSpinBox()
        self.initial_conditions_additive.setDecimals(1)
        self.initial_conditions_additive.setAccelerated(True)
        self.initial_conditions_additive.setMaximum(1)
        self.initial_conditions_additive.setMinimum(-1)
        self.initial_conditions_additive.setValue(self.parent.initial_conditions_additive)
        self.initial_conditions_additive.setSingleStep(0.1)           
        hbox.addWidget(self.initial_conditions_additive) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("x[0],y[0] multiplier (m*(n+random(-0.1,0.1)))")
        self.initial_conditions_multiplier = QtWidgets.QDoubleSpinBox()
        self.initial_conditions_multiplier.setDecimals(1)
        self.initial_conditions_multiplier.setAccelerated(True)
        self.initial_conditions_multiplier.setMaximum(10)
        self.initial_conditions_multiplier.setMinimum(0)
        self.initial_conditions_multiplier.setValue(self.parent.initial_conditions_multiplier)
        self.initial_conditions_multiplier.setSingleStep(0.1)           
        hbox.addWidget(self.initial_conditions_multiplier) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        group_init.setLayout(vbox)        
        vbox_tab_calculation.addWidget(group_init)

        group_multi = QtWidgets.QGroupBox("Multithreading")
        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Thread count")
        self.thread_count = QtWidgets.QSpinBox()
        self.thread_count.setAccelerated(True)
        self.thread_count.setMaximum(cpu_count())
        self.thread_count.setMinimum(1)
        self.thread_count.setValue(self.parent.thread_count)
        self.thread_count.setSingleStep(1)           
        hbox.addWidget(self.thread_count) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("OpenCL global work size (2^n)")
        self.global_work_size = QtWidgets.QSpinBox()
        self.global_work_size.setAccelerated(True)
        self.global_work_size.setMaximum(16)
        self.global_work_size.setMinimum(0)
        self.global_work_size.setValue(self.parent.global_work_size)           
        hbox.addWidget(self.global_work_size) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("OpenCL orbit work size multiplier (2^n)")
        self.orbit_multiplier = QtWidgets.QSpinBox()
        self.orbit_multiplier.setAccelerated(True)
        self.orbit_multiplier.setMaximum(16)  # max allowed n is 32 due to uint32
        self.orbit_multiplier.setMinimum(0)
        self.orbit_multiplier.setValue(self.parent.orbit_multiplier)           
        hbox.addWidget(self.orbit_multiplier) 
        hbox.addWidget(description)
        hbox.addStretch(1)                
        vbox.addLayout(hbox)

        group_multi.setLayout(vbox)        
        vbox_tab_calculation.addWidget(group_multi)

        hbox = QtWidgets.QHBoxLayout()
        self.opencl_enabled = QtWidgets.QCheckBox("Enable OpenCL")
        self.opencl_enabled.setDisabled(not self.parent.module_opencl_present)
        self.opencl_enabled.setChecked(self.parent.opencl_enabled)
        hbox.addWidget(self.opencl_enabled)
        hbox.addStretch(1)                
        vbox_tab_calculation.addLayout(hbox)

        if self.parent.module_opencl_present:
            self.scroll_area = QtWidgets.QScrollArea()
            checkbox_widget = QtWidgets.QWidget()
            checkbox_vbox = QtWidgets.QVBoxLayout()
            
            self.devices_cb = []

            num = 0
            for platform in cl.get_platforms():
                #platform_name = QtWidgets.QLabel("Platform: " + platform.name)
                #checkbox_vbox.addWidget(platform_name)
                for device in platform.get_devices():
                    self.devices_cb.append(QtWidgets.QCheckBox(device.name))
                    self.devices_cb[num].setMinimumWidth(400) # prevent obscured text
                    checkbox_vbox.addWidget(self.devices_cb[num])
                    if num in self.parent.device_selection:
                        self.devices_cb[num].setChecked(True)                     
                    num += 1

            checkbox_widget.setLayout(checkbox_vbox)
            self.scroll_area.setWidget(checkbox_widget)
            vbox_tab_calculation.addWidget(self.scroll_area)
        
        else:
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel("OpenCL driver not detected. OpenCL function was disabled.")
            hbox.addWidget(description)
            hbox.addStretch(1)                
            vbox_tab_calculation.addLayout(hbox)

        vbox_tab_calculation.addStretch(1)
        generic_widget_calculation = QtWidgets.QWidget()
        generic_widget_calculation.setLayout(vbox_tab_calculation)
        tabwidget.addTab(generic_widget_calculation, "Calculation")
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tabwidget)

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft)

        layout.addWidget(buttonbox)
        self.setMinimumWidth(512)

    def switch_enlarge_rare_pixels(self, event):
        # function for making QLabel near checkbox clickable
        self.enlarge_rare_pixels.setChecked(not self.enlarge_rare_pixels.isChecked())

    def switch_iter_auto_mode(self, event):
        # function for making QLabel near checkbox clickable
        self.iter_auto_mode.setChecked(not self.iter_auto_mode.isChecked())
        self.max_iter.setDisabled(self.iter_auto_mode.isChecked())
        self.plot_interval.setDisabled(self.iter_auto_mode.isChecked())
        
    def switch_iter_auto_mode_orbit(self, event):
        # function for making QLabel near checkbox clickable
        self.iter_auto_mode_orbit.setChecked(not self.iter_auto_mode_orbit.isChecked())
        self.max_iter_orbit.setDisabled(self.iter_auto_mode_orbit.isChecked())
        self.plot_interval_orbit.setDisabled(self.iter_auto_mode_orbit.isChecked())        
        
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

        if not self.iter_auto_mode.isChecked():
            # only read it if auto mode is turned off
            self.parent.max_iter = self.max_iter.value()
            self.parent.plot_interval = self.plot_interval.value()

        self.parent.iter_auto_mode = self.iter_auto_mode.isChecked()
        self.parent.color = self.color_combobox.currentIndex()
        self.parent.super_sampling = self.sampling_combobox.currentIndex()
        #self.parent.resize_method = self.resize_method_combobox.currentIndex()
        
        ### Animation settings ###
        self.parent.hena_start = self.hena_start.value()
        self.parent.hena_stop = self.hena_stop.value()
        self.parent.hena_increment = self.hena_increment.value()
        self.parent.hena_anim = self.hena_anim.isChecked()
        
        self.parent.henb_start = self.henb_start.value()
        self.parent.henb_stop = self.henb_stop.value()
        self.parent.henb_increment = self.henb_increment.value()
        self.parent.henb_anim = self.henb_anim.isChecked()

        self.parent.plot_interval_anim = self.plot_interval_anim.value()        
        self.parent.animation_delay = self.animation_delay.value()
        #self.parent.enlarge_rare_pixels = self.enlarge_rare_pixels.isChecked()

        ### Orbit map settings ###
        self.parent.max_iter_orbit = self.max_iter_orbit.value()
        self.parent.plot_interval_orbit = self.plot_interval_orbit.value()
        self.parent.iter_auto_mode_orbit = self.iter_auto_mode_orbit.isChecked()
        
        orbit_mode_changed = False 
        if not (self.parent.orbit_parameter == self.orbit_parameter_a.isChecked()):
            self.parent.orbit_parameter = self.orbit_parameter_a.isChecked()
            orbit_mode_changed = True
            
        if not (self.parent.orbit_coordinate == self.orbit_coordinate_y.isChecked()):
            self.parent.orbit_coordinate = self.orbit_coordinate_y.isChecked()
            orbit_mode_changed = True
        
        if self.parent.orbit_mode and orbit_mode_changed:
            # re-initialize if orbit mode is active and was changed (parameter or coordinate)
            self.parent.initialize_orbit_mode()

        ### Calculation settings ###
        self.parent.drop_iter = self.drop_iter.value()
        self.parent.thread_count = self.thread_count.value()            
        self.parent.initial_conditions_multiplier = self.initial_conditions_multiplier.value()
        self.parent.initial_conditions_additive = self.initial_conditions_additive.value()

        if self.parent.module_opencl_present:
            self.parent.opencl_enabled = self.opencl_enabled.isChecked()            
            
            self.parent.global_work_size = self.global_work_size.value()

            self.parent.orbit_multiplier = self.orbit_multiplier.value()
            
            self.parent.device_selection = []
            for i in range(len(self.devices_cb)):
                if self.devices_cb[i].isChecked():
                    self.parent.device_selection.append(i)
        
            if self.opencl_enabled.isChecked():
                self.parent.initialize_opencl()
        
        # trigger resize event to force implementation of super-sampling setting
        self.parent.Henon_widget.trigger_resizeEvent()

        self.parent.statusBar().showMessage(self.tr("Parameter settings updated"), 1000)
        self.accept()