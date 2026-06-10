import numpy as np
from numpy.polynomial.polynomial import polyfit


class InfinityExtrapolation:
  def __init__(self, coords : np.ndarray, vals : np.ndarray, deg=2):
    self.coords = np.asarray(coords, dtype=float)
    self.vals = np.asarray(vals, dtype=float)
    self.deg = deg
    self.val_inf = None

    if self.coords.ndim != 1:
      raise ValueError(
        f"coords must be 1D, got coords.shape={self.coords.shape}"
      )

    self.x = 1.0 / self.coords

    if self.vals.ndim == 1:
      self._extrapolate_1d()
    else:
      self._extrapolate_nd()

  def _extrapolate_1d(self):
    if self.vals.size != self.x.size:
      raise ValueError(
        f"For 1D vals, vals.size must match coords.size. "
        f"Got vals.size={self.vals.size}, coords.size={self.x.size}"
      )

    self.coeffs = polyfit(self.x, self.vals, deg=self.deg)

    # constant term = value at x = 0 = coords -> infinity
    self.val_inf = self.coeffs[0]

  def _extrapolate_nd(self):
    matching_axes = [
      axis for axis, size in enumerate(self.vals.shape)
      if size == self.x.size
    ]

    if len(matching_axes) == 0:
      raise ValueError(
        f"No axis of vals matches coords.size={self.x.size}. "
        f"vals.shape={self.vals.shape}"
      )

    if len(matching_axes) > 1:
      raise ValueError(
        f"Ambiguous: multiple axes of vals match coords.size={self.x.size}. "
        f"vals.shape={self.vals.shape}"
      )

    self.fit_axis = matching_axes[0]

    # polyfit wants y.shape = (len(x), ...)
    self.vals_fit = np.moveaxis(self.vals, self.fit_axis, 0)

    self.coeffs = polyfit(self.x, self.vals_fit, deg=self.deg)

    # constant term = value at x = 0 = coords -> infinity
    self.val_inf = self.coeffs[0]
