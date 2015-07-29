# -*- coding: utf-8 -*-
from __future__ import division
from OpenGL import GL
from OpenGL.arrays import vbo
from PyQt4 import QtOpenGL, QtGui, QtCore
import numpy as np

class Henon(QtOpenGL.QGLWidget):
    
    def __init__(self, _parent = None):
        
        super(Henon, self).__init__(_parent)

        self.parent = _parent
        self.xleft = -1.5
        self.ytop = 0.4
        self.xright = 1.5
        self.ybottom = -0.4
        self.hena = 1.4
        self.henb = 0.3
        self.henx = 0.1
        self.heny = 0.1
        self.calc_limit = 100000
        self.first_run = True
        self.do_not_draw = False # prevent re-draw during area selection as it is a bit slow currently

        # For selecting areas        
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)     

    def paintGL(self):

        if self.do_not_draw:
            return
        
        # set color and draw pixels
        GL.glColor3f(1.0, 1.0, 1.0)
        GL.glBegin(GL.GL_POINTS)
        
        for i in range(self.window_width):
            for j in range(self.window_height):
                if self.window_representation[i][j]:
                    GL.glVertex2f(i, j)

        GL.glEnd()
        
        #GL.glDrawPixels() # faster implementation, but does not work yet
        #GL.glFlush()

    def resizeGL(self, w, h):

        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.window_width = w
        self.window_height = h

        # make new window representation
        self.window_representation = np.zeros([self.window_width,self.window_height], dtype=np.bool)
        
        # calculate new x, y ratios
        self.xratio = self.window_width/(self.xright-self.xleft) # ratio screenwidth to valuewidth
        self.yratio = self.window_height/(self.ytop-self.ybottom)

        if(not self.first_run): # resize is called twice during initialization
            # perform Henon iteration
            self.calc_henon()
        else:
            self.first_run = False

        # set mode to 2D        
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0.0, w, 0.0, h, 0.0, 1.0)
        GL.glMatrixMode (GL.GL_MODELVIEW)
        GL.glLoadIdentity()        

    def initializeGL(self):
        
        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
    def calc_henon(self):
        
        for i in range(self.calc_limit):
            henxtemp = 1-(self.hena*self.henx*self.henx) + self.heny
            self.heny = self.henb * self.henx
            self.henx = henxtemp
            x_draw = int((self.henx-self.xleft) * self.xratio)
            y_draw = int((self.heny-self.ybottom) * self.yratio)
            
            if (0 < x_draw < self.window_width) and (0 < y_draw < self.window_height):
                self.window_representation[x_draw][y_draw] = True
              
    def mousePressEvent(self, event):
        
        # Register left mouse click for drawing selection area        
        
        if event.button() == QtCore.Qt.LeftButton:
            self.do_not_draw = True
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
        
        temp_xleft = self.xleft + (self.xright - self.xleft)*(left_edge/self.window_width)
        self.xright = self.xleft + (self.xright - self.xleft)*(right_edge/self.window_width)        
        self.xleft = temp_xleft

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
        
        temp_ybottom = self.ybottom + (self.ytop - self.ybottom)*(bottom_edge/self.window_height)
        self.ytop = self.ybottom + (self.ytop - self.ybottom)*(top_edge/self.window_height)
        self.ybottom = temp_ybottom
      
        self.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))
        self.updateGL()
        
        self.parent.statusBar().showMessage(self.tr("Press space to zoom out again"))        

    def reset_scale(self):
        
        self.xleft = -1.5
        self.ytop = 0.4
        self.xright = 1.5
        self.ybottom = -0.4
        self.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))
        self.updateGL()
        self.parent.statusBar().showMessage(self.tr("Ready"))