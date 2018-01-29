"Random value generating functions"

import typing as _t

import string as _string
import numpy as _np

_Size = _t.Union[_t.Tuple[int], int]

_IntArray = _t.Union[_np.ndarray, int]
def rint(size: _Size = None, low: int = 0, high: int = 10) -> _IntArray:
    """
    Gives an array of integers between 'low' and 'high' (exclusive) of size 
    'size'.
    """
    return _np.random.randint(low, high, size)


def rstr(size: int = 1, spaces: int = 0, caps: bool = False, underscores: int = 0) \
        -> str:
    """
    Gives a random string of lower-case letters plus, optionally:
    spaces (give a number to specify frequency), cpas or underscores.
    String is of length "size".
    """
    letters = _string.ascii_lowercase
    letters += ' '*spaces
    letters += '_'*underscores
    if caps:
        letters += _string.ascii_uppercase

    return ''.join(rchoice(letters, size=size))


_FloatArray = _t.Union[_np.ndarray, float]
def rfloat(size: _Size = None, low: int = 0, high: int = 1) -> _FloatArray:
    """
    Gives an array of floats between low and high (exclusive) of size 'size'
    """
    return _np.random.random(size)*(high - low) + low


_T = _t.TypeVar('_T')
_TArray = _t.Union[_np.ndarray, _T]
def rchoice(iterable: _t.Iterable[_T], size: _Size = None,
            p: _t.Iterable[float] = None) -> _TArray:
    """
    Return random elements of `iterable` of length `size` (as a numpy array).
    If `size` is None, a single value is returned instead. 
    Optional `p` argument is the a weighting function.
    """
    # Is this better than random.choice?
    return _np.random.choice(list(iterable), size=size, p=p)
