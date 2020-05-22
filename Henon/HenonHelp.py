# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtWidgets

help_text = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
<h1>H&eacute;non map browser</h1>
<a href="#keyboard" style="color:#ff4f00;">Keyboard shortcuts</a><br>
<a href="#settings" style="color:#ff4f00;">Settings window</a><br> 
<a href="#bifurcation" style="color:#ff4f00;">Bifurcation map</a><br>
<a href="#animations" style="color:#ff4f00;">Animations</a>

<p>This program was made for exploring the H&eacute;non map, which is defined by:</p><br>

<code>x<sub>n+1</sub> = 1 + y<sub>n</sub> - a * x<sub>n</sub><sup>2</sup></code><br>
<code>y<sub>n+1</sub> = b * x<sub>n</sub></code><br>

<p>Starting from initial conditions (x<sub>0</sub>, y<sub>0</sub>) and parameters (a, b) the map tells you what the system (x, y)
will look like for any value of n. More information about the map is available on
<a href="https://en.wikipedia.org/w/index.php?title=H&eacute;non_map&oldid=955487766" style="color:#ff4f00;">wikipedia</a>.</p>

<p>After start-up the program calculates one or more orbits in the basin of the H&eacute;non attractor
and you get to see the resulting strange attractor of the H&eacute;non map (a = 1.4, b = 0.3).
The calculation stops automatically when the maximum iteration limit has been reached, which depends on window size, area size
and the number of CPU or GPU threads available.</p>

<p>You can zoom-in on the attractor by selecting an area. Press F5 or use right mouse click to zoom out again. When zooming in on the H&eacute;non attractor
the program will automatically increase the iteration limit. Zooming in can be done indefinitely but the calculation time needed to get a decent amount of points
on the screen will increase sharply with zoom-factor. The OpenCL functionality can be used to get a large decrease in calculation time.</p>

<p><h2><a name="keyboard">Keyboard shortcuts</a></h2></p>

- Press F to toggle the full-screen mode<br>

- Press X to stop current calculation<br>

- Press R to re-draw the screen with current settings<br>

- Press S to change settings such as the H&eacute;non map parameters<br>

- Press W to open a settings window for the scale of the x- and y-axis<br>

- Press O to toggle between bifurcation map and standard mode<br>

- Press A to start animations. See the Animation section for details.

- Press B to toggle benchmark mode.

<p><h2><a name="settings">Settings window</a></h2></p>
Here you can define the H&eacute;non parameter values that you would like to try, define bifurcation map mode and animations and set some calculation parameters.

<p><b>General settings</b></p>
<p>The definition of parameters a and b is straightforward, but keep in mind that some settings may not yield a stable attractor or not even any periodic behaviour, so the screen may remain empty.</p>

<p>To control the calculations it is possible to define the maximum number of iterations for each thread and define the iteration interval after which the result is sent to the screen.
By default these settings are determined automatically by the program, which calculates optimized settings based on the window size, zoom-level and the number of availabe threads.
The user can disable the auto-mode and set their own values but keep in mind that some sanity checks are done before the calculation is started, so the program may change the
entered settings.</p>

<p>Supersampling can increase the image quality greatly by generating 2-8x the amount of pixels on the x- and y-axis, after which the image is scaled down to the window dimensions.
A high supersampling setting will increase the calculation time significantly so it is recommended to use the OpenCL functionality to compensate for that.</p>

<p><b>Bifurcation map settings</b></p>
In bifurcation map mode the horizonal axis represents a parameter (a or b) and the vertical axis a coordinate (x or y). In this screen one can choose the parameter and coordinate to use and
one can set some calculation settings. It is possible to change the plot interval and the max iterations that will be used for each pixel/parameter value along the screen width.
The plot interval value only does something when OpenCL is enabled.

<p><b>Animation settings</b></p>
<p>In the animation tab one can set the start, stop and increment values for H&eacute;non parameters a and b in order to define the animation settings. You can also
select whether you want to animate either a or b or both at the same time.</p>

<p>For animations it is necessary to lower the maximum number of iterations compared to those used for viewing still images, so these values can be defined separately and have
lower default values. The minimum time delay between each animation frame can be set. The actual delay may be longer depending on how long it takes to calculate each frame.</p>

<p><b>Calculation settings</b></p>

<p>Initial conditions<br>
The number of dropped iterations that are performed for each thread can be set here. Each calculation thread starts from x,y values that are chosen randomly
in the range of (-0.1,0.1), so that each thread can follow an independent path. Since the first few hundred iterations may not have reached the
attractor yet it is possible to have the program drop some iterations before it starts passing the information to the screen.</p>

<p>The range in which the random x,y values are generated can be set also, to be able to capture a larger set of possible orbits. Keep in mind that larger ranges will
result in more orbits going to infinity, so the screen may become more empty. One can try to compensate by increasing the thread count.</p>

<p>Thread count<br>
The program runs several threads at the same time by default in order to speed up the calculations. Each thread receives a random x,y value as an initial condition.
By default the thread count is equal to the number of CPU's detected.</p>

<p>It is also possible to define the number of threads in OpenCL mode. In standard mode it is equal to the OpenCL global work size and has a default value of 256 (2^8).
In bifurcation map mode it is equal to the entered value times the amount of pixels along the x-axis.

<p>Enable OpenCL<br>
There is support for OpenCL for CPU/GPU multithreading to enable a much shorter calculation time. The OpenCL functionality can be enabled if the PyOpenCL Python module can be loaded successfully, 
which may require installing appropriate drivers (from Intel/AMD/NVIDIA). One or more devices can be selected to run the calculations on. Not all devices or device combinations may work well,
but the program will give a message if this occurs.</p>

<p><h2><a name="bifurcation">Bifurcation map</a></h2></p>

<p>In bifurcation map mode the horizontal axis represents a parameter (a or b) and the vertical axis a coordinate (x or y). It is another way of visualizing the H&eacute;non
attractor and is especially suited for showing the bifurcations and appearance and disappearance of chaotic behaviour. By default, the selected parameter is 'a' and the vertical coordinate is 'y'.
It is possible to zoom-in on the image by selecting an area with the mouse.</p>

<p><h2><a name="animations">Animations</a></h2></p>

<p>The program has default animation settings that can be activated in the settings window by clicking on the 'Animate' checkboxes for parameter a or b. The animation can then be
started in the main screen by pressing 'A'. These default animations demonstrate some general aspects of the H&eacute;non map. For parameter b the animation starts with
a stable point that doubles its period a few times before it grows into the H&eacute;non attractor. For parameter a the animation features look similar but it also shows
some sudden disappearances of the attractor (e.g. near a = 1.2).</p>

</body>
</html>
"""

class HenonHelp(QtWidgets.QDialog):
    # Generates help document browser    
    
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        
        self.parent = parent       
        
        self.setWindowTitle(self.tr("Help"))
        vbox = QtWidgets.QVBoxLayout()
        
        browser = QtWidgets.QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.insertHtml(help_text)
        browser.moveCursor(QtGui.QTextCursor.Start)

        vbox.addWidget(browser)

        ### Buttonbox for ok or cancel ###
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.close)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumHeight(576)
        self.setMinimumWidth(1024)