#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 16:21:53 2024

@author: ananya
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 12:26:14 2024

@author: ananya
"""

import time
import os
import logging
from logging import info
import datetime
import sys
from ast import literal_eval
from itertools import product
import shutil

logger = logging.getLogger(__name__)

pr = False # True

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

def objects_in_dir(path,**kwargs):

  get_dir = False
  if 'get_dir' in kwargs.keys() and kwargs['get_dir']==True:
    get_dir = True

  exclude = []
  if 'exclude' in kwargs.keys():
    exclude = kwargs['exclude']
    
  end = ''
  start = ''
  contains = ''
  contains_not = ''
  
  if 'end' in kwargs.keys():
    end = kwargs['end']
  
  if 'start' in kwargs.keys():
    start = kwargs['start']
    
  if 'contains' in kwargs.keys():
    contains = kwargs['contains']
    
  if 'contains_not' in kwargs.keys():
    contains_not = kwargs['contains_not']
    
  if path[-1] != "/": path += "/"
  
  objs = []
  names = [] # names of files finally kept

  # if path is a directory
  if os.path.isdir(path):

    
    # getting list of files and dirs in path
    ls = os.listdir(path)
    
    if ls:
      for name in ls: # checking objects in path
        # if include object
        if name not in exclude \
           and name.endswith(end) and name.startswith(start) \
           and contains in name \
           and (not contains_not or contains_not not in name): 
          # full path of file
          full_name = path + name
          # if object is a file
          if not get_dir and os.path.isfile(full_name):
            objs.append(full_name)
            names.append(name)
          elif get_dir and os.path.isdir(full_name):
            objs.append(full_name)
            names.append(name)
      
      # creating sorted list
      objs.sort()
      names.sort()
    
  return objs,names

##########################################

# main part

dl = '------------------------------------------------------------------------'

args = sys.argv[1:]
na   = len(args)

if na == 0:
  
  print("Usage:")
  print("switch_chckpt.py path n_previous_checkpoint")
  print("path: path of run output directory")
  print("n_previous_checkpoint: how many previous checkpoints to keep")
  print()
  print("If n_previous_checkpoint > 2, the oldest (n_previous_checkpoint - 2)")
  print("checkpoints will be compressed and stored in path_checkpoints.")

elif na != 2:

  print("Incorrect number of commandline args. Exiting.")

else:
  
  # setting some flags
  first = True # fist time looking for checkpoints
  last_time = None # time stamp of last backed up checkpoint
  nMPI = "" # number of MPI processes
  
  path = args[0] # path of output dir
  
  if os.path.isdir(path): # if path is a directory
  
    if pr:
      print("Dir exists.")
      print(path)
    
    if type_embedded_in_string(args[1]) == int: # if backup count is integer
      
      if pr:  print("Number on n previous found.")
      
      n = int(args[1]) # backup previous checkpoints count
      
      if pr:  print(n)

      if n >0: # if valid count
        
        names = None
        i_n = 0
        
        if pr:  print("Looking for stdout files.")
        
        for i in range(20):
          if pr:  print("Attempt: {}".format(i))
          stdouts, names = objects_in_dir(path,start='stdout')
          
          if pr:
            print("Found in this attempt:")
            print(stdouts)
            print(names)
          
          if names and first: # found names of stdout
            i_n = i
            first= False
            if pr:
              print("Found stdout files.")
              print("Found in attempt {}".format(i_n))
          if i == i_n+1: # double checking to make sure all stdouts are created
            if pr:
              print("Breaking out of for loop.")
              print("i: {}".format(i))
            break # done finidng stdouts
          
          if pr:
            print("Going to sleep for 600 sec (10 minutes)")
            print(datetime.datetime.now())
          
          time.sleep(600) # sleep before trying again to find stdouts
        
        if names: # it stdouts found
        
          if pr : 
            print("Done looking for stdout. Found them.")
            print("Setting up logger.")

          first = True # looking for checkpoints for first time

          ##########################################

          # get the fully-qualified logger for module

          tokens = (str(datetime.datetime.now())).split()
          tokens[1] = tokens[1].split('.')[0]
          # cur_time = tokens[0].replace('-','')+tokens[1].replace(':','')
          cur_time = tokens[0]+"."+tokens[1].replace(':','-')
          if path[-1] != '/':
            l_name = path+'.'+cur_time
          else:
            l_name = path[:-1]+'.'+cur_time
          logging.basicConfig(level=logging.INFO,
                                          format='%(message)s',
                                          filename=l_name,
                                          filemode='w')
          
          ##########################################
          
          info(dl)
          info("backup_checkpoints.py")
          info(dl)
          
          if pr :  print(names[-1])
          nMPI = names[-1].split('.')[-1] # number of mpi procs
          if pr :
            print(nMPI)
          n_stdout = len(names) # number of stdout files
          
          
          # for i in range(2):
          while True: # start looping forever to backup files

            info(dl)
            info("Waking up.")
            # os.system("touch "+path+"/checkpoint.0?")
            # os.system("ls *.txt")
            info("Time: "+str(datetime.datetime.now()))
            
            # get checkpoint file names and paths, excluding backups
            checkpoints, names = objects_in_dir(path,start='checkpoint',
                                                contains_not='-')
            
            if pr:
              print(checkpoints)
              print(names)
            
            if names: # checkpoints found
            
              # check if finished renaming all _new checkpoints
              if not names[-1].endswith('new') \
                 and names[-1].split('.')[-1] == nMPI:
                
                n_checkpoints = len(names) # number of checkpoints
                # if number of stdouts match number of checkpoints
                if n_stdout+1 == n_checkpoints:
                
                  if pr:  print("Checkpoints files found.")
                  # get time stamp of last MPI proc checkpoint as it
                  # is created last of all by bam
                  timestamp = os.path.getmtime(checkpoints[-1])
                  
                  if pr:
                    print(timestamp)
                    print(last_time)
                  # if new file created and so time stamp is different
                  if timestamp != last_time:
                    # update time stamp of last backed up checkpoints 
                    last_time = timestamp 
                    if pr:
                      print("Found new chckpoints.")
                      print("Backing up checkpoints:")
                    info("Found new chckpoints.")
                    info("Backing up checkpoints:")
                    
                    # rename previous backup files
                    for name,checkpoint in zip(names,checkpoints):
                      if n>1: # if more than one backups
                        for i in range(n-1, 0, -1): # count backwards
                          backup_iPlus1 = checkpoint+'-'+str(i+1) # i+1th file
                          backup_i      = checkpoint+'-'+str(i)   # ith file
                          if os.path.isfile(backup_i): # if ith backup exists
                            if pr :
                              print(name+'-'+str(i)+" to "+name+'-'+str(i+1))
                              # print("mv "+backup_i+" "+backup_iPlus1)
                            info(name+'-'+str(i)+" to "+name+'-'+str(i+1))
                            # move ith backup to i+1th backup
                            shutil.move(backup_i,backup_iPlus1)
                        info(name+" to "+name+'-'+str(i))
                        if pr :
                          print(name+" to "+name+'-'+str(i))
                      else: # if only one backup to be kept
                        backup_i = checkpoint+'-'+str(n)
                        info(name+" to "+name+'-'+str(n))
                        if pr :
                          print(name+" to "+name+'-'+str(n))
                      # copy latest checkpoint to newest backup
                      shutil.copy(checkpoint,backup_i)
                      
                  else:
                    info("No new checkpoints.")
                    if pr:
                      print("No new checkpoints.")
                
                else:
                  info("Number of checkpoints not same as number of stdouts.")
                  if pr:  print("Number of checkpoints not same as number of"
                                "stdouts.")
                
              else:
                info("Writing of new checkpont files ongoing.")
                if pr:  print("Writing of new checkpont files ongoing.")
            
            else:
              info("No checkpoints yet.")
              if pr:  print("No checkpoints yet.")
            
            info("Time: "+str(datetime.datetime.now()))
            info("Going to sleep.")
            info(dl)
            time.sleep(1800)
            
            
          info("Exiting program.")
          info(dl)
        
        else:
          print("Could not locate stdout files after 200 minutes. Exiting.")
        
      else:
        print("Must have: n_previous_checkpoint > 0. Exiting.")
    
    else:
      print("Value of n_previous_checkpoint must be integer. Exiting.")
  
  else:
    print("Path entered is not a directory. Exiting.")
  
  # prl()
  # print("Exiting program.")
  # prl()