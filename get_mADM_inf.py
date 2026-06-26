#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-06-06 14:01:52 UTC

@author: ananya
"""

################################################
# imports

import sys
import os
import glob
from pathlib import Path

import numpy as np
import argparse
import textwrap
from typing import Optional, List

from infinity_extrapolator import InfinityExtrapolation

###################################################

class IntOrStr:
  def __call__(self, value) -> int | str:
    try:
      return int(value)
    except ValueError:
      return value

###################################################

class MassFileData:
  def __init__(self, path: Path, verb: int) -> None:
    self.datalines:Optional[List[str]] = None
    # try:
    header = [] # ""
    lines  = None
    with open(path,"r") as file:
      lines = file.readlines()
    if lines:
      i_first = 0 # first data line
      data_lines = None
      # check for header lines
      for i in range(len(lines)):
        # first data line found
        if lines[i].split()[0][0] != '"' and lines[i].split()[0][0] != '#':
          i_first = i
          break
        else: # still header lines
          header.append(lines[i])
          # header += lines[i]
      data_lines = lines[i_first:] # remove the header lines
      if data_lines:
        # self.datalines = np.loadtxt(data_lines)
        self.datalines = data_lines
        # self.shape = self.data.shape
        # self.rows = self.shape[0]
        # self.cols = self.shape[1]
        self.path = path.resolve()
        self.name = Path(path).name
        self.header = header
        self.header_nrows = i_first
        if verb > 2:  print("Loaded file data.")
      else:
        print("File:")
        print(path.resolve())
        print("File has no data lines.")
    else:
      print("File:")
      print(path.resolve())
      print("File has no content.")
    # except:
    #   print("Something went wrong with loading file data.")
    #   print("Check file and try again.")

  @staticmethod
  def _get_line_data(line : str, column_offset : int,
                     header_line=False) -> np.ndarray:
    data_cols = line
    # print(line)
    if header_line:
      comment_char = line.lstrip()[0]
      data_cols = line.lstrip(f'{comment_char} ')
    return np.loadtxt(data_cols.strip().split()[column_offset:])

  def _remove_repeated_times(self, tcol: int, verb: int) -> None:
    ln_std = None
    ln     = None
    lcount = 0
    self.data:Optional[np.ndarray] = None
    clean_lines = []
    # last time for which data is read into clean file
    last_included  = None
    if self.target_data_lines:
      # reading through each data line in file
      for l in self.target_data_lines:
        if l:
          tokens = l.split()
          # print(d[0])
          # first time value or next time value to be read
          if not last_included or float(tokens[tcol]) > last_included:
            if not last_included:  ln_std = len(tokens) # number of items in first line
            ln = len(tokens) # number of items in currnt line
            if ln == ln_std: # if current line has same number of items as first
              last_included = float(tokens[tcol]) # setting new time to last read
              # l = ""
              # for num in d:  l+="{} ".format(num)
              # f.write(l+"\n")
              # f.write(l)
              clean_lines.append(l)
              # print(d)
            elif lcount==1: # if second line problematic, not sure what is happening
              print("Something is problematic in file.")
              break

        lcount += 1

      # transform cleaned lines into data:
      if clean_lines:
        self.data = np.loadtxt(clean_lines)
        if verb > 2:  print("Removed repeated times in data.")

  def get_mADM_at_infinity(self, rrow : int, mrow : IntOrStr, cof : int,
                           verb : int) -> None:
    self.r : None | np.ndarray = None
    self.m : None | np.ndarray = None
    self.data : None | np.ndarray = None

    # print(ddl)
    # print(self.header)

    if self.datalines:
      if rrow < self.header_nrows:
        # print(rrow, mrow, cof)
        # print(type(self.header))
        # rline =
        self.r = self._get_line_data(self.header[rrow], cof,
                                     header_line=True)
      else:
        self.r = self._get_line_data(self.datalines[rrow-self.header_nrows],
                                     cof)

      if type(mrow) == int:
        if mrow < self.header_nrows:
          self.m = self._get_line_data(self.header[mrow], cof, header=True)
        else:
          self.m = self._get_line_data(self.datalines[mrow-self.header_nrows],
                                       cof)
      else:
        data_mrow = 0 if rrow < self.header_nrows else rrow-self.header_nrows+1
        self.target_data_lines = self.datalines[data_mrow:]
        self._remove_repeated_times(tcol, verb)
        if np.any(self.data):
          self.m = self.data[:,cof:]

      if not np.any(self.r):
        print("Could not figure out radii data. Skipping.")
        return
      if not np.any(self.m):
        print("Could not figure out mass data. Skipping.")
        return

      mADM = InfinityExtrapolation(self.r, self.m, deg=5)
      if np.any(mADM.val_inf):
        if self.m.ndim == 1:
          print(f"mADM(∞) = {float(mADM.val_inf)}")
        else:
          t = self.data[:,tcol]
          np.savetxt(f"{str(self.path)}.mADM.rinf",
                     np.transpose([t,mADM.val_inf]),
                     header = "t mADM(∞)")
          if verb > 1:
            print("Output in file:")
            print(Path(f"{str(self.path)}.mADM.rinf").resolve())

      # # print(self.data)
      # # print(self.data.ndim)
      # outpath = f"{self.path}.prop.t"
      # outheader =  f"col {c}: porper time\n"
      # if verb > 2:  print("Integrated lapse to get proper time.")

      # outheader += f"col {c}: coordinate time\n"
      # outheader += f"col {c}: lapse"

      # # save to file
      # np.savetxt(outpath, np.transpose(outdata), header=outheader)
      # if verb > 1:
        # print("Output in file:")
        # print(os.path.relpath(Path(outpath).resolve(), Path.cwd()))

###################################################
# Using both RawTextHelpFormatter and ArgumentDefaultsHelpFormatter
class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
  def __init__(self, *args, **kwargs) -> None:
    # Set a custom max_help_position to widen the space for arguments
    kwargs['max_help_position'] = 45
    super().__init__(*args, **kwargs)

  def _format_action_invocation(self, action):
    # Custom formatting for parfiles
    if action.dest == 'paths':
        # Display the custom metavar format for multiple parfiles
        return 'PATH1 [ PATH2 ... ]'
    return super()._format_action_invocation(action)

###################################################
# main part

  # Custom usage string
custom_usage = "get_mADM_inf.py PATH1 [ PATH2 ... ] [ -rr RROW ] [ -mr MROW ] "\
                                                "[ -co COF ] [ -tc TCOL ]\n" \
               "                       [ -msp MASS_SUB_PATH ] [ -xp EXCLUDE_PATHS ] " \
                                  "[ -r ] [ -v VERB ] [ -h ]\n"

parser = argparse.ArgumentParser(
  prog='get_mADM_inf',
  # formatter_class=argparse.RawDescriptionHelpFormatter,
  # formatter_class=argparse.RawTextHelpFormatter,
  # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  # formatter_class=argparse.MetavarTypeHelpFormatter,
  formatter_class=CustomHelpFormatter,
  add_help=False,
  usage=custom_usage,  # Custom usage string.
  description=textwrap.dedent('Compute ADM mass at infinity from 1D data'),
  epilog=textwrap.dedent('NOTES: (a) The defaults are adjusted to extract t=0\n' \
                         '           mass from `bamps` file: `output_spheres/ana.admMintegrand`.\n' \
                         '       (b) Wild card expressions are allowed for paths.\n'
                           \
                         '       (c) Setting --massrow to `rest` gets all other rows.\n' \
                         '           TCOL is then used to create output vs. time.'
                        )
)

required = parser.add_argument_group('Required',)
required.add_argument('paths',
                      help="Data paths that can be either files or directories",
                      metavar='paths',
                      nargs='+',)

optional = parser.add_argument_group('Optional')
optional.add_argument('-rr', '--radiirow', dest='rrow', type=int, default=0,
                      help='row (counting from 0) in file that cotains radii values')
optional.add_argument('-mr', '--massrow', dest='mrow', type=IntOrStr(), default=1,
                      help='row (counting from 0) in file that cotains mass values')
optional.add_argument('-co', '--columnoffset', dest='cof', type=int, default=1,
                      help='column offset (counting from 0) to read row values')
optional.add_argument('-tc', '--timecol', dest='tcol', type=int, default=0,
                      help='time column offset (counting from 0)')
optional.add_argument('-msp','--masssubpath', dest='msubpath', type=str,
                      metavar='MASS_SUB_PATH',
                      help="sub path string to the mass data file inside\n"
                      "the data dir paths",
                      default='output_spheres/ana.admMintegrand')
optional.add_argument('-xp','--excludepaths', dest='excludepaths', type=str,
                      metavar='EXCLUDE_PATHS',
                      help="Space delimited list of paths to exclude\n"
                      "when using the `--recursive` option or wildcard expr.",)
optional.add_argument('-r','--recursive', dest="recursive", action='store_true',
                      help="Whether paths contains multiple data subdirs",)
optional.add_argument('--verbose', '-v', dest='verb', action='count', default=0,
                      help="verbosity level (0 to 3)",)
optional.add_argument('-h', '--help', action='help',
                      help="show this help message and exit")

args = parser.parse_args()

dl  = "-------------------------------------------------------------------"
ddl = "==================================================================="

paths         = args.paths
rrow          = args.rrow
mrow          = args.mrow
cof           = args.cof
tcol          = args.tcol
msubpath      = args.msubpath
recursive     = args.recursive
exclude_paths = args.excludepaths
verb          = args.verb

if verb > 0:
  print(ddl)
  print("'get_mADM_inf.py'")
  print(ddl)

# set expectied type for paths
paths_are_not_files = True
path_type = 'directory'
right_path_type = Path.is_dir
try:
  first_path = next(Path().glob(paths[0])) # glob.glob(paths[0])[0]
except:
  print(f"Could not parse this into actual paths:\n{paths[0]}")
  sys.exit("Exiting.")
# check if path exists
# if not first_path.exists():
#   print(f"First path in list does not exist:\n{first_path}")
#   sys.exit("Exiting.")
if not Path(first_path).is_file() and not Path(first_path).is_dir():
  print(f"First path in list is neither file not directory:\n{first_path}")
  sys.exit("Exiting.")
# update if needed
if Path(first_path).is_file():
  paths_are_not_files = False
  path_type = 'file'
  right_path_type = Path.is_file
  joinK = False
if(recursive) and not paths_are_not_files:
  print("Option `--recursive` does not work with files.")
  print("To process multiple paths, list them all in the command line.")
  sys.exit("Exiting.")

if type(mrow) == str:
  if mrow != 'rest':
    sys.exit("Only accepted str value for MROW is `rest`. Exiting.")
  elif not cof > tcol:
    sys.exit("COF <= TCOL : not supported with MROW = `rest`. Exiting.")

if verb > 0:
  print(f"First path in list is a {path_type}:\n{first_path}")
  print(f"Setting '{path_type}' as the correct path type.")
  print("Starting to process paths iteratively.")
  if verb > 1:  print("********\nPaths:")

exclude_paths = exclude_paths.split() if exclude_paths else []

for path_string in paths:
  this_paths_batch = None
  # get glob expansion of possible wild character expression
  try:
    this_paths_batch = list(Path().glob(path_string)) # glob.glob(path_string)
  except:
    print(f"Could not parse this into actual paths:\n{path_string}")
    print("Skipping this.")

  # print(f"recursive = {recursive}")
  # loop over this glob expanded batch
  if this_paths_batch:
    for path in this_paths_batch:
      # if the correct path type and not in exlcuded paths
      if right_path_type(Path(path)) and \
          Path(path).name not in exclude_paths:
        if paths_are_not_files:
          # collect directories
          dirs = None
          if recursive:
            # print(path)
            dirs = [p for p in Path(path).iterdir() if p.is_dir()]
            # print(dirs)
            # sys.exit(1)
          else:
            dirs = [path]
          for dir in dirs:
            # process data
            if verb > 2:  print(dl)
            if verb > 1:  print(f"{dir}")
            massfilepath = Path(dir) / msubpath
            if verb > 2:
              print("Mass file path:")
              print(os.path.relpath(massfilepath.resolve(), Path.cwd()))
            if massfilepath.exists():
              if verb > 2:  print("Checking mass file.")
              mass_data = MassFileData(massfilepath,verb)
              mass_data.get_mADM_at_infinity(rrow,mrow,cof,verb) # type: ignore
            else:
              print("Cannot find this file:")
              print(os.path.relpath(Path(massfilepath).resolve(),
                                    Path.cwd()))
              print("Skipping.")
        else:
          if verb > 2:  print(dl)
          if verb > 1:  print(f"{path}")
          if path.exists():
            mass_data = MassFileData(path,verb)
            mass_data.get_mADM_at_infinity(rrow,mrow,cof,verb) # type: ignore
          else:
            print("Cannot find this file:")
            print(os.path.relpath(Path(path).resolve(),
                                  Path.cwd()))
            print("Skipping.")
      # if()
      # pass

if verb > 0:
  print(ddl)
  print("Exiting program.")
  print(ddl)

