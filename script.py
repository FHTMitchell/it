"""
Useful scripts used repeatedly throughout code
For use in other modules copy into new file, don't reference this
"""

from __future__ import print_function as _, division as _

import time
import sys
import os
import collections
import itertools
import functools
import keyword
import bisect as _bisect

from . import cls as _cls
from .timers import Timer

try:
    import pandas as pd
except ImportError:
    pass

try:
    # noinspection PyUnresolvedReferences
    collections.abc
except AttributeError:
    collections.abc = collections


### str & io functions ###

def pluralize(n, singular, plural):
    """Returns singular if n == 1 else plural"""
    return singular if n == 1 else plural

def _splitter(str_iter, sep):
    return flatten(s.split(sep) for s in str_iter)

def splitall(s, seps, strip=False, filter_empty=False):
    s = [s]
    for sep in seps:
        s = _splitter(s, sep)
    if strip:
        s = map(str.strip, s)
    if filter_empty:
        s = filter(bool, s)
    return s

    
def remove(container, *elems):
    """ Remove elems from containers

    For each elem in elems, if elem in container, remove from container and
    return it.
    """
    if isinstance(container, str):
        for elem in elems:
            container = container.replace(elem, '')
    elif isinstance(container, list):
        container = container.copy()
        for elem in elems:
            while elem in container:
                container.remove(elem)
    else:
        raise TypeError('not supported for type: {}'.format(_cls.name(container)))
        
    return container
    

def overwrite(text=None, end=' ', pause=0, linelen=79):
    """ Overwrite the last line in stdout

    Returns None so do not print, will automatically print to stdout. Use pause 
    to pause between writes. If text is None the line will be cleared.
    """
    if text is None:
        text = ''
    text = '{: <{}}'.format(text, linelen)  # right pad text with spaces to linelen
    sys.stdout.write('\r{}{}'.format(text, end))
    sys.stdout.flush()
    time.sleep(pause)


def load_icon(pause=1, timelimit=None):
    """A spinning load icon"""
    timer = Timer()
    cycle = itertools.cycle('\|/-')
    try:
        while timelimit is None or timer.time() < timelimit:
            overwrite(next(cycle), end='', pause=pause)
    except KeyboardInterrupt:
        pass
    overwrite('  ')


### iterable operators ###

class contains(int):  # subclass int so understood as bool
    """namespace for contains.all() and contains.any()

    Calling contains() is a wrapper for contains.any()
    """
    
    @staticmethod
    def any(obj, *contents):
        """Returns True, if any of contents are in obj, else False"""
        return any((c in obj) for c in contents)
    
    @staticmethod
    def all(obj, *contents):
        """Returns True, if all of contents are in obj, else False"""
        return all((c in obj) for c in contents)

    # Alias contains() as contains.any()
    # noinspection PyInitNewSignature
    def __new__(cls, obj, *contents):
        return cls.any(obj, *contents)

        
def flatten(a):
    """generator of flattened n-deep iterable (excluding str/bytes) a."""
    for elem in a:
        if not isinstance(elem, (str, bytes)):
            try:
                yield from flatten(elem)
            except TypeError:
                yield elem
        else:
            yield elem
        
        
def flatten_fast(a):
    """generator of flattened n-deep iterable (including str/bytes) a."""
    for elem in a:
        try:
            yield from flatten_fast(elem)
        except TypeError:
            yield elem


def timestamp(unix_time=None, show_zone=True):
    """Show time (current if None) in the format 'yyyy-mm-dd HH:MM:SS [TZ]'"""
    if unix_time is None:
        unix_time = time.time()
    str_ = '%Y-%m-%d %H:%M:%S'
    if show_zone:
        str_ += ' %z'
    return time.strftime(str_, time.localtime(unix_time))


def default_namedtuple(typename, field_names, default_values=()):
    """
    Returns a collections.namedtuple except with default_values.
    default_values can be specified with a tuple of length < len(field_names) or 
    as a dict. Any field_names not referenced in the dict will have a default of
    None.
    """
    T = collections.namedtuple(typename, field_names)
    if isinstance(default_values, collections.Mapping):
        T.__new__.__defaults__ = (None,)*len(T._fields)
        default_values = T(**default_values)
    T.__new__.__defaults__ = tuple(default_values)
    return T


def precision(x):
    """The precision of x"""
    if isinstance(x, float):
        decimal_part = repr(x).split('.')[1]
        return len(decimal_part) if decimal_part != '0' else 0
    elif isinstance(x, int):
        return 0
    else:
        msg = 'x must be a real number, not {}'.format(type(x).__name__)
        raise TypeError(msg)


