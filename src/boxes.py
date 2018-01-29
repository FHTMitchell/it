#!/usr/bin/env python3
# it/boxes.py

import itertools as _itertools
import collections as _collections
import bisect as _bisect
import typing as _t

from . import cls as _cls
from . import iters as _iters
from . import string as _string

_T = _t.TypeVar('T')

class contains(int):  # subclass int so understood as bool
    """namespace for contains.all() and contains.any()

    Calling contains() is a wrapper for contains.any()
    """

    @staticmethod
    def any(obj: _t.Collection, *contents) -> bool:
        """Returns True, if any of contents are in obj, else False"""
        return any((c in obj) for c in contents)

    @staticmethod
    def all(obj: _t.Collection, *contents) -> bool:
        """Returns True, if all of contents are in obj, else False"""
        return all((c in obj) for c in contents)

    # Alias contains() as contains.any()
    # noinspection PyInitNewSignature
    def __new__(cls, obj, *contents):
        return cls.any(obj, *contents)


def remove(container: _t.Container, *elems) -> _t.Container:
    """ Remove elems from containers (str and list supported)

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


def ordered_unique(a: _t.Sequence[_T]) -> _t.List[_T]:
    """Returns a list of all unique elements in a retaining order

    Only works in python 3.6 or greater"""
    return list(dict.fromkeys(a))

def _ordered_unique(a):
    """Returns a list of all unique elements in a retaining order

    For compatibility - ~100x slower the ordered_unqiue
    """
    res = []
    for elem in a:
        if elem not in a:
            res.append(elem)
    return res


def iter_index(a: _t.Sequence, key: _t.Union[int, slice],
               *, return_slice_type: _T = tuple) -> _t.Any:
    """Finds the index or slice of a if a has __len__ method"""

    assert hasattr(a, '__len__'), 'Need len method for advanced indexing'
    assert hasattr(a, '__reversed__'), 'Need reversed method for advanced indexing'

    if isinstance(key, int):
        if key < 0:
            key += len(a)
        if not 0 <= key < len(a):
            raise IndexError('{} index out of range'
                             .format(a.__class__.__name__))
        return _iters.nth(a, key)

    elif isinstance(key, slice):
        # This is more memory efficient but much more complicated and
        # slower than tuple(self)[key]
        if key.step is None or key.step > 0:
            step = key.step
            start = key.start
            stop = key.stop
            itr = iter(a)
        elif key.step < 0:
            step = -key.step
            start = None if key.start is None else -key.start - 1
            stop = None if key.stop is None else -key.stop - 1
            itr = reversed(a)
        else:  # step == 0
            raise ValueError('Slice step cannot be zero')

        if start is not None and start < 0:
            if start > -len(a):
                start += len(a)
            else:
                start = 0

        if stop is not None and stop < 0:
            if stop > -len(a):
                stop += len(a)
            else:
                stop = 0

        # noinspection PyCallingNonCallable
        return return_slice_type(_itertools.islice(itr, start, stop, step))

    else:
        raise TypeError("Key must be int or slice, not {}"
                        .format(type(key).__name__))


def default_namedtuple(typename: str, field_names: _t.Union[str, _t.Iterable[str]],
                       default_values: tuple = ()) -> _t.Callable:
    """
    Returns a collections.namedtuple except with default_values.
    default_values can be specified with a tuple of length < len(field_names) or
    as a dict. Any field_names not referenced in the dict will have a default of
    None.
    """
    T = _collections.namedtuple(typename, field_names)
    if isinstance(default_values, _collections.Mapping):
        T.__new__.__defaults__ = (None,)*len(T._fields)
        default_values = T(**default_values)
    T.__new__.__defaults__ = tuple(default_values)
    return T


def bisect(a, elem, low=0, high=None, right=True):
    """
    Equivalent to the bisect.<side>_bisect (right or left) library functions with
    additional check.
    """
    lst = list(a)
    lst.sort()
    assert all(i == j for i, j in zip(a, lst)), "array is not sorted"
    args = (lst, elem, low, high)
    return _bisect.bisect_right(*args) if right else _bisect.bisect_left(*args)


class AttrDict(_collections.OrderedDict, _collections.abc.Sequence):
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
        # too complicated to do parsing ourselves, use OrderedDict
        setup_d = _collections.OrderedDict(*args, **kwargs)
        for key in setup_d.keys():
            self._test(key)
        super().__init__(setup_d)

    # don't override __repr__ for recursion reasons
    def __str__(self):
        # Will not be ordered in py_ver < 3.5
        # noinspection PyCallByClass
        return repr(dict(sorted(self.items()))).replace(',', ',\n')

    def __iter__(self):
        return iter(self.values())

    def __reversed__(self):
        return reversed(self.values())

    def __getitem__(self, key: _t.Union[int, str, slice]):

        if isinstance(key, str):
            return super().__getitem__(key)
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            elif not 0 <= key < len(self):
                raise IndexError('{} index out of range'.format(_cls.name(self)))
            return _iters.nth(self, key)
        elif isinstance(key, slice):
            # quicker than iter_index but less memory efficients
            return tuple(self)[key]
        else:
            msg = "key ({!r}) must be type str, int or slice; not {}"
            raise self.KeyAttrError(msg.format(key, key.__class__.__name__))

    # namedtuple/dict-like methods
    # noinspection PyMethodOverriding
    def __setitem__(self, key: _t.Union[int, str, slice], value):
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

    def _test(self, key: str):
        "Check if the key is a str and does not conflict with dict attrs"
        if not isinstance(key, str):
            msg = "key ({!r}) needs to be a str, not {!r}"
            raise TypeError(msg.format(key, type(key).__name__))
        if not _string.isidentifier(key):
            msg = "key ({!r}) is not a valid python identifier"
            raise ValueError(msg.format(key))
        if key in dir(self):  # set to self since the keys are not added to __dict__
            msg = "{!r} is already a static attribute of {}"
            raise self.KeyAttrError(msg.format(key, type(self).__name__))



class Hist(object):
    """
    A histogram in which a spread of connected values share the same values. The
    steps are often discontinuous.
    """
    f = _collections.namedtuple('f', ['x', 'y'])

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