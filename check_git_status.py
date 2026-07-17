#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 14:11:32 2023

@author: ananya
"""

import os
from pathlib import Path
import datetime

def prl():
  print("-------------------------------------------------------")

prl()
print("'check_git_status.py'")

tokens = (str(datetime.datetime.now())).split()
tokens[1] = tokens[1].split('.')[0]
# cur_time = tokens[0].replace('-','')+tokens[1].replace(':','')
cur_time = tokens[0]+"."+tokens[1].replace(':','-')
common_piece = f"diff_{cur_time}.patch"

def perform_operations(d):

  prl()
  print("In: "+d)
  print()
  print("Absolute path:\n"+os.getcwd())
  print()
  print("Remote repository:")
  os.system("git remote -v")
  print()
  print("Branch:")
  os.system("git branch -a")
  print()
  print("Status:")
  os.system("git status")
  print()
  print("Current git repo version:\n")
  # os.system("git rev-parse HEAD")
  os.system("git log -1 | head -5")
  print()
  name = f"{d}_{common_piece}"
  print(f"Creating diff patch: {name}")
  os.system(f"git diff > {name}")
  patch_file = Path(name)
  if patch_file.is_file() and patch_file.stat().st_size == 0:
    print("No diffs found. Deleting file.")
    patch_file.unlink()

projects_dir = "src/projects/"
if not os.path.isdir(projects_dir):
  projects_dir = "src/Projects/"
  if not os.path.isdir(projects_dir):
    projects_dir = None
    print("Projects directory not found.")

perform_operations("main")

if projects_dir:

  os.chdir(projects_dir)
  dls_all = os.listdir()

  for d in dls_all:
    if not d.startswith('.'):
      os.chdir(d)
      perform_operations(d)
      os.chdir("..")

prl()
print("Exiting program.")
prl()