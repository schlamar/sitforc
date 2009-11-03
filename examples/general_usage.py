# encoding: utf-8

'''
Example uses of ``sitforc``.
'''
from sitforc import modellib
from sitforc.core import PolyFitter
from sitforc.demo import generate_rand_data

# Working with modellib
print 'Print all models:\n'
print modellib, '\n'

print 'Access to a specific model:\n'
print modellib['pt1'], '\n'
print modellib.gaussian, '\n'

# Using a model
print modellib.pt2(5, modellib.pt2.default_params)
print modellib.pt2(5)
print modellib.pt2(3, k=47, w0=3, d0=7), '\n'

# Polynomial fitting:
x, y = generate_rand_data(modellib.gaussian)
cp = PolyFitter(x, y, degree=4)
print cp, '\n'
print cp.repr_func(), '\n'
print cp.repr_func(1), '\n'
print cp.repr_func(2), '\n'
print cp.repr_func(3), '\n'
print cp.repr_func(4), '\n'

y2 = cp.get_values(1)