# encoding: utf-8

'''
SITforC stands for System Identification Toolkit for 
Control theory. It is a simple, but powerful open-source 
application to identify a control system by experimental 
data.

Website: http://sitforc.ms4py.org/
'''

__author__ = 'Marc Schlaich'
__version__ = '0.2.0'
__license__ = 'MIT'

from core import modellib, load_csv, identify_reg, identify_itm
from fitting import PolyFitter, ModelFitter

