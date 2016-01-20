import os
from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext

ext_modules=[
    Extension("test_run", ["test_run.py"])
]

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
