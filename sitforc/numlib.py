#coding: utf-8

'''
Numerische Berechnungen.
'''

from scipy import optimize

from math import factorial as fac
from numpy import exp, sin, cos

def generate_func(funcstring):
    return eval('lambda x,p: {0}'.format(funcstring))

def modelfit(function, paramdict, x, y):
    '''
    Fits the parameters of the function to the given
    data using the least square 
    '''
    params = [paramdict[key] for key in sorted(paramdict.keys())]
    
    def fill_pdict(params):
        for i, key in enumerate(sorted(paramdict.keys())):
            paramdict[key] = params[i]
            
    def f_error(params):
        fill_pdict(params)
        return y - function(x, paramdict)
    # REPORT: Function equivalent to MATLAB ``lsqcurvefit``
    params, success = optimize.leastsq(f_error, params) 
    fill_pdict(params)
    return success

import numpy

def smooth(x, window_len=11):
    """
    veränderte Version von
    http://www.scipy.org/Cookbook/SignalSmooth
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len < 3:
        return x

    s=numpy.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    w=numpy.ones(window_len,'d')

    y=numpy.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]
