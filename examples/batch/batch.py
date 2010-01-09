#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from sitforc import modellib, load_csv
from sitforc.core import RegressionIdentifier, ITMIdentifier

#Öffne Datei zum Lesen
with open('results.txt', 'w') as f_out: 
    #Standardausgabe in Datei lenken
    sys.stdout = f_out
    
    #Alle Dateien des aktuelle Ordners auslesen
    for filename in os.listdir(''):
        #CSV-Dateien filtern
        if filename.endswith('.csv'):
            #Ausgabe
            print 'File: {0}'.format(filename)
            #Daten laden
            x, y = load_csv(filename)
            #Fitting an Regressionsmodell
            ident = RegressionIdentifier(x, y, modellib.pt2)
            #Ausgabe
            mf = ident.model_fitter
            print 'Params for PT-2 Model: {0}'.format(mf.params)
            
            #Wendetangentenverfahren
            degree = 11 #Grad des Polynoms
            ident = ITMIdentifier(x, y, degree)
            #Ausgabe
            print 'Params for ITM'
            print 'Tu\t\t{0:.3f}'.format(ident.tu)
            print 'Tg\t\t{0:.3f}'.format(ident.tg)
            print 'Tu/Tg\t\t{0:.3f}'.format(ident.tu/ident.tg)
            print
