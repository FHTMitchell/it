"Random value generating functions"

from __future__ import print_function as _, division as _

import string as _string

import numpy as _np


def rint(size=None, low=0, high=10):
    """
    Gives an array of integers between 'low' and 'high' (exclusive) of size 
    'size'.
    """
    return _np.random.randint(low, high, size)


def rstr(size=1, spaces=0, caps=False, underscores=0):
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


def rfloat(size=None, low=0, high=1):
    """
    Gives an array of floats between low and high (exclusive) of size 'size'
    """
    return _np.random.random(size)*(high - low) + low


def rchoice(iterable, size=None, p=None):
    """
    Return random elements of `iterable` of length `size` (as a numpy array).
    If `size` is None, a single value is returned instead. 
    Optional `p` argument is the a weighting function.
    """
    # Is this better than random.choice?
    return _np.random.choice(list(iterable), size=size, p=p)
