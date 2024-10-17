#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 09:35:46 AM EDT 2024

@author: ananya
"""

import sys

import argparse
import textwrap

# Using both RawTextHelpFormatter and ArgumentDefaultsHelpFormatter
class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
    def __init__(self, *args, **kwargs):
      # Set a custom max_help_position to widen the space for arguments
      kwargs['max_help_position'] = 40 
      super().__init__(*args, **kwargs)

#######################################################
# class for central box object

class Box:
  def __init__(self, href : int, dout : float ,
               CSph : bool , dc : float,
               line : bool ,plane: bool, nboxes : bool,
               verbose : bool) -> None:

    # set initial value
    self.l = href
    self.xl = -dout
    self.x0 = 0
    self.xu = dout
    self.y0 = 0
    self.yl = -dout
    self.yu = dout
    self.z0 = 0
    self.zl = -dout
    self.zu = dout
    self.verbose = verbose

    # check special cases to update values
    if CSph and dc > dout:
      self.xl = -dc
      self.xu = dc
      self.yl = -dc
      self.yu = dc
      self.zl = -dc
      self.zu = dc
      if self.verbose:
        print("Found: dc > dout.")
        print("Setting extent with amr_CubedSphere_dc.")
    else:
      if self.verbose:
        print("Setting extent with amr_BoxMesh_dout.")
      if line:
        if not nboxes:
          print("\nSpec missing for -nboxes.")
          print("You have to specify -nboxes with -line.")
          print("Check usage through:")
          print("find_domain_center.py -h")
          sys.exit()
        elif nboxes%2 == 0: # even number of boxes
          print("Even number of boxes in line specified.")
          print("Assuming boxes are lined along x axis.")
          print("Hence, shifting initial box center away\n"
                f"from (0,0,0) to ({dout},0,0).") 
          print("This will cause dissimilar value for the")
          print("first coordinate in shifted origin.")
          print("If your box line is along a different axis,")
          print("you have to swap the dissimilar value to")
          print("the corresponding axis coordinate position.")
          self.x0 += dout
          self.xl += dout
          self.xu += dout
      elif plane:
        # get number of boxes along an axis
        if not nboxes:
          print("\nSpec missing for -nboxes.")
          print("You have to specify -nboxes with -plane.")
          print("Check usage through:")
          print("find_domain_center.py -h")
          sys.exit()
        else:
          n_along_line = int(nboxes**0.5)
          if nboxes%2 == 0: # even number of boxes along an axis
            print("Even number of boxes along an axis specified.")
            print("Assuming boxex are arranged on xy plane.")
            print("Hence, shifting initial box center away\n"
                  f"from (0,0,0) to ({dout},{dout},0).") 
            print("This will cause dissimilar value for the")
            print("last coordinate in shifted origin.")
            print("If your box plane is a different one,")
            print("you have to swap the dissimilar value to")
            print("the corresponding axis coordinate position")
            print("for the axis perpendicular to the plane.")
            self.x0 += dout
            self.xl += dout
            self.xu += dout
            self.y0 += dout
            self.yl += dout
            self.yu += dout

    if self.verbose:
      print(f"H-refinement level of box centered at"
            f"({self.x0}, {self.y0}, {self.z0}),: {self.l}")
      print(f"Extent of box in each direction:"
            f"[{-self.xl},{self.xu}],[{-self.yl},{self.yu}],"
            f"[{-self.yl},{self.yu}]\n")

  def get_shifted_origin(self) -> None:
    """
    Compute center location in each direction through:
      xc = [xu + xl]/2                       , for l = 0
      xc = [xu + xl]/2 + [xu - xl]/2^(l+1)   , for l > 0
    where xl and xu are the lower and upper
    bounds of the box along a direction.
    """
    if self.verbose:
      print(f"Initial origin: {self.x0} {self.y0} {self.z0}")
      print(f"Shifting according to l = {self.l}.\n")

    self.xs = (self.xl+self.xu)/2
    self.ys = (self.yl+self.yu)/2
    self.zs = (self.zl+self.zu)/2

    if self.l:
      self.xs += (self.xu - self.xl)/(2**(self.l+1))
      self.ys += (self.yu - self.yl)/(2**(self.l+1))
      self.zs += (self.zu - self.zl)/(2**(self.l+1))

    print(f"Shifted origin: {self.xs} {self.ys} {self.zs}")
  
  def __repr__(self) -> str:
    # Dynamically print only the attributes that currently exist
    return f"{self.__class__.__name__}({self.__dict__})"

###################################################
# main part
if __name__ == "__main__":

  parser = argparse.ArgumentParser(
          prog='find_domain_center',
          # formatter_class=argparse.RawDescriptionHelpFormatter,
          # formatter_class=argparse.RawTextHelpFormatter,
          # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          # formatter_class=argparse.MetavarTypeHelpFormatter,
          formatter_class=CustomHelpFormatter,
          description=textwrap.dedent('Finds domain center closest to origin.\n \n'                      
                "This program helps find the domain center for a case\n"
                "of any general h-refinement level for a Nmesh grid.\n"
                "It will always find the center of the domain in the\n"
                "(+x, +y, +z) direction with respect to the origin.\n"
                "It assumes that initially grid is centered on (0,0,0)."),
          add_help=False,
          epilog="NOTES:\n"
                 "(a) The values for the Nmesh pars for the optional\n"
                 "    arguments should be copied from the par file or\n"
                 "    log output as necessary.\n"
                 "(b) The defaults of optional args has been set as\n"
                 "    they are in Nmesh as of Oct 17, 2024.\n"
                 "    So, if you are running with Nmesh defaults for these,\n"
                 "    and they are the same as on Oct 17, 2024, you don't\n"
                 "    need to specify them.",
          )

  required = parser.add_argument_group('Required',)
  required.add_argument(
          '-href',
          help="h-refinement level in box adjacent to (0,0,0)\n"
                "This should be the maximum h-refinement level\n"
                "in the leaf domain in the (+x, +y, +z) direction\n"
                "with respect to the origin.\n"
                "You have to figure this out by looking at your\n"
                "grid setup and one or more of these pars:\n"
                "  amr_luni, amr_hrefine_p, amr_hrefine_sphere_levels\n"
                "  center1_amr_lmax, center2_amr_lmax\n"
                "  C3GH_refine_lmax.",
          required=True,
          type=int,
          metavar='origin+_href_l',
          )
  optional = parser.add_argument_group('Optional')
  optional.add_argument(
          '-dout',
          help="value of par amr_BoxMesh_dout\n ",
          type=float,
          default=1,
          metavar='amr_BoxMesh_dout',
          )
  optional.add_argument(
          '-CSph',
          help="whether amr_mesh_type value contains 'CubedSpheres'.\n",
          action='store_true',
          )
  optional.add_argument(
          '-dc',
          help="value of par amr_CubedSphere_dc\n"
              "This is only checked when -CSph is specified.\n",
          type=float,
          default=0.5,
          metavar='amr_CubedSphere_dc',
          )
  optional.add_argument(
          '-line',
          help="whether amr_mesh_type value contains 'BoxMesh Line'\n",
          action='store_true',
          )
  optional.add_argument(
          '-plane',
          help="whether amr_mesh_type value contains 'BoxMesh Plane'\n",
          action='store_true',
          )
  optional.add_argument(
          '-nboxes',
          help="value of par amr_BoxMesh_npatches\n",
          type=int,
          default=0,
          metavar='amr_BoxMesh_npatches',
          )
  optional.add_argument(
          '-h', '--help',
          action='help',
          help="show this help message and exit")
  optional.add_argument(
          '-v', '--verbose',
          help="print more information when executing.\n",
          action='store_true',
          dest='verbose'
          )

  args = parser.parse_args()
  verbose = args.verbose

  if verbose:
    print("-------------------------------------------------------------------")
    print("'find_domain_center.py'")
    print("-------------------------------------------------------------------")
    print('\n'.join(
                f"{key}: {value}" for key, value in vars(args).items()), "\n")

  # read args into some vars
  href   = args.href
  dout   = args.dout
  CSph   = args.CSph
  dc     = args.dc
  line   = args.line
  plane  = args.plane
  nboxes = args.nboxes

  if verbose:  print("Setting central box.")
  central_box = Box(href,dout,CSph,dc,line,plane,nboxes,verbose)
  if verbose:  print("Finding shifted origin.")
  central_box.get_shifted_origin()

  if (verbose):
    print("-------------------------------------------------------------------")
    print("'Exiting program'")
    print("-------------------------------------------------------------------")
