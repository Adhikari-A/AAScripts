#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 14:38:45 2022

@author: ananya
"""

import os
import sys

##########################################

# dashed line in output

def prl():
  
  print("--------------------------------------------------------")
  
prl()
print("sgrid_plot.py")
prl()

args = sys.argv[1:]
n = len(args)

if n == 0:
  
  prl()
  print("Usage:")
  print("sgrid_plot.py [VAR_NAME_PATH] [LOCATION] [OPTIONS]")
  print()
  print("LOCATION: XY , XZ, YZ")
  print("OPTIONS: all, in, s1, s2, s1+, s2+")
  print()
  
elif n == 3:
  
  var = args[0]
  loc  = args[1]
  op  = args[2]
  
  command = "tgraph.py -c 1:2:3"
    
  boxes = {
            'XY':['[01234]','[789]','10','1[34567]','2[0123]','2[6789]'],
            'XZ':['[012]','[78]','1[345]','2[01]','2[67]'],
            'YZ':['[1234]']
          }
  
  if op == 'all':
    
    included_boxes = boxes[loc]

  elif loc == 'XY' or loc == 'XZ':
    
    if   op == 'in' :  included_boxes = boxes[loc][:-1]
    elif op == 's1+':  included_boxes = boxes[loc][:-3]
    elif op == 's2+':  included_boxes = boxes[loc][-3:-1]
    elif op == 's1' :  included_boxes = [boxes[loc][0]]
    elif op == 's2' :  included_boxes = [boxes[loc][-3]]
  
  for b in included_boxes:
    command += " "+var+"."+loc+b
    
  os.system(command)
  
else:
  
  print("Incorrect commandline options.")
  
prl()
print("Exiting program.")
prl()