def at_precision(of, pad=0, fmt='g'):
    """
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


def bisect(array, elem, low=0, high=None, right=True):
    """
    Equivalent to the bisect.<side>_bisect (right or left) library functions with
    additional check.
    """
    lst = list(array)
    assert lst == sorted(lst), "array is not sorted"
    args = (lst, elem, low, high)
    return _bisect.bisect(*args) if right else _bisect.left_bisect(*args)


#
# def find_pattern(expr, src, printout=True, ret_list=False):
#     """
#     Returns the expressions found from
#     """
#     raise NotImplementedError  # TODO write find pattern
#     if isinstance(expr, str):
#         expr.count('($:') < (expr.count('(') + expr.count('\('))
#         if printout:
#             msg = 'Warning: ' # warn about capturing
#             print(msg)
#         expr = re.compile(expr)
#
#     if ret_list:  # after  capture check
#         printout = False
#
#     if isinstance(src, str):
#         ans = expr.findall(src)
#         if printout:
#             print(ans)
#         return len(ans) if not ret_list else ans


def isidentifier(s):  # used in AttrDict
    """
    Returns True is s (a str) is a valid python identifier (a variable name)
    """
    return str.isidentifier(s) and not keyword.iskeyword(s)


def pd2latex(df, cols=None, *, fmts='.2f', names=None):
    """
    TODO
    """

    if cols is not None:
        if isinstance(cols, str):
            cols = [cols]
        df = df[list(cols)]
    else:
        cols = list(df)

    if isinstance(fmts, str):
        fmts = [fmts]*len(cols)
    else:
        assert len(fmts) == len(cols)

    if names is None:
        names = cols
    else:
        assert len(names) == len(cols)

    header = ' & '.join(names)
    data = ' \\\\\n'.join(' & '.join(format(elem, fmt)
                                     for elem, fmt in zip(row, fmts))
                          for index, row in df.iterrows())

    return "{} \\\\ \n \\hline \n{}".format(header, data)


###### CLASSES ######

