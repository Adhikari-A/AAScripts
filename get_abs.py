#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-03-23 10:54:59 UTC

@author: ananya
"""
################################################
# imports

import sys
from pathlib import Path

import argparse
import textwrap
from typing import Optional, List
from ast import literal_eval

###################################################

class FileData:
  @staticmethod
  def _type_embedded_in_string(string):
    """
    this function checks the type of information
    embedded inside "string" and returns appropriate value
    """
    try:
      return type(literal_eval(string))
    except (ValueError, SyntaxError):
      return str

  ###############
  def __init__(self, path: Path, verb: bool) -> None:
    self.lines:Optional[List[str]] = None
    if verb:
      print("Trying to read file:")
      print(str(path))
    if path.is_file():
      with open(path,"r") as file:
        self.lines = file.readlines()
      if not self.lines:
        print("No lines read in file:")
        print(str(path.resolve()))
      else:
        if verb: print("Done reading.")
        self.path = path
        self.name = path.name
    else:
      print("Could not find file:")
      print(str(path))
      print("Skipping.")

  ###############
  def make_column_abs(self, col: int, verb: bool):
    if self.lines:
      self.outpath = Path(f"{str(self.path)}.c{col}.abs")
      # self.out_string = ""
      if verb > 0: print(f"Starting to convert column {col} to absolute value.")
      with open(self.outpath, 'w+') as outfile:
        col_count_in_first_row:Optional[int] = None
        for counter, l in enumerate(self.lines, start=1):
          line = l.strip()
          tokens = line.split()
          # if it is a blank line, keep it as is
          if not tokens:
            # self.out_string+=line
            outfile.write(l)
            continue
          # if it is a comment of some kind, keep it as is
          if self._type_embedded_in_string(tokens[0]) == str:
            # self.out_string+=line
            outfile.write(l)
            continue

          # check if columns count is consistent:
          if not col_count_in_first_row:
            col_count_in_first_row = len(tokens)

          if len(tokens) != col_count_in_first_row:
            print(f"Columns count ({len(tokens)}) in line {counter} != in first"
                  "data line.")
            print("Skipping this file:")
            print(str(self.path.resolve()))
            # self.out_string = ""
            return

          if col > len(tokens):
            print(f"Columns count ({len(tokens)}) in line {counter} > {col}.")
            print("Skipping this file:")
            print(str(self.path.resolve()))
            # self.out_string = ""
            return

          # do the actual conversion: simply remove the preceding '-' sign
          tokens[col] = tokens[col].lstrip('-')
          # self.out_string += f"{' '.join(tokens)}\n"
          outfile.write(f"{' '.join(tokens)}\n")

        if verb:
          print("Done with conversion.")
          print(f"Output in file:\n{self.outpath}")

      # write to file
      # if self.out_string:
      #   self.outpath = Path(f"{str(self.path)}.c{col}.abs")
      #   if verb: print("Done with conversion.")
      #   with open(self.outpath, 'w+') as outfile:
      #     outfile.write(self.out_string)
      #     if verb: print(f"Output in file:\n{self.outpath}")

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

################################################
# main part
if __name__ == "__main__":

  # Custom usage string
  custom_usage = "get_abs.py PATH1 [ PATH2 ... ] [ -c COL ] " \
                 "[ -xp EXCLUDE_PATHS ] [ -h ] [ -v ]"
  parser = argparse.ArgumentParser(
          prog='get_strain_with_watpy',
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Convert a column in a file to absolute value.'
                                      ),
          epilog=textwrap.dedent('NOTES: Same column will be converted to abs ' \
                                 'for all files.')
          )
  required = parser.add_argument_group('Required',)
  required.add_argument('paths',
                        help="Data paths for files (can be glob expressions)",
                        metavar='paths',
                        nargs='+',)

  optional = parser.add_argument_group('Optional')
  optional.add_argument('-c','--col',
                        dest="col",
                        help="column (counting from 0) in data file to make abs",
                        type=int,
                        default=1,
                        metavar='COL')
  optional.add_argument('-xp','--excludepaths',
                        dest='excludepaths',
                        metavar='EXCLUDE_PATHS',
                        help="Space delimited list of paths to exclude\n"
                        "when using the `--nesteddata` option or wildcard expr.",
                        type=str)
  optional.add_argument('--verbose', '-v',
                        dest='verb',
                        help="verbosity",
                        action='store_true')
  optional.add_argument('-h', '--help',
                        action='help',
                        help="show this help message and exit")

  args = parser.parse_args()

  dl  = "-------------------------------------------------------------------"
  ddl = "==================================================================="

  paths             = args.paths
  col               = args.col
  exclude_paths     = args.excludepaths
  verb              = args.verb

  if verb:
    print(ddl)
    print("'get_abs.py'")
    print(ddl)
    print(f"Column to conver(counting from 0): {col}")

  if col < 0:
    sys.exit(f"Column to convert: {col} < 0.\nExitting.\n")

  exclude_paths = exclude_paths.split() if exclude_paths else []
  for path_string in paths:
    this_paths_batch:Optional[List[Path]] = None
    # get glob expansion of possible wild character expression
    try:
      this_paths_batch = sorted(Path().glob(path_string)) # glob.glob(path_string)
    except:
      print(f"Could not parse this into actual paths:\n{path_string}")
      print("Skipping this.")

    # loop over this glob expanded batch
    if this_paths_batch:
      for path in this_paths_batch:
        if path.name not in exclude_paths:
          if verb:
            print(dl)
            # print(f"{path}")
          filedata = FileData(path, verb=verb)
          filedata.make_column_abs(col=col,verb=verb)

  if verb:
    print(ddl)
    print("Exiting program.")
    print(ddl)