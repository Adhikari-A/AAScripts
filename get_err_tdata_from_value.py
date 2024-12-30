#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-11-20 11:05:04 EST

@author: ananya
"""

import sys
import os
import glob

import numpy as np
import argparse
import textwrap

class FileData:
  def __init__(self, path : str) -> None:
    self.data = None
    try:
      self.data = np.loadtxt(path)
      self.shape = self.data.shape
      self.rows = self.shape[0]
      self.cols = self.shape[1]
      self.path = os.path.abspath(path)
      self.name = os.path.basename(self.path)
      print("Loaded file data.")
    except:
      print("Something went wrong with loading file data.")
      print("Check file and try again.")

  def compute_error_in_mass(self, out_file : str, v : float,
                            tcol : int, dcol : int) -> None :
    if tcol > self.cols -1 :
      print(f"Total column count in file: {self.cols}")
      print("Time column index out of bound.")
      print("Exiting.")
      sys.exit(6)
    if dcol > self.cols -1 :
      print(f"Total column count in file: {self.cols}")
      print("Time column index out of bound.")
      print("Exiting.")
      sys.exit(9)
    time = self.data[:,tcol]
    data = self.data[:,dcol]
    # print(time)
    print("Computing error data.")
    error_data = data - v
    abs_error_data = np.abs(error_data)
    rel_error_data = error_data/v
    abs_rel_error_data = abs_error_data/v
    print("Output file:")
    print(out_file)
    header = f"v = {v}\n"
    header += f"data file: {data_file}\n"
    header += f"Time column (counting from 1) in data file: {tcol+1}\n"
    header += f"Data column (counting from 1) in data file: {dcol+1}\n"
    header += "Output columns below:\n"
    header += "Column 1: Time\n"
    header += "Column 2: Error (Data - Value)\n"
    header += "Column 3: Absolute Error (|Data - Value|)\n"
    header += "Column 4: Relative Error ([Data - Value]/Value)\n"
    header += "Column 5: Absolute Relative Error (|Data - Value|/Value)\n"
    np.savetxt(out_file, np.transpose([time,error_data,abs_error_data,
                                       rel_error_data,abs_rel_error_data]),
                header=header)

###################################################
# Using both RawTextHelpFormatter and ArgumentDefaultsHelpFormatter
class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
    def __init__(self, *args, **kwargs) -> None:
      # Set a custom max_help_position to widen the space for arguments
      kwargs['max_help_position'] = 40 
      super().__init__(*args, **kwargs)

    def _format_action_invocation(self, action) -> None:
        # Custom formatting for parfiles
        if action.dest == 'paths':
            # Display the custom metavar format for multiple parfiles
            return 'PATH1 [ PATH2 ... ]'
        return super()._format_action_invocation(action)

###################################################
# main part
if __name__ == "__main__":

  # Custom usage string
  custom_usage = "get_err_tdata_from_value.py PATH1 [ PATH2 ... ] " \
                                                      "-v VALUE\n" \
                 "                                         " \
                                            "[ -tcol TCOL ] [ -dcol DCOL ]\n" \
                 "                                         " \
                                        "[ -out OUTPUT_PATH ] [ -suf SUF ]\n" \
                 "                                         " \
                                        "[ -outbydir ] [ -keepindir ] [ -h ]\n"
  parser = argparse.ArgumentParser(
          prog='get_err_tdata_from_value',
          # formatter_class=argparse.RawDescriptionHelpFormatter,
          # formatter_class=argparse.RawTextHelpFormatter,
          # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          # formatter_class=argparse.MetavarTypeHelpFormatter,
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Finds error using given correct value of quantity '     
                                      'for each file provided.'),
          epilog=textwrap.dedent('NOTE: By default { PATH1 [ PATH2 ... ] }, '
                          'are taken to be files.\n'
                          'However, specifying -file option treats them as dirs.\n'
                          'This can be wildcard shell expression.')
          )
  required = parser.add_argument_group('Required',)
  required.add_argument('paths',
                        help="paths to compute difference for",
                        metavar='paths',
                        nargs='+',)
  required.add_argument('-v',
                        metavar='VALUE',
                        help="correct value of object",
                        type=float,
                        required=True,)
  optional = parser.add_argument_group('Optional')
  optional.add_argument('-file',
                        help="file name for data if { PATH1 [ PATH2 ... ] } are dirs",
                        type=str,)
  optional.add_argument('-tcol',
                        help="time column(counting from 0) in file",
                        type=int,
                        default=0)
  optional.add_argument('-dcol',
                        help="data column(counting from 0) in file",
                        type=int,
                        default=1)
  optional.add_argument('-out',
                        metavar='OUTPUT_PATH',
                        help="path where difference outputs will be stored",
                        type=str,
                        default='./')
  optional.add_argument('-suf',
                        help="suffix for error file names for outputs",
                        type=str,
                        default='.err')
  optional.add_argument('-outbydir',
                        help="name output files by name of parent dir of files",
                        action='store_true')
  optional.add_argument('-keepindir',
                        help="keep output files in parent dir of files",
                        action='store_true')
  optional.add_argument(
          '-h', '--help',
          action='help',
          help="show this help message and exit")

  args = parser.parse_args()

  print("-------------------------------------------------------------------")
  print("'get_err_tdata_from_value.py'")
  print("-------------------------------------------------------------------")

  out = args.out
  keepindir = args.keepindir
  outbydir = args.outbydir
  suf = args.suf
  tcol = args.tcol
  dcol = args.dcol
  v = args.v

  print(f"Given value: {v:.16f}")
  print(f"Time column(counting from 0): {tcol}")
  print(f"Data column(counting from 0): {dcol}")

  if keepindir:
    out = "dummy_out_dir_name"
  elif out != './':
    print("-------------------------------------------------------------------")
    print("Checking output path:")
    print(out)
    if not os.path.isdir(out):
      print("Path not a valid directory.")
      print("Try again with a valid directory path.")
      out = None
  
  if out:
    if out[-1] != '/':  out+='/'
    paths = args.paths
    file = args.file
    for path in paths:
      expanded_paths = glob.glob(path)
      for this_path in expanded_paths:
        data_file = None
        if file:
          if os.path.isdir(this_path):
            if this_path[-1] != '/':  this_path+='/'
            data_file = this_path + file
        else:
          data_file = this_path
        if data_file and os.path.isfile(data_file):
          print("-------------------------------------------------------------------")  
          print("Checking data file:")
          print(data_file)
          file_data = FileData(data_file)
          if np.any(file_data.data):
            out_file_base = None
            if keepindir:
              out = this_path
              if not os.path.isdir(out):
                out = os.path.dirname(out)
                out += '/'
            if outbydir:
              out_file_base = os.path.basename(os.path.dirname(data_file))
            else:
              out_file_base = os.path.basename(data_file)
            if out_file_base:
              if suf[0] != '.':  suf = f".{suf}"
              out_file = f"{out}{out_file_base}{suf}"
              file_data.compute_error_in_mass(out_file,v,tcol,dcol)
            else:
              print("Something went wrong with figuring out output file name.")
              print("Please recheck output file option combination and retry.")

  print("-------------------------------------------------------------------")
  print("Exiting program")
  print("-------------------------------------------------------------------")
