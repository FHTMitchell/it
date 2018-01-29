#!/usr/bin/env python3
# it/string.py

import sys as _sys
import itertools as _itertools
import time as _time
import keyword as _keyword

from . import iters as _iters

from .timers import Timer as _Timer


def pluralize(n, singular, plural, prefix=""):
    """Returns singular if n == 1 else plural"""
    return prefix + (singular if n == 1 else plural)


def join(itr, sep=""):
    """ Join str of each element of itr into a string joined by sep

    Equivalent to sep.join(map(str, itr))
    `itr` must be iterable and `sep` must be a string
    """
    # Use str.join so if sep is not a str TypeError (not AttrError) is raised
    return str.join(sep, map(str, itr))

def separator(s, sep, n):
    """ Split string s with sep every n characters (form the right) """
    assert isinstance(sep, str), sep
    assert isinstance(n, int), n

    a = []
    for i, c in enumerate(reversed(s)):
        a.append(c)
        if i % n == n - 1:
            a.append(sep)
    return join(a)


def _splitter(str_iter, sep):
    return _iters.flatten(s.split(sep) for s in str_iter)


def splitall(s, seps, strip=False, filter_empty=False):
    s = [s]
    for sep in seps:
        s = _splitter(s, sep)
    if strip:
        s = map(str.strip, s)
    if filter_empty:
        s = filter(bool, s)
    return s


def overwrite(text=None, end=' ', pause=0, linelen=79):
    """ Overwrite the last line in stdout

    Returns None so do not print, will automatically print to stdout. Use pause
    to pause between writes. If text is None the line will be cleared.
    """
    if text is None:
        text = ''
    text = '{: <{}}'.format(text, linelen)  # right pad text with spaces to linelen
    _sys.stdout.write('\r{}{}'.format(text, end))
    _sys.stdout.flush()
    _time.sleep(pause)


def load_icon(pause=1, timelimit=None):
    """A spinning load icon"""
    timer = _Timer()
    cycle = _itertools.cycle('\|/-')
    try:
        while timelimit is None or timer.time() < timelimit:
            overwrite(next(cycle), end='', pause=pause)
    except KeyboardInterrupt:
        pass
    overwrite('  ')




def at_precision(of, pad=0, fmt='g'):
    """ Build function which will format it's arguments to the precision of `of`.

    Return a function that formats a value v according to the specifier:
        '>{pad}.{precision(of)}{fmt}'
    pad is an integer that will pre-pad the value with spaces up to a total size `pad`.
    of is the value which is the desired precision if a float, otherwise just the precision.
    fmt is either 'f', 'g', or 'e'. See python format specifiers.
    """
    p = len(str(of).split('e')[0].split('.')[-1]) if isinstance(of, float) else of

    def inner(v):
        return format(v, '>{pad}.{p}{fmt}'.format(pad=pad, p=p, fmt=fmt))

    return inner



def isidentifier(s):  # used in AttrDict
    """
    Returns True is s (a str) is a valid python identifier (a variable name)
    """
    return str.isidentifier(s) and not _keyword.iskeyword(s)