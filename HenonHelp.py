# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui

help_text = """
<html>
<head><head/>
<body>
<h1>H&eacute;non explorer</h1>

* <a href="#general">Introduction</a><br>
* <a href="#settings">Settings dialog</a><br> 
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

<p><h3>Possible actions</h3></p>
<p><b>Zoom in</b></p>
Look at a portion of the screen by selecting an area. The selection will trigger a new calculation and points that end up in the selected area are shown.
You can zoom in on the H&eacute;non attractor indefinitely and all the while the image remains similar, but unlike Mandelbrot fractals,
the calculation time increases sharply with zoom-factor. Press space or F5 to zoom out again.

<p><b>Show full-screen</b></p>
Press 'F' to toggle the full-screen mode.

<p><b>Change H&eacute;non map parameters</b></p>
Press 'S' to open a settings dialog.

<p><b>Run animations of the attractor</b></p>
You can see the H&eacute;non map as its are parameters are changing. See the Animation section.

<p><b>Generic actions</b></p>
- Stop current calculation. To bail out of just about anything, press ESC.
- Re-start the calculation. If you wish to re-start the calculation using the current settings, press R.
- Quit program. Press Q.

<p><h2><a name="settings">Settings dialog</a></h2></p>
The settings dialog can be opened by pressing 'S' or using the menu. In it you can define the H&eacute;non parameters a and b that you would like to try,
set some calculation parameters and define animation settings. Please see the next section about animations.

<p><b>H&eacute;non map parameter definition</b></p>
The definition of a and b is straightforward, but keep in mind that some settings may not yield a stable attractor or periodic behaviour, so the screen may remain empty.

<p><b>Thread count</b></p>
The program runs several threads at the same time by default in order to speed up the calculations. The thread count is equal to the number of CPU's in the computer by default, but
it can be set to a lower value.

<p><b>Iteration settings</b></p>
For control over the calculations it is possible to define the maximum iterations for each thread and define the iteration interval after which the result is drawn to screen.
By default these settings are determined automatically by the program, which determines optimal settings based on the window size, zoom-level and the number of availabe threads.
The user can disable the auto-mode and set their own values. Please keep in mind that some sanity checks are done before the calculation is started, so the program may change the
entered settings. For the plot interval it should also be understood that there is also a minimum time defined between screen updates, so for very low plot interval values the program
will drop some draw requests if they present themselves too soon after the previous one.

<p><h2><a name="animations">Animations</a></h2></p>

<p>In the settings dialog you can set the mid-point, range and increment for H&eacute;non parameters a and b in order to define the animation settings. You can also
enable/disable animation of either parameter. The animation will start at (midpoint - 0.5 * range) and end when the range has been reached.
The animations can be started by pressing 'A'. Please note that the program does not return to your previous settings after completing an animation.</p>

<p>The default animation settings for a and b demonstrate the basic idea. For parameter 'B' it starts with a stable point that doubles
its period a few times and then becomes the H&eacute;non attractor. For parameter 'A' the result is similar, but it also shows a crisis, i.e.
the sudden disappearance of the attractor at a = &plusmn;1.2. When the attractor has formed more or less, you may notice that the attractor disappears a few times.
These must be periodic windows where there is a brief reappearance of periodic behaviour.</p>

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