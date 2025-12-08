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
# from ast import literal_eval
from itertools import product
import shutil
import subprocess

import argparse
import textwrap

logger = logging.getLogger(__name__)

pr = False # True

##########################################
# Using both RawTextHelpFormatter and ArgumentDefaultsHelpFormatter
class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
    def __init__(self, *args, **kwargs):
      # Set a custom max_help_position to widen the space for arguments
      kwargs['max_help_position'] = 40
      super().__init__(*args, **kwargs)

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

custom_usage="usage: backup_checkpoints path [-n N] [-tmin TMIN] [-bampsout]"

parser = argparse.ArgumentParser(
        prog='backup_checkpoints',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        # formatter_class=argparse.RawTextHelpFormatter,
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        # formatter_class=argparse.MetavarTypeHelpFormatter,
        formatter_class=CustomHelpFormatter,
        description=textwrap.dedent('Backup n checkpoints.'),
        add_help=False,
        usage=custom_usage,
        # epilog="NOTES:\n"
        #         "(a) The values for the Nmesh pars for the optional\n"
        #         "    arguments should be copied from the par file or\n"
        #         "    log output as necessary.\n"
        #         "(b) The defaults of optional args has been set as\n"
        #         "    they are in Nmesh as of Oct 17, 2024.\n"
        #         "    So, if you are running with Nmesh defaults for these,\n"
        #         "    and they are the same as on Oct 17, 2024, you don't\n"
        #         "    need to specify them.",
        )

required = parser.add_argument_group('Required',)
required.add_argument('path',
                      help="top path of run output dir to backup checkpoint for",)
optional = parser.add_argument_group('Optional')
optional.add_argument('-n',
                      help="number of backup chechpoints to keep",
                      type=int,
                      default=1)
optional.add_argument('-tmin',
                      help="time in minutes to sleep between checkping for new checkpoints",
                      type=float,
                      default=30)
optional.add_argument(
        '-bampsout',
        help="whether dir is bamps output (assumes bam output by default)\n ",
        action='store_true'
        )
optional.add_argument(
          '-h', '--help',
          action='help',
          help="show this help message and exit")

args = parser.parse_args()

# setting some flags
first = True # fist time looking for checkpoints
last_time = None # time stamp of last backed up checkpoint
nMPI = "" # number of MPI processes

# path = args[0] # path of output dir
path     = args.path
n        = args.n
tmin     = 60*args.tmin # convert to seconds
bampsout = args.bampsout

if not os.path.isdir(path): # if path is not a directory
  print("Path entered:")
  print(path)
  print("This is not a directory. Exiting.")
  sys.exit(1)

if pr:
  print("Dir exists.")
  print(path)


if pr:  print("Number on n previous found.")

if pr:  print(n)

if n < 1: # if invalid count
  print(f"Given N(number of backups to keep): {n}")
  print("Must have: N >= 1. Exiting.")
  sys.exit(2)

names = None
n_stdout = None
i_n = 0

if not bampsout:

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

  if not names: # it stdouts found
    print("Could not locate stdout files after 200 minutes. Exiting.")
    sys.exit(3)

  if pr :
    print("Done looking for stdout. Found them.")
    print("Setting up logger.")
else:
  time.sleep(600) # sleep before starting to be safe

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

if not bampsout:
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

  if not bampsout:
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
              # shutil.copy(checkpoint,backup_i)
              rsync_com = (f"rsync -av f{checkpoint} {backup_i}")
              os.system(rsync_com)

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

  # bamps case
  else:
    info("bamps outdir.")
    info(dl)
    # path to the checkpoint created by bamps
    checkpoint = os.path.join(path,"checkpoint")
    # if at checkpoint exists
    if os.path.isdir(checkpoint):
      # get time stamp of last checkpoint created by bamps
      timestamp = os.path.getmtime(checkpoint)
      # if new file created and so time stamp is different
      if timestamp != last_time:
        # update time stamp of last backed up checkpoints
        last_time = timestamp
        if pr:
          print("Found new chckpoint.")
          print("Backing up checkpoint:")
        info("Found new chckpoint.")
        info("Backing up checkpoint:")
        # delete n-th checkppoint backup if it exists
        checkpoint_n = os.path.join(path,f"checkpoint-{n}")
        if os.path.isdir(checkpoint_n):
          if pr :  print(f"Deleting {checkpoint_n} .")
          info(f"Deleting {checkpoint_n} .")
          # shutil.rmtree(checkpoint_n)
          subprocess.run(["rm", "-rf", checkpoint_n], check=True)
        # first = True
        # back up 1 through n-1 to plus one index
        if pr :  print("Moving:")
        info("Moving:")
        for i in range(n-1, 0, -1): # count backwards
          checkpoint_i      = os.path.join(path,f"checkpoint-{i}")
          # check if i-th backup exists
          if os.path.isdir(checkpoint_i):
            checkpoint_iPlus1 = os.path.join(path,f"checkpoint-{i+1}")
            # move to i+1
            # if first:
            # first = False
            if pr :
              print(f"{os.path.basename(checkpoint_i)} ->"
                    f" {os.path.basename(checkpoint_iPlus1)}")
            info(f"{os.path.basename(checkpoint_i)} ->"
                 f" {os.path.basename(checkpoint_iPlus1)}")
            shutil.move(checkpoint_i, checkpoint_iPlus1)
        # backup the latest checkpoint
        checkpoint_1 = os.path.join(path,f"checkpoint-1")
        # shutil.copytree(checkpoint,checkpoint_1)
        # os.system
        # rsync_com = (f"rsync -av {checkpoint} {checkpoint_1}")
        # os.system(rsync_com)
        if pr :
          print(f"{os.path.basename(checkpoint)} ->"
                f" {os.path.basename(checkpoint_1)}")
        info(f"{os.path.basename(checkpoint)} ->"
             f" {os.path.basename(checkpoint_1)}")
        subprocess.run(
          ["rsync", "-av", checkpoint + "/", checkpoint_1],
          check=True
        )
      else:
        info("No new checkpoint.")
        if pr:
          print("No new checkpoint.")
    else:
        info("No checkpoint yet.")
        if pr:
          print("No checkpoint yet.")


  info("Time: "+str(datetime.datetime.now()))
  info("Going to sleep.")
  info(dl)
  time.sleep(tmin)

info("Exiting program.")
info(dl)

# prl()
# print("Exiting program.")
# prl()
