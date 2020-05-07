# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui
import HenonResources
from HenonWidget import HenonWidget # for PyQt-only Henon widget
from HenonUpdate import HenonUpdate
from HenonCalc import HenonCalc
from HenonHelp import HenonHelp
from HenonSettings import HenonSettings
from multiprocessing import cpu_count
import ntpath, pickle
from math import ceil

try:
    # check if PyOpenCL is present as it is optional
    import pyopencl as cl
    from HenonCalc2 import HenonCalc2
    module_opencl_present = True
except ImportError:
    module_opencl_present = False

class StopSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)

class MainGui(QtWidgets.QMainWindow):
    # Main user interface; starts up main window and initiates a first Henon calculation
    # and then waits for user input
    
    def __init__(self, parent=None):
        
        super(MainGui, self).__init__(parent)
        
        self.setWindowTitle(self.tr("H\xe9non browser"))
        self.setWindowIcon(QtGui.QIcon(":HenonBrowser.png"))

        ### Set initial geometry and center the window on the screen ###
        self.resize(1024, 576)
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())        
        
        ### Set default font size ###
        self.setStyleSheet('font-size: 12pt;')         

        self.default_settings = {} # put parameters in dict for easy saving/loading
        self.previous_views = [] # previous zoom-in view settings
        
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
        self.color = 0
        self.default_settings['color'] = self.color
        self.color_options = ['white','blue','red','green','orange','purple','light blue']
        self.super_sampling = 0
        self.default_settings['super_sampling'] = self.super_sampling
        self.super_sampling_options = ['1x','2x','4x','8x']
        self.resize_method = 0
        self.default_settings['resize_method'] = self.resize_method
        
        # calculation settings        
        self.opencl_enabled = False
        self.default_settings['opencl_enabled'] = self.opencl_enabled
        self.device_selection = [] # selected OpenCL devices
        self.default_settings['device_selection'] = self.device_selection
        
        self.thread_count = cpu_count()
        self.default_settings['thread_count'] = self.thread_count
        self.global_work_size = 8
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
        self.orbit_multiplier = 0
        self.default_settings['orbit_multiplier'] = self.orbit_multiplier
        
        # animation settings
        self.hena_start = 0.8
        self.default_settings['hena_start'] = self.hena_start
        self.hena_stop = 1.4
        self.default_settings['hena_stop'] = self.hena_stop
        self.hena_increment = 0.01
        self.default_settings['hena_increment'] = self.hena_increment
        self.hena_anim = True
        self.default_settings['hena_anim'] = self.hena_anim
        self.henb_start = 0
        self.default_settings['henb_start'] = self.henb_start
        self.henb_stop = 0.3
        self.default_settings['henb_stop'] = self.henb_stop
        self.henb_increment = 0.01
        self.default_settings['henb_increment'] = self.henb_increment
        self.henb_anim = False
        self.default_settings['henb_anim'] = self.henb_anim
        self.max_iter_anim = 30000
        self.default_settings['max_iter_anim'] = self.max_iter_anim
        self.plot_interval_anim = 30000
        self.default_settings['plot_interval_anim'] = self.plot_interval_anim
        self.animation_delay = 20
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
        self.plot_interval_orbit = 100
        self.default_settings['plot_interval_orbit'] = self.plot_interval_orbit
        self.iter_auto_mode_orbit = True
        self.default_settings['iter_auto_mode_orbit'] = self.iter_auto_mode_orbit

        # misc settings (not for saving)
        self.first_run = True
        self.full_screen = False
        self.prev_dir_path = ""
        self.animation_running = False
        self.module_opencl_present = module_opencl_present
        self.enable_arrow_keys = False
        
        self.create_menu()
        self.create_main_frame()

    def on_about(self):
        msg = self.tr("H\xe9non browser\nAuthor: Ronald Naber\nLicense: Public domain")
        QtWidgets.QMessageBox.about(self, self.tr("About the application"), msg)

    def keyPressEvent(self, e):             
        if (e.key() == QtCore.Qt.Key_Escape):
            # exit full-screen mode with escape button or stop calculation
            if (self.full_screen):                
                self.toggle_full_screen()
            else:
                self.stop_user_command()
        elif (e.key() == QtCore.Qt.Key_Up):
            if self.enable_arrow_keys:
                self.increase_hena()
        elif (e.key() == QtCore.Qt.Key_Down):
            if self.enable_arrow_keys:
                self.decrease_hena()
        elif (e.key() == QtCore.Qt.Key_Left):
            if self.enable_arrow_keys:
                self.decrease_henb()
        elif (e.key() == QtCore.Qt.Key_Right):
            if self.enable_arrow_keys:
                self.increase_henb()        

    @QtCore.pyqtSlot()
    def update_screen(self):
        #print("[MainGui] Updating screen")
        
        self.Henon_widget.showEvent(QtGui.QShowEvent()) # for PyQt-only Henon widget

    def wait_thread_end(self, thread):
        
        while True:            
            if thread.isRunning():
                thread.quit()
            else:
                return

    @QtCore.pyqtSlot(str)
    def updates_stopped(self,result):          
        
        message = "Computation finished"
        
        if self.benchmark:
            message = "Computation finished in " + str(result)
        
        self.statusBar().showMessage(message,1000)
        self.animation_running = False            

    def initialize_calculation(self):
        
        #print("[MainGui] Initializing calculation")
        
        # stop any current calculation and make sure
        # threads have finished before proceeding
        self.stop_calculation()
        
        if not self.first_run:
            self.wait_thread_end(self.Henon_update)
            self.wait_thread_end(self.Henon_calc)          
        
        if self.first_run:
            self.first_run = False

        if self.opencl_enabled and self.orbit_mode:
            threads = self.Henon_widget.window_width*pow(2,self.orbit_multiplier)
        elif self.opencl_enabled:
            threads = pow(2,self.global_work_size)
        else:
            threads = self.thread_count

        #print("[MainGui] Thread count: " + str(threads))

        if not self.orbit_mode:
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
                
            #print("[MainGui] Maximum iterations: " + str(self.max_iter))
            #print("[MainGui] Plot interval for iterations: " + str(self.plot_interval))                 
        else:
            if self.iter_auto_mode_orbit:
                if self.orbit_coordinate:
                    range_factor = (self.ytop - self.ybottom) / 0.8
                else:
                    range_factor = (self.ytop - self.ybottom) / 3.0
                    
                #self.max_iter_orbit = int(self.Henon_widget.window_height/(range_factor**0.5))
                self.max_iter_orbit = int(self.Henon_widget.window_height/(pow(2,self.orbit_multiplier)*(range_factor**0.5)))
                self.plot_interval_orbit = self.max_iter_orbit

            if self.plot_interval_orbit > self.max_iter_orbit: # sanity check
                self.plot_interval_orbit = self.max_iter_orbit
            
            if (not self.max_iter_orbit): # sanity check
                self.max_iter_orbit = 1
                
            #print("[MainGui] Maximum iterations: " + str(self.max_iter_orbit))
            #print("[MainGui] Plot interval for iterations: " + str(self.plot_interval_orbit))   
        
        #print("[MainGui] Window width: " + str(self.Henon_widget.window_width))
        #print("[MainGui] Window height: " + str(self.Henon_widget.window_height))
        
        # set widget plot area
        self.Henon_widget.xleft = self.xleft
        self.Henon_widget.ytop = self.ytop
        self.Henon_widget.xright = self.xright
        self.Henon_widget.ybottom = self.ybottom
        self.Henon_widget.window_representation[:] = 0
        
        current_settings = self.get_settings()
        current_settings['window_width'] = self.Henon_widget.window_width
        current_settings['window_height'] = self.Henon_widget.window_height
        current_settings['animation_running'] = self.animation_running

        if not self.opencl_enabled: # for multiprocessing            
            self.Henon_calc = HenonCalc(current_settings) # Henon_calc will start workers and wait for stop signal
        else: # for OpenCL            
            self.Henon_calc = HenonCalc2(current_settings, self.context, self.command_queue, self.mem_flags, self.program)

        # Henon_update will wait for worker signals and then send screen update signals
        self.Henon_update = HenonUpdate(current_settings,self.Henon_calc.interval_flags,\
                self.Henon_calc.stop_signal, self.Henon_calc.array, self.Henon_widget.window_representation)
        
        self.stop_signal = StopSignal()
        self.stop_signal.sig.connect(self.Henon_calc.stop)
        self.Henon_update.signal.sig.connect(self.update_screen) # Get signal for screen updates
        self.Henon_update.updates_stopped.sig.connect(self.updates_stopped) # Check if animation was running
        self.Henon_widget.signal.sig.connect(self.Henon_update.screen_update_finished) # Screen update is finished        
        
        #print("[MainGui] Starting calculations")
        self.Henon_calc.start()        
        self.Henon_update.start()

    def initialize_opencl(self):

        if len(self.device_selection) == 0:
            self.opencl_enabled = False
            msg = self.tr("No OpenCL devices selected. OpenCL function has been turned off automatically.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
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
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
            return

        self.command_queue = cl.CommandQueue(self.context)    
        self.mem_flags = cl.mem_flags
        '''

                __kernel void henon(__global double2 *q, __global ushort *local_array,
                                    __global uint const *int_params, __global double const *float_params)
        '''
        if not self.orbit_mode: # kernel for normal Henon calculations
            try: #uint for 32-bit (ulong for 64-bit not recommended due to much longer execution time)
                self.program = cl.Program(self.context, """
                #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable    
                __kernel void henon(__global double2 *q, __global bool *local_array,
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
                            local_array[location] = 1;
                        }
                    }
                    
                    q[gid].x = x;
                    q[gid].y = y;
                }
                """).build()
            except:
                self.opencl_enabled = False
                msg = self.tr("Error during OpenCL kernel build. OpenCL function has been turned off automatically.")
                QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
                return
        else: # kernel for orbit map calculations
            try:
                #__kernel void henon(__global double2 *q, __global ushort *window_representation,
                #                    __global uint const *int_params, __global double const *float_params)                
                
                self.program = cl.Program(self.context, """
                #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable    
                __kernel void henon(__global double2 *q, __global bool *local_array,
                                    __global uint const *int_params, __global double const *float_params)
                {
                    int gid = get_global_id(0);
                    double x,y,xtemp,y_draw;
                    x = q[gid].x;
                    y = q[gid].y;
    
                    int orbit_parameter,orbit_coordinate,orbit_multiplier,pos;
                    orbit_parameter = int_params[4];
                    orbit_coordinate = int_params[5];
                    orbit_multiplier = int_params[6];
                    pos = gid/orbit_multiplier;
            
                    double a, b;
                    if (orbit_parameter > 0) {
                        a = float_params[2];
                        a = a + pos/float_params[4];
                        b = float_params[1];
                    }
                    else {
                        a = float_params[0];
                        b = float_params[2];
                        b = b + pos/float_params[4];
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
                            int location = convert_int(((int_params[2]-y_draw)*int_params[3]) + pos);
                            local_array[location] = 1;
                        }
                    }
                    
                    q[pos].x = x;
                    q[pos].y = y;
                }
                """).build()
            except:
                self.opencl_enabled = False
                msg = self.tr("Error during OpenCL kernel build. OpenCL function has been turned off automatically.")
                QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
                return            

    def initialize_animation(self):
        
        if self.first_run:
            return
        
        if self.animation_running:
            return

        if (not self.hena_anim) and (not self.henb_anim):
            # cannot animate if no variables are selected for animation
            self.statusBar().showMessage(self.tr("No parameter selected for animation"),1000)
            return
            
        if self.orbit_mode: # check that selected animation parameter is consistent with orbit map
            if self.hena_anim and self.orbit_parameter:
                self.statusBar().showMessage(self.tr("Set animation parameter is the same as orbit map parameter"),1000)
                return
        
            if self.henb_anim and not self.orbit_parameter:
                self.statusBar().showMessage(self.tr("Set animation parameter is the same as orbit map parameter"),1000)
                return                

        #print("[MainGui] Starting animation")

        self.stop_calculation()

        a_frames = 0
        b_frames = 0

        if (self.hena_anim):
            a_frames = abs(ceil((self.hena_stop - self.hena_start) / self.hena_increment) + 1)

        if (self.henb_anim):
            b_frames = abs(ceil((self.henb_stop - self.henb_start) / self.henb_increment) + 1)

        if not self.orbit_mode:
            self.max_iter_anim = max([a_frames,b_frames]) * self.plot_interval_anim
        else:
            self.max_iter_anim = max([a_frames,b_frames]) * self.plot_interval_orbit
        
        self.animation_running = True

        self.initialize_calculation()
    
    def reset_view(self):        
        self.previous_views = [] # empty previous zoom-in view list

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

    def increase_hena(self):        

        if not round(self.hena+0.05,3) > 2:
            self.hena = round(self.hena+0.05,3)        
            self.initialize_calculation()
        
        self.statusBar().showMessage("a = " + str(self.hena), 1000)

    def decrease_hena(self):        

        if not round(self.hena-0.05,3) < 0:
            self.hena = round(self.hena-0.05,3)        
            self.initialize_calculation()
        
        self.statusBar().showMessage("a = " + str(self.hena), 1000)

    def increase_henb(self):        

        if not round(self.henb+0.05,3) > 1:
            self.henb = round(self.henb+0.05,3)        
            self.initialize_calculation()
        
        self.statusBar().showMessage("b = " + str(self.henb), 1000)

    def decrease_henb(self):        

        if not round(self.henb-0.05,3) < -1:
            self.henb = round(self.henb-0.05,3)        
            self.initialize_calculation()
        
        self.statusBar().showMessage("b = " + str(self.henb), 1000)

    def previous_view(self):
        if not len(self.previous_views):
            self.statusBar().showMessage(self.tr("No previous view available"), 1000)
            return

        if self.animation_running:
            self.animation_running = False

        self.xleft = self.previous_views[-1][0]
        self.xright = self.previous_views[-1][1]
        self.ybottom = self.previous_views[-1][2]
        self.ytop = self.previous_views[-1][3]
            
        self.previous_views.pop()
        self.initialize_calculation()

    def toggle_full_screen(self):
        self.stop_calculation()
        
        if not self.full_screen: # toggle full screen mode
            self.showFullScreen()
            self.full_screen = True
            self.statusBar().showMessage(self.tr("Press Escape to exit full-screen mode"), 1000)             
        else:
            self.showNormal()
            self.full_screen = False
        return            

    def restart_calculation(self):      
        self.statusBar().showMessage(self.tr("Restarting..."), 1000)
        self.initialize_calculation()

    def stop_calculation(self):
        if not self.first_run:
            self.stop_signal.sig.emit()

    def stop_user_command(self):
        self.statusBar().showMessage(self.tr("Sending stop signal..."), 1000)
        
        if self.animation_running:
            self.animation_running = False
            
        self.stop_calculation()       

    def toggle_benchmark(self):
        if self.animation_running:
            return
        
        self.benchmark = not self.benchmark
        
        if self.benchmark:
            self.statusBar().showMessage(self.tr("Benchmarking turned on"),1000)
        else:
            self.statusBar().showMessage(self.tr("Benchmarking turned off"),1000)

    def toggle_orbit_mode(self):

        if self.animation_running:
            return

        self.previous_views = [] # empty previous zoom-in view list
        
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

    def toggle_arrow_keys(self):
        if self.animation_running:
            return
        
        self.enable_arrow_keys = not self.enable_arrow_keys
        
        if self.enable_arrow_keys:
            self.statusBar().showMessage(self.tr("Arrow keys enabled"),1000)
        else:
            self.statusBar().showMessage(self.tr("Arrow keys disabled"),1000)

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

    def zoom_out(self):
        if self.animation_running:
            return
        
        if not self.orbit_mode:
            self.xleft = -3
            self.ytop = 0.8
            self.xright = 3
            self.ybottom = -0.8
        else:
            if self.orbit_coordinate: # y-coordinate
                self.ytop = 0.8
                self.ybottom = -0.8
            else: # x-coordinate
                self.ytop = 3
                self.ybottom = -3        
        
        self.restart_calculation()

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
        if self.animation_running:
            self.stop_user_command()
        
        filename = QtWidgets.QFileDialog.getOpenFileName(self,self.tr("Open file"), self.prev_dir_path, "Settings Files (*.conf)")
        filename = filename[0]
        
        if (not filename):
            return

        try:
            filename.encode('ascii')
        except:
            msg = self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg) 
            return
        
        self.prev_dir_path = ntpath.dirname(str(filename))
        
        with open(str(filename), 'rb') as f:
            all_settings = pickle.load(f)

        self.implement_settings(all_settings)

        # trigger resize event to force implementation of super-sampling setting
        self.Henon_widget.trigger_resizeEvent()    
        #self.initialize_calculation()
            
        self.statusBar().showMessage(self.tr("New settings loaded"),1000)
    
    def save_settings(self):
        if self.animation_running:
            self.stop_user_command()        
        
        filename = QtWidgets.QFileDialog.getSaveFileName(self,self.tr("Save file"), self.prev_dir_path, "Settings Files (*.conf)")
        filename = filename[0]
        
        if (not filename):
            return

        try:
            filename.encode('ascii')
        except:
            msg = self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg) 
            return
        
        self.prev_dir_path = ntpath.dirname(str(filename))

        current_settings = self.get_settings()
        
        with open(str(filename), 'wb') as f:
            pickle.dump(current_settings, f)
            
        self.statusBar().showMessage(self.tr("File saved"),1000) 

    def load_default_settings(self):
        self.implement_settings(self.default_settings)
        self.statusBar().showMessage(self.tr("Default settings loaded"),1000)

    def save_image(self):
        if self.animation_running:
            self.stop_user_command()
        
        save_path = QtWidgets.QFileDialog.getSaveFileName(self,self.tr("Save file"), "", "PNG File (*.png)")
        save_path = save_path[0]
                
        if not save_path:
            return
        
        self.Henon_widget.save_image(save_path,self.color)
        
        self.statusBar().showMessage(self.tr("File saved"),1000)

    def get_settings(self):

        settings = {}
        
        try:
            settings['hena'] = self.hena
            settings['henb'] = self.henb
            settings['xleft'] = self.xleft
            settings['ytop'] = self.ytop
            settings['xright'] = self.xright
            settings['ybottom'] = self.ybottom
            settings['color'] = self.color
            settings['super_sampling'] = self.super_sampling        
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
            settings['hena_start'] = self.hena_start
            settings['hena_stop'] = self.hena_stop
            settings['hena_increment'] = self.hena_increment
            settings['hena_anim'] = self.hena_anim
            settings['henb_start'] = self.henb_start
            settings['henb_stop'] = self.henb_stop
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
            settings['iter_auto_mode_orbit'] = self.iter_auto_mode_orbit
            settings['orbit_multiplier'] = self.orbit_multiplier
            settings['resize_method'] = self.resize_method
        except:
            msg = self.tr("An error occurred while retrieving settings.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
        
        return settings
    
    def implement_settings(self,settings):
        self.stop_calculation()
        
        try:
            self.hena = settings['hena']
            self.henb = settings['henb']
            self.xleft = settings['xleft']
            self.ytop = settings['ytop']
            self.xright = settings['xright']
            self.ybottom = settings['ybottom']
            self.color = settings['color']
            self.super_sampling = settings['super_sampling']        
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
            self.hena_start = settings['hena_start']
            self.hena_stop = settings['hena_stop']
            self.hena_increment = settings['hena_increment']
            self.hena_anim = settings['hena_anim']
            self.henb_start = settings['henb_start']
            self.henb_stop = settings['henb_stop']
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
            self.iter_auto_mode_orbit = settings['iter_auto_mode_orbit']       
            self.orbit_multiplier = settings['orbit_multiplier']
            self.resize_method = settings['resize_method']
        except:
            msg = self.tr("An error occurred while implementing settings.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)                

        if self.module_opencl_present:
            if self.opencl_enabled:
                self.initialize_opencl() 

    def create_main_frame(self):
        
        self.Henon_widget = HenonWidget(self)
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0,0,0,0) # .setMargin(0)
        vbox.addWidget(self.Henon_widget)

        main_frame = QtWidgets.QWidget()
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

        self.status_text = QtWidgets.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr(""))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))         

        tip = self.tr("Load settings")        
        load_action = QtWidgets.QAction(self.tr("Load settings"), self)
        load_action.setIcon(QtGui.QIcon(":open.png"))
        load_action.triggered.connect(self.load_settings)        
        load_action.setToolTip(tip)
        load_action.setStatusTip(tip)

        tip = self.tr("Save settings")        
        save_action = QtWidgets.QAction(self.tr("Save settings"), self)
        save_action.setIcon(QtGui.QIcon(":save.png"))
        save_action.triggered.connect(self.save_settings)        
        save_action.setToolTip(tip)
        save_action.setStatusTip(tip)

        tip = self.tr("Change settings")        
        settings_action = QtWidgets.QAction(self.tr("Change settings"), self)
        settings_action.setIcon(QtGui.QIcon(":gear.png"))
        settings_action.triggered.connect(self.open_settings_dialog)        
        settings_action.setToolTip(tip)
        settings_action.setStatusTip(tip)
        settings_action.setShortcut('S')

        tip = self.tr("Default settings")        
        default_action = QtWidgets.QAction(self.tr("Default settings"), self)
        default_action.setIcon(QtGui.QIcon(":revert.png"))
        default_action.triggered.connect(self.load_default_settings)        
        default_action.setToolTip(tip)
        default_action.setStatusTip(tip)

        tip = self.tr("Save image")        
        img_action = QtWidgets.QAction(self.tr("Save image"), self)
        img_action.setIcon(QtGui.QIcon(":save.png"))
        img_action.triggered.connect(self.save_image)        
        img_action.setToolTip(tip)
        img_action.setStatusTip(tip)
        img_action.setShortcut('CTRL+S')

        tip = self.tr("Quit")        
        quit_action = QtWidgets.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)        
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Q')

        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(settings_action)
        self.file_menu.addAction(default_action)        
        self.file_menu.addAction(img_action)         
        self.file_menu.addAction(quit_action)
        
        self.run_menu = self.menuBar().addMenu(self.tr("Run"))      

        tip = self.tr("Re-draw screen")        
        start_action = QtWidgets.QAction(self.tr("Re-draw"), self)
        start_action.setIcon(QtGui.QIcon(":redo.png"))
        start_action.triggered.connect(self.restart_calculation)        
        start_action.setToolTip(tip)
        start_action.setStatusTip(tip)
        start_action.setShortcut('R')

        tip = self.tr("Stop")        
        stop_action = QtWidgets.QAction(self.tr("Stop"), self)
        stop_action.setIcon(QtGui.QIcon(":stop.png"))
        stop_action.triggered.connect(self.stop_user_command)        
        stop_action.setToolTip(tip)
        stop_action.setStatusTip(tip)
        stop_action.setShortcut('X')

        tip = self.tr("Animate")        
        animate_action = QtWidgets.QAction(self.tr("Animate"), self)
        animate_action.setIcon(QtGui.QIcon(":play.png"))
        animate_action.triggered.connect(self.initialize_animation)        
        animate_action.setToolTip(tip)
        animate_action.setStatusTip(tip)
        animate_action.setShortcut('A')

        tip = self.tr("Benchmark")        
        benchmark_action = QtWidgets.QAction(self.tr("Benchmark"), self)
        benchmark_action.setIcon(QtGui.QIcon(":clock.png"))
        benchmark_action.triggered.connect(self.toggle_benchmark)        
        benchmark_action.setToolTip(tip)
        benchmark_action.setStatusTip(tip)
        benchmark_action.setShortcut('B')

        tip = self.tr("Arrow keys")        
        arrow_keys_action = QtWidgets.QAction(self.tr("Arrow keys"), self)
        arrow_keys_action.setIcon(QtGui.QIcon(":arrows.png"))
        arrow_keys_action.triggered.connect(self.toggle_arrow_keys)        
        arrow_keys_action.setToolTip(tip)
        arrow_keys_action.setStatusTip(tip)
        arrow_keys_action.setShortcut('K')

        self.run_menu.addAction(start_action)
        self.run_menu.addAction(stop_action)        
        self.run_menu.addAction(arrow_keys_action)        
        self.run_menu.addAction(animate_action)
        self.run_menu.addAction(benchmark_action)

        self.view_menu = self.menuBar().addMenu(self.tr("View"))

        tip = self.tr("Reset view")        
        reset_action = QtWidgets.QAction(self.tr("Reset view"), self)
        reset_action.setIcon(QtGui.QIcon(":revert.png"))
        reset_action.triggered.connect(self.reset_view)         
        reset_action.setToolTip(tip)
        reset_action.setStatusTip(tip)
        reset_action.setShortcut('F5')

        tip = self.tr("Orbit map")        
        orbit_action = QtWidgets.QAction(self.tr("Orbit map"), self)
        orbit_action.triggered.connect(self.toggle_orbit_mode)         
        orbit_action.setToolTip(tip)
        orbit_action.setStatusTip(tip)
        orbit_action.setShortcut('O')

        tip = self.tr("Full-screen")        
        fullscreen_action = QtWidgets.QAction(self.tr("Full-screen"), self)
        fullscreen_action.setIcon(QtGui.QIcon(":expand.png"))
        fullscreen_action.triggered.connect(self.toggle_full_screen)         
        fullscreen_action.setToolTip(tip)
        fullscreen_action.setStatusTip(tip)
        fullscreen_action.setShortcut('F')
        
        tip = self.tr("Zoom out")        
        zoomout_action = QtWidgets.QAction(self.tr("Zoom out"), self)
        zoomout_action.triggered.connect(self.zoom_out)         
        zoomout_action.setToolTip(tip)
        zoomout_action.setStatusTip(tip)
        zoomout_action.setShortcut('Z')        

        self.view_menu.addAction(reset_action)
        self.view_menu.addAction(orbit_action)
        self.view_menu.addAction(fullscreen_action)
        self.view_menu.addAction(zoomout_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("Help information")        
        help_action = QtWidgets.QAction(self.tr("Help..."), self)
        help_action.setIcon(QtGui.QIcon(":help.png"))
        help_action.triggered.connect(self.open_help_dialog)         
        help_action.setToolTip(tip)
        help_action.setStatusTip(tip)
        help_action.setShortcut('H')

        tip = self.tr("About the application")        
        about_action = QtWidgets.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(help_action)
        self.help_menu.addAction(about_action)
        
        QtCore.QTimer.singleShot(3000, self.set_menu_style) # hide menu after a delay

    def set_menu_style(self):        
        self.menuBar().setStyleSheet("QMenuBar { color: black; } QMenuBar::item:selected { color: white; }")        
