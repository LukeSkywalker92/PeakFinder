from distutils.core import setup
import py2exe

setup(windows = [{'script': "peakfinder.py"}], zipfile = None)