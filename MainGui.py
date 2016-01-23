# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore, QtGui
import HenonResources
#from HenonWidget import HenonWidget # for OpenGL Henon widget
from HenonWidget2 import HenonWidget # for PyQt-only Henon widget
from HenonUpdate import HenonUpdate
from HenonCalc import HenonCalc
from HenonCalcOrbit import HenonCalcOrbit
from HenonHelp import HenonHelp
from HenonSettings import HenonSettings
from multiprocessing import cpu_count
import os, ntpath, pickle
from math import ceil

try:
    # check if PyOpenCL is present as it is optional
    import pyopencl as cl
    from HenonCalc2 import HenonCalc2
    from HenonCalc2Orbit import HenonCalc2Orbit
    from HenonUpdate2 import HenonUpdate2
    module_opencl_present = True
except ImportError:
    module_opencl_present = False

class MainGui(QtGui.QMainWindow):
    # Main user interface; starts up main window and initiates a first Henon calculation
    # and then waits for user input
    
    def __init__(self, parent=None):
        
        super(MainGui, self).__init__(parent)
        
        self.setWindowTitle(self.tr("H\xe9non explorer"))
        self.setWindowIcon(QtGui.QIcon(":HenonExplorer.png"))

        ### Set initial geometry and center the window on the screen ###
        self.resize(1024, 576)
        frameGm = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())        
        
        ### Set default font size ###
        self.setStyleSheet('font-size: 12pt;')         
        
        self.create_menu()
        self.create_main_frame()        

        self.default_settings = {} # put parameters in dict for easy saving/loading
        
        # general settings
        self.hena = 1.4
        self.default_settings['hena'] = self.hena
        self.henb = 0.3
        self.default_settings['henb'] = self.henb
        self.xleft = -1.5
        self.default_settings['xleft'] = self.xleft
        self.ytop = 0.4
        self.default_settings['ytop'] = self.ytop
        self.xright = 1.5
        self.default_settings['xright'] = self.xright
        self.ybottom = -0.4
        self.default_settings['ybottom'] = self.ybottom
        
        # calculation settings        
        self.opencl_enabled = False
        self.default_settings['opencl_enabled'] = self.opencl_enabled
        self.device_selection = [] # selected OpenCL devices
        self.default_settings['device_selection'] = self.device_selection
        
        self.thread_count = cpu_count()
        self.default_settings['thread_count'] = self.thread_count
        self.global_work_size = 256
        self.default_settings['global_work_size'] = self.global_work_size
        self.plot_interval = 1
        self.default_settings['plot_interval'] = self.plot_interval
        self.max_iter = 1
        self.default_settings['max_iter'] = self.max_iter
        self.drop_iter = 1000
        self.default_settings['drop_iter'] = self.drop_iter
        self.iter_auto_mode = True
        self.default_settings['iter_auto_mode'] = self.iter_auto_mode
        self.enlarge_rare_pixels = False
        self.default_settings['enlarge_rare_pixels'] = self.enlarge_rare_pixels
        self.benchmark = False
        self.default_settings['benchmark'] = self.benchmark
        
        # animation settings
        self.hena_mid = 0.8
        self.default_settings['hena_mid'] = self.hena_mid
        self.hena_range = 1.2
        self.default_settings['hena_range'] = self.hena_range
        self.hena_increment = 0.05
        self.default_settings['hena_increment'] = self.hena_increment
        self.hena_anim = False
        self.default_settings['hena_anim'] = self.hena_anim
        self.henb_mid = -0.05
        self.default_settings['henb_mid'] = self.henb_mid
        self.henb_range = 0.7
        self.default_settings['henb_range'] = self.henb_range
        self.henb_increment = 0.05
        self.default_settings['henb_increment'] = self.henb_increment
        self.henb_anim = False
        self.default_settings['henb_anim'] = self.henb_anim
        self.max_iter_anim = 10000
        self.default_settings['max_iter_anim'] = self.max_iter_anim
        self.plot_interval_anim = 10000
        self.default_settings['plot_interval_anim'] = self.plot_interval_anim
        self.animation_delay = 999
        self.default_settings['animation_delay'] = self.animation_delay

        # orbit mode settings
        self.orbit_mode = False
        self.default_settings['orbit_mode'] = self.orbit_mode
        self.orbit_parameter = True # true is parameter a; false is parameter b
        self.default_settings['orbit_parameter'] = self.orbit_parameter
        self.orbit_coordinate = True # true is y-coordinate; false is x-coordinate
        self.default_settings['orbit_coordinate'] = self.orbit_coordinate
        self.max_iter_orbit = 500
        self.default_settings['max_iter_orbit'] = self.max_iter_orbit
        self.plot_interval_orbit = 500
        self.default_settings['plot_interval_orbit'] = self.plot_interval_orbit

        # misc settings (not for saving)
        self.first_run = True
        self.full_screen = False
        self.prev_dir_path = ""
        self.animation_running = False
        self.module_opencl_present = module_opencl_present
        self.hena_max = round(self.hena_mid + 0.5*self.hena_range,3)
        self.henb_max = round(self.henb_mid + 0.5*self.henb_range,3)
        
        # program flow controls        
        self.qt_thread0 = QtCore.QThread(self) # Separate Qt thread for generating screen update signals        
        self.qt_thread1 = QtCore.QThread(self) # Separate Qt thread for generating screen pixels

    def on_about(self):
        msg = self.tr("H\xe9non explorer\n\nAuthor: Ronald Naber\nLicense: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)

    def keyPressEvent(self, e):             
        if (e.key() == QtCore.Qt.Key_Escape):
            # exit full-screen mode with escape button or stop calculation
            if (self.full_screen):                
                self.toggle_full_screen()
            else:
                self.stop_user_command()             

    @QtCore.pyqtSlot()
    def update_screen(self):
          
        #self.Henon_widget.updateGL() # for OpenGL Henon widget
        self.Henon_widget.showEvent(QtGui.QShowEvent()) # for PyQt-only Henon widget
        
        if self.animation_running:

            self.statusBar().showMessage("a = " + str('%.3f' % self.hena) + "; b = " + str('%.3f' % self.henb))
            
            if (self.hena_anim):
                new_hena = round(self.hena + self.hena_increment,3)
                if new_hena <= self.hena_max:
                    self.hena = new_hena                
                
            if (self.henb_anim):
                new_henb = round(self.henb + self.henb_increment,3)
                if new_henb <= self.henb_max:
                    self.henb = new_henb         

    def wait_thread_end(self, thread):
        
        while True:            
            if thread.isRunning():
                thread.quit()
            else:
                return

    @QtCore.pyqtSlot()
    def animation_stopped(self):
        if self.animation_running:            
            self.animation_running = False
                
            self.statusBar().showMessage("Animation finished",1000)
    
    @QtCore.pyqtSlot(str)
    def benchmark_result(self,result):
        self.statusBar().showMessage(result,1000)

    def initialize_calculation(self):
        
        # stop any current calculation and make sure
        # threads have finished before proceeding
        self.stop_calculation()
        self.wait_thread_end(self.qt_thread0)
        self.wait_thread_end(self.qt_thread1)          

        self.Henon_widget.clear_screen()
        
        if self.first_run:
            self.first_run = False

        if self.opencl_enabled:
            threads = self.global_work_size
        else:
            threads = self.thread_count

        if self.iter_auto_mode: 
            # set default maximum number of iterations
            # heavily optimized formula for calculating required number of iterations
            # as a function of the number of screen pixels and the x,y space represented by it
            area_factor = (self.xright - self.xleft) * (self.ytop - self.ybottom) / 2.4           
            self.max_iter = int(self.Henon_widget.window_width*self.Henon_widget.window_height/(threads*(area_factor**0.4)))
            self.plot_interval = int(200000/threads)
            
            if self.plot_interval < 10000:
                # avoid low numbers for high thread-count simulations
                self.plot_interval = 10000
            
        if self.plot_interval > self.max_iter: # sanity check
            self.plot_interval = self.max_iter
        
        if (not self.max_iter): # sanity check
            self.max_iter = 1
        
#        print "[MainGui] Window width: " + str(self.Henon_widget.window_width) #DEBUG
#        print "[MainGui] Window height: " + str(self.Henon_widget.window_height) #DEBUG
#        print "[MainGui] Thread count: " + str(self.thread_count) #DEBUG            
#        print "[MainGui] Maximum iterations: " + str(self.max_iter) #DEBUG
#        print "[MainGui] Plot interval for iterations: " + str(self.plot_interval) #DEBUG
        
        # set widget plot area
        self.Henon_widget.xleft = self.xleft
        self.Henon_widget.ytop = self.ytop
        self.Henon_widget.xright = self.xright
        self.Henon_widget.ybottom = self.ybottom
        
        current_settings = self.get_settings()
        current_settings['window_width'] = self.Henon_widget.window_width
        current_settings['window_height'] = self.Henon_widget.window_height
        current_settings['animation_running'] = self.animation_running

        if not self.opencl_enabled and not self.orbit_mode: # for multiprocessing
            # Henon_calc will start workers and wait for stop signal
            self.Henon_calc = HenonCalc(current_settings) 
            # Henon_update will will wait for worker signals and then send screen update signals
            self.Henon_update = HenonUpdate(current_settings,self.Henon_calc.interval_flags,\
                self.Henon_calc.stop_signal, self.Henon_calc.mp_arr, self.Henon_widget.window_representation)
        elif self.opencl_enabled and not self.orbit_mode: # for OpenCL            
            self.Henon_calc = HenonCalc2(current_settings, self.context, self.command_queue, self.mem_flags, self.program)
            self.Henon_update = HenonUpdate2(current_settings, self.Henon_calc.interval_flag,\
                self.Henon_calc.stop_signal, self.Henon_calc.cl_arr, self.Henon_widget.window_representation)
        elif not self.opencl_enabled and self.orbit_mode: # for orbit mode with multiprocessing
            self.Henon_calc = HenonCalcOrbit(current_settings) 
            self.Henon_update = HenonUpdate(current_settings,self.Henon_calc.interval_flags,\
                self.Henon_calc.stop_signal, self.Henon_calc.mp_arr, self.Henon_widget.window_representation)
        elif self.opencl_enabled and self.orbit_mode: # for orbit mode with OpenCL
            self.Henon_calc = HenonCalc2Orbit(current_settings, self.context, self.command_queue, self.mem_flags, self.program)
            self.Henon_update = HenonUpdate2(current_settings, self.Henon_calc.interval_flag,\
                self.Henon_calc.stop_signal, self.Henon_calc.cl_arr, self.Henon_widget.window_representation)
                
        self.Henon_update.moveToThread(self.qt_thread0) # Move updater to separate thread
        self.Henon_calc.moveToThread(self.qt_thread1)
        
        # connecting like this appears crucial to make the thread run independently
        # and prevent GUI freeze
        self.qt_thread0.started.connect(self.Henon_update.run)            
        self.qt_thread1.started.connect(self.Henon_calc.run)

        self.Henon_update.signal.sig.connect(self.update_screen) # Get signal for screen updates
        self.Henon_update.quit_signal.sig.connect(self.qt_thread0.quit) # Quit thread when finished
        self.Henon_update.quit_signal.sig.connect(self.animation_stopped) # Check if animation was running
        self.Henon_calc.quit_signal.sig.connect(self.qt_thread1.quit) # Quit thread when finished

        if self.benchmark:        
            self.Henon_update.benchmark_signal.sig.connect(self.benchmark_result)
        
        self.qt_thread0.start()        
        self.qt_thread1.start()

    def initialize_opencl(self):

        if len(self.device_selection) == 0:
            self.opencl_enabled = False
            msg = self.tr("No OpenCL devices selected. OpenCL function has been turned off automatically.")
            QtGui.QMessageBox.about(self, self.tr("Warning"), msg)
            return

        num = 0
        included_devices = []
        for platform in cl.get_platforms():
            for device in platform.get_devices():
                if num in self.device_selection:
                    included_devices.append(device)
                num += 1
        
        try:
            self.context = cl.Context(devices=included_devices)
        except:
            self.opencl_enabled = False
            msg = self.tr("Current OpenCL device selection does not work. OpenCL function has been turned off automatically.")
            QtGui.QMessageBox.about(self, self.tr("Warning"), msg)
            return

        self.command_queue = cl.CommandQueue(self.context)    
        self.mem_flags = cl.mem_flags
    
        if not self.orbit_mode: # kernel for normal Henon calculations
            try: #uint for 32-bit (ulong for 64-bit not recommended due to much longer execution time)
                self.program = cl.Program(self.context, """
                #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable    
                __kernel void henon(__global double2 *q, __global ushort *window_representation,
                                    __global uint const *int_params, __global double const *float_params)
                {
                    int gid = get_global_id(0);
                    double x,y,xtemp,x_draw,y_draw;
                    x = q[gid].x;
                    y = q[gid].y;
        
                    // drop first set of iterations
                    for(int curiter = 0; curiter < int_params[1]; curiter++) {
                        xtemp = x;
                        x = 1 + y - (float_params[0] * x * x);
                        y = float_params[1] * xtemp;            
                    }
            
                    // perform main Henon calculation and assign pixels into window
                    for(int curiter = 0; curiter < int_params[0]; curiter++) {
                        xtemp = x;
                        x = 1 + y - (float_params[0] * x * x);
                        y = float_params[1] * xtemp;
                        
                        if (x < float_params[2] || y < float_params[3]) { // convert_int cannot deal with negative numbers
                            x_draw = 0;
                            y_draw = 0;
                        }
                        else {
                            x_draw = convert_int_sat((x-float_params[2]) * float_params[4]); // sat modifier avoids NaN problems
                            y_draw = convert_int_sat((y-float_params[3]) * float_params[5]);
                        }
                        
                        if ((0 < x_draw) && (x_draw < int_params[3]) && (0 < y_draw) && (y_draw < int_params[2])) {
                            int location = convert_int(((int_params[2]-y_draw)*int_params[3]) + x_draw); // for top-left origin
                            //int location = convert_int((y_draw*int_params[3]) + x_draw); // for bottom-left origin
                            window_representation[location] = 255;
                        }
                    }
                    
                    q[gid].x = x;
                    q[gid].y = y;
                }
                """).build()
            except:
                self.opencl_enabled = False
                msg = self.tr("Error during OpenCL kernel build. OpenCL function has been turned off automatically.")
                QtGui.QMessageBox.about(self, self.tr("Warning"), msg)
                return
        else: # kernel for orbit map calculations
            try:
                self.program = cl.Program(self.context, """
                #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable    
                __kernel void henon(__global double2 *q, __global ushort *window_representation,
                                    __global uint const *int_params, __global double const *float_params)
                {
                    int gid = get_global_id(0);
                    double x,y,xtemp,y_draw;
                    x = q[gid].x;
                    y = q[gid].y;
    
                    int orbit_parameter,orbit_coordinate;
                    orbit_parameter = int_params[4];
                    orbit_coordinate = int_params[5];
            
                    double a, b;
                    if (orbit_parameter > 0) {
                        a = float_params[2];
                        a = a + gid/float_params[4];
                        b = float_params[1];
                    }
                    else {
                        a = float_params[0];
                        b = float_params[2];
                        b = b + gid/float_params[4];
                    }
        
                    // drop first set of iterations
                    for(int curiter = 0; curiter < int_params[1]; curiter++) {
                        xtemp = x;
                        x = 1 + y - (a * x * x);
                        y = b * xtemp;            
                    }
            
                    // perform main Henon calculation and assign pixels into window
                    for(int curiter = 0; curiter < int_params[0]; curiter++) {
                        xtemp = x;
                        x = 1 + y - (a * x * x);
                        y = b * xtemp;
                        
                        if (orbit_coordinate > 0) {
                            // convert_int cannot deal with negative numbers
                            if (y < float_params[3]) { y_draw = 0; }
                            else { y_draw = convert_int_sat((y-float_params[3]) * float_params[5]); }
                        }
                        else {
                            if (x < float_params[3]) { y_draw = 0; }
                            else { y_draw = convert_int_sat((x-float_params[3]) * float_params[5]); }                    
                        }
                        
                        if ((0 < y_draw) && (y_draw < int_params[2])) {
                            int location = convert_int(((int_params[2]-y_draw)*int_params[3]) + gid);
                            window_representation[location] = 255;
                        }
                    }
                    
                    q[gid].x = x;
                    q[gid].y = y;
                }
                """).build()
            except:
                self.opencl_enabled = False
                msg = self.tr("Error during OpenCL kernel build. OpenCL function has been turned off automatically.")
                QtGui.QMessageBox.about(self, self.tr("Warning"), msg)
                return            

    def initialize_animation(self):
        
        if self.first_run:
            return
            
        if self.orbit_mode:
            self.statusBar().showMessage(self.tr("Animation is not available in orbit map mode"),1000)
            return
        
        if (not self.hena_anim) and (not self.henb_anim):
            # cannot animate if no variables are selected for animation
            return

        self.benchmark = False # make sure status bar can show a/b values

#        print "[MainGui] Starting animation" #DEBUG

        self.stop_calculation()

        a_frames = 0
        b_frames = 0

        if (self.hena_anim):
            self.hena = self.hena_mid - 0.5*self.hena_range
            a_frames = ceil(self.hena_range / self.hena_increment) + 1

        if (self.henb_anim):
            self.henb = self.henb_mid - 0.5*self.henb_range
            b_frames = ceil(self.henb_range / self.henb_increment) + 1

        self.max_iter_anim = max([a_frames,b_frames]) * self.plot_interval_anim
        self.hena_max = round(self.hena_mid + 0.5*self.hena_range,3)
        self.henb_max = round(self.henb_mid + 0.5*self.henb_range,3)
        
        self.animation_running = True

        self.initialize_calculation()
    
    def reset_view(self):       
        self.statusBar().showMessage(self.tr("Resetting view..."), 1000)

        if self.animation_running:
            self.animation_running = False

        if not self.orbit_mode:
            self.xleft = -1.5
            self.ytop = 0.4
            self.xright = 1.5
            self.ybottom = -0.4
        else:
            self.initialize_orbit_mode()
            
        self.initialize_calculation()

    def toggle_full_screen(self):
        self.stop_calculation()
        
        if not self.full_screen: # toggle full screen mode
            self.showFullScreen()
            self.full_screen = True
            self.statusBar().showMessage(self.tr("Press escape to exit full-screen mode"), 1000)             
        else:
            self.showNormal()
            self.full_screen = False
        return            

    def restart_calculation(self):      
        self.statusBar().showMessage(self.tr("Restarting..."), 1000)
        self.initialize_calculation()

    def stop_calculation(self):
        if (not self.first_run):
            self.Henon_calc.stop()

    def stop_user_command(self):
        self.statusBar().showMessage(self.tr("Sending stop signal..."), 1000)
        
        if self.animation_running:
            self.animation_running = False
            
        self.stop_calculation()       

    def toggle_benchmark(self):
        self.benchmark = not self.benchmark
        
        if self.benchmark:
            self.statusBar().showMessage(self.tr("Benchmarking turned on"),1000)
        else:
            self.statusBar().showMessage(self.tr("Benchmarking turned off"),1000)

    def toggle_orbit_mode(self):

        if self.animation_running:
            self.statusBar().showMessage(self.tr("Orbit mode is not available during animation"),1000)
            return
        
        if self.orbit_mode:
            self.orbit_mode = False
            if self.opencl_enabled:
                self.initialize_opencl()            
            self.reset_view()
            return
                
        self.orbit_mode = True
        self.initialize_orbit_mode()
        if self.opencl_enabled:
            self.initialize_opencl()

        self.initialize_calculation()
        self.statusBar().showMessage(self.tr("Press O to exit orbit map mode"),1000)

    def initialize_orbit_mode(self):
        if self.orbit_parameter: # parameter a
            self.xleft = 0.9
            self.xright = 1.4                
        else: # parameter b
            self.xleft = -0.3
            self.xright = 0.3

        if self.orbit_coordinate: # y-coordinate
            self.ytop = 0.4
            self.ybottom = -0.4
        else: # x-coordinate
            self.ytop = 1.5
            self.ybottom = -1.5        

    def closeEvent(self, event):
        # call stop function in order to terminate calculation processes
        # processes will continue after window close otherwise
        self.stop_calculation()

    def open_help_dialog(self):
        help_dialog = HenonHelp(self)
        help_dialog.setModal(True)
        help_dialog.show()        

    def open_settings_dialog(self):            
        settings_dialog = HenonSettings(self)
        settings_dialog.setModal(True)
        settings_dialog.show() 

    def load_settings(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,self.tr("Open file"), self.prev_dir_path, "Settings Files (*.conf)")
        
        if (not filename):
            return

        if (not os.path.isfile(filename.toAscii())):
            msg = self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            QtGui.QMessageBox.about(self, self.tr("Warning"), msg) 
            return
        
        self.prev_dir_path = ntpath.dirname(str(filename))
        
        with open(str(filename)) as f:
            all_settings = pickle.load(f)

        self.implement_settings(all_settings)
            
        self.statusBar().showMessage(self.tr("New settings loaded"),1000)
    
    def save_settings(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,self.tr("Save file"), self.prev_dir_path, "Settings Files (*.conf)")
        
        if (not filename):
            return

        # Check for non-ASCII here does not seem to work        
        self.prev_dir_path = ntpath.dirname(str(filename))

        current_settings = self.get_settings()
        
        with open(str(filename), 'w') as f:
            pickle.dump(current_settings, f)
            
        self.statusBar().showMessage(self.tr("File saved"),1000) 

    def load_default_settings(self):
        self.implement_settings(self.default_settings)
        self.statusBar().showMessage(self.tr("Default settings loaded"),1000)

    def get_settings(self):
        settings = {}
        settings['hena'] = self.hena
        settings['henb'] = self.henb
        settings['xleft'] = self.xleft
        settings['ytop'] = self.ytop
        settings['xright'] = self.xright
        settings['ybottom'] = self.ybottom
        settings['opencl_enabled'] = self.opencl_enabled
        settings['device_selection'] = self.device_selection
        settings['thread_count'] = self.thread_count
        settings['global_work_size'] = self.global_work_size
        settings['plot_interval'] = self.plot_interval
        settings['max_iter'] = self.max_iter
        settings['drop_iter'] = self.drop_iter
        settings['iter_auto_mode'] = self.iter_auto_mode
        settings['enlarge_rare_pixels'] = self.enlarge_rare_pixels
        settings['benchmark'] = self.benchmark
        settings['hena_mid'] = self.hena_mid
        settings['hena_range'] = self.hena_range
        settings['hena_increment'] = self.hena_increment
        settings['hena_anim'] = self.hena_anim
        settings['henb_mid'] = self.henb_mid
        settings['henb_range'] = self.henb_range
        settings['henb_increment'] = self.henb_increment
        settings['henb_anim'] = self.henb_anim
        settings['max_iter_anim'] = self.max_iter_anim
        settings['plot_interval_anim'] = self.plot_interval_anim 
        settings['animation_delay'] = self.animation_delay
        settings['orbit_mode'] = self.orbit_mode
        settings['orbit_parameter'] = self.orbit_parameter
        settings['orbit_coordinate'] = self.orbit_coordinate
        settings['max_iter_orbit'] = self.max_iter_orbit
        settings['plot_interval_orbit'] = self.plot_interval_orbit        
        return settings
    
    def implement_settings(self,settings):
        self.stop_calculation()
        
        self.hena = settings['hena']
        self.henb = settings['henb']
        self.xleft = settings['xleft']
        self.ytop = settings['ytop']
        self.xright = settings['xright']
        self.ybottom = settings['ybottom']
        if self.module_opencl_present:
            self.opencl_enabled = settings['opencl_enabled']
        else:
            self.opencl_enabled = False
        self.device_selection = settings['device_selection']
        self.thread_count = settings['thread_count']
        self.global_work_size = settings['global_work_size']
        self.plot_interval = settings['plot_interval']
        self.max_iter = settings['max_iter']
        self.drop_iter = settings['drop_iter']
        self.iter_auto_mode = settings['iter_auto_mode']
        self.enlarge_rare_pixels = settings['enlarge_rare_pixels']
        self.benchmark = settings['benchmark']
        self.hena_mid = settings['hena_mid']
        self.hena_range = settings['hena_range']
        self.hena_increment = settings['hena_increment']
        self.hena_anim = settings['hena_anim']
        self.henb_mid = settings['henb_mid']
        self.henb_range = settings['henb_range']
        self.henb_increment = settings['henb_increment']
        self.henb_anim = settings['henb_anim']
        self.max_iter_anim = settings['max_iter_anim']
        self.plot_interval_anim = settings['plot_interval_anim']
        self.animation_delay = settings['animation_delay']
        self.orbit_mode = settings['orbit_mode']
        self.orbit_parameter = settings['orbit_parameter']
        self.orbit_coordinate = settings['orbit_coordinate']
        self.max_iter_orbit = settings['max_iter_orbit']
        self.plot_interval_orbit = settings['plot_interval_orbit']

        if self.module_opencl_present:
            if self.opencl_enabled:
                self.initialize_opencl()

    def create_main_frame(self):
        
        self.Henon_widget = HenonWidget(self)
        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setMargin(0)
        vbox.addWidget(self.Henon_widget)

        main_frame = QtGui.QWidget()
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

        self.status_text = QtGui.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr(""))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))         

        tip = self.tr("Load settings")        
        load_action = QtGui.QAction(self.tr("Load settings"), self)
        load_action.setIcon(QtGui.QIcon(":open.png"))
        load_action.triggered.connect(self.load_settings)        
        load_action.setToolTip(tip)
        load_action.setStatusTip(tip)
        load_action.setShortcut('CTRL+L')

        tip = self.tr("Save settings")        
        save_action = QtGui.QAction(self.tr("Save settings"), self)
        save_action.setIcon(QtGui.QIcon(":save.png"))
        save_action.triggered.connect(self.save_settings)        
        save_action.setToolTip(tip)
        save_action.setStatusTip(tip)
        save_action.setShortcut('CTRL+S')

        tip = self.tr("Change settings")        
        settings_action = QtGui.QAction(self.tr("Change settings"), self)
        settings_action.setIcon(QtGui.QIcon(":gear.png"))
        settings_action.triggered.connect(self.open_settings_dialog)        
        settings_action.setToolTip(tip)
        settings_action.setStatusTip(tip)
        settings_action.setShortcut('S')

        tip = self.tr("Default settings")        
        default_action = QtGui.QAction(self.tr("Default settings"), self)
        default_action.setIcon(QtGui.QIcon(":revert.png"))
        default_action.triggered.connect(self.load_default_settings)        
        default_action.setToolTip(tip)
        default_action.setStatusTip(tip)
        default_action.setShortcut('D')

        tip = self.tr("Quit")        
        quit_action = QtGui.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)        
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Q')

        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(settings_action)
        self.file_menu.addAction(default_action)        
        self.file_menu.addAction(quit_action)
        
        self.run_menu = self.menuBar().addMenu(self.tr("Run"))      

        tip = self.tr("Re-draw screen")        
        start_action = QtGui.QAction(self.tr("Re-draw"), self)
        start_action.setIcon(QtGui.QIcon(":redo.png"))
        start_action.triggered.connect(self.restart_calculation)        
        start_action.setToolTip(tip)
        start_action.setStatusTip(tip)
        start_action.setShortcut('R')

        tip = self.tr("Stop")        
        stop_action = QtGui.QAction(self.tr("Stop"), self)
        stop_action.setIcon(QtGui.QIcon(":stop.png"))
        stop_action.triggered.connect(self.stop_user_command)        
        stop_action.setToolTip(tip)
        stop_action.setStatusTip(tip)
        stop_action.setShortcut('X')

        tip = self.tr("Animate")        
        animate_action = QtGui.QAction(self.tr("Animate"), self)
        animate_action.setIcon(QtGui.QIcon(":play.png"))
        animate_action.triggered.connect(self.initialize_animation)        
        animate_action.setToolTip(tip)
        animate_action.setStatusTip(tip)
        animate_action.setShortcut('A')

        tip = self.tr("Benchmark")        
        benchmark_action = QtGui.QAction(self.tr("Benchmark"), self)
        benchmark_action.setIcon(QtGui.QIcon(":clock.png"))
        benchmark_action.triggered.connect(self.toggle_benchmark)        
        benchmark_action.setToolTip(tip)
        benchmark_action.setStatusTip(tip)
        benchmark_action.setShortcut('B')

        self.run_menu.addAction(start_action)
        self.run_menu.addAction(stop_action)        
        self.run_menu.addAction(animate_action)
        self.run_menu.addAction(benchmark_action)

        self.view_menu = self.menuBar().addMenu(self.tr("View"))

        tip = self.tr("Reset view")        
        reset_action = QtGui.QAction(self.tr("Reset view"), self)
        reset_action.setIcon(QtGui.QIcon(":revert.png"))
        reset_action.triggered.connect(self.reset_view)         
        reset_action.setToolTip(tip)
        reset_action.setStatusTip(tip)
        reset_action.setShortcut('F5')

        tip = self.tr("Orbit map")        
        orbit_action = QtGui.QAction(self.tr("Orbit map"), self)
        orbit_action.triggered.connect(self.toggle_orbit_mode)         
        orbit_action.setToolTip(tip)
        orbit_action.setStatusTip(tip)
        orbit_action.setShortcut('O')

        tip = self.tr("Full-screen")        
        fullscreen_action = QtGui.QAction(self.tr("Full-screen"), self)
        fullscreen_action.setIcon(QtGui.QIcon(":expand.png"))
        fullscreen_action.triggered.connect(self.toggle_full_screen)         
        fullscreen_action.setToolTip(tip)
        fullscreen_action.setStatusTip(tip)
        fullscreen_action.setShortcut('F')

        self.view_menu.addAction(reset_action)
        self.view_menu.addAction(orbit_action)
        self.view_menu.addAction(fullscreen_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("Help information")        
        help_action = QtGui.QAction(self.tr("Help..."), self)
        help_action.setIcon(QtGui.QIcon(":help.png"))
        help_action.triggered.connect(self.open_help_dialog)         
        help_action.setToolTip(tip)
        help_action.setStatusTip(tip)
        help_action.setShortcut('H')

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(help_action)
        self.help_menu.addAction(about_action)
