'''
Created on 16.10.2009

Module for numeric calculations.
'''

from scipy import optimize

from math import factorial as fac
from numpy import exp, sin

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

def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
       
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
    
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len < 3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]
