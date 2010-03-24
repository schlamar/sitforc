# encoding: utf-8

'''
"SITforC" stands for System Identification 
Toolkit for Control theory. This package provides
a GUI for identifying a control system by 
experimental data.
'''

__author__ = 'Marc Schlaich'
__version__ = '0.2.0'
__license__ = 'MIT'

from core import modellib, load_csv, identify_reg, identify_itm
from fitting import PolyFitter, ModelFitter

