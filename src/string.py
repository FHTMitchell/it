#!/usr/bin/env python3
# it/string.py

import sys as _sys
import itertools as _itertools
import time as _time
import keyword as _keyword
import typing as _t
import numbers as _n
import dataclasses as _dc

from . import iters as _iters
from .timers import Timer as _Timer
from .cls import name as _cls_name


# pluralizing

def pluralize(n: int, singular: str, plural: str, prefix: str = "") -> str:
    """Returns singular if n == 1 else plural"""
    return prefix + (singular if n == 1 else plural)


def pluralize_factory(singular: str, plural: str, prefix: str = "") \
        -> _t.Callable[[int], str]:
    def inner(n: int):
        return pluralize(n, singular, plural, prefix)
    return inner


# Stuff to do with splitting and joining strings

def join(itr: _t.Iterable[_t.Any], sep: str = "") -> str:
    """ Join str of each element of itr into a string joined by sep

    Equivalent to sep.join(map(str, itr))
    `itr` must be iterable and `sep` must be a string
    """
    # Use str.join so if sep is not a str TypeError (not AttrError) is raised
    return str.join(sep, map(str, itr))


def separator(s: str, sep: str, n: int) -> str:
    """ Split string s with sep every n characters (from the right) """
    assert isinstance(sep, str), sep
    assert isinstance(n, int), n
    a = []
    for i, c in enumerate(reversed(s)):
        a.append(c)
        if i % n == n - 1:
            a.append(sep)
    return join(reversed(a))


def _splitter(str_iter: _t.Iterable[str], sep: _t.Union[str, None]) \
        -> _t.Iterator[str]:
    """Returns flat iterator of all strings split by sep that are in
    `str_iter`, an iterable of strigs"""
    if sep is None:
        itr = map(str.split, str_iter)
    else:
        itr = (s.split(sep) for s in str_iter)
    return _iters.flatten1deep(itr)


def splitall(s: str, seps: _t.Iterable[_t.Union[str, None]], strip: bool = False,
             remove_empty: bool = False) -> _t.List[str]:
    """Split a string by all seperators in seps. If None in seps,
    remove whitespace as well"""
    s = [s]
    for sep in seps:
        s = _splitter(s, sep)
    if strip:
        s = map(str.strip, s)
    if remove_empty:
        s = filter(bool, s)
    return s


# overwriting in consoles

def overwrite(text: str = None, end: str = '', pause: float = 0,
              padlength: int = 79) -> None:
    """ Overwrite the last line in stdout

    Returns None so do not print, will automatically print to stdout. Use pause
    to pause between writes. If text is None the line will be cleared.
    """
    if text is None:
        text = ''
    if padlength:
        text = '{: <{}}'.format(text, padlength)  # right pad text with spaces
    _sys.stdout.write('\r{}{}'.format(text, end))
    _sys.stdout.flush()
    if pause:
        _time.sleep(pause)


def load_icon(pause: int = 1, timelimit: float = None) -> None:
    """A spinning load icon"""
    timer = _Timer()
    cycle = _itertools.cycle(r'\|/-')
    try:
        while timelimit is None or timer.time() < timelimit:
            overwrite(next(cycle), end='', pause=pause)
    except KeyboardInterrupt:
        pass
    overwrite('  ')

class ProgressBar:

    prefix: str
    suffix: str
    precision: int
    length: int
    progress_char: str
    empty_char: str

    _timer: _Timer
    _cycle: _t.Iterator[str]

    def __init__(self, update_rate: float = 0, prefix: str = 'Progress',
                 suffix: str = 'complete', precision: int = 1, length: int = 80,
                 progress_char: str = r'█', empty_char: str = '_'):
        self.prefix = prefix
        self.suffix = suffix
        self.precision = precision
        self.length = length
        self.progress_char = self._assert_char(progress_char)
        self.empty_char = self._assert_char(empty_char)

        self._cycle = _itertools.cycle(r'\|/-')
        self._timer = _Timer(update_rate)

    @staticmethod
    def _assert_char(s: str) -> str:
        assert isinstance(s, str), repr(s)
        assert len(s) == 1, repr(s)
        return s

    def print_init(self) -> None:
        self.print_progress(0)
        self._timer.restart()

    def print_progress(self, fraction: float, total: float = 1) -> None:

        if self._timer.checktime != 0 and not self._timer.check():
            return

        if total != 1:
            fraction /= total
        percent = f'{fraction * 100:.{self.precision}f}%'

        filled_length = int(fraction * self.length)  # truncate towards 0
        left_fill = self.progress_char*filled_length
        right_fill = self.empty_char * (self.length - filled_length - 1)
        load_char = next(self._cycle) if filled_length != self.length else ''

        bar = left_fill + load_char + right_fill

        print(f'\r{self.prefix} |{bar}| {percent} {self.suffix}', end='\r', flush=True)

        if fraction == 1:
            print(flush=True)


# formatting numbers

def at_precision(of: _n.Real, pad: int = 0, fmt: str = 'g') \
        -> _t.Callable[[_n.Real], str]:
    """ Build function which will format it's arguments to the precision of `of`.

    Return a function that formats a value v according to the specifier:
        '>{pad}.{precision(of)}{fmt}'
    pad is an integer that will pre-pad the value with spaces up to a total size `pad`.
    of is the value which is the desired precision if a float, otherwise just the precision.
    fmt is either 'f', 'g', or 'e'. See python format specifiers.
    """
    if isinstance(of, float):
        mantissa = str(of).split('e')[0]
        if fmt == 'g':
            p = len(mantissa[-1]) - 1
        elif fmt == 'f':
            p = len(mantissa.split('.')[-1])
        else:
            raise ValueError(
                    f"If `of` is a float, `fmt` must be 'f' or 'g', not {fmt!r}")
    elif isinstance(of, int):
        p = of
    else:
        raise TypeError(f'`of` must be a float or an int, not {_cls_name(of)}')

    def inner(v: _n.Real) -> str:
        return format(v, '>{pad}.{p}{fmt}'.format(pad=pad, p=p, fmt=fmt))

    return inner


def fmt_float_no_trailing_zeros(x: _n.Real) -> str:
    return ('%f' % x).rstrip('0').rstrip('.')


# tests

def isidentifier(s: str) -> bool:  # used in AttrDict
    """
    Returns True is s (a str) is a valid python identifier (a variable name)
    """
    return str.isidentifier(s) and not _keyword.iskeyword(s)

