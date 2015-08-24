# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui

help_text = """
<html>
<head><head/>
<body>
<h1>H&eacute;non explorer</h1>

* <a href="#general">Introduction</a><br>
* <a href="#quick">Quick-start</a><br>
* <a href="#settings">Settings dialog</a><br> 
* <a href="#animations">Animations</a><br>

<p><h2><a name="general">Introduction</a></h2></p>

<p>This program is for exploring the H&eacute;non map, which is defined by:</p><br>

<code>x<sub>n+1</sub> = 1 + y<sub>n</sub> - a * x<sub>n</sub><sup>2</sup></code><br>
<code>y<sub>n+1</sub> = b * x<sub>n</sub></code><br>

<p>A map definition such as this one is used in the field of discontinuous time-dynamics.
Starting from initial conditions (x<sub>0</sub>, y<sub>0</sub>) and parameters (a, b) the map tells you what the system (x, y)
will look like for n = 1, 2... (n to n+1 stands for an increase of time, such as a second or an hour).</p>

<p>After start-up the program calculates one or more orbits in the basin of the H&eacute;non attractor
and you get to see the resulting strange attractor of the H&eacute;non map (with parameters a = 1.4, b = 0.3).
The calculation stops automatically when the maximum iteration limit has been reached, which depends on window size, area size
and the number of CPU's available.</p>

<p><h2><a name="quick">Quick-start</a></h2></p>
<p>A quick overview of the program features:</p>
<p><b>Zoom in</b><br>
Look at a portion of the screen by selecting an area. The selection will trigger a new calculation and points that end up in the selected area are shown.
You can zoom in on the H&eacute;non attractor indefinitely and all the while the image remains similar, but unlike Mandelbrot fractals,
the calculation time increases sharply with zoom-factor. Press F5 or use right mouse click to zoom out again.</p>

<p><b>Show full-screen</b><br>
Press 'F' to toggle the full-screen mode.</p>

<p><b>Change H&eacute;non map parameters</b><br>
Press 'S' to open a settings dialog.</p>

<p><b>Run animations of the attractor</b><br>
You can view the H&eacute;non map as its parameters are changing. See the Animation section for details.</p>

<p><b>Generic actions</b><br>
- Stop current calculation with 'ESC'. To bail out of just about anything, press Escape.<br>
- Re-start the calculation with 'R'. If you wish to re-start the calculation using the current settings, press 'R'.</p>

<p><h2><a name="settings">Settings dialog</a></h2></p>
The settings dialog can be opened by pressing 'S'. In it you can define the H&eacute;non parameter values that you would like to try,
define animations (in which the H&eacute;non parameter values are varied) and set some calculation parameters. Please see the next section about animations.

<p><b>General settings</b></p>
<p>The definition of a and b is straightforward, but keep in mind that some settings may not yield a stable attractor or not even any periodic behaviour, so the screen may remain empty.</p>

<p>The viewing area can be set manually by selecting values for the left edge, bottom edge, width and height of the area. There are some restrictions to these values
in order to prevent algorithm execution problems. These restrictions are enforced immediately after changing to a new value.</p>

<p>For certain a,b values there will be periodic behaviour, which means that only a few pixels will show up on the screen. Single pixels can be hard to see so this is why the program
can enlarge such rare pixels. This functionality can be turned on using the 'Enlarge rare pixels' checkbox. If there are between 1 and 16 pixels in total during any screen update then they will
be enlarged to nine pixels for better visibility.</p>

<p>For control over the calculations it is possible to define the maximum number of iterations for each thread and define the iteration interval after which the result is plotted to screen.
By default these settings are determined automatically by the program, which calculates optimized settings based on the window size, zoom-level and the number of availabe threads.
The user can disable the auto-mode and set their own values. Please keep in mind that some sanity checks are done before the calculation is started, so the program may change the
entered settings. For the plot interval it should also be understood that there is also a minimum time defined between screen updates of 100 ms, so for very low plot interval values
the program may drop some screen plot requests if they present themselves too soon after the previous one. These restrictions are in place to maintain the responsiveness of the user
interface.</p>

<p><b>Animation settings</b></p>
<p>In the animation tab one can set the mid-point, range and increment for H&eacute;non parameters a and b in order to define the animation settings. ou can also
select whether you want to animate either a or b or both at the same time. The animation will start at (midpoint - 0.5 * range) and end when the range limit has been reached.</p>

<p>For animations it is necessary to lower the maximum number of iterations and plot interval compared to those used for viewing still images, so these values can be defined separately and have
lower default values. The parameter itself is the same as for still images however.</p>

<p>Please note that the program does not return to your previous settings after completing an animation. The a/b and iteration parameters remain as they are, although the iteration
parameters are by default set automatically to optimized settings.</p>

<p><b>Calculation settings</b></p>

<p><b>Thread count</b><br>
The program runs several threads at the same time by default in order to speed up the calculations. By default the thread count is equal to the number of CPU's detected, but
it can be set to a lower value.</p>

<p><b>Drop iterations</b><br>
The number of dropped iterations that are performed for each thread can be set here. Each calculation thread starts from x,y values that are chosen randomly
in the range of (-0.1,0.1), so that each thread can follow an independent path along the attractor, but the first few hundred iterations may not have reached the
attractor yet, so this is why the program performs a few hundred iterations before it starts passing the information to the screen.</p>

<p><b>Enable OpenCL</b><br>
There is support for OpenCL for CPU/GPU multithreading. The OpenCL functionality can be enabled if the PyOpenCL Python module is installed and the environment
variable 'PYOPEN_CTX' is set in order to select the OpenCL platform (Intel/AMD/NVIDIA) and device (CPU/GPU). This manual configuration
is intended as a temporary solution. A dialog for selecting a platform and one or more devices still needs to be implemented.</p>

<p><h2><a name="animations">Animations</a></h2></p>

<p>The program has default animation settings that can be activated in the settings dialog by clicking on the 'Animate' checkboxes for parameter a or b. The animation can then be
started in the main screen by pressing 'A'. These default animations demonstrate some general aspects of the H&eacute;non map. For parameter 'B' the animation starts with
a stable point that doubles its period a few times before it grows into the H&eacute;non attractor. For parameter 'A' the animation features look similar but it also shows a crisis,
i.e. the sudden disappearance of the attractor near a = 1.2. When the attractor has formed almost fully you may notice that the attractor disappears again a few times.
These must be periodic windows where there is a brief reappearance of periodic behaviour</p>

</body>
</html>
"""

class HenonHelp(QtGui.QDialog):
    # Generates help document browser    
    
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