class switch(object):
    """
    Simple switch - case statements. Use as follows
    
    with switch(obj) as case:
        if case(a):
            do_a()
        elif case(b):
            do_b()
        elif case(c, d):
            do_c_or_d()
        ...
        else:  # can also be `elif case.default:`
            do_default()
    """

    default = True  # const - just a wrapper for True

    def __init__(self, obj):
        "obj - object to be compared"
        self.obj = obj

    def __repr__(self):
        return _cls.class_repr(self, 'obj')

    def __call__(self, *values):
        if len(values) == 0:
            return self.obj is None
        #if callable(values[0]):
        #    return any(value(self.obj) for value in values)
        return any(self.obj == value for value in values)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class AttrDict(collections.OrderedDict, collections.abc.Sequence):
    """Attribute-access mapping - OrderedDict + namedtuple

    A dictionary which can be accessed and edited through the attribute notation,
    hence `ad['x'] is ad.x`. Works for getting, setting and deleting. Used in 
    place of:
    * `return collections.namedtuple(name, keys)(*values)`,
    * `return dict(k1=v1, k2=v2)`
    for the user to be able to specify both the ordering and names of returned
    values.
    
    DIFFERENCES FROM DICT CLASSES: 
      * Only strings can be used as keys, and then only ones which are valid 
        identifiers and not used as static attributes (which are shown in
        `dir(AttrDict)`).
        
      * `iter(ad)` will give the VALUES of AttrDict in order to
        provide tuple like behaviour (note that this means items of AttrDict 
        keep their order). Use `iter(ad.keys())` for normal dict behavior.
        
      * where `s` is an int or slice, `ad[s]` will return the correct value /
        slice at the given index `s`.
        
    * `dict(ad)` and `OrderedDict(ad)` will return key, value pairs.
    * `tuple(ad)` and `list(ad)` will return just the values.
    
    The way dictionaries were meant to be...
    """

    # update to inherit only from dict (since dict now ordered)?

    class KeyAttrError(KeyError, AttributeError):
        "Exception which inherits from both KeyError and AttributeError"
        pass

    def __init__(self, *args, **kwargs):
        # to complicated to do parsing ourselves, use OrderedDict
        setup_d = collections.OrderedDict(*args, **kwargs)
        for key in setup_d.keys():
            self._test(key)
        super().__init__(setup_d)

    # don't override __repr__ for recursion reasons
    def __str__(self):
        # Will not be ordered in py_ver < 3.5
        # noinspection PyCallByClass
        return dict.__repr__(sorted(self.items()))

    def __iter__(self):
        return iter(self.values())

    def __reversed__(self):
        return reversed(self.values())

    def __getitem__(self, key):
        if isinstance(key, str):
            return super().__getitem__(key)
        elif isinstance(key, (int, slice)):
            return tuple(self.values())[key]
        else:
            msg = "key ({!r}) must be type str, int or slice; not {!r}"
            raise self.KeyAttrError(msg.format(key, type(key).__name__))

    # namedtuple/dict-like methods
    # noinspection PyMethodOverriding
    def __setitem__(self, key, value):
        self._test(key)
        super().__setitem__(key, value)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise self.KeyAttrError(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            pass
        try:
            super().__delattr__(attr)
        except AttributeError:
            raise self.KeyAttrError(attr)

    def _test(self, key):
        "Check if the key is a str and does not conflict with dict attrs"
        if not isinstance(key, str):
            msg = "key ({!r}) needs to be a str, not {!r}"
            raise TypeError(msg.format(key, type(key).__name__))
        if not isidentifier(key):
            msg = "key ({!r}) is not a valid python identifier"
            raise ValueError(msg.format(key))
        if key in dir(self):  # set to self since the keys are not added to __dict__
            msg = "{!r} is already a static attribute of {}"
            raise self.KeyAttrError(msg.format(key, type(self).__name__))


class Flag(object):
    def __init__(self, name='', showid=False):
        assert isinstance(name, str), name
        self.__name = name
        self.__showid = showid
    def __repr__(self):
        info = ''
        if self.__name:
            info += ' ' + self.__name
        if self.__showid:
            info += ' @ {:#X}'.format(id(self))
        return "<Flag{}>".format(info)


class Hist(object):
    """
    A histogram in which a spread of connected values share the same values. The 
    steps are often discontinuous.
    """
    f = collections.namedtuple('f', ['x', 'y'])

    def __init__(self, maps, end, if_below=None, if_above=None):
        """maps is a dictionary"""
        self.maps = sorted([self.f(x, y) for x, y in maps.items()],
                           key=lambda v: v.x)
        self.start = self.maps[0].x
        self.end = end
        self.if_below = if_below
        self.if_above = if_above

    def __repr__(self):
        lines = ['x < {}: {}'.format(self.start, self.if_below)] \
            if self.if_below != None else []
        for index, (x, y) in enumerate(self.maps):
            try:
                lines.append('{} <= x < {}: {}'
                             .format(x, self.maps[index + 1].x, y))
            except IndexError:
                lines.append('{} <= x < {}: {}'
                             .format(x, self.end, y))
        if self.if_above != None:
            lines.append('{} <= x: {}'.format(self.end, self.if_above))
        return '{0}{{\n     {1}\n    }}'.format(self.__class__.__name__,
                                                ',\n     '.join(lines))

    def __str__(self):
        lines = '\n'.join([line[4:] for line in repr(self).splitlines()[1:]])
        return '{{\n{}'.format(lines)

    def __call__(self, v):
        if v < self.start:
            if self.if_below is None:
                raise ValueError('Hist is undefined below {}.'.format(self.start))
            return self.if_below
        if v >= self.end:
            if self.if_above is None:
                raise ValueError('Hist is undefined above {}.'.format(self.end))
            return self.if_above
        for x, y in reversed(self.maps):
            if x <= v:
                return y


class Path(str):
    """
    Barebones replacement for pathlib.Path in py_ver < 3.3.

    Has most of the same methods, should work as a replacement.
    Nb. subclass of str so some errors may be suppressed.
    """
    sep = os.path.sep

    def __new__(cls, *s):
        # noinspection PyTypeChecker
        return str.__new__(cls, os.path.normpath(os.path.join(*s)))

    def __repr__(self):
        return "it.Path({!r})".format(self.as_posix())

    # def __fspath__(self):
    #    # don't use in order to test in 3.6 (subclass of str so unneeded)
    #    return str(self)

    def __truediv__(self, other):
        return self.joinpath(other)

    def __rtruediv__(self, other):
        return Path(other)/self

    def joinpath(self, *others):
        return Path(os.path.join(self, *others))

    def iterdir(self):
        for item in os.listdir(self):
            yield Path(self, item)  # or just `yield from os.lisdir(self)`

    def as_posix(self):
        return '/'.join(self.parts)

    def absolute(self):
        return Path(os.path.abspath(self))

    def open(self):
        return open(self)

    def rename(self, target):
        os.rename(self, target)

    @staticmethod
    def cwd():
        return Path(os.getcwd())

    @property
    def parts(self):
        return self.split(self.sep)

    @property
    def suffix(self):
        return os.path.splitext(self)[1]

    @property
    def name(self):
        return os.path.split(self)[1]

    @property
    def parent(self):
        return Path(os.path.split(self)[0])

    @property
    def parents(self):
        p = self.parent
        if p == self:
            return []
        return [p] + p.parents

    def exists(self):
        return os.path.exists(self)

    def is_absolute(self):
        return os.path.isabs(self)

    def is_dir(self):
        return os.path.isdir(self)

    def is_file(self):
        return os.path.isfile(self)


# Disallow use of numpy in it.script
for m in ('np', '_np', 'numpy', '_numpy'):
    try:
        eval(m + '.array')
    except (NameError, AttributeError):
        pass
    else:
        raise RuntimeError('Do not use numpy in it.script')
