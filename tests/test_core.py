# coding: utf-8

from warnings import catch_warnings
import os
import unittest

import configobj

from sitforc.core import Model, modellib
from sitforc.core import SitforcWarning

class TestModel(unittest.TestCase):    
    def test_model(self):
        name = 'a1'
        func = lambda x, p: x + p["c"]
        funcstring = 'x + p["c"]'
        latex = '$(x + c)$'
        model = Model(name, func, funcstring, latex, c=1)
        
        # check calling
        self.assertEqual(model(1), 2)
        
        # check setting default params
        model.set_default_params(c=2)
        self.assertEqual(model.default_params["c"], 2)
        self.assertEqual(model(1), 3)
        
class TestModelLibrary(unittest.TestCase): 
    def tearDown(self):
        modellib.reset()
        
    def test_modellib(self):
        modellib.new_model('m1', None, None, None)
        # Warnung abfangen
        with catch_warnings(record=True) as w:
            modellib.new_model('m1', None, None, None)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, SitforcWarning))
    
    def test_fileops_modellib(self):
        # check file operations of modellib
        
        fpath = os.path.join('..', 'sitforc')
        os.rename(os.path.join(fpath, 'modellib.sfm'),
                  os.path.join(fpath, 'modellib2.sfm'))
        try:
            with catch_warnings(record=True) as w:
                modellib.reset()
                self.assertEqual(len(w), 1)
                self.assertTrue(issubclass(w[0].category, SitforcWarning)) 
                
            with open(os.path.join(fpath, 'modellib.sfm'), 'w') as fobj:
                fobj.write('[section\nwithout=end')
            try:
                self.assertRaises(configobj.ConfigObjError, modellib.reset)
            finally:
                os.remove(os.path.join(fpath, 'modellib.sfm'))
            
            try:    
                modellib.new_model('m1', None, '2 + 3', None, c=2)
                modellib.save()
                modelfile='''[m1]
func = 2 + 3
c = 2
'''
                with open(os.path.join(fpath, 'modellib.sfm')) as fobj:
                    self.assertEqual(modelfile, fobj.read())
            finally:
                os.remove(os.path.join(fpath, 'modellib.sfm'))
            
                      
        finally:
            os.rename(os.path.join(fpath, 'modellib2.sfm'),
                      os.path.join(fpath, 'modellib.sfm'))

        
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestModel))
suite.addTest(unittest.makeSuite(TestModelLibrary))

if __name__ == '__main__':
    unittest.main()        
