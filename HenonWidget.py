# -*- coding: utf-8 -*-
from __future__ import division
from OpenGL import GL
from PyQt4 import QtOpenGL, QtGui, QtCore
import numpy as np

class HenonWidget(QtOpenGL.QGLWidget):
    
    def __init__(self, _parent = None):
        
        super(HenonWidget, self).__init__(_parent)
       
        self.parent = _parent
        
        self.first_run = True
        self.do_not_draw = False # prevent re-draw during area selection
        
        # For selecting areas        
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)

    def paintGL(self):

        if self.do_not_draw:
            return
        
        # set color and draw pixels
        GL.glColor3f(1.0, 1.0, 1.0)        
        GL.glDrawPixels(self.window_width, self.window_height, GL.GL_RGBA, GL.GL_UNSIGNED_INT_8_8_8_8, np.ascontiguousarray(self.window_representation.transpose()))
        GL.glFlush()       

    def resizeGL(self, w, h):
        
#        print "Resize event..." #DEBUG        

        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.window_width = w
        self.window_height = h

        # make new window representation
        self.window_representation = np.zeros([self.window_width,self.window_height], dtype=np.uint32)
        
        # calculate new x, y ratios
        self.xratio = self.window_width/(self.parent.xright-self.parent.xleft) # ratio screenwidth to valuewidth
        self.yratio = self.window_height/(self.parent.ytop-self.parent.ybottom)

        # set mode to 2D        
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0.0, w, 0.0, h, 0.0, 1.0)
        GL.glMatrixMode (GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        if (not self.first_run):
            # resize is called twice during start-up for some reason
            # only initialize calculation threads when screen dimensions are fixed
            self.parent.initialize_calculation()
        else:
            self.first_run = False

    def initializeGL(self):
        
        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
              
    def mousePressEvent(self, event):
        
        # Register left mouse click for drawing selection area        
        
        if event.button() == QtCore.Qt.LeftButton:
            self.do_not_draw = True
            self.parent.stop_calculation()           
            self.select_begin = QtCore.QPoint(event.pos())
            self.rubberBand.setGeometry(QtCore.QRect(self.select_begin, QtCore.QSize()))
            self.rubberBand.show()
     
    def mouseMoveEvent(self, event):

        # Draw selection area    
     
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

        # calculate new coordinate system and re-draw
        # in opengl (0,0) is in the bottom_left, but in PyQt it is in the top_left

        left_edge = 0
        right_edge = 0

        if (self.select_begin.x() < self.select_end.x()): # if the first point is more to the left
            
            if (self.window_width > self.select_begin.x() > 0): # if inside the screen
                left_edge = self.select_begin.x()
            else:
                left_edge = 0
            
            if (self.window_width > self.select_end.x() > 0):
                right_edge = self.select_end.x()
            else:                
                right_edge = self.window_width
                
        else:
            
            if (self.window_width > self.select_end.x() > 0):
                left_edge = self.select_end.x()
            else:                
                left_edge = 0
            
            if (self.window_width > self.select_begin.x() > 0):
                right_edge = self.select_begin.x()
            else:                
                right_edge = self.window_width                
        
        temp_xleft = self.parent.xleft + (self.parent.xright - self.parent.xleft)*(left_edge/self.window_width)
        self.parent.xright = self.parent.xleft + (self.parent.xright - self.parent.xleft)*(right_edge/self.window_width)        
        self.parent.xleft = temp_xleft

        top_edge = 0
        bottom_edge = 0

        if (self.select_begin.y() < self.select_end.y()):
            # image is reversed; towards the top is towards zero and negative
            
            if (self.window_height > self.select_begin.y() > 0): # if inside the screen
                top_edge = self.select_begin.y()
            else:
                top_edge = 0
            
            if (self.window_height > self.select_end.y() > 0):
                bottom_edge = self.select_end.y()
            else:                
                bottom_edge = self.window_height
            
        else:
            
            if (self.window_height > self.select_end.y() > 0): # if inside the screen
                top_edge = self.select_end.y()
            else:
                top_edge = 0
            
            if (self.window_height > self.select_begin.y() > 0):
                bottom_edge = self.select_begin.y()
            else:                
                bottom_edge = self.window_height            

        # invert the result
        bottom_edge = self.window_height - bottom_edge
        top_edge = self.window_height - top_edge
        
        temp_ybottom = self.parent.ybottom + (self.parent.ytop - self.parent.ybottom)*(bottom_edge/self.window_height)
        self.parent.ytop = self.parent.ybottom + (self.parent.ytop - self.parent.ybottom)*(top_edge/self.window_height)
        self.parent.ybottom = temp_ybottom
      
        self.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))