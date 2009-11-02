#coding: utf-8

'''
Enthält Klassen und Methoden für die Identifikation
von gegebenen Daten und zum Anzeigen, Ändern und 
Erstellen von Regressionsmodellen.
'''

import os
from abc import ABCMeta, abstractmethod
from functools import partial

import numpy
from configobj import ConfigObj
from matplotlib.pyplot import (figure, legend, grid, text, show,
                               subplot, plot)

from funcparser import parse_func
from fitting import ModelFitter

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
        figure(figsize=(12, 2))
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
        config = ConfigObj(os.path.join(folder, 'modellib.sfm'))
        # Hinweis: Endung "sfm" steht für (s)it(f)orc(m)odels
        for modelname in config:
            params = dict()
            comment = ''
            for key in config[modelname]:
                if key == 'func':
                    funcstring = config[modelname][key]
                elif key == 'comment':
                    comment = config[modelname][key]
                else:
                    params[key] = config[modelname].as_float(key)
            func, latex, ident_params = parse_func(funcstring)
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

load_csv = partial(numpy.loadtxt, delimiter=';', unpack=True)
#TODO: improve?

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
               'wurden an folgende Werte angenaehert:\n{1}\nDamit ergibt sich '
               'die Funktion\n{2}').format(mf.model.name, mf.params, 
                                          mf.repr_func())
        modellib[mf.model.name].show()
        figure()
        plot(self.x, self.y, label='data')
        plot(mf.x, mf.y, label='fitted')
        legend()
        grid()
        show()
    
    def print_solution(self):
        mf = self.model_fitter
        



def _shift_data(x, y, width):
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
        x, y = _shift_data(x, y, shift)
    ri = RegressionIdentifier(x, y, model)
    ri.show_solution()
        