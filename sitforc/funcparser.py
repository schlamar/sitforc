'''
funcparser
'''

from __future__ import division

import ast

import numlib

ALLOWED_CALLS = ['fac', 'exp', 'sin']

class ParseException(Exception):
    pass

class parse_rules:
    '''
    Contains the rules for parsing a function.
    '''
    def __init__(self):
        raise ParseException('Cannot instantiate the parser class')
        
    def Expression_eval(expr, glob, p):
        body = expr.body.eval(glob, p)
        return r'$%s$' % body
   
    def BinOp_eval(op, glob, p):
        left = op.left.eval(glob, p)
        right = op.right.eval(glob, p)
        return op.op(left, right)
    
    def UnaryOp_eval(op, glob, p):
        operand = op.operand.eval(glob, p)
        return op.op(operand)
       
    def Name_eval(name, glob, p):
        keywords = ['x', 'p']
        keywords.extend(ALLOWED_CALLS)
        if name.id in keywords:
            return name.id
        raise ParseException('Undefined Keyword("{0}")'
                             .format(name.id))
   
    def Call_eval(call, glob, p):
        func = call.func.eval(glob, p)
        args = [a.eval(glob, p) for a in call.args]
        if func in ALLOWED_CALLS:
            if not len(args) == 1:
                raise ParseException('Function "{0}" expects one argument'
                                     .format(func))
            if func == 'exp':
                return r'\mathrm{e}^{%s}' % args[0]
            if func == 'sin':
                return r'\sin{%s}' % args[0]
            if func == 'fac':
                return r'%s\mathrm{!}' % args[0]
        raise ParseException('Undefined Function("{0}")'
                             .format(func))
   
    def Subscript_eval(subscr, glob, p):
        value = subscr.value.eval(glob, p)
        if value == 'p':
            key = subscr.slice.eval(glob, p)
            p[key] = 1
            return key
        raise ParseException('Use only "p" for subscript(used "{0}")'
                             .format(value))

    def Index_eval(index, glob, p):
        return index.value.eval(glob, p)
   
    def Str_eval(str, glob, p):
        return str.s
    
    def Num_eval(num, glob, p):
        return num.n
    
    # Binary operators:
    
    def Add___call__(add, l, r):
        return r'(%s + %s)' % (l, r)
    
    def Sub___call__(sub, l, r):
        return r'(%s - %s)' % (l, r)
    
    def Div___call__(div, l, r):
        return r'\frac{%s}{%s}' % (l, r)
    
    def Mult___call__(mult, l, r):
        return r'%s \cdot %s' % (l, r)
    
    def Pow___call__(power, l, r):
        return r'(%s)^{%s}' % (l, r)
    
    
    # Unary operators:
    
    def USub___call__(usub, o):
        return r'-(%s)' % o
   
    @classmethod
    def install(cls):
        for name, method in cls.__dict__.items():
            if name[0].isupper():
                c, n = name.split("_", 1)
                setattr(getattr(ast, c), n, method)
             
parse_rules.install()

def parse_func(funcstring):
    '''
    Parsing a function.
    @return: Tuple with 3 elements:
        1) Generated lambda function.
        2) Parsed latex expression.
        3) A list with names of the identified parameters.
    '''
    params = dict()
    
    try:
        expr = ast.parse(funcstring, mode='eval')
    except Exception, e:
        raise ParseException('{0}: {1} '
                             .format(e.__class__.__name__,
                                     funcstring))
    try:
        latex = expr.eval(globals(), params)
    except ParseException, e:
        raise ParseException('{0}: {1} '.format(e, funcstring))
    except Exception, e:
        raise ParseException('{0}: {1} '
                             .format(e.__class__.__name__,
                                     funcstring))
    
    ident_params = params.keys()
    
    func = numlib.generate_func(funcstring)
        
    return func, latex, ident_params
