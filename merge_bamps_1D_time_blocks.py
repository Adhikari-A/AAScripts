#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-08-03 14:42:21 UTC

@author: ananya
"""

import glob
import os
import sys

import re
import numpy as np
import argparse
import textwrap
from decimal import Decimal   # exact-value alternative to float

class FileData:
  def __init__(self, path : str) -> None:
    self.lines = None
    with open(path, 'r') as file:
      self.lines = file.readlines()

    if self.lines:
      print("Loaded file data.")
      self.path = os.path.abspath(path)
      self.name = os.path.basename(self.path)
      self.data = None
    else:
      print("No lines found in file")
      sys.exit(1)

  def collect_time_pieces(self):
    if self.lines != None:
      self.time_pieces = {}
      # self.grid_pieces = {}

      # new_time = False
      current_time = None
      current_time_piece = []
      # last_time = None

      print("Collecting time pieces.")

      count = 0
      for line in self.lines:
        _ = line.strip()
        if _:
          if "Time" in _:
            # print("Found time.")
            # new_time = True
            tokens = line[1:].split()
            # last_time = current_time
            this_time = tokens[-1]
            if this_time != current_time:
              count += 1
              if current_time:
                # new_time = True
                # print(current_time_piece)
                # print(f"time = {this_time}")
                # time_data = np.loadtxt(current_time_piece)
                # time_data[:] = time_data[time_data[:,0].argsort()]
                self.time_pieces[current_time] = sorted(current_time_piece,
                                                        key=lambda ln: Decimal(ln.split()[0]))
                current_time_piece = []
                current_time = this_time
              current_time = this_time

          elif not _.startswith('"'):
            current_time_piece.append(line)
            # if new_time:
            #   new_time = False
            #   if current_time_piece:
            #     self.time_pieces[last_time] = np.loadtxt(current_time_piece)
            # else:

      if current_time_piece:
        self.time_pieces[current_time] = sorted(current_time_piece,
                                                        key=lambda ln: Decimal(ln.split()[0]))

      print("Done.")
    else:
      print("Skipping file with no lines.")

  def save_time_pieces(self):
    if self.time_pieces:
      print("Saving output.")
      outfile = f"{self.path}.tgrf"
      print(f"Output file:\n{outfile}")
      with open(outfile, 'w+') as out:
        for time,time_piece in self.time_pieces.items():
          out.write(f'# "time = {time}"\n')
          out.writelines(time_piece)
          out.write("\n")
    else:
      print("Nothing there to be saved.")


###################################################
# Using both RawTextHelpFormatter and ArgumentDefaultsHelpFormatter

class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
    def __init__(self, *args, **kwargs):
      # Set a custom max_help_position to widen the space for arguments
      kwargs['max_help_position'] = 40
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
  custom_usage = "merge_bamps_1D_time_blocks.py PATH1 [ PATH2 ... ] " \
                 "[ -notsrcdirs ] [ -h ]"
  parser = argparse.ArgumentParser(
          prog='merge_bamps_1D_time_blocks',
          # formatter_class=argparse.RawDescriptionHelpFormatter,
          # formatter_class=argparse.RawTextHelpFormatter,
          # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          # formatter_class=argparse.MetavarTypeHelpFormatter,
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Arrange the data from bamps in python '
                                      'readable format.'),
          # epilog=textwrap.dedent('NOTE: If REFERENCE_FILE is in { FILE1 [ FILE2 ... ] }, '
          #                 'it will be automatically excluded\n'
          #                 '      when calculating differences.')
          )
  required = parser.add_argument_group('Required',)
  required.add_argument('paths',
                        help="paths to process",
                        metavar='paths',
                        nargs='+',)

  optional = parser.add_argument_group('Optional')
  optional.add_argument('-notsrcdirs',
                        help="whether paths are not bamps source dirs",
                        action='store_true')
  optional.add_argument(
          '-h', '--help',
          action='help',
          help="show this help message and exit")


  args = parser.parse_args()
  dl  = "-------------------------------------------------------------------"
  ddl = "==================================================================="

  print(ddl)
  print("'merge_bamps_1D_time_blocks.py'")
  print(ddl)

  in_paths = args.paths
  srcdirs = not args.notsrcdirs
  # print(srcdirs)
  # for

  files = []
  subdirs = ["output_1d/d", "output_1d/x", "output_1d/z"]

  print("Paths:")
  for in_path in in_paths:
    if in_path[-1] == '/':  paths = glob.glob(in_path[:-1])
    else                 :  paths = glob.glob(in_path)
    for path in paths:
      print(f"{path}")
      if os.path.isfile(path):
        files.append(path)
      elif os.path.isdir(path):
        if srcdirs:
          for subdir in subdirs:
            if os.path.isdir(f"{path}/{subdir}"):
              # files += glob.glob(f"{path}/{subdir}/*")
              for _ in glob.glob(f"{path}/{subdir}/*"):
                if 'tgrf' not in _ :
                  files.append(_)
        else:
          for _ in glob.glob(f"{path}/*"):
                if 'tgrf' not in _ and os.path.isfile(_):
                  files.append(_)
          # files += glob.glob(f"{path}/*")

  if files:
    for file in files:
      print(dl)
      print(f"Processing:\n{file}")
      # outfile = f"{file}.tgrf"
      # outfile_old = f"{outfile}.old"
      # print(f"Output file:\n{outfile}")
      # if os.path.isdir(outdir_old):
      #   print(f"Found old data dir:\n{outdir_old}")
      #   print("Deleting old data dir.")
      #   print(f"System call: rm -rf {outdir_old}")
      #   os.system(f"rm -rf {outdir_old}")
      # if os.path.isdir(outdir):
      #   print(f"Found exsiting data dir:\n{outdir}")
      #   print("Moving existing data dir.")
      #   print(f"System call: mv -v {outdir} {outdir_old}")
      #   os.system(f"mv -v {outdir} {outdir_old}")
      # print(f"Making output dir.")
      # os.mkdir(outdir)

      file_data = FileData(file)
      file_data.collect_time_pieces()
      file_data.save_time_pieces()

  print(ddl)
  print("Exiting program.")
  print(ddl)
