'''
For demonstration purposes only.
'''
from numpy import linspace
from numpy.random import rand

def generate_rand_data(model, range=(0,5), datasize=200, d_error=0.5):
    '''
    Generates random data with the given parameters.
    '''
    start, stop = range
    x = linspace(start, stop, datasize)
    
    y = model(x, model.default_params)
    
    # creating errors
    y = y + d_error * rand(y.shape[0])
                   
    return x, y