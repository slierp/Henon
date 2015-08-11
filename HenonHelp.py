# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui

help_text = """
<html>
<head><head/>
<body>
<h1>H&eacute;non explorer</h1>

* <a href="#general">Introduction</a><br>
* <a href="#settings">Change settings</a><br> 
* <a href="#animations">Animations</a><br>

<p><h2><a name="general">Introduction</a></h2></p>

<p>This program is for exploring the H&eacute;non map, which is defined by:</p><br>

<code>x[n+1] = 1 - a * x[n]^2 + y[n]</code><br>
<code>y[n+1] = b * x[n]</code><br>

<p>A map definition such as this one is used in the field of discontinuous time-dynamics.
Starting from initial conditions (x[0], y[0]) and parameters (a, b) the map tells you what the system (x, y)
will look like for n = 1, 2... (n to n+1 stands for an increase of a large body of time, like a second or an hour).</p>

<p>After start-up the program calculates a single orbit in the basin of the H&eacute;non attractor
and you get to see the resulting strange attractor of the H&eacute;non map (with parameters a = 1.4, b = 0.3).
The calculation stops automatically when the maximum iteration has been reached, which depends on screen size and x,y area.</p>

<p>You can then do a few things:</p>
<p>- Look at a portion of the screen by zooming in on it. Select a section of screen and
the calculation starts over again; points that end up in the selected area are plotted.
You can zoom in on the H&eacute;non attractor indefinitely and all the while the image remains similar,
but unlike Mandelbrot fractals, the calculation time increases sharply with zoom-factor.
Press space or F5 to zoom out again.</p>

<p>- Show full-screen. Press 'F' to toggle the full-screen mode.</p>

<p>- Change H&eacute;non map parameters. To be implemented.</p>

<p>- Animate by varying H&eacute;non map parameters. To be implemented. See the Animation section.</p>

<p>Other short-cuts:</p>
<p>- Stop current calculation. To bail out of just about anything, press ESC.</p>

<p>- Re-start the calculation. If you wish to re-start the calculation using the current settings, press R.</p>

<p>- Quit program. Press Q.</p>

<p><h2><a name="settings">Change settings</a></h2></p>
To be implemented

<p><h2><a name="animations">Animations</a></h2></p>
To be implemented

<p>In the set variables screen you can set the increment; the amount you want a or b changed for each
'animation-frame'. And you can set the range: the animation then starts at variable -0.5 * range and ends at
variable +0.5 * range. You can switch which variable to animate using the 's' key. The animation starts running on key
'a'. Using the 'c' key you can toggle whether you want to clean the screen after each frame or just draw on top of each other.</p>

<p>Demo 1 is an animation that will ultimately show the 'start-up'screen. It starts with a stable point that doubles
its period, as a function of b, and then becomes the attractor. Demo 2 is basically the same idea, except we're
varying a instead of b. It also shows a crisis; the sudden disappearance of the attractor at a = &plusmn;1.2.
When the attractor has formed more or less, you may notice the attractor 'faltering' a bit; disappearing for a little while.
These must be periodic windows where there is a brief reappearance of periodic behaviour. Please note that the program does not return to
your previous settings after completing a demo.</p>

</body>
</html>
"""

class HenonHelp(QtGui.QDialog):
    def __init__(self, parent):
        super(QtGui.QDialog, self).__init__(parent)
        
        self.parent = parent       
        
        self.setWindowTitle(self.tr("Help"))
        vbox = QtGui.QVBoxLayout()

        browser = QtGui.QTextBrowser()
        browser.insertHtml(help_text)
        browser.moveCursor(QtGui.QTextCursor.Start)

        vbox.addWidget(browser)

        ### Buttonbox for ok or cancel ###
        hbox = QtGui.QHBoxLayout()
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.close)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumHeight(576)
        self.setMinimumWidth(1024)