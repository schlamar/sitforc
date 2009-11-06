#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import unittest
import sys

import test_core
import test_funcparser

 
suite = unittest.TestSuite()
suite.addTest(test_core.suite)
suite.addTest(test_funcparser.suite)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    sys.exit((result.errors or result.failures) and 1 or 0)