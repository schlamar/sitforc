#!/usr/bin/python
# -*- coding: utf-8 -*-

from sitforc import modellib, load_csv, identify_reg, identify_itm

x, y = load_csv('data.csv')
print 'Identifikation mit PT3-Regressionsmodell:\n'
identify_reg(x, y, modellib.pt3 , shift=1.8)
print '\n'

print 'Identifikation mit Wendetangentenverfahren:\n'
identify_itm(x, y, shift=1.8)