#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from sitforc import modellib, load_csv
from sitforc.core import RegressionIdentifier, ITMIdentifier

with open('results.txt', 'w') as f_out: 
    sys.stdout = f_out
    
    for filename in os.listdir(''):
        if filename.endswith('.csv'):
            print 'File: {0}'.format(filename)
            x, y = load_csv(filename)
            
            ident = RegressionIdentifier(x, y, modellib.pt2)
            mf = ident.model_fitter
            print 'Params for PT-2 Model: {0}'.format(mf.params)
            
            degree = 11
            ident = ITMIdentifier(x, y, degree)
            print 'Params for ITM'
            print 'Tu\t\t{0:.3f}'.format(ident.tu)
            print 'Tg\t\t{0:.3f}'.format(ident.tg)
            print 'Tu/Tg\t\t{0:.3f}'.format(ident.tu/ident.tg)
            print
