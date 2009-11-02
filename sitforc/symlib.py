# coding: utf-8

'''
Library for symbolic calculations.
'''

from sympy import factorial as fac
from sympy import exp, sin

from sympy import Symbol, diff

def generate_sym_func(funcstring, p):
    '''
    Generates a symbolic function of the
    given string and the parameters p.
    '''
    x = Symbol('x')
    return eval(funcstring)

def diff_func(sym_func, n):
    x = Symbol('x')
    return diff(sym_func, x, n)