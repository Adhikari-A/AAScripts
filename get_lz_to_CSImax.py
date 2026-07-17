#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-07-05 13:20:40 UTC

@author: ananya
"""

from __future__ import annotations

import sys
import os
import glob

import numpy as np
from scipy.integrate import cumulative_simpson
from typing import Optional, List
from pathlib import Path

import argparse
import textwrap


###################################################
class FileData:
  def __init__(self, path: Path, verb: int, file_0d = False,
               tcol: None | int = None) -> None:
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
        if file_0d:
          if tcol is None:
            sys.exit("Time column not provided for 0D data. Exiting.")
          self._remove_repeated_times(tcol, verb)
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

  def _remove_repeated_times(self, tcol: int, verb: int) -> None:
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

  @staticmethod
  def _get_a2_at_val_in_a1(a1: np.ndarray, a2:np.ndarray, val: float) -> float:
    return a2[np.abs(a1 - val).argmin()]

  def get_lz_to_Imax(self, data_Imax:FileData,
                     tcol:int, z0col:int, Imcol:int, zcol:int, gzzcol:int,
                     intstart:float, verb:int) -> None:
    if np.any(data_Imax.data):
      if verb > 1:  print("Trying to collect lz data")
      t     = data_Imax.data[:,tcol]  # type:ignore
      z0    = data_Imax.data[:,z0col] # type:ignore
      Imax0 = data_Imax.data[:,Imcol] # type:ignore
      this_t = None
      this_t_data_lines = [] # array to collect current time's data
      time, lz, z, Imax = [], [], [], []
      if self.datalines:
        for line in self.datalines:
          _ = line.strip()
          if _:
            if "time" in _:
              # print(_)
              t_val = float(_.strip().strip('"').split()[-1])
              if this_t != t_val:
                if this_t != None:
                  this_t_data        = np.loadtxt(this_t_data_lines)
                  this_t_z_Imax      = self._get_a2_at_val_in_a1(t, z0, this_t)
                  this_t_z           = this_t_data[:,zcol]
                  this_t_gzz         = this_t_data[:,gzzcol]
                  this_t_iz_Imax     = np.abs(this_t_z-this_t_z_Imax).argmin()
                  this_t_z_to_Imax   = this_t_z[:this_t_iz_Imax+1]
                  this_t_gzz_to_Imax = this_t_gzz[:this_t_iz_Imax+1]
                  # Sort both arrays by increasing z
                  idx = np.argsort(this_t_z_to_Imax)
                  this_t_z_to_Imax = this_t_z_to_Imax[idx]
                  this_t_gzz_to_Imax = this_t_gzz_to_Imax[idx]
                  # Collapse repeated z values, averaging the corresponding gzz values
                  z_unique, inv, counts = np.unique(this_t_z_to_Imax,
                                                    return_inverse=True,
                                                    return_counts=True)
                  gzz_avg = np.bincount(inv, weights=this_t_gzz_to_Imax) / counts
                  this_t_z_to_Imax = z_unique
                  this_t_gzz_to_Imax = gzz_avg
                  # integrate
                  this_t_lz_to_Imax  = cumulative_simpson(
                                          np.sqrt(this_t_gzz_to_Imax),
                                          x=this_t_z_to_Imax,
                                          initial=intstart
                                       )
                  time.append(t_val)
                  z.append(this_t_z_to_Imax[-1])
                  lz.append(this_t_lz_to_Imax[-1])
                  Imax.append(self._get_a2_at_val_in_a1(t, Imax0, t_val))
                # update values for next time data
                this_t, this_t_data_lines = t_val, []
            elif not _.startswith('"'):
              this_t_data_lines.append(line)

        # after having collected data
        if time and lz:
          if verb > 1:  print("Finished collecting lz data.")
          time, lz = np.array(time), np.array(lz)
          iImax = Imax0.argmax()
          t_maxImax, z_maxImax, maxImax = t[iImax], z0[iImax], Imax0[iImax]
          lz_maxImax = self._get_a2_at_val_in_a1(time, lz, t_maxImax)
          outpath = data_Imax.path.parent / "Imax.lz"
          header = f"max(max(I)) = {maxImax}, lz(max(max(I))) = {lz_maxImax}"
          header = f"{header}, z(max(max(I))) = {z_maxImax}, t(max(max(I))) = {t_maxImax}\n"
          header = f"{header}t lz(max(I)) z(max(I)) max(I)"
          np.savetxt(outpath, np.transpose([time, lz, z, Imax]),
                     header=header)
          if verb > 1:
            print("Saved data in file:")
            print(outpath.resolve())
        else:
          print("No lz data obtained in current step. Skipping.")

      else:
        print("No gzz 1D data found. Skipping.")
    else:
      print("No kretsch max data found. Skipping.")

###################################################
# Using both RawTextHelpFormatter and ArgumentDefaultsHelpFormatter
class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
  def __init__(self, *args, **kwargs) -> None:
    # Set a custom max_help_position to widen the space for arguments
    kwargs['max_help_position'] = 50
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
  custom_usage = "get_lz_to_CSImax.py PATH1 [ PATH2 ... ]\n" \
                 "                           [ -Kms KRETCH_MAX_SUB_PATH ] "\
                    "[ -tc TIME_COLUMN ] " \
                    "[ -Kmc KRETCH_MAX_COLUMN ] [ -z0c Z0_COLUMN ]\n"\
                 "                           [ -gzzs GZZ_SUB_PATH ] "\
                 " [ -gzzc GZZ_COLUMN ] [ -zc Z_COLUMN ] [ -i INT_START ]\n" \
                 "                           [ -r ] [ -xd EXCLUDE_DIRS ] [ -h ]"
                #  "[ -i INT_START ] " \

  parser = argparse.ArgumentParser(
          prog='get_lz_to_CSImax',
          # formatter_class=argparse.RawDescriptionHelpFormatter,
          # formatter_class=argparse.RawTextHelpFormatter,
          # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          # formatter_class=argparse.MetavarTypeHelpFormatter,
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Get proper length lz along z-axis to max of Kretschmann\n' \
                                      'for all times in bamps 1D output.'),
    # epilog=textwrap.dedent('NOTES: (a) When `--recursive` is specified, ' \
    #                                   'only directories\n' \
    # )
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
  optional.add_argument('-Kms','--kretschmaxsubpath',
                        dest='Imaxsubpath',
                        metavar='KRETCH_MAX_SUB_PATH',
                        help="sub path string to 0D Kretschmann max file",
                        type=str,
                        default='output_0d/max/ana.CSI.c1.abs')
  optional.add_argument('-tc','--timecolumn',
                        dest="tcol",
                        help="coordinate time column (counting from 0) in KRETCH_MAX_SUB_PATH",
                        type=int,
                        default=0,
                        metavar='TIME_COLUMN')
  optional.add_argument('-Kmc','--kretschmaxcol',
                        dest="Imcol",
                        help="Kretschmann max column (counting from 0) in KRETCH_MAX_SUB_PATH",
                        type=int,
                        default=1,
                        metavar='KMAX_COLUMN')
  optional.add_argument('-z0c','--z0Dcolumn',
                        dest="z0col",
                        help="z coordinate column (counting from 0) in KRETCH_MAX_SUB_PATH",
                        type=int,
                        default=4,
                        metavar='Z0_COLUMN')
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
  optional.add_argument('-gzzs','--gzzsubpath',
                        dest='gzzsubpath',
                        metavar='GZZ_SUB_PATH',
                        help="sub path string to the z-axis gzz 1D data file",
                        type=str,
                        default='output_1d/z/u.gzz.tgrf')
  optional.add_argument('-gzzc','--gzzcolumn',
                        dest="gzzcol",
                        help="gzz column (counting from 0) in GZZ_SUB_PATH",
                        type=int,
                        default=1,
                        metavar='GZZ_COLUMN')
  optional.add_argument('-zc','--zcolumn',
                        dest="zcol",
                        help="gzz file's z column (counting from 0) in GZZ_SUB_PATH",
                        type=int,
                        default=0,
                        metavar='Z_COLUMN')
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

  paths          = args.paths
  intstart       = args.intstart
  Imaxsubpath    = args.Imaxsubpath
  tcol           = args.tcol
  Imcol          = args.Imcol
  z0col          = args.z0col
  gzzcol         = args.gzzcol
  zcol           = args.zcol
  recursive      = args.recursive
  exclude_paths  = args.excludepaths
  gzzsubpath     = args.gzzsubpath
  verb           = args.verb

  if verb > 0:
    print(ddl)
    print("'get_proper_time.py'")
    print(ddl)

  try:
    first_path = next(Path().glob(paths[0])) # glob.glob(paths[0])[0]
  except:
    print(f"Could not parse this into actual paths:\n{paths[0]}")
    sys.exit("Exiting.")

  if not Path(first_path).is_file() and not Path(first_path).is_dir():
    print(f"First path in list is neither file not directory:\n{first_path}")
    sys.exit("Exiting.")

  if verb > 0:
    print("Starting to process paths iteratively.")
    print("Function used for integration: scipy.integrate.cumulative_simpson")
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
        if Path(path).name not in exclude_paths:
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
            Imaxpath = Path(dir) / Imaxsubpath
            gzzfilepath = Path(dir) / gzzsubpath
            if verb > 2:
              print("Kretschmann max file path:")
              print(os.path.relpath(Imaxpath.resolve(), Path.cwd()))
            if Imaxpath.exists():
              if verb > 2:  print("Checking Kretschmann max file.")
              data_Imax = FileData(Imaxpath,verb,file_0d=True,tcol=tcol)
              if verb > 2:
                print("gzz z-axis file path:")
                print(os.path.relpath(gzzfilepath.resolve(), Path.cwd()))
              if gzzfilepath.exists():
                if verb > 2:  print("Checking gzz z-axis file.")
                data_gzz = FileData(gzzfilepath,verb)
                data_gzz.get_lz_to_Imax(data_Imax,tcol,z0col,Imcol,zcol,gzzcol,
                                         intstart,verb)
              else:
                print("Cannot find this file:")
                print(os.path.relpath(gzzfilepath.resolve(),
                                      Path.cwd()))
                print("Skipping.")
            else:
              print("Cannot find this file:")
              print(os.path.relpath(Imaxpath.resolve(),
                                    Path.cwd()))
              print("Skipping.")

  if verb > 0:
    print(ddl)
    print("Exiting program.")
    print(ddl)
