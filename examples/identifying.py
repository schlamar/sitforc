#!/usr/bin/python
# -*- coding: utf-8 -*-

from sitforc import modellib, load_csv, identify_reg, identify_itm

x, y = load_csv('data.csv')
print 'Identification with regression model of 3rd-order time-delay element:\n'
identify_reg(x, y, modellib.pt3 , shift=1.8)
print '\n'

print 'Identification with inflectional tangent method:\n'
identify_itm(x, y, shift=1.8)