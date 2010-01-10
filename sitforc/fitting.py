# coding: utf-8

'''
Dieses Modul enthält Klassen für das CurveFitting.
Es stehen ein polynomischer Fitter (L{PolyFitter}) und
ein Fitter für die Regressionsmodelle (L{ModelFitter}) zur
Verfügung.
'''

from abc import ABCMeta, abstractmethod

import numpy
import sympy

from sitforc import numlib, symlib

class Fitter(object):
    '''
    Abstrakte Basisklasse (ABC steht für
    AbstractBaseClass) für das CurveFitting.
    '''
    __metaclass__ = ABCMeta
    def __init__(self, x, y):
        self.data = x, y
        self.data_cache = dict()
        '''
        Für jede berechnete Ableitung wird in diesem Dictionary 
        ein Dictionary mit der Nummer der Ableitung 
        als Key angelegt. Dieses "innere" Dictionary
        speichert das Python-Objekt (Key "obj"), das die 
        gefittete Funktion darstellt, eine String-Repräsentation 
        (Key "repr") dieses Objekts und alle berechneten 
        Funktionswerte (Key "values") für diese Ableitung.
        '''
        
    @property
    def x(self):
        '''
        Property.
        '''
        return self.data[0]
    
    @property
    def y(self):
        '''
        Property.
        Gibt die Funktionswerte der nullten Ableitung 
        (der gefitteten Funktion) zurück.
        '''
        return self.data_cache[0]['values']
    
    def _fill_cache(self, n, obj, values, repr_str):
        '''
        Schreibt die Daten in den Cache.
        Siehe L{Fitter.data_cache} für genauere 
        Informationen.
        '''
        self.data_cache[n] = dict()
        self.data_cache[n]['obj'] = obj
        self.data_cache[n]['values'] = values
        self.data_cache[n]['repr'] = repr_str
    
    @abstractmethod
    def _derivate(self, n):
        '''
        Berechnet die 3 Werte der n-ten Ableitung 
        (s. L{Fitter.data_cache}).
        '''
        pass
    
    def repr_func(self, n=0):
        '''
        Gibt die String-Repräsentation der n-ten Ableitung 
        zurück.
        '''
        self._derivate(n)
        return self.data_cache[n]['repr']
    
    def get_values(self, n=0):
        '''
        Gibt die Funktionswerte der n-ten Ableitung 
        zurück.
        '''
        self._derivate(n)
        return self.data_cache[n]['values']
    
class PolyFitter(Fitter):
    '''
    Klasse zum polynomischen CurveFitting.
    '''
    def __init__(self, x, y, degree):
        Fitter.__init__(self, x, y)
        
        coeffs = numpy.polyfit(x, y, degree)
        repr_str = str(numpy.poly1d(coeffs))
        values = numpy.polyval(coeffs, self.x)
        self._fill_cache(0, coeffs, values, repr_str)
    
    def __str__(self):
        return self.data_cache[0]['repr']
        
    @property
    def degree(self):
        '''
        Property.
        Grad der polynomischen Näherungskurve.
        Das ist die Anzahl der Koeffizienten der nullten
        Ableitung - 1.
        '''
        return len(self.data_cache[0]['obj']) - 1
        
    def _derivate(self, n):
        '''
        Berechnet die Werte der n-ten Ableitung.
        Hier kommt der Nutzen des Datencaches (L{Fitter.data_cache}) 
        zum Vorschein. Falls n noch nicht im Cache ist, wird
        die größte Ableitung m im Cache gesucht, die kleiner als n
        ist. Wenn man nun die m-te Ableitung (n-m) mal ableitet, 
        ist dies die n-te Ableitung der Ausgangsfunktion, allerdings
        mit weniger Rechenaufwand.
        '''
        if n not in self.data_cache:
            m = max((d for d in self.data_cache if d < n))
            coeffs_m = self.data_cache[m]['obj']

            coeffs = numpy.polyder(coeffs_m, n - m)
            repr_str = str(numpy.poly1d(coeffs))
            values = numpy.polyval(coeffs, self.x)
            self._fill_cache(n, coeffs, values, repr_str)
            
    
    def get_inflec_points(self):
        '''
        Berechnet alle (realen) Wendepunkte
        im Bereich von x.
        '''
        coeffs = self.data_cache[0]['obj']
        self._derivate(1)
        coeffs1 = self.data_cache[1]['obj'] # 1. Ableitung
        self._derivate(2)
        coeffs2 = self.data_cache[2]['obj'] # 2. Ableitung
        self._derivate(3)
        coeffs3 = self.data_cache[3]['obj'] # 3. Ableitung
        inflec_points = [float(x_val) for x_val 
                         in sorted(numpy.roots(coeffs2))
                         if x_val.imag == 0 and 
                         numpy.polyval(coeffs3, float(x_val)) != 0 and
                         self.x[0] <= float(x_val) <= self.x[-1]]
        #x_vals = numpy.array(inflec_points)
        #y_vals = numpy.polyval(coeffs, x_vals)
        #slopes = numpy.polyval(coeffs1, x_vals)
        return [(x_point, numpy.polyval(coeffs, x_point), 
                 numpy.polyval(coeffs1, x_point)) 
                 for x_point in inflec_points]
        #return x_vals, y_vals, slopes
    
class ModelFitter(Fitter):
    '''
    CurveFitting mit einem Regressionsmodell.
    Genauere Erläuterungen zur Verwendung von Modellen 
    finden sich unter L{core.Model} und L{core.ModelLibrary}.
    '''
    def __init__(self, x, y, model, **params):
        Fitter.__init__(self, x, y)
        self.model = model
        self.params = dict(self.model.default_params)
        self.params.update(params)
        
        numlib.modelfit(self.model, self.params, x, y)
        
        sym_func = symlib.generate_sym_func(self.model.funcstring, 
                                            self.params)
        repr_str = sympy.pretty(sym_func)
        values = self.model(self.x, self.params)
        self._fill_cache(0, sym_func, values, repr_str)
        
    def __str__(self):
        return self.data_cache[0]['repr']
        
    def _derivate(self, n):
        if n not in self.data_cache:
            m = max((d for d in self.data_cache if d < n))
            sym_func = self.data_cache[m]['obj']

            derivate = symlib.diff_func(sym_func, n - m)
            repr_str = sympy.pretty(derivate)
            func = numlib.generate_func(derivate)
            values = func(self.x, None)
            self._fill_cache(n, derivate, values, repr_str)
        

