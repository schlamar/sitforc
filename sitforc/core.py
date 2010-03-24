#coding: utf-8

'''
Classes and functions for the identification
and for working with regression models.
'''


import os
from abc import ABCMeta, abstractmethod
from functools import partial
from itertools import izip
from warnings import warn

import numpy
import configobj
from configobj import ConfigObj

import matplotlib
matplotlib.use('GTKAgg')
from matplotlib.pyplot import (figure, legend, grid, text, show,
                               subplot, plot)

from sitforc.funcparser import parse_func, ParseException
from sitforc.fitting import ModelFitter, PolyFitter

class SitforcWarning(Warning):
    pass

class Model(object):
    '''
    This class represents a regression model.
    The model itself is a string of a
    mathematical function (using Python syntax).
    This string is parsed and evaluated to a
    "real" (lambda-) function.
    '''
    def __init__(self, name, func, funcstring, latex, **params):
        self.name = name
        self.func = func
        self.funcstring = funcstring
        self.default_params = params
        self.latex = latex
        self.comment = ''
        
    def __call__(self, x, p=None, **p_kws):
        '''
        Calls the function with the given x
        values. Parameters can be passed as a 
        dictionary or as keyword parameters.
        If no parameters are delivered, the 
        default parameters are used. 
        '''
        if p:
            return self.func(x, p)
        elif p_kws:
            params = dict(self.default_params)
            params.update(p_kws)
            return self.func(x, params)
        else:
            return self.func(x, self.default_params)
        
    def __str__(self):
        return ('** Regression model **\n'
                'Name: {0}\nFunc: {1}\nStandard-Params: {2}'
               .format(self.name, self.funcstring, 
                       self.default_params))
        
    def set_default_params(self, **params):
        '''
        Changes the default parameters for this model.
        '''
        self.default_params.update(params)
        
    def show(self):
        '''
        Shows the function of the model in a seperate window. 
        
        Therefore the LaTeX representation is automatically
        rendered.
        '''
        figure(figsize=(10, 2))
        subplot(111, frameon=False, xticks=[], yticks=[])
        text(0.5, 0.5, self.latex, fontsize=30, horizontalalignment='center')
        
    def plot(self, x=None):
        '''
        Plots the curve of the model from [0..10] if
        x is not passed.
        '''
        
        if not x:
            x = numpy.arange(0, 10, 0.1)
        figure()
        plot(x, self(x))
        show()

        
class ModelLibrary(object):
    '''
    This class contains the regression
    models, which are defined in the file
    "modellib.sfm". New models can be added
    and saved into this file.
    
    Hint: See this class as singleton. Don't
    instantiate it. Use the attribute "modellib"
    of this module if you want to work with 
    the model library.
    '''
    def __init__(self):
        self.lib = dict()
        self._load()
        
    def __str__(self):
        models = '\n\n'.join((str(self.lib[k]) for k in sorted(self.lib)))
        return ('\n\n{0}\n\n'.format(models)
                .join(['**** Model Library of SITforC *****'] * 2))
    
    def __getattr__(self, name):
        return self.lib[name]
    
    def __getitem__(self, name):
        return self.lib[name]
    
    def __iter__(self):
        return iter(self.lib.values())
    
    def __len__(self):
        return len(self.lib)
    
    def _load(self):
        '''
        Loads the defined models from "modellib.sfm".
        '''
        folder = os.path.dirname(__file__)
        try:
            config = ConfigObj(os.path.join(folder, 'modellib.sfm'))
        except configobj.ConfigObjError as e:
            txt = 'File "modellib.sfm" has an error: {0}'.format(e)
            raise configobj.ConfigObjError(txt)
        if not config:
            warn('File "modellib.sfm" could not read or is empty. '
                 'No models in modellib.', SitforcWarning)
        for modelname in config:
            params = dict()
            comment = ''
            funcstring = ''
            for key in config[modelname]:
                if key == 'func':
                    funcstring = config[modelname][key]
                elif key == 'comment':
                    comment = config[modelname][key]
                else:
                    params[key] = config[modelname].as_float(key)
            if not funcstring:
                warn('Function not defined for model "{0}" '
                     '(in "modellib.sfm").'.format(modelname), 
                     SitforcWarning)
                continue
            try:
                func, latex, ident_params = parse_func(funcstring)
            except ParseException as e:
                warn('Function for model "{0}" in "modellib.sfm" has '
                     'an error: {1}'.format(modelname, e), 
                     SitforcWarning)
                continue

            try:
                func(1, params)
            except KeyError as e:
                warn('Param {0} for model "{1}" is not defined '
                     'in "modellib.sfm".'.format(e, modelname), 
                     SitforcWarning)
                continue
            
            self.lib[modelname] = Model(modelname, func, 
                                        funcstring, latex, 
                                        **params)
            self.lib[modelname].comment = comment
            
    def reset(self):
        '''
        Reset the library to the last saved state.
        '''
        self.lib = dict()
        self._load()
        
    def save(self):
        '''
        Saves the library.
        '''
        config = ConfigObj()
        folder = os.path.dirname(__file__)
        config.filename = os.path.join(folder, 'modellib.sfm')
        for model in self.lib.values():
            config[model.name] = {}
            config[model.name]['func'] = model.funcstring
            config[model.name].update(model.default_params)
            if model.comment:
                config[model.name]['comment'] = model.comment
        config.write()
        
    
    def new_model(self, name, func, funcstring, latex, **params):
        '''
        Adds a new model to the library.
        '''
        model = Model(name, func, funcstring, latex, **params)
        if name not in self.lib:
            self.lib[name] = model
        else:
            warn('This Model already exists in modellib. '
                 'No changes to "{0}"'.format(name), SitforcWarning)
        
        
