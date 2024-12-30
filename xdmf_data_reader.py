#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2024-12-29 10:30:04 UTC

@author: ananya
"""

import os
import sys

import numpy as np
from itertools import groupby
import xml.etree.ElementTree as ET

class XDMFData:
  """
  This data class is to create an object by reading data from XDMF file.
  Currently it is targetted towards the Nmesh time varrying data files
  and has been tested for 2D data files.

  Initially, the object is initialized with only the data structure from the
  .xmf file, as reading the binary files is slower. Single, multiple, or all
  time frames can then be extracted as needed using the functions
  `get_frame_data` or `get_single_frama_data`.

  Successful reading of the data structure can be checked by the value of the
  qeuantity `XDMFData.Nframes`, which gives the total number of tie frames
  that has been found in the file. Upon successfully reading, it will have a
  non-zero or not None value.

  Additionally there is an option to compute rms value of data
  in each time frame. This can be done by setting `get_rms=True` when calling
  functions. 

  Lastly, if for sake of log computation or rendering somewhere, negative and
  0 data values need to be replaced by some `floor_value`, then it can be passed
  in as `floor = floor_value` to functions.
  """ 
  def __init__(self, file_path : str) -> None:
    self.Nframes : int = None
    # parse the data file
    if os.path.isfile(file_path):
      try:
        self.tree = ET.parse(file_path) # data  structure tree
        self.root = self.tree.getroot()
        frames = self.root.findall(".//Grid[@CollectionType='Spatial']")
        frame_time_pairs = [
            (frame, float(frame.find('Time').attrib['Value']))
            for frame in frames
        ]
        # Sort by time: time is index '1' in (frame,time) pair
        frame_time_pairs.sort(key=lambda pair: pair[1])
        # Group by the time_value, and take the last item from each group
        unique_frame_time_pairs = []
        for _, group in groupby(frame_time_pairs, key=lambda x: x[1]):
            last_element = None
            for element in group:
                last_element = element
            unique_frame_time_pairs.append(last_element)
        # extract frames and times
        self.frames = [pair[0] for pair in unique_frame_time_pairs] 
        self.times = np.array([pair[1] for pair in unique_frame_time_pairs])
        self.Nframes = len(self.frames) # count of total frames
        self.frames_grid_data = {} # to store data in later
        self.path = os.path.abspath(file_path)
        self.name = os.path.basename(self.path)
        self.parent_dir = os.path.dirname(self.path)+'/'
      except:
        print("Something went wrong with reading XDMF file data collection. :(")
    else:
      print("Could not find this file:")
      print(file_path)

  ################################
  # accepted float types
  float_types = (int, float, np.floating)

  ################################
  @staticmethod
  def read_binary(file_path, shape, dtype=np.float32,  offset=0):
    """
    This function reads data from a specific position in a binary file.
    Strictly, this does not require any attribute of the `XDMFData` class.
    However, this is being placed here as it ties into the
    XDMF data reading process conceptually.
    """
    with open(file_path, 'rb') as f:
      f.seek(offset)
      data = np.fromfile(f, dtype=dtype, count=np.prod(shape))
    return data.reshape(shape)

  ################################
  def get_single_frama_data(self, time, offset = 0, floor : float = None,
                            get_rms = False, verbose: bool = False) -> int:
    """
    This function gets data for a single frame from the binary file.
    It enters the time frame data to `XDMFData.frames_grid_data` dictionary as
    an entry: `{t : data_dict}`, where `t` is the time value.
    Here `t` is maintained as `float` for easy operations later if necessary.
    The dictionary data_dict in turn has a key `grids` that contains all the
    grids data. If "rms" is calculated, it will also have a not None value
    for the key `rms` stores the rms values.
    The `XDMFData.frames_grid_data[t][grids]` is a list of the grids on the mesh
    at the time t. Each grid in `XDMFData.frames_grid_data[t][grids]` is in turn
    a dictionary that has structure:\n
    ```
    {
     coords: coords_data,
     variable_data: variable_data,
     dims: (Nx, Ny), # points count in each direction
     N : Nx*Ny, # total points in grid
     rms : rms # None if get_rms = False
    }
     ```

    Summarily, this is:
    - `XDMFData.frames_grid_data = [{t_0 : data_dict_0},{t_1 : data_dict_1},...]`
    - data_dict = {`grids`: grids_data, `rms` : rms_value}
    - ```
      grids_data =[{
                    coords: coords_data_0,
                    variable_data: variable_data_0,
                    dims: (Nx_0, Ny_0) # dimension,
                    N : Nx_0 * Ny_0, # points count
                    rms : rms_0 # if get_rms = False
                   },
                   {
                    coords: coords_data_1,
                    variable_data: variable_data_1,
                    dims: (Nx_1, Ny_1) # points count
                    N : Nx_1 * Ny_1, # points count
                    rms : rms_1 # if get_rms = False
                   },
                   ... ]
                   ```
    where rms values are `None` if `get_rms = False`.
    """
    if verbose:
      print(f"t={time}", end=" ", flush=True)
    i_close = 0
    # if type(time) not in self.float_types:
    if not isinstance(time,self.float_types):
      # print("Type: ", type(time))
      print(f"\nERROR: Time value not int or float type: {time}")
    else:
      times_in_range = self.times[offset:]
      # find index of closest time value in data
      if time < self.times[0]: # don't look if lower than lowest
        i_close = 0
      elif time > self.times[-1]: # same for higher than highest
        i_close = self.Nframes - 1
      else: # look in values above offset 
        i_close = np.abs(times_in_range - time).argmin()
      # extract data from binary
      t = self.times[i_close] # get closest time value
      frame = self.frames[i_close] # get corresponding frame data
      """
      Loop over grids in the mesh.
      This 'grid' is the equivalent of our elements in Nmesh.
      """
      grids = [] # grid collection for whole mesh in current step
      total_points = 0 # total points in mesh in current frame
      weighted_rms_sum = 0 # weighted sum to combine grid rmss
      total_rms = None # rms for whole grid
      all_good = True
      for grid in frame.findall('Grid'):
        topology = grid.find('Topology')
        geometry = grid.find('Geometry')
        attribute = grid.find('Attribute')
        dims = list(map(int, topology.attrib['Dimensions'].split()))
        # print(dims, end=" ")
        Nx, Ny = dims[1], dims[2]
        # Read geometry (coordinate data)
        geometry_data_item = geometry.find('DataItem')
        coords_shape = (Nx*Ny, 3)
        coords_offset = int(geometry_data_item.attrib['Seek'])
        # print(coords_offset, end=" ")
        coord_file_path = self.parent_dir + geometry_data_item.text.strip()
        if not os.path.isfile(coord_file_path):
          print(f"\nERROR: Could not find data file: {coord_file_path}")
          coord_file_path = None
          # sys.exit()
        # Read variable data
        variable_data_item = attribute.find('DataItem')
        variable_shape = tuple(map(int,
                               variable_data_item.attrib['Dimensions'].split()))
        variable_offset = int(variable_data_item.attrib['Seek'])
        # print(variable_offset, end=" ")
        variable_file_path = self.parent_dir + variable_data_item.text.strip()
        if not os.path.isfile(variable_file_path):
          print(f"\nERROR: Could not find data file: {variable_file_path}")
          variable_file_path = None
          # sys.exit()
        # print(variable_file_path)
        if coord_file_path and variable_file_path:
          coords = self.read_binary(coord_file_path,
                                    shape=coords_shape, offset=coords_offset)
          variable_data = self.read_binary(variable_file_path,
                                          shape=variable_shape,
                                          offset=variable_offset)
          rms = None
          N = Nx * Ny # points in this grid          
          if get_rms:
            rms = np.sqrt(np.mean(variable_data**2))
            total_points += N
            weighted_rms_sum += N * (rms**2)
          if floor and floor in self.float_types:
            # Replace non-positive values with a small number for log scale
            variable_data[variable_data <= 0] = floor
          grids.append({
            'coords': coords, # shape (Nx*Ny, 3) because it is in (x,y,z) format
            'variable_data': variable_data.reshape(Nx, Ny),
            'dims': (Nx, Ny), # dimension
            'N' : N, # total number of points in this grid
            'rms': rms,    # store the RMS value
          })
        else:
          all_good = False
      if all_good:
        if get_rms:
          total_rms = np.sqrt(weighted_rms_sum/total_points)
          # print(total_rms, end=", ")
        # print()
        # print(len(grids))
        # print("--------------")
        grid_data = {'grids' : grids, 'rms' : total_rms}
        self.frames_grid_data[t] = grid_data

  ################################
  def get_frame_data(self, times = None, all_frames = False,
                     floor : float = None, get_rms = False ,
                     verbose = False) -> None :
    """
    This function extracts binary data for single or multiple time frames.
    The argument `times` can either be a `list` or tuple of times (numbers)
    or one time value or `None`.
    If `times` is none, then `all_frames` has to be `True`,
    which will get all frames data.
    To compute rms values of variable data at each `time` in `times`, add
    `get_rms = True`.
    To replace negative and 0 data variable data values by a `floor_value`
    during log calculation or rendering, set `floor = floor_value`.
    For increased verbosity, use `verbose = True`.
    """
    if not times and not all_frames: # no time frames specified
      print("At least one time has to be specified for extracting data.")
    else:
      find_times = None # all times at which to get data
      # count_frames_to_get = None # count of total time frames to get data for
      if type(times) == list or type(times) == tuple: # if list of times
        # check if the time values are all valid type
        if all(type(element) in self.float_types for element in times):
          find_times = list(set(times))
          find_times.sort() # sort time values to find
          # count_frames_to_get = len(find_times)
        else:
          print("Time values have to int or float type.")
      elif type(times) in self.float_types:
        # single frame extraction
        # count_frames_to_get = 1
        find_times = [times]
      elif all_frames: # get all frames data
        find_times = self.times

      if np.any(find_times) : # some frames to be extracted
        if verbose:
          print("Extracting data for frames at specified times.")
          print("Time being read:")
        i_last = 0 # index where the previous time value has been found
        for time in find_times: # loop over the time values to find
          i_last = self.get_single_frama_data(time, offset=i_last, floor=floor,
                                              get_rms=get_rms, verbose=verbose)
        print()
