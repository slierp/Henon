cd Henon
del *.c
del *.pyc
del *.pyd
rmdir build /s /q
rmdir dist /s /q
rmdir Henon.egg-info /s /q
rmdir __pycache__ /s /q
"C:\WinPython\python-3.7.7.amd64\python.exe" -m cProfile -s tottime Main.py
pause
