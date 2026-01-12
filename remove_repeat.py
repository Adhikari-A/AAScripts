#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 17:37:10 2023

@author: ananya
"""
##########################################
import sys
import os
import numpy as np
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

def prl():
  print("-----------------------------------------------")

##########################################

def instructions():
  print("Purpose:")
  print("Removes repeated time lines by keeping")
  print("only the first occurence of each time data.")
  print()
  print("Usage:")
  print("remove_repeat.py path [-t TIME_COLUMN]")
  print()
  print("Here path can be path to a single file or")
  print("path to a directory containing all files")
  print("to be cleaned. This must be first argument")
  print("in commandline after executable.")
  print()
  print("Option '-t' can be used to specify specific")
  print("time column index in file, counting from 0.")
  print("By default, 0-th column is taken as time column.")

##########################################
# list files in a directory

def files_in_dir(path,**kwargs):

  if path[-1] != "/": path += "/"

  files = [] # list of all files in path
  names = [] # names of files finally kept

  # if path is a directory
  if os.path.isdir(path):

    # getting list of files and dirs in path
    ls = os.listdir(path)

    if ls:
      for name in ls: # checking objects in path
        # full path of file
        full_name = path + name
        # if object is a file
        if os.path.isfile(full_name):
          files.append(full_name)
          names.append(name)

      # creating sorted list
      files.sort()
      names.sort()
    else:
      print("No files in directory. :(")

  else:
    print("Path is not a directory. :(")

  return files,names

##########################################

def clean_file(in_path,o_path,ti):

  try:
    fi = open(in_path,"r")
    lines = fi.readlines()
    fi.close()

    ln_std = None
    ln     = None
    lcount = 0

    # if lines[0][0] == '"':
    #   lines = lines[1:]

    # data = np.loadtxt(in_path)
    # data = np.loadtxt(lines)
    f = open(o_path,"w+") # output file

    last_included  = None # last time for which data is read into clean file
    # increasing = True #

    # for d in data: # reading through each data line in file
    for l in lines: # reading through each data line in file
      if l:
        if l[0]=='"' or l[0]=='#': # header line
          header_line = f"# {l}"
          f.write(header_line)
        else: # data line
          tokens = l.split()
          # print(d[0])
          # first time value or next time value to be read
          if not last_included or float(tokens[ti]) > last_included:
            if not last_included:  ln_std = len(tokens) # number of items in first line
            ln = len(tokens) # number of items in currnt line
            if ln == ln_std: # if current line has same number of items as first
              last_included = float(tokens[ti]) # setting new time to last read
              # l = ""
              # for num in d:  l+="{} ".format(num)
              # f.write(l+"\n")
              f.write(l)
              # print(d)
            elif lcount==1: # if second line problematic, not sure what is happening
              print("Something is problematic in file.")
              break

      lcount += 1

    f.close()
  except:
    print("Problem with reading file:")
    print(in_path)

##########################################

def clean(path,ti):

  if os.path.isfile(path): # if only one file to be cleaned

    o_path = path+'_rr.txt'
    print("Output in file:")
    print(o_path)
    clean_file(path,o_path,ti)

  elif os.path.isdir(path): # if multiple files to be cleaned in a directory

    if path[-1] == '/' :  path = path[:-1]
    o_dir = path+'_rr'
    print("Outputs in directory:")
    print(o_dir)
    if os.path.isdir(o_dir):
      os.system('rm -rf '+o_dir)
    os.mkdir(o_dir)
    files,names = files_in_dir(path)

    for file,name in zip(files,names):
      o_path = o_dir+'/'+name
      clean_file(file,o_path,ti)
      # print(file)
      # print(o_path)

##########################################
###############
# main part   #
###############
prl()
print("'remove_repeat.py'")
prl()

args = sys.argv[1:]
n = len(args)

if n==0:
  instructions()

elif n > 3:
  print("Unknown commandline arguments specification. :(")

else:

  path = args[0]

  if not os.path.isdir(path) and not os.path.isfile(path):

    print("Commandline argument not file or directory. :(")

  else:

    # set time column index
    ti = 0
    if '-t' in args and args.index('-t')!= n-1 and \
      type_embedded_in_string(args[args.index('-t')+1]) != 'int':
        ti = int(args[args.index('-t')+1])

    print("Time column index (counting from 0): {}\n".format(ti))

    clean(path,ti)

prl()
print("Exiting program.")
prl()