#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-06-15 10:16:17 UTC

@author: ananya
"""

################################################
# imports

import sys
from pathlib import Path
import shutil
from contextlib import ExitStack
import struct
import datetime

import argparse
import textwrap
from typing import Optional, List
from ast import literal_eval

from bamps_ah_file_metadata import BampsAHFileMetaData as AHFInfo

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

custom_usage = "create_times_file_from_bin_files.py PATH1 [ PATH2 ... ] [ -ahs AH_SUBDIR ] [ -p PLANE ] \n" \
               "                            [ -tf TIMES_FILE ]  [ -xp EXCLUDE_PATHS ] [ -h ] [ -v ] "

parser = argparse.ArgumentParser(
        prog='create_times_file_from_bin_files',
        formatter_class=CustomHelpFormatter,
        add_help=False,
        usage=custom_usage,  # Custom usage string.
        description=textwrap.dedent('Create times file containing only iterations present in PLANE dir.'),
        epilog=textwrap.dedent('NOTES: If TIMES_FILE already exits in path, a new unique name will ' \
        'be automatically created to avoid conflict.')
        )
required = parser.add_argument_group('Required',)
required.add_argument('paths', metavar='paths', nargs='+',
                      help="bamps output data dir paths (can be glob expressions)",)

optional = parser.add_argument_group('Optional')
optional.add_argument('-ahs', '--ahsubdir', type=str, default='output_ah',
                      dest='ahs', metavar='AH_SUBDIR',
                      help='subdir inside output directory containing PLANE')
optional.add_argument('-p', '--plane', type=str, default='xz', dest='plane',
                      help='output plane')
optional.add_argument('-tf', '--timesfile', type=str, dest='tf',
                      metavar='TIMES_FILE', default='times.syn',
                      help='name of file in which times data is saved')
optional.add_argument('-xp','--excludepaths', dest='excludepaths',
                      metavar='EXCLUDE_PATHS', type=str,
                      help="Space delimited list of paths to exclude "
                      "when using wildcard expr.",)

optional.add_argument('-h', '--help', action='help',
                        help="show this help message and exit")

args = parser.parse_args()

dl  = "-------------------------------------------------------------------"
ddl = "==================================================================="

paths         = args.paths
ahs           = args.ahs
plane         = args.plane
tf            = args.tf
exclude_paths = args.excludepaths

print(ddl)
print("'create_times_file_from_bin_files.py'")
print(ddl)

exclude_paths = exclude_paths.split() if exclude_paths else []
for path_string in paths:
  this_paths_batch = sorted(Path().glob(path_string))

  # loop over this glob expanded batch
  if this_paths_batch:
    for path in this_paths_batch:
      if path.name not in exclude_paths:
        oah = path / ahs
        print(dl)
        print("Processing:")
        print(str(oah.resolve()))
        print()
        if not oah.is_dir():
          print("Could not locate output_ah dir:")
          print(str(oah.resolve()))
          print("Skipping.")
          continue
        bindir = oah / plane
        if not bindir.is_dir():
          print(f"Could not locate {plane} output_ah dir:")
          print(str(bindir.resolve()))
          print("Skipping.")
          continue
        ah_times_files = list(Path(bindir).glob("*.bin"))
        if not ah_times_files:
          print(f"Could not locate .bin files in dir:")
          print(str(bindir.resolve()))
          sys.exit("Skipping.")
        print(f"Number of files found: {len(ah_times_files)}. Sorting files.")

        indexed = [(int(f.name.split('.')[0]), f) for f in ah_times_files]
        indexed.sort(key=lambda t: t[0])
        timesfile = oah / tf
        if timesfile.is_file():
          print(f"File already exists:\n{str(timesfile.resolve())}")
          tokens = (str(datetime.datetime.now())).split()
          tokens[1] = tokens[1].split('.')[0]
          # cur_time = tokens[0].replace('-','')+tokens[1].replace(':','')
          cur_time = tokens[0]+"."+tokens[1].replace(':','-')
          timesfile = oah / f"{tf}.{cur_time}"
          print(f"Storing output in alternate file:\n{str(timesfile.resolve())}")
        else:
          print(f"Storing output in file:\n{str(timesfile.resolve())}")

        with open(timesfile, 'w') as ftimes:
          for it, fbin in indexed:
            ahinfo = AHFInfo(fbin)
            # print(it, fbin.name, ahinfo.evolve_step, ahinfo.time)
            ftimes.write(f"{ahinfo.evolve_step} {ahinfo.time}\n")

print(ddl)
print("'Exiting program.'")
print(ddl)
