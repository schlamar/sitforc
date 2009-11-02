# encoding: utf-8

'''
"SITforC" stands for System Identification 
Toolkit for Control theory. This package provides
methods for identifying a control system by 
experimental data.
'''
__version__ = '0.1'

from core import modellib, load_csv, identify_reg
from fitting import PolyFitter, ModelFitter

