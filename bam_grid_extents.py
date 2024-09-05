#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 16:45:55 2023

@author: ananya
"""

import sys
from sympy import *

def prl():
  print("-----------------------------------------------------")

prl()
print("'bam_grid_extents.py'")
prl()

args = sys.argv[1:]
argc = len(args)

if argc == 0:
  
  print("Usage:")
  print("bam_grid_extents.py amr_lmax nxyz amr_move_lcube amr_move_nxyz dxyz")
  print()
  print("Arguments can be simple expression within quoatation.")
  print("Examples:")
  print("dxyz = '14.5/96 * 16.'")
  print("nxyz = '128*1.5'")
  
elif argc != 5:
  print("Incorrect commandline arguments. Check usage.")

else:
  lmax = int(round(simplify(args[0])))
  n = int(round(simplify(args[1])))
  lcube = int(round(simplify(args[2])))
  nm = int(round(simplify(args[3])))
  h = simplify(args[4])
  
  print("Key:")
  print("l -> box level index\n"
        "n(l) -> number of grid points at level l\n"
        "h(l) -> grid spacing at level l\n"
        "L(l) -> total extent of each box at level l.")
  
  for l in range(lmax+1):
    
    if l>lcube:  nl = nm
    else:        nl = n
    
    prl()
    print("l    =",l)
    print("n(l) =",nl)
    print("h(l) =",h)
    print("L(l) =",h*nl)
    
    h/=2
  
prl()
print("Exiting program.")
prl()