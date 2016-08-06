# -*- coding: utf-8 -*-
from __future__ import division
from OpenGL import GL
from PyQt4 import QtOpenGL, QtGui, QtCore
import numpy as np

class HenonWidget(QtOpenGL.QGLWidget):
    # Shows Henon map and enables zoom-in selection
    # Implementation done with OpenGL
    
    def __init__(self, _parent = None):
        
        super(HenonWidget, self).__init__(_parent)
       
        self.parent = _parent
        
        self.first_run = True
        self.second_run = False
        self.do_not_draw = False # prevent re-draw during area selection
        
        # For selecting areas        
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        
        # Delay new calculation some time after resize events to prevent
        # slowing down GUI with heavy than necessary load
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timer_trigger_calculation)        

    def paintGL(self):

        if self.do_not_draw:
            return
        
        GL.glColor3f(1.0,1.0,1.0)
        GL.glDrawPixels(self.window_width, self.window_height, GL.GL_LUMINANCE, GL.GL_UNSIGNED_BYTE, np.ascontiguousarray(self.window_representation))
        GL.glFlush()

#    def paintGL(self):
#
#        if self.do_not_draw:
#            return
#
#        # set scaling because texture is larger than Henon map image        
#        GL.glPushMatrix()
#        GL.glScaled(self.tex_width/self.window_width,self.tex_height/self.window_height,1)    
#
#        # redefine part of texture
#        GL.glTexSubImage2D(GL.GL_TEXTURE_2D,0,0,0,self.tex_width,self.tex_height,GL.GL_LUMINANCE,GL.GL_UNSIGNED_BYTE,self.window_representation)
#        
#        # define quad to draw texture onto       
#        GL.glColor3ub(255,255,255)      
#        GL.glEnable(GL.GL_TEXTURE_2D)
#        GL.glBindTexture(GL.GL_TEXTURE_2D,self.texture_id)
#        GL.glBegin(GL.GL_QUADS)
#        GL.glTexCoord2i(0,0)
#        GL.glVertex2i(0,0)
#        GL.glTexCoord2i(1,0)
#        GL.glVertex2i(1,0)
#        GL.glTexCoord2i(1,1)
#        GL.glVertex2i(1,1)
#        GL.glTexCoord2i(0,1)
#        GL.glVertex2i(0,1)
#        GL.glEnd()
#
#        GL.glPopMatrix()
        
    def resizeGL(self, w, h):
    
#        print "[HenonWidget] Resize event" #DEBUG        

        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.window_width = w
        self.window_height = h
        
        # make larger texture size due to 2**n size requirement
        #self.tex_width = self.calc_texture_size(w)
        #self.tex_height = self.calc_texture_size(h)
        
        # make new window representation
        self.window_representation = np.zeros((self.window_height,self.window_width), dtype=np.byte)
        #self.window_representation = np.zeros((self.tex_height,self.tex_width), dtype=np.byte)
        
        # calculate new x, y ratios
        self.xratio = self.window_width/(self.parent.xright-self.parent.xleft) # ratio screenwidth to valuewidth
        self.yratio = self.window_height/(self.parent.ytop-self.parent.ybottom)

        # set mode to 2D
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        
        # set window coordinates (left/right/bottom/top)
        GL.glOrtho(0, 1, 0, 1, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # define texture
        #self.do_not_draw = True # prevent drawing texture while changing it
        #self.texture_id = GL.glGenTextures(1)
        #GL.glBindTexture(GL.GL_TEXTURE_2D,self.texture_id)
        #GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_MAG_FILTER,GL.GL_LINEAR)
        #GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_MIN_FILTER,GL.GL_LINEAR)
        #GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        #GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        #GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_LUMINANCE, self.tex_width, self.tex_height, 0, GL.GL_LUMINANCE, GL.GL_UNSIGNED_BYTE, None)
        
        # define quad to draw texture onto
        #GL.glBindTexture(GL.GL_TEXTURE_2D,self.texture_id)
        #GL.glBegin(GL.GL_QUADS)
        #GL.glTexCoord2i(0,0)
        #GL.glVertex2i(0,0)
        #GL.glTexCoord2i(1,0)
        #GL.glVertex2i(1,0)
        #GL.glTexCoord2i(1,1)
        #GL.glVertex2i(1,1)
        #GL.glTexCoord2i(0,1)
        #GL.glVertex2i(0,1)
        #GL.glEnd()
        
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

#    def calc_texture_size(self, number):
#        # find n for 2**n that is just larger than the input number;
#        # needed for fitting an arbitraty resolution image into a texture
#        # that can only have 2**n width or length
#        n = 0
#        while True:
#            size = 2**n
#            
#            if size > number:
#                return size
#                
#            n += 1
    
    def timer_trigger_calculation(self):
        self.timer.stop()    
        self.parent.stop_calculation()
        self.parent.initialize_calculation()            
            
    def initializeGL(self):

#        print "OpenGL version information: " + GL.glGetString(GL.GL_VERSION) #DEBUG
        
        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        # avoid excess bytes at the end of rows
        # will give drawing artefacts otherwise
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        
        # disable some OpenGL features to try to speed up drawing pixels
        GL.glDisable(GL.GL_ALPHA_TEST)
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_DITHER)
        GL.glDisable(GL.GL_FOG)
        GL.glDisable(GL.GL_LIGHTING)
        GL.glDisable(GL.GL_LOGIC_OP)
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glDisable(GL.GL_TEXTURE_1D)
        GL.glDisable(GL.GL_TEXTURE_2D)        
        GL.glPixelTransferi(GL.GL_MAP_COLOR, GL.GL_FALSE)
        GL.glPixelTransferi(GL.GL_RED_SCALE, 1)
        GL.glPixelTransferi(GL.GL_RED_BIAS, 0)
        GL.glPixelTransferi(GL.GL_GREEN_SCALE, 1)
        GL.glPixelTransferi(GL.GL_GREEN_BIAS, 0)
        GL.glPixelTransferi(GL.GL_BLUE_SCALE, 1)
        GL.glPixelTransferi(GL.GL_BLUE_BIAS, 0)
        GL.glPixelTransferi(GL.GL_ALPHA_SCALE, 1)
        GL.glPixelTransferi(GL.GL_ALPHA_BIAS, 0)       
              
    def mousePressEvent(self, event):
        
        # Register left mouse click for drawing selection area        
        
        if event.button() == QtCore.Qt.LeftButton:
            self.do_not_draw = True
            self.parent.stop_calculation()           
            self.select_begin = QtCore.QPoint(event.pos())
            self.rubberBand.setGeometry(QtCore.QRect(self.select_begin, QtCore.QSize()))
            self.rubberBand.show()
        elif event.button() == QtCore.Qt.RightButton:
            self.parent.reset_view()                   
     
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
      
        self.clear_screen()
        self.parent.stop_calculation()
        self.parent.initialize_calculation()
        
    def clear_screen(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
     
        self.window_representation[:] = 0