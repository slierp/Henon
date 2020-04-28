# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np

class HenonWidget(QtWidgets.QLabel):
    # Shows Henon map and enables zoom-in selection
    # Implementation done with PyQt only
    
    def __init__(self, _parent = None):
        
        super(HenonWidget, self).__init__(_parent)
        
        self.parent = _parent
        
        self.first_run = True
        self.second_run = False
        self.do_not_draw = False # prevent re-draw during area selection
        self.select_begin = None

        # For selecting areas 
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        
        # Delay new calculation some time after resize events to prevent
        # slowing down GUI with heavy than necessary load
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timer_trigger_calculation)
        
        # turn off internal margins
        self.setMargin(0)
        
        # scale pixmap along with label
        self.setScaledContents(True)
        #self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        
        # set low minimum size to force a resize event after exiting full-screen mode;
        # without resize the window attains the size of the full-screen pixmap
        self.setMinimumSize(1,1)

        self.color_options = [[200,200,200],[79,129,189],[192,80,77],[155,187,89],[247,150,70],[128,100,162],[75,172,198]]

    def showEvent(self,event):

        if self.do_not_draw:
            return
        
        # second window_width is bytes per line; needed to avoid image distortion when resizing the window
        image=QtGui.QImage(self.window_representation.data, self.window_width, self.window_height, self.window_width, QtGui.QImage.Format_Indexed8)            
        self.setPixmap(QtGui.QPixmap.fromImage(image))

    def showEvent_color(self,event,color):

        if self.do_not_draw:
            return
        
        r = self.color_options[color][0]
        g = self.color_options[color][1]
        b = self.color_options[color][2]
        
        # second window_width is bytes per line; needed to avoid image distortion when resizing the window
        image=QtGui.QImage(self.window_representation.data, self.window_width, self.window_height, self.window_width, QtGui.QImage.Format_Indexed8)
        image.setColor(200,QtGui.qRgb(r,g,b))            
        self.setPixmap(QtGui.QPixmap.fromImage(image))

    def resizeEvent(self,event):
    
        #print("[HenonWidget] Resize event") #DEBUG

        sampling = pow(2,self.parent.super_sampling)
        self.window_width = sampling*self.geometry().width()
        self.window_height = sampling*self.geometry().height()
        
        # make new window representation
        self.window_representation = np.zeros((self.window_height,self.window_width), dtype=np.byte)
        
        self.do_not_draw = False # resume drawing texture

        if self.first_run:
            # resize is called twice during start-up for some reason
            # so skip the first run
            self.first_run = False
            self.second_run = True
        elif self.second_run:
            # second run can start calculation immediately
            self.parent.initialize_calculation()
            self.second_run = False
        else:
            # (re-)start timer for starting new calculation after resize event
            # prevents too frequent calculation thread start-ups
            self.timer.start(500)
    
    def timer_trigger_calculation(self):
        self.timer.stop()    
        self.parent.stop_calculation()
        self.parent.initialize_calculation()
              
    def mousePressEvent(self, event):
        
        # Register left mouse click for drawing selection area        
        
        if event.button() == QtCore.Qt.LeftButton:
            self.do_not_draw = True
            self.parent.stop_calculation()           
            self.select_begin = QtCore.QPoint(event.pos())
            self.rubberBand.setGeometry(QtCore.QRect(self.select_begin, QtCore.QSize()))
            self.rubberBand.show()
        elif event.button() == QtCore.Qt.RightButton:
            self.parent.previous_view()                
     
    def mouseMoveEvent(self, event):

        # Draw selection area     
        if self.select_begin:
            if not self.select_begin.isNull():
                self.rubberBand.setGeometry(QtCore.QRect(self.select_begin, event.pos()).normalized())
     
    def mouseReleaseEvent(self, event):

        # Register left mouse button release to finish selection area and process selection
     
        if event.button() == QtCore.Qt.LeftButton:
            self.do_not_draw = False            
            self.rubberBand.hide()
            self.select_end = QtCore.QPoint(event.pos())
            
            if (abs(self.select_end.x() - self.select_begin.x()) > 10) and (abs(self.select_end.y() - self.select_begin.y()) > 10):
                # avoid accidental zoom-in with extremely small selected areas
                self.zoom_selected_area()
            
    def zoom_selected_area(self):
        
        #print("Zooming into selected area")

        # store current view
        previous_view = [self.parent.xleft,self.parent.xright,self.parent.ybottom,self.parent.ytop]
        self.parent.previous_views.append(previous_view)

        # calculate real window dimensions without super sampling
        
        sampling = pow(2,self.parent.super_sampling)
        width = self.window_width/sampling
        height = self.window_height/sampling

        # calculate new coordinate system and re-draw
        # in opengl (0,0) is in the bottom_left, but in PyQt it is in the top_left

        left_edge = 0
        right_edge = 0
        
        if (self.select_begin.x() < self.select_end.x()): # if the first point is more to the left
            
            if (width > self.select_begin.x() > 0): # if inside the screen
                left_edge = self.select_begin.x()
            else:
                left_edge = 0
            
            if (width > self.select_end.x() > 0):
                right_edge = self.select_end.x()
            else:                
                right_edge = width
                
        else:
            
            if (width > self.select_end.x() > 0):
                left_edge = self.select_end.x()
            else:                
                left_edge = 0
            
            if (width > self.select_begin.x() > 0):
                right_edge = self.select_begin.x()
            else:                
                right_edge = width                
        
        temp_xleft = self.parent.xleft + (self.parent.xright - self.parent.xleft)*(left_edge/width)
        self.parent.xright = self.parent.xleft + (self.parent.xright - self.parent.xleft)*(right_edge/width)        
        self.parent.xleft = temp_xleft

        top_edge = 0
        bottom_edge = 0

        if (self.select_begin.y() < self.select_end.y()):
            # image is reversed; towards the top is towards zero and negative
            
            if (height > self.select_begin.y() > 0): # if inside the screen
                top_edge = self.select_begin.y()
            else:
                top_edge = 0
            
            if (height > self.select_end.y() > 0):
                bottom_edge = self.select_end.y()
            else:                
                bottom_edge = height
            
        else:
            
            if (height > self.select_end.y() > 0): # if inside the screen
                top_edge = self.select_end.y()
            else:
                top_edge = 0
            
            if (height > self.select_begin.y() > 0):
                bottom_edge = self.select_begin.y()
            else:                
                bottom_edge = height            

        # invert the result
        bottom_edge = height - bottom_edge
        top_edge = height - top_edge
        
        temp_ybottom = self.parent.ybottom + (self.parent.ytop - self.parent.ybottom)*(bottom_edge/height)
        self.parent.ytop = self.parent.ybottom + (self.parent.ytop - self.parent.ybottom)*(top_edge/height)
        self.parent.ybottom = temp_ybottom
      
        self.clear_screen()
        self.parent.stop_calculation()
        self.parent.initialize_calculation()
        
    def clear_screen(self):     
        self.window_representation[:] = 0

    def trigger_resizeEvent(self):
        old_size = QtCore.QSize(self.geometry().width(), self.geometry().height())
        size = QtCore.QSize(self.geometry().width(), self.geometry().height())
        resize = QtGui.QResizeEvent(size, old_size)
        self.resizeEvent(resize)
        
    def save_image(self,save_path,color):
        r = self.color_options[color][0]
        g = self.color_options[color][1]
        b = self.color_options[color][2]        
        
        image = QtGui.QImage(self.window_representation.data, self.window_width, self.window_height, self.window_width, QtGui.QImage.Format_Indexed8)
        image.setColor(200,QtGui.qRgb(r,g,b)) 
        image.save(save_path[0])