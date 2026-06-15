#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-06-15 11:30:26 UTC

@author: ananya
"""

from contextlib import ExitStack
from pathlib import Path
import struct
from typing import BinaryIO

class BampsAHFileMetaData:
  _fmt = '<i3d3i2id'

  def __init__(self, file) -> None:
    with ExitStack() as stack:
      if not hasattr(file, 'read'):
        file = stack.enter_context(open(file, 'rb'))

      size = struct.calcsize(self._fmt)
      raw = file.read(size)

      if len(raw) != size:
        raise IOError(f"Expected {size} bytes, received {len(raw)}")

      (
        self.domain_type,
        self.cu_max,
        self.cs_max,
        self.ss_max,
        reflect_x,
        reflect_y,
        reflect_z,
        self.n_grids,
        self.evolve_step,
        self.time,
      ) = struct.unpack(self._fmt, raw)

      self.reflect_x = bool(reflect_x)
      self.reflect_y = bool(reflect_y)
      self.reflect_z = bool(reflect_z)
