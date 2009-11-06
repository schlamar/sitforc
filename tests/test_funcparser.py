import unittest

from sitforc.funcparser import parse_func, ParseException

class TestFuncparser(unittest.TestCase):
    
    def test_parse_func(self):
        # exceptions
        
        funcstring = 'open("/etc/passwd").read()' # try injection
        self.assertRaises(ParseException, parse_func, funcstring)
        
        funcstring = '(2 + 3' # general syntax error
        self.assertRaises(ParseException, parse_func, funcstring)
        
        funcstring = '2 * x + 3 * y' # using not allowed keyword (1)
        self.assertRaises(ParseException, parse_func, funcstring)
        
        funcstring = '2 * 3 + t["dx"] * x' # using not allowed keyword (2)
        self.assertRaises(ParseException, parse_func, funcstring)
        
        # check resulting values
        
        funcstring = 'p["dx"]'
        f = parse_func(funcstring)[0]
        for value in [-1, 0, 1, 2, 3]:
            p = dict()
            p['dx'] = value
            self.assertEqual(f(0, p), value)
            
        funcstring = 'x'
        f = parse_func(funcstring)[0]
        g = lambda x: x
        for value in xrange(-5, 5):
            self.assertEqual(f(value, None), g(value))
            
        funcstring = '(x - 3) * (x + 2)'
        f = parse_func(funcstring)[0]
        funcstring = 'x**2 - x - 6' # funcs are equivalent
        g = parse_func(funcstring)[0]
        for value in xrange(-5, 5):
            self.assertEqual(f(value, None), g(value, None))
        self.assertEqual(f(3, None), 0) # root1
        self.assertEqual(f(-2, None), 0) # root2
        
        # check generated latex expressions
        
        funcstring = '2 + 3'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$(2 + 3)$')
        
        funcstring = '2 - 3'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$(2 - 3)$')
        
        funcstring = '2 * 3'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$2 \cdot 3$')

        funcstring = '2 / 3'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$\frac{2}{3}$')
        
        funcstring = '2 ** 3'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$(2)^{3}$')
        
        funcstring = '-(2 + 3)'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$-((2 + 3))$')
        
        funcstring = '-(x)'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$-(x)$')
        
        funcstring = 'x + p["c"]'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$(x + c)$')
        
        funcstring = 'exp(2)'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$\mathrm{e}^{2}$')
        
        funcstring = 'sin(x)'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$\sin{x}$')
        
        funcstring = 'fac(x)'
        latex = parse_func(funcstring)[1]
        self.assertEqual(latex, r'$x\mathrm{!}$')
        
        # check identified parameters
        
        params = ['dx']
        funcstring = 'p["dx"]'
        identified_params = parse_func(funcstring)[2]
        for param in params:
            self.assertTrue(param in identified_params)
            
        params = ['t1', 't2', 't3']
        funcstring = 'p["t1"] + p["t2"] + p["t3"]'
        identified_params = parse_func(funcstring)[2]
        for param in params:
            self.assertTrue(param in identified_params)
            
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestFuncparser))

if __name__ == '__main__':
    unittest.main()