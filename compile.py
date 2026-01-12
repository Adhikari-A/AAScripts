#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 12:39:49 2023

@author: ananya
"""

import os
import sys
import subprocess
import datetime

##############################################
### Function to print a line in output #######
##############################################

def prl():
  print("-----------------------------------------------------------------------")

##############################################
### Perform operation in each repo path ######
##############################################

def perform_operations(name,git_versions,special_branches):
  good = True
  print("In "+name+".")
  print()
  print("Absolute path:\n"+os.getcwd())
  print()
  print("Remote repository:")
  os.system("git remote -v")
  print()
  print("Current branch:")
  os.system("git branch -a")
  print()
  if '-kb' not in sys.argv and '-r' not in sys.argv \
     and special_branches and name in special_branches.keys():
    branch = special_branches[name]
    print("Changing to branch:",branch)
    # print("git checkout "+branch)
    os.system("git checkout "+branch)
    print()
    print("After change:")
    os.system("git branch -a")
  if '-rh' in sys.argv and '-r' not in sys.argv:
    if '-kb' not in sys.argv and special_branches \
                         and name in special_branches.keys():
      branch = special_branches[name]
    else:
      branch = 'master'
    print("Changing to branch "+branch+".")
    # print("git checkout "+branch)
    os.system("git checkout "+branch)
    print()
    print("After change:")
    os.system("git branch -a")
  if '-p' in sys.argv and '-r' not in sys.argv:
    if 'detached' in subprocess.check_output(['git', 'branch'],
                                             text=True,
                                             stderr=subprocess.PIPE):
      print("WARNING: You are in a 'detached HEAD' state.")
      print()
      print("Pulling with a detached HEAD is not healthy for you. :(")
      print("I can only proceed with pulling after restoring HEAD to")
      print("either the master branch or branches specified in the")
      print("special_branches file.")
      print()
      op = input("Do you want to proceed with\n"
                 "pulling after restoring head? (y/n): ")
      if op != 'y':  good =  False
      else        :  sys.argv.append('-rh')
    if good:
      print()
      print("Pulling from remote origin.")
      print()
      #print("git pull")
      os.system("git pull")
      print()
  elif '-r' in sys.argv and '-p' not in sys.argv \
       and '-rh' not in sys.argv and git_versions and '-kb' not in sys.argv:
    print("Checking out version:")
    # print(git_versions[name])
    os.system("git show "+git_versions[name]+" | head -3")
    print()
    os.system("git checkout "+git_versions[name])
    print()
    print("Changed git status:")
    # os.system("git rev-parse HEAD")
    os.system("git status | head -1")


  if '-r' not in sys.argv and good:
    print()
    print("Current git repo version:")
    # os.system("git rev-parse HEAD")
    os.system("git log -1 | head -3")
    print()
    print("Saving git repo version hash to file:")
    print(git_ver_file)
    # Run the command and capture the output
    result = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                   text=True, stderr=subprocess.PIPE)
                                   # Remove any trailing newline characters
    git_hash = result.strip()
    f.write(name+" "+git_hash+"\n")

  print()
  print("Done with "+name+".")

##############################################
################## main part #################
##############################################
prl()
print("'compile.py'")
prl()

if '-h' in sys.argv:

  print("Purpose:")
  print("Compile or pull BAM, Sgrid or Nmesh with proper branches")
  print("While retaining git repo versions for last stable build.")
  print()
  print("Usage:")
  print("compile.py [OPTIONS]")
  print()
  print("-p                   : pull from remote for main part and projects")
  print("-r git_versions_file : revert all projects to version specified in")
  print("                       the file 'git_versions_file'")
  print("-rh                  : reset head to either special branches or master")
  print("-kb                  : keep current branches")
  print("-nc                  : do not compile")
  print("-ncl                 : do not do 'make clean'")
  print("-h                   : print help info")
  print()
  print("When pulling from remote, the current stable git repo versions will")
  print("be saved to a file with name of form: git_repo_versions.date.time.")
  print()
  print("Special branches for certain projects can be specified in the file")
  print("named 'special_branches' in the top directory path where 'src' is.")
  print("Example of what this file's contents can be:")
  print("---------")
  print("main BAM23")
  print("BNSdataReader MirrorDarkMatter_reader")
  print("eos MultiEOS")
  print("---------")
  print()
  print("In all cases 'main' stands for main part of the program.")
  print()
  print("Precompilation setups, such a module loading and removing,")
  print("can be done through file precompile_setup.")
  print("This file is checked and each line in is executed")
  print("as a command before compiling.")
  print("In this file, part of the line following '#' is treated as comment.")

else:
  #if '-p' in sys.argv:
  #  print("Pulling all projects.")
  #  prl()
  #  os.system("make git_pull")
  #  prl()

  if '-nc' not in sys.argv and '-ncl' not in sys.argv:
    print("Make clean:")
    prl()
    os.system("make clean")
    prl()

  tokens = (str(datetime.datetime.now())).split()
  tokens[1] = tokens[1].split('.')[0]
  # cur_time = tokens[0].replace('-','')+tokens[1].replace(':','')
  cur_time = tokens[0]+"."+tokens[1].replace(':','-')

  good = True
  keep_branches = False
  top = "../.."
  projects_dir = "src/projects/"
  if not os.path.isdir(projects_dir):
    projects_dir = "src/Projects/"
    if not os.path.isdir(projects_dir):
      projects_dir = None
      print("Projects directory not found.")
      good = False

  path = os.getcwd()
  git_ver_file = path+"/git_repo_versions."+cur_time
  git_ver_file_last = None
  #git_ver_file = path+"/git_repo_versions.txt"
  #git_ver_file_last = path+"/git_repo_versions_last.txt"
  git_versions = {}

  if '-p' in sys.argv and '-r' not in sys.argv:

    if 'detached' in subprocess.check_output(['git', 'branch'],
                                             text=True,
                                             stderr=subprocess.PIPE):
      print("WARNING: You are in a 'detached HEAD' state.")
      print()
      print("Pulling with a detached HEAD is not healthy for you. :(")
      print("I can only proceed with pulling after restoring HEAD to")
      print("either the master branch or branches specified in the")
      print("special_branches file.")
      print()
      op = input("Do you want to proceed with\n"
                 "pulling after restoring head? (y/n): ")
      if op != 'y':  good =  False
      else        :  sys.argv.append('-rh')
    if good :
      exe = "exe/bam"
      if not os.path.isfile(exe):
        exe = "exe/nmesh"
        if not os.path.isfile(exe):
          exe = "exe/sgrid"
          if not os.path.isfile(exe):
            exe = None
            print("No current executable")

      if exe and '-nc' not in sys.argv:
        print("Keeping current stable executable as "+exe+"_stable."+cur_time+".")
        os.system("mv "+exe+" "+exe+"_stable."+cur_time)

  #  print("Adding key to agent.")
  #  os.system("eval `add-key.py ~/.ssh/id_rsa`")
  #  print("Renaming git_repo_versions.txt to git_repo_versions_last.txt.")
  #  os.system("mv "+git_ver_file+" "+git_ver_file_last)
  if '-r' in sys.argv and '-p' not in sys.argv \
    and '-rh' not in sys.argv and '-kb' not in sys.argv:
    try:
      git_ver_file_last = sys.argv[sys.argv.index('-r')+1]
    except:
      pass

    if git_ver_file_last and os.path.isfile(git_ver_file_last):
      with open(git_ver_file_last) as file:
        print("Reading git repo versions to revert to\n"
              "from git repo versions file:")
        print(git_ver_file_last)
        git_versions = {line.split()[0]: line.split()[-1] for line in file}
        if not git_versions:
          print("No git repo version information found.")
          op = input("Do you want to proceed? (y/n): ")
          if op != 'y':  good =  False

    else:
      print("Last git repo versions file not found.")
      print("Choosing default configuration: no -p and no -r.")
      op = input("Do you want to proceed? (y/n): ")
      if op != 'y':  good =  False
  #  for p,v in git_versions.items():
  #      print("{} : {}".format(p,v))
  elif '-p' in sys.argv and '-r' in sys.argv:
    print("Cannot specify -r and -p options at once.")
    print("Choosing default configuration: no -p and no -r.")
    op = input("Do you want to proceed? (y/n): ")
    if op != 'y':  good =  False
  elif '-r' in sys.argv and '-rh' in sys.argv:
    print("Cannot specify -r and -rh options at once.")
    print("Choosing default configuration: no -r and no -rh.")
    op = input("Do you want to proceed? (y/n): ")
    if op != 'y':  good =  False
  elif '-r' in sys.argv and '-kb' in sys.argv:
    print("Cannot specify -r and -kb options at once.")
    print("Choosing default configuration: no -r and no -kb.")
    op = input("Do you want to proceed? (y/n): ")
    if op != 'y':  good =  False

  if good:

    special_branches = {}
    exe = "exe/bam"
    if not os.path.isfile(exe):
      exe = "exe/nmesh"
      if not os.path.isfile(exe):
        exe = "exe/sgrid"
        if not os.path.isfile(exe):
          print("No current executable")
          exe = None
    if exe and '-nc' not in sys.argv:
      os.system("mv "+exe+" "+exe+"."+cur_time)

    if '-r' not in sys.argv:
      print("Opening git repo versions file to write into:")
      print(git_ver_file)
      f = open(git_ver_file,"w+")

      prl()
      if '-kb' not in sys.argv:
        print("Checking for special_branches file.")
        if os.path.isfile("special_branches"):
          with open("special_branches", 'r') as file:
            print("Reading special_branches file.")
            # print("special_branches")
            special_branches = {line.split()[0]: line.split()[1] for line in file}
            if not special_branches:
              print("No special branch information found.")
              op = input("Do you want to proceed? (y/n): ")
              if op != 'y':  good =  False
        else:
          print("No special_branches file found.")
          print("Keeping pre-checked branches for all repos.")
          op = input("Do you want to proceed? (y/n): ")
          if op != 'y':  good =  False

  if good:

    prl()
    perform_operations("main",git_versions,special_branches)

    if projects_dir:

      prl()
      print("Going into projects.")
      os.chdir(projects_dir)
      print("Projects:")
      os.system("ls")
      dls_all = os.listdir()

      # print(git_versions)

      for d in dls_all:
        if not d.startswith('.') and os.path.isdir(d) and good:
          prl()
          os.chdir(d)
          perform_operations(d,git_versions,special_branches)
          os.chdir("..")

    if '-r' not in sys.argv:
      print("Closing git repo versions file.")
      f.close()

    if good:
      prl()
      print("Done checking out Branches and/or versions. :)")
      if '-nc' not in sys.argv:
        os.chdir(top)
        print("Checking for file precompile_setup.")
        if os.path.isfile('precompile_setup'):
          print("Found. Executing lines in file.")
          lines = None
          with open('precompile_setup', 'r') as pcfile:
            lines = pcfile.readlines()
          if lines:
            print("---------------")
            for line in lines:
              if line:
                com=line.split('#', 1)[0].strip()
                if com:
                  print("Command:\n"+com)
                  print("===========")
                  os.system(com)
                  print("===========")
          else:
            print("File is empty")
        else:
          print("Not found.")
        prl()
        print("Now, building executable. :)")
        if '-ncl' not in sys.argv:
          print("Make clean:")
          prl()
          os.system("make clean")
          prl()
        prl()
        #print("make -j 12")
        os.system("make -j 12")
    prl()
    print("All done! :)")

prl()
print("Exiting program.")
prl()