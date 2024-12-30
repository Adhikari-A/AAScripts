#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-12-29 11:50:37 UTC

@author: ananya
"""

import sys
import os
import glob

import numpy as np
import argparse
import textwrap

from xdmf_data_reader import XDMFData

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
  custom_usage = "get_rms_from_xdmf.py PATH1 [ PATH2 ... ]\n" \
                 "                            [ -out OUTPUT_PATH ] [ -suf SUF ]\n" \
                 "                            [ -outbydir ] [ -keepindir ] [ -h ]\n"
  parser = argparse.ArgumentParser(
          prog='get_rms_from_xdmf',
          # formatter_class=argparse.RawDescriptionHelpFormatter,
          # formatter_class=argparse.RawTextHelpFormatter,
          # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          # formatter_class=argparse.MetavarTypeHelpFormatter,
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Finds time wise rms of quantity in XDMF file.'),
          epilog=textwrap.dedent('NOTE: By default { PATH1 [ PATH2 ... ] }, '
                          'are taken to be files.\n'
                          'However, specifying -file option treats them as dirs.\n'
                          'This can be wildcard shell expression(s).')
          )
  required = parser.add_argument_group('Required',)
  required.add_argument('paths',
                        help="paths to compute difference for",
                        metavar='paths',
                        nargs='+',)
  optional = parser.add_argument_group('Optional')
  optional.add_argument('-file',
                        help="file name for data if { PATH1 [ PATH2 ... ] } are dirs",
                        type=str,)
  optional.add_argument('-out',
                        metavar='OUTPUT_PATH',
                        help="path where difference outputs will be stored",
                        type=str,
                        default='./')
  optional.add_argument('-suf',
                        help="suffix for error file names for outputs",
                        type=str,
                        default='.rms')
  optional.add_argument('-outbydir',
                        help="name output files by name of parent dir of files",
                        action='store_true')
  optional.add_argument('-keepindir',
                        help="keep output files in parent dir of files",
                        action='store_true')
  optional.add_argument('-v', '--verbose',
                        dest='verbose',
                        help="print more info when operating",
                        action='store_true')
  optional.add_argument(
          '-h', '--help',
          action='help',
          help="show this help message and exit")

  args = parser.parse_args()

  dl = "-------------------------------------------------------------------"
  print(dl)
  print("'get_rms_from_xdmf.py'")
  print(dl)

  out = args.out
  keepindir = args.keepindir
  outbydir = args.outbydir
  suf = args.suf
  verbose = args.verbose

  if keepindir:
    out = "dummy_out_dir_name"
  elif out != './':
    if verbose:
      print(dl)
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
      expanded_paths = glob.glob(path) # expand if shell wild card expressions 
      for this_path in expanded_paths: # loop over paths in expansion
        data_file = None # final data file path
        if file: # have to find file inside 'this_path', which should be a dir
          if os.path.isdir(this_path):
            if this_path[-1] != '/':  this_path+='/'
            data_file = this_path + file
        else: # 'this_path' expected to be a file itself
          data_file = this_path
        if data_file and os.path.isfile(data_file): # found some file
          if verbose:
            print(dl)  
            print("Checking data file:")
            print(data_file)
          xmf_data = XDMFData(data_file)
          if xmf_data.Nframes: # if found some time frames in data tree
            xmf_data.get_frame_data(all_frames=True, get_rms=True, verbose=verbose)
            # xmf_data.get_frame_data(times=[0,12,20], get_rms=True,
                                    # verbose=verbose)
            # xmf_data.get_frame_data(times=40, get_rms=True,verbose=verbose)
            # xmf_data.get_single_frama_data(time=40, get_rms=True,verbose=verbose)
            if xmf_data.frames_grid_data: # some data found
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
                rms_data = np.array([[t, tData['rms']] 
                             for t, tData in xmf_data.frames_grid_data.items()])
                # print(rms_data)
                print("Output file:")
                print(out_file)
                header = f"Source file:\n{xmf_data.path}\n"
                header += "Column 1: Time\n"
                header += "Column 2: RMS Data"
                np.savetxt(out_file, rms_data, header=header)
              else:
                print("Something went wrong with figuring out output file name.")
                print("Please recheck output file option combination and retry.")

  print("-------------------------------------------------------------------")
  print("Exiting program")
  print("-------------------------------------------------------------------")
