Hénon
=====

A Python program for exploring the Hénon attractor. For an explanation of what the Hénon attractor is please see <a href="http://en.wikipedia.org/wiki/H%C3%A9non_map">Wikipedia</a>.

<b>How to use the program</b>

With this program you can draw the Hénon attractor and interact with it in various ways. You can zoom in by selecting an area, vary the Henon parameters manually and even make animations with them. There is a help function included that explains in more detail how to use the program.

<b>Multithreading support</b>

The program uses the Python multiprocessing module for multithreading support. The Hénon calculation is started in several threads simultaneously using slightly different starting conditions in order to speed up the overall calculation. On Linux the attractor can be drawn with a reasonable resolution within ~0.1 seconds. When zooming in the program increases the maximum iteration threshold for each thread in order to generate the required level of detail.

<b>Sidenote</b>

This program is a re-implementation of an old Visual C++ program. The installer of that program is still functional up until Windows 7 at least. The old installer is available as the first release.
