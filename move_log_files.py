#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 10:14:54 2023

@author: ananya
"""

import os
import sys

dl = "----------------------------------------------------------"
print(dl)
print("'move_log_files.py'")
print(dl)

args = sys.argv[1:]
n = len(args)

if n > 3:
  print("Wrong commandline specifications. Try again.")
  
else:

  mv_a     = False # move all or not
  mv       = False # whether move files or print instructions
  parfile  = None  # name of file when only one par file is target
  
  if n == 0:
    
    print("For usage instructions, type:")
    print("move_log_files.py -h")
    print(dl)
    mv = True
    
  elif args[-1] == '-h':
    
    print("Usage:")
    print("move_log_files.py")
    print("move_log_files.py -a")
    print("move_log_files.py -p name.par")
    print()
    print("If '-a' option is specified, moves all")
    print("logfiles created by the 'submitjob'")
    print("script in current working directory to")
    print("a directory called 'logfiles' in there.")
    print()
    print("If '-a' is not specified, moves all")
    print("logfiles except the last one for each")
    print("parfile.")
    print()
    print("If '-p' is used, then logfiles corresponding")
    print("to only 'name.par' are moved. This can be used")
    print("with '-a' to move all logfiles for 'name.par'.")
    
  else:
    
    if '-a' in args:
    
      print("WARNING: You have selected '-a' option.")
      print("This will move all logfiles. If there")
      print("are ongoing runs, they will be hampered.")
      op = input("Do you want to proceed? (y/n): ")
      
      if op == 'y':
        print("Your response is 'y'. Moving all logfiles.")
        mv_a = True
      else:
        print("Your response is not 'y'.\n"
              "Moving all but last logfiles for each parfile.")
        
      mv = True
      print(dl)
  
    if '-p' in args:
      
      if os.path.isfile(args[args.index('-p') + 1]) and \
        args[args.index('-p') + 1].endswith(".par"):
        parfile = args[args.index('-p') + 1]
        mv = True
      else:
        print("This is not a par file:")
        print(parfile)
        mv = False
  
  if mv:
    
    create_dir = True

    # listing all files in curent directory      
    all_files = os.listdir()
    all_files.sort()

    # getting par file names
    par_files = []
    if parfile:
      par_files.append(parfile)
    else:
      print("Parfiles found in directory:\n")
      for file in all_files:
        if file.endswith(".par"): 
          print(file)
          par_files.append(file)
    
    if not par_files:
      print("No parfiles found.")
      
    else:
      print(dl)
      
      for par_file in par_files:
        print("Getting logfiles corresponding to parfile:")
        print(par_file)
        logfiles = []
        # getting logfiles for current par file
        for file in all_files:
          if file.startswith(par_file+'.o'):  logfiles.append(file)
        
        if not mv_a:  logfiles = logfiles[:-1]
        
        if logfiles:
          
          if create_dir:
            # make the 'logfiles' directory if it does not exists
            if not os.path.isdir('logfiles'):
              os.mkdir('logfiles')
            create_dir = False
          
          print("Moving to 'logfiles' directory.")
          command = "mv "
          for lf in logfiles:  command+=lf+" "
          command+="logfiles"
          os.system(command)
          print("Done! :)")
        else:
          print("No logfiles to move.")
        print(dl)
  
      print("Finished everything! :)")

print(dl)
print("Exiting program.")
print(dl)