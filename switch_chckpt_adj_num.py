#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 15:20:00 2023

@author: ananya
"""

import os
import sys
from ast import literal_eval

##########################################
"""
this function checks the type of information
embedded inside "string"
"""
def type_embedded_in_string(string):
  
  info_type = None
  
  try:
    info_type = type(literal_eval(string))

  except (ValueError, SyntaxError):
    info_type = str

  return info_type


##########################################

print("====================================================")
print("'switch_chckpt.py'")
print("====================================================")

args = sys.argv[1:]
na   = len(args)

if na == 0:
  
  print("Usage:")
  print("switch_chckpt.py path nMPI bkup_index")
  print()
  print("path: path of run output directory")
  print("nMPI: total number of MPI jobs for given run")
  print("bkup_index: suffix index for the backup checkpoints of choice (0 or 1)")
  
elif na != 3:

  print("Incorrect number of commandline args.")

else:
  
  path = args[0]
  print("Beginning to switch checkpoints in directory:")
  print(path)
  print()
  
  if os.path.isdir(path):
    
    if path[-1] != "/": path += "/"
    # print("path ="+path)
    snmpi      = args[1]
    sibkup     = args[2]
    # print("snmpi ="+ snmpi)
    # print("sibkup ="+ sibkup)
    typ_nmpi  = type_embedded_in_string(snmpi)
    typ_ibkup = type_embedded_in_string(sibkup)
    
    if typ_nmpi != int or typ_ibkup != int:
      print("Specs for nmpi and bkup_index must be integers.")
    elif int(sibkup) != 0 and int(sibkup) != 1:
      print("Spec for bkup_index can only be 1 or 0.")
    else:
      impi  = int(snmpi)
      # ibkup = int(sibkup)
      base = 'checkpoint.'
      nd = len(snmpi)
      print("====================================================")
      print("Switching:\n")      
      for i in range(impi):
        si        = str(i)
        adji      = si.rjust(nd,'0')
        file      = base+adji
        file_bkup = base+adji+"_"+sibkup
        print(file+" with "+file_bkup)
        file = path+file
        file_bkup = path+file_bkup
        os.system("mv "+file_bkup+" "+file)
    
  else:
    print("This is not a directory.")
    print("Path provided must be a directory.")
    
print("====================================================")    
print("Exiting program.")
print("====================================================")
