#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-06-14 18:59:29 UTC

@author: ananya
"""
import sys
from pathlib import Path
import shutil
from typing import List, Tuple, Optional
import argparse
import textwrap

import numpy as np

class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
  def __init__(self, *args, **kwargs) -> None:
    # Set a custom max_help_position to widen the space for arguments
    kwargs['max_help_position'] = 45
    super().__init__(*args, **kwargs)
  

def iter_key(name:str) -> int | None:
  if not name.endswith('.bin'):  return None
  iter_part = name.split('.')[0]
  if iter_part.isdigit():  return int(iter_part)
  else:                    return None

def get_iter_sorted_file_list(files : List[Path],itah : int | None) \
              -> Tuple[List[Path], int | None ]:
  indexed = [(iter_key(f.name), f) for f in files if iter_key(f.name) is not None]
  if not indexed:
    raise RuntimeError("No .bin files with numeric names found.")

  indexed.sort(key=lambda t: t[0]) # type: ignore
  files_sorted_all = [f for _, f in indexed]
  iterations = [iteration for iteration, _ in indexed]

  indah = None
  if itah is not None:
    try:
      indah = iterations.index(itah)
    except ValueError:
      pass

  return files_sorted_all, indah

custom_usage = "extract_output_ah_to_keep.py PATH [ -indah INDAH ] " \
                                                    "[ -itah ITAH ] [ plane PLANE ]\n" \
               "                             [ -nkeep NKEEP ] [ -nprev NPREV ] [ -nfirst NFIRST ]\n" \
               "                             [ -xp EXCLUDE_PATHS ] [ -h ]"

parser = argparse.ArgumentParser(
  prog='extract_output_ah_to_keep',
          formatter_class=CustomHelpFormatter,
          add_help=False,
          usage=custom_usage,  # Custom usage string.
          description=textwrap.dedent('Extract .bin files in output_ah to keep.'
                                      ),
          # epilog=textwrap.dedent('NOTES: Same column will be converted to abs ' \
                                #  'for all files.')
          )

required = parser.add_argument_group('Required',)
required.add_argument('path', type=Path,
                      help="Data path for bamps output with PATH/output_ah/PLANE",
                      metavar='PATH',
                      )

optional = parser.add_argument_group('Optional')
optional.add_argument('-indah', type=int,
                      help="index of first AH containing file in list of files",)
optional.add_argument('-itah', type=int,
                      help="iteration key of first AH containing file",)
optional.add_argument('-nkeep', type=int, default=50,
                      help="total files to keep",)
optional.add_argument('-nprev', type=int, default=2,
                      help="number of files to keep before first AH file",)
optional.add_argument('-nfirst', type=int, default=30,
                      help="number of consecutive files to keep form first AH file",)
optional.add_argument('-plane', type=str, default='xz',
                      help='output plane')
optional.add_argument('-sp','--savepath', dest='savepath',
                      metavar='SAVE_PATH', type=str,
                      help="path to save files we retain\n"
                      "(defaul: PATH/output_ah/keep)",)
optional.add_argument('-xp','--excludepaths', dest='excludepaths',
                      metavar='EXCLUDE_PATHS', type=str,
                      help="Space delimited list of paths to exclude "
                      "when using wildcard expr.",)
optional.add_argument('-h', '--help', action='help',
                      help="show this help message and exit")

args = parser.parse_args()

dl  = "-------------------------------------------------------------------"
ddl = "==================================================================="

path          = args.path
indah         = args.indah
itah          = args.itah
nkeep         = args.nkeep
nprev         = args.nprev
nfirst        = args.nfirst
plane         = args.plane
savepath      = args.savepath
exclude_paths = args.excludepaths

print(ddl)
print("'extract_output_ah_to_keep.py'")
print(ddl)

if not path.is_dir():
  sys.exit(f"Could not find path:\n{str(path)}\nExiting.")

if indah == None and itah == None:
  sys.exit("Must provide one: INDAH or ITAH. Exiting.")

if indah != None and itah != None:
  sys.exit("Must ONLY one: INDAH or ITAH. Exiting.")

if indah != None and indah < 0:
  sys.exit("INDAH < 0. Exiting.")

if itah != None and itah < 0:
  sys.exit("ITAH < 0. Exiting.")

if nkeep < 0 or nprev < 0 or nfirst < 0:
  sys.exit("NKEEP || NPREV || NFIRST < 0. Exiting.")

exclude_paths = exclude_paths.split() if exclude_paths else []

# for path_string in paths:
# this_paths_batch:Optional[List[Path]] = None
# get glob expansion of possible wild character expression
# this_paths_batch = sorted(Path().glob(path_string))

if path.name not in exclude_paths:
  print(dl)
  print("Processing:")
  print(str(path.resolve()))
  print()
  oah = path / "output_ah" 
  if not oah.is_dir():
    print("Could not locate output_ah dir:")
    print(str(oah.resolve()))
    sys.exit("Skipping.")
  bindir = oah / plane
  if not bindir.is_dir():
    print(f"Could not locate {plane} output_ah dir:")
    print(str(bindir.resolve()))
    sys.exit("Skipping.")
  print("Getting .bin files sorted by iteration key.")
  files = list(bindir.glob("*.bin"))
  if not files:
    print(f"Could not locate .bin files in dir:")
    print(str(bindir.resolve()))
    sys.exit("Skipping.")
  sorted_files, ind_itah = get_iter_sorted_file_list(files,itah)
  print("Extracting files to keep.")
  indah = ind_itah if ind_itah != None else indah
  if itah and not indah:
    print(f"Could not locate file: {itah}.bin in dir:")
    print(str(bindir.resolve()))
  if indah == None:
    print("Could not figure out index of first AH file")
    sys.exit("Skipping.")
  if indah > len(sorted_files)-1:
    print("INDAH > total number of files - 1")
    sys.exit("Skipping.")
  nkeep = len(sorted_files) if len(sorted_files) < nkeep else nkeep
  nprev = nfirst if nprev > nfirst else nprev
  if nfirst+nprev > nkeep:
    nfirst = nkeep-indah
    nprev = indah
  print(f"Keeping previous {nprev} + consecutive {nfirst} files starting from "
        f"{sorted_files[indah]}, and total {nkeep}.")
  keep1 = sorted_files[indah-nprev:indah+nfirst]
  rest = sorted_files[indah+nfirst:]
  inds = np.linspace(0, len(rest)-1, nkeep-len(keep1), dtype=int)
  keep2 = [rest[i] for i in inds]
  keep = keep1+keep2
  if len(keep) < 0:
    print("No files found to keep")
    sys.exit("Skipping.")
  print("Making save directory.")
  keep_dir = Path(savepath) if savepath else oah / "keep"
  keep_dir.mkdir(parents=True, exist_ok=True)
  print("Moving files to save dir:")
  print(str(keep_dir.resolve()))
  print("Files being moved:")
  for file in keep:
    print(f"{file.name}", end=' ')
    shutil.move(file, keep_dir)
  print()

print(ddl)
print("Exiting program")
print(ddl)
