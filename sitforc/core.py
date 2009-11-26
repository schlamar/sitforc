#coding: utf-8

'''
Enthält Klassen und Methoden für die Identifikation
von gegebenen Daten und zum Anzeigen, Ändern und 
Erstellen von Regressionsmodellen.
'''


import os
from abc import ABCMeta, abstractmethod
from functools import partial
from itertools import izip
from warnings import warn

import numpy
import configobj
from configobj import ConfigObj
from matplotlib.pyplot import (figure, legend, grid, text, show,
                               subplot, plot)

from sitforc.funcparser import parse_func, ParseException
from sitforc.fitting import ModelFitter, PolyFitter

class SitforcWarning(Warning):
    pass

class Model(object):
    '''
    Diese Klasse stellt ein Regressionsmodell dar. Das Modell
    ist dabei als String einer mathematischen Funktion
    hinterlegt, dabei wird die Syntax von Python verwendet.
    Dieser String wird geparst und mit Hilfe der "eval"-Funktion
    zu einer echten (lambda-)Funktion evaluiert.
    '''
    def __init__(self, name, func, funcstring, latex, **params):
        self.name = name
        self.func = func
        self.funcstring = funcstring
        self.default_params = params
        self.latex = latex
        self.comment = ''
        
    def __call__(self, x, *p, **p_kws):
        '''
        Ruft die Funktion mit den übergebenen
        x-Werten auf. Die Parameter können entweder als
        Dictionary übergeben werden oder als
        Keyword-Parameter. Wenn keine Parameter übergeben
        werden, wird die Funktion mit den Default-Werten
        aufgerufen.
        '''
        if p:
            return self.func(x, p[0])
        elif p_kws:
            params =  dict(self.default_params)
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
        Ändert die Default-Parameter für dieses Model.
        '''
        self.default_params.update(params)
        
    def show(self):
        '''
        Zeigt die Modelfunktion in einem Fenster. 
        
        Dafür wird der generatierte LaTeX-String automatisch
        gerendert.
        '''
        figure(figsize=(10, 2))
        subplot(111, frameon=False, xticks=[], yticks=[])
        text(0.5, 0.5, self.latex, fontsize=30, horizontalalignment='center')
        #show()
        
    def plot(self, x=None):
        if x == None:
            x = numpy.arange(0, 10, 0.1)
        figure()
        plot(x, self(x))
        show()

        
# REPORT: explain why not implemented as singleton
class ModelLibrary(object):
    '''
    Diese Klasse beinhaltet alle definierten 
    Regressionsmodelle, die in der Datei "modellib.sfm"
    hinterlegt sind. Es können weitere Modelle hinzugefügt
    werden und in der Datei abgespeichert werden.
    
    Hinweis: Diese Klasse ist als Singleton zu betrachten.
    Es darf keine Instanz dieser Klasse erzeugt werden, 
    stattdessen sollte man das Attribut "modellib" 
    dieses Moduls verwenden.
    '''
    def __init__(self):
        self.lib = dict()
        self._load()
        
    def __str__(self):
        models = '\n\n'.join((str(self.lib[k]) for k in sorted(self.lib)))
        return ('\n\n{0}\n\n'.format(models)
                .join(['**** Model Library of SITforC *****'] * 2))
        
    def __call__(self, name):
        return self.lib[name]
    
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
        Lädt die definierten Modelle in der Datei "modellib.sfm".
        '''
        folder = os.path.dirname(__file__)
        try:
            config = ConfigObj(os.path.join(folder, 'modellib.sfm'))
        except configobj.ConfigObjError, e:
            raise configobj.ConfigObjError('File "modellib.sfm" has an error: {0}'
                                       .format(e))
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
            except ParseException, e:
                warn('Function for model "{0}" in "modellib.sfm" has '
                     'an error: {1}'.format(modelname, e), 
                     SitforcWarning)
                continue

            try:
                func(1, params)
            except KeyError, e:
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
        Setzt die Bibliothek zurück auf den Stand
        des letzten Speichervorgangs.
        '''
        self.lib = dict()
        self._load()
        
    def save(self):
        '''
        Speichert die Bibliothek.
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
        Legt ein neues Modell in der Bibliothek an.
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
    Abstrakte Basisklasse zum Identifizieren
    von Daten.
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
        pass
    
    @abstractmethod
    def plot_solution(self):
        pass
    
class RegressionIdentifier(Identifier):
    '''
    Klasse zum Identifizieren von Daten mit einem
    Regressionsmodell.
    '''
    def __init__(self, x, y, model):
        Identifier.__init__(self, x, y)
        
        self.model_fitter = ModelFitter(x, y, model)
        
    def show_solution(self):
        mf = self.model_fitter
        
        print ('Die Parameter des Modells "{0}" mit der Funktion in Fig. 1 '
               'wurden an folgende Werte angenaehert:\n{1}').format(
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
    def __init__(self, x, y, degree):
        Identifier.__init__(self, x, y)
        
        self.poly_fitter = PolyFitter(x, y, degree)
        self.i_points = self.poly_fitter.get_inflec_points()
        
        self.calculate_inflec_point(0)
    
    @property    
    def t_x(self):
        ''' 
        x-Werte der Tangente
        '''
        return numpy.arange(self.death_time, self.end_time, 0.1)
    
    @property    
    def t_y(self):
        '''
        y-Werte der Tangente
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
        # Jedes Tuple in i_points enthält, den x und y-Wert
        # sowie die Steigung
        x, y, m = self.i_points[num]
        
        # Tangentenform "mx + b = y"
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
        print 'Tangente: {0}x + {1}'.format(m, b)
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
    Verschiebt die Daten um ``width`` und schneidet die 
    Daten < 0 aus. Die Funktion wird also auf der x-Achse 
    nach links verschoben. Funktioniert nur für positive Werte.
    
    Kann beispielsweise verwendet werden, wenn der Sprung 
    nicht zum Zeitpunkt t=0 auf das System gegeben wurde,
    sondern erst später.
    '''    
    i = numpy.nonzero(x > width)
    return x[i] - width, y[i]

def identify_reg(x, y, model, shift=0.0):
    if shift > 0:
        x, y = shift_data(x, y, shift)
    ri = RegressionIdentifier(x, y, model)
    ri.show_solution()
    
def identify_itm(x, y, degree=11, shift=0.0):
    if shift > 0:
        x, y = shift_data(x, y, shift)
    itmi = ITMIdentifier(x, y, degree)
    itmi.show_solution()

def _convert_excel_float(value):
    return float(value.replace(',', '.'))  
load_csv = partial(numpy.loadtxt, delimiter=';', unpack=True, 
                   converters = {0: _convert_excel_float, 
                                 1: _convert_excel_float} )
#TODO: kommentare
        