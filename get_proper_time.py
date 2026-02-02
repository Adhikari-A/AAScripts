#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-12-08 22:05:03 UTC

@author: ananya
"""

import sys
import os
import glob

import numpy as np
from scipy.integrate import cumulative_simpson
from typing import Optional, List
from pathlib import Path

import argparse
import textwrap
from typing import Optional

class FileData:
  def __init__(self, path: Path, verb: int) -> None:
    self.datalines:Optional[List[str]] = None
    # try:
    header = ""
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
          header += lines[i]
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

  def remove_repeated_times(self, tcol: int, verb: int) -> None:
    ln_std = None
    ln     = None
    lcount = 0
    self.data:Optional[np.ndarray] = None
    clean_lines = []
    # last time for which data is read into clean file
    last_included  = None
    if self.datalines:
      # reading through each data line in file
      for l in self.datalines:
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

  def save_proper_time_data(self, tcol: int, lcol: int, intstart:float,
                            joinK: bool, getZ: bool, kretschpath: Path,
                            kcol: int, ktcol: int, verb: int) -> None:
    if np.any(self.data):
      # print(self.data)
      # print(self.data.ndim)
      proper_time = cumulative_simpson(
                      self.data[:,lcol],
                      x=self.data[:,tcol],
                      initial=intstart)
      outpath = f"{self.path}.prop.t"
      outdata = [proper_time]
      c = 0
      outheader =  f"col {c}: porper time\n"
      c += 1
      if verb > 2:  print("Integrated lapse to get proper time.")

      kretch:Optional[np.ndarray] = None
      if joinK:
        if kretschpath.exists():
          if verb > 2:  print("Checking Kretschman file.")
          dataK = FileData(kretschpath,verb)
          dataK.remove_repeated_times(ktcol,verb)
          if np.any(dataK.data):
            kretch = dataK.data[:,kcol]
            if len(kretch) != len(proper_time):
              raise ValueError(
                f"Length mismatch: len(prop. t)={len(proper_time)}, "
                f"len(kretch)={len(kretch)}")
            outheader += f"col {c}: Kretschmann scalar\n"
            c += 1
            outdata.append(kretch)
            if getZ:
              if verb > 2:  print("Computing zeta.")
              zeta = np.sqrt(kretch/12)
              outheader += f"col {c}: zeta\n"
              c += 1
              outdata.append(zeta)
        else:
          print("Kretschmann file does not exist:")
          print(os.path.relpath(Path(kretschpath).resolve(), Path.cwd()))
          print("Skipping.")

      outdata.append(self.data[:,tcol])
      outheader += f"col {c}: coordinate time\n"
      c += 1
      outdata.append(self.data[:,lcol])
      outheader += f"col {c}: lapse"
      c += 1

      # save to file
      np.savetxt(outpath, np.transpose(outdata), header=outheader)
      if verb > 1:
        print("Output in file:")
        print(os.path.relpath(Path(outpath).resolve(), Path.cwd()))

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
if __name__ == "__main__":

  # Custom usage string
  custom_usage = "get_proper_time.py PATH1 [ PATH2 ... ] " \
                 "[ -i INT_START ] [ -nb ]\n" \
                 "                                [ -fsp FILE_SUB_PATH ] "\
                                                  "[ -tc TIME_COLUMN ]\n" \
                 "                                [ -lc LAPSE_COLUMN ] "\
                                                  "[ -r ] [ -xd EXCLUDE_DIRS ]\n" \
                 "                                [ -h ]"
  parser = argparse.ArgumentParser(
          prog='get_proper_time',
          # formatter_class=argparse.RawDescriptionHelpFormatter,
          # formatter_class=argparse.RawTextHelpFormatter,
          # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          # formatter_class=argparse.MetavarTypeHelpFormatter,
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Compute proper time by integrating lapse\n' \
                                      'against the coordinate time.'),
          epilog=textwrap.dedent('NOTES: (a) When `--recursive` is specified, ' \
                                      'only directories\n' \
                                      '           inside the top paths are considered.\n' \
                                      '       (b) Wild card expressions are allowed for paths.\n' \
                                      '       (c) The default file subpaths are for'
                                      ' bamps.\n'
                                      '       (d) When paths are files, `--joinkretsch` is not allowed.\n' \
                                      '       (E) `--getzeta` works only when `--joinkretsch` is True.')
          )
  required = parser.add_argument_group('Required',)
  required.add_argument('paths',
                        help="Data paths that can be either files or directories",
                        metavar='paths',
                        nargs='+',)

  optional = parser.add_argument_group('Optional')
  optional.add_argument('-i','--intstart',
                        dest="intstart",
                        help="Starting point of integral",
                        type=float,
                        default=0.0,
                        metavar='INT_START')
  # optional.add_argument('-nb','--notbampsout',
  #                       dest="notbampsout",
  #                       help="if paths are not direct `bamps` output dirs",
  #                       action='store_true',)
  optional.add_argument('-lsp','--lapsesubpath',
                        dest='lapsesubpath',
                        metavar='LAPSE_SUB_PATH',
                        help="sub path string to the lapse data file inside\n"
                        "the data dir paths",
                        type=str,
                        default='output_0d/origin/ana.alpha')
  optional.add_argument('-tc','--timecolumn',
                        dest="tcol",
                        help="coordinate time column (counting from 0) in data file",
                        type=int,
                        default=0,
                        metavar='TIME_COLUMN')
  optional.add_argument('-lc','--lapsecolumn',
                        dest="lcol",
                        help="lapse column (counting from 0) in data file",
                        type=int,
                        default=1,
                        metavar='LAPSE_COLUMN')
  optional.add_argument('-r','--recursive',
                        dest="recursive",
                        help="Whether paths contains multiple data subdirs",
                        action='store_true')
  optional.add_argument('-xp','--excludepaths',
                        dest='excludepaths',
                        metavar='EXCLUDE_PATHS',
                        help="Space delimited list of paths to exclude\n"
                        "when using the `--recursive` option or wildcard expr.",
                        type=str)
  optional.add_argument('-jk', '--joinkretsch',
                        dest='joinK',
                        help="Join the Kretchman scalar as a column in the output",
                        action='store_true')
  optional.add_argument('-gz', '--getzeta',
                        dest='getZ',
                        help="Calculate zeta from Kretchmann and save as an" \
                             "output column",
                        action='store_true')
  optional.add_argument('-ksp','--kretschsubpath',
                        dest='kretschsubpath',
                        metavar='KRETSCH_SUB_PATH',
                        help="sub path string to the Kretschmann data file inside\n"
                        "the data dir paths",
                        type=str,
                        default='output_0d/origin/ana.CSI')
  optional.add_argument('-kc','--kretschcolumn',
                        dest="kcol",
                        help="Kretschmann column (counting from 0) in Kretschmann file",
                        type=int,
                        default=1,
                        metavar='KRETSCH_COLUMN')
  optional.add_argument('-ktc','--krtimecolumn',
                        dest="ktcol",
                        help="Kretschmann file's time column (counting from 0)\n"
                        "in data file",
                        type=int,
                        default=0,
                        metavar='KRETSCH_TIME_COLUMN')
  optional.add_argument('--verbose', '-v',
                        dest='verb',
                        help="verbosity level (0 to 3)",
                        action='count',
                        default=0)
  optional.add_argument('-h', '--help',
                        action='help',
                        help="show this help message and exit")

  args = parser.parse_args()

  dl  = "-------------------------------------------------------------------"
  ddl = "==================================================================="

  paths            = args.paths
  intstart         = args.intstart
  lapse_sub_path   = args.lapsesubpath
  tcol             = args.tcol
  lcol             = args.lcol
  kcol             = args.kcol
  ktcol            = args.ktcol
  recursive        = args.recursive
  exclude_paths    = args.excludepaths
  joinK            = args.joinK
  getZ             = args.getZ
  kretsch_sub_path = args.kretschsubpath
  verb             = args.verb

  if verb > 0:
    print(ddl)
    print("'get_proper_time.py'")
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

  if verb > 0:
    print(f"First path in list is a {path_type}:\n{first_path}")
    print(f"Setting '{path_type}' as the correct path type.")
    print("Starting to process paths iteratively.")
    print("Function used for integration: scipy.integrate.cumulative_simpson")
    print("Output file path: <lapse_file_path>.prop.t")
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
              lapsefilepath = Path(dir) / lapse_sub_path
              kretschfilepath = Path(dir) / kretsch_sub_path
              if verb > 2:
                print("Lapse file path:")
                print(os.path.relpath(lapsefilepath.resolve(), Path.cwd()))
                if joinK:
                  print("Kretschmann file path:")
                  print(os.path.relpath(kretschfilepath.resolve(), Path.cwd()))
              if lapsefilepath.exists():
                if verb > 2:  print("Checking lapse file.")
                data_lapse = FileData(lapsefilepath,verb)
                data_lapse.remove_repeated_times(tcol,verb)
                data_lapse.save_proper_time_data(tcol,lcol,intstart,joinK,getZ,
                                                 kretschfilepath,
                                                 kcol, ktcol, verb)
              else:
                print("Cannot find this file:")
                print(os.path.relpath(Path(lapsefilepath).resolve(),
                                      Path.cwd()))
                print("Skipping.")
          else:
            if verb > 2:  print(dl)
            if verb > 1:  print(f"{path}")
            if Path(path).exists():
              data_lapse = FileData(path,verb)
              data_lapse.remove_repeated_times(tcol,verb)
              data_lapse.save_proper_time_data(tcol,lcol,intstart,joinK,getZ,
                                              kretschfilepath,
                                              kcol, ktcol, verb)
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

