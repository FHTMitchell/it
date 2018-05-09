"""
Helper function for numpy arrays
"""

import numpy as _np
import numbers as _n
import typing as _t

from .boxes import default_namedtuple as _default_namedtuple



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