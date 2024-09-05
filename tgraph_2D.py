#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 14:38:45 2022

@author: ananya
"""

import os
import sys
import glob

##########################################

# dashed line in output

def prl():
  
  print("--------------------------------------------------------")
  
prl()
print("tgraph_2D.py")
prl()

args = sys.argv[1:]
n = len(args)

if n == 0:
  
  prl()
  print("Usage:")
  print("tgraph_2D.py [expr_FILE1 expr_FILE2 ...]")
  print()
  print("NOTE: When specifying list of arguments with shell ")
  print("command line experssions with characters like ")
  print("'*','?','[]',etc., the expression has to be inside")
  print(" \" \" to signify a single string and it must have")
  print("the string specifying the plane (XY, XZ, YZ) and")
  print("at least be completed upto the '.' in the file name.")
  prl()
  
else:
  
  expr = args[0] # expression provided

  command = "tgraph.py -c 3:6:9" # command to be executed
  
  c1 = '' # first coordinate/column
  c2 = '' # second coordinate/column
  
  if   expr.find('XY')!= -1: # plotting on XY plane
    c1 = 'x' # first coordinate/column
    c2 = 'y' # second coordinate/column
  elif expr.find('XZ')!= -1: # plotting on XY plane
    c1 = 'x' # first coordinate/column
    c2 = 'z' # second coordinate/column
  elif expr.find('YZ')!= -1: # plotting on XY plane
    c1 = 'x' # first coordinate/column
    c2 = 'z' # second coordinate/column
  else:
    print("I don't know which plane to plot on. :(")
    
  if c1:

    files = glob.glob(expr, recursive=False)
    for file in files: # iterating over file names
      # creating coordinate 1 and 2 file names
      i_sl = file.rfind('/')
      path = file[:i_sl+1] # getting path of var file
      name = file[i_sl+1:] # entire name of var file
      i_d = name.rfind('.')
      end = name[i_d:] # getting ending of var file after .
      c1file = path+c1+end # coord 1 file
      c2file = path+c2+end # coord 2 file
      
      # appending to command properly
      command += " { "+c1file+" "+c2file+" "+file+" }"

    # creating plot
    # print(command)
    os.system(command)
  

prl()
print("Exiting program.")
prl()