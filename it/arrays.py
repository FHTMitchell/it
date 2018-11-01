"""
Helper function for numpy arrays
"""

import numpy as _np
import matplotlib.pyplot as _plt
import numbers as _n
import typing as _t

from .boxes import default_namedtuple as _default_namedtuple
from .cls import name as _name


def apply(func: _t.Callable, array: _np.ndarray, dtype: _np.dtype = None) \
        -> _np.ndarray:
    array = _np.asarray(array)
    if dtype is None:
        dtype = array.dtype
    return _np.fromiter(map(func, array), dtype, count=len(array))



_RealArray = _t.TypeVar('Array', _np.ndarray, _n.Real)
Ball = _default_namedtuple('Ball', ('max', 'min'), (1, 0))
def scale(x: _RealArray, inrange: Ball, outrange: Ball) -> _RealArray:
    """ Returns x scaled from
        [inrange.min, inrange.max] -> [outrange.min, outrange.max]
    """
    in_ = Ball(inrange)
    out = Ball(outrange)
    return (x - in_.min) * ((out.max - out.min)/(in_.max - in_.min)) + out.min


def first_consec_index(array: _np.ndarray, length: int) -> int:
    idx = _np.flatnonzero(_np.r_[True, array, True])
    lens = _np.diff(idx) - 1
    return idx[(lens >= length).argmax()]

class FigureAxes(_t.NamedTuple):
    fig: _plt.Figure
    ax: _plt.Axes

def plot_colormap(x: _np.ndarray, y: _np.ndarray,
                  apply: _t.Callable[[_np.ndarray, _np.ndarray], _np.ndarray],
                  auto_aspect: bool = True, **kwargs) -> FigureAxes:

    figax = FigureAxes(*_plt.subplots())

    xs, ys = _np.meshgrid(x, y)
    z = apply(xs, ys)

    aspect = 'auto' if auto_aspect else 'equal'
    img = figax.ax.imshow(z, interpolation='none', origin='lower',
                          extent=[x[0], x[-1], y[0], y[-1]], aspect=aspect,
                          **kwargs)
    figax.fig.colorbar(img)

    return figax


class Array(_np.ndarray):
    def __new__(cls, array):
        return _np.asarray(array).view(cls)

class Coord(Array):
    coords = {'x': 0, 'y': 1, 'z': 2}

    def __init__(self, array):
        assert isinstance(self.coords, dict) and self.coords, repr(self.coords)
        if self.shape != (len(self.coords),):
            msg = "{}.shape should be {}, not {}"
            raise ValueError(msg.format(_name(self), (len(self.coords),), self.shape))
        # noinspection PyArgumentList
        super().__init__()

    def __getattr__(self, attr):
        if attr in self.coords:
            return self[self.coords[attr]]
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr in self.coords:
            self[self.coords[attr]] = value
        else:
            super().__setattr__(attr, value)
