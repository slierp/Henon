# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
from random import uniform
from datetime import datetime

"""
Test to see whether numpy matrix notation could help to speed up calculation

"""

hena = 1.4
henb = 0.3
henx = uniform(-0.1,0.1)
heny = uniform(-0.1,0.1)
xleft = -1.5
ytop = 0.4
xright = 1.5
ybottom = -0.4
xratio = 1920/(xright-xleft)
yratio = 1020/(ytop-ybottom)

time_start = datetime.now()

for i in xrange(1000000):
    try:
        x_test, y_test = 1 + heny - (hena*(henx**2)), henb * henx
        #print x_test, y_test
    
        x_draw = int((henx-xleft) * xratio) # adding rounding here is slightly more correct
        y_draw = int((heny-ybottom) * yratio) # but takes considerably more time
        #print int(x_draw), int(y_draw)
    except:
        pass

delta = datetime.now() - time_start
print "Time: " + str(delta.seconds) + " seconds; " + str(delta.microseconds) + " microseconds"


xy = np.array([henx,heny]) # initialization
A = np.array([[(1/xy[0])-hena*xy[0],1],[henb,0]]) # Henon formula
B = np.array([[(1-xleft/xy[0])*xratio,0],[0,(1-ybottom/xy[1])*yratio]])

time_start = datetime.now()

for i in xrange(1000000):
    try:
        xy = np.sum(A*xy,axis=1) # iteration
        #print xy
        xy_draw = np.sum(B*xy,axis=1).astype(int)
        #print xy_draw
    except:
        pass

delta = datetime.now() - time_start    
print "Time: " + str(delta.seconds) + " seconds; " + str(delta.microseconds) + " microseconds"