modellib = ModelLibrary()

class Identifier(object):
    '''
    Abstract base class for identifying data.
    '''
    __metaclass__ = ABCMeta
    def __init__(self, x, y):
        self.data = x, y
        
    @property
    def x(self):
        return self.data[0]
    
    @property
    def y(self):
        return self.data[1]
    
            
    @abstractmethod
    def show_solution(self):
        '''
        Print result and show plot.
        '''
        pass
    
    @abstractmethod
    def plot_solution(self):
        '''
        Plots the data and fitted curve to
        a separate figure window.
        '''
        pass
    
class RegressionIdentifier(Identifier):
    '''
    Identifies data with a regression model.
    '''
    def __init__(self, x, y, model):
        Identifier.__init__(self, x, y)
        
        self.model_fitter = ModelFitter(x, y, model)
        
    def show_solution(self):
        mf = self.model_fitter
        
        print ('The Parameters of the model "{0}" with the function in Fig. 1 '
               'were approximated to:\n{1}').format(
                mf.model.name, mf.params)
        modellib[mf.model.name].show()
        self.plot_solution()
        
    def plot_solution(self):
        mf = self.model_fitter
        figure()
        plot(self.x, self.y, label='data')
        plot(mf.x, mf.y, label='fitted')
        legend()
        grid()
        show()
        
class ITMIdentifier(Identifier):
    '''
    Identifies data with the inflectional tangent method.
    '''
    def __init__(self, x, y, degree):
        Identifier.__init__(self, x, y)
        
        self.poly_fitter = PolyFitter(x, y, degree)
        self.i_points = self.poly_fitter.get_inflec_points()
        
        self.calculate_inflec_point(0)
    
    @property    
    def t_x(self):
        ''' 
        x-values of the tangent.
        '''
        return numpy.arange(self.death_time, self.end_time, 0.1)
    
    @property    
    def t_y(self):
        '''
        y-values of the tangent.
        '''
        m = self.tangent_slope
        b = self.tangent_offset
        return m * self.t_x + b
    
    @property
    def tu(self):
        return self.death_time
    
    @property
    def tg(self):
        return self.end_time - self.death_time
        
    def calculate_inflec_point(self, num):
        '''
        Calculates the point of inflection.
        '''
        # Each tuple in i_points contains the x and y-value
        # plus the slope
        x, y, m = self.i_points[num]
        
        # tangential form: "mx + b = y"
        b = y - m*x
        self.death_time = -b/m
        self.tangent_slope = m
        self.tangent_offset = b
        self.split_point = self._calculate_split_point(x)
        
        i = numpy.nonzero(self.x > self.split_point)
        x, y = self.x[i], self.y[i]
        
        self.model_fitter = ModelFitter(x, y, modellib.exp_approach)
        mf = self.model_fitter
        self.height = mf.params['c']
        self.end_time = (self.height - b) / m
        
    def _calculate_split_point(self, begin):
        '''
        Calculate a useful point, where the tangent should stop
        and the exponential function begin.
        '''
        delta = 0.1
        x = self.poly_fitter.x
        y = self.poly_fitter.get_values(1)
        i = numpy.nonzero(x > begin)
        x, y = x[i], y[i]
        for x_val, y_val in izip(x, y):
            if abs(y_val - self.tangent_slope) > delta:
                return x_val
        
        
    def show_solution(self):
        m = self.tangent_slope
        b = self.tangent_offset
        print 'Tangent: {0}x + {1}'.format(m, b)
        print 'Tu: {0}'.format(self.tu)
        print 'Tg: {0}'.format(self.tg)
        print 'Tu/Tg: {0}'.format(self.tu/self.tg)
        print 'Tg/Tu: {0}'.format(self.tg/self.tu)
        self.plot_solution()
        
    def plot_solution(self):
        c = self.height
        plot(self.x, self.y, label='data')
        plot([self.x[0], self.x[-1]], [c, c], '--', label='limit')
        plot(self.t_x, self.t_y, label='tangent')
        legend()
        grid()
        show()
    
def shift_data(x, y, width):
    '''
    Shifts the data by "width" and cuts all values
    with x < 0. Use this function if the step response does
    not begin at t=0.
    '''    
    i = numpy.nonzero(x > width)
    return x[i] - width, y[i]

def identify_reg(x, y, model, shift=0.0):
    '''
    Processes regression model identifying.
    '''
    if shift > 0:
        x, y = shift_data(x, y, shift)
    ri = RegressionIdentifier(x, y, model)
    ri.show_solution()
    
def identify_itm(x, y, degree=11, shift=0.0):
    '''
    Processes the identification with the
    inflectional tangent method.
    '''
    if shift > 0:
        x, y = shift_data(x, y, shift)
    itmi = ITMIdentifier(x, y, degree)
    itmi.show_solution()

def _convert_excel_float(value):
    return float(value.replace(',', '.'))  

load_csv = partial(numpy.loadtxt, delimiter=';', unpack=True, 
                   converters = {0: _convert_excel_float, 
                                 1: _convert_excel_float} )
        
