#!/usr/bin/env python3
# it/boxes.py

import itertools as _itertools
import collections as _collections
import bisect as _bisect
import typing as _t
from collections import abc as _abc

from . import cls as _cls
from . import iters as _iters
from . import string as _string

_T = _t.TypeVar('T')
_T_co = _t.TypeVar('T_co')


# contains

def _contains_any(obj: _t.Collection, *contents) -> bool:
    """Returns True, if any of contents are in obj, else False"""
    return any((c in obj) for c in contents)

def _contains_all(obj: _t.Collection, *contents) -> bool:
    """Returns True, if all of contents are in obj, else False"""
    return all((c in obj) for c in contents)

contains = _contains_any
contains.any = _contains_any
contains.all = _contains_all

# sets

def intersection(*itrs: _t.Iterable) -> set:
    return set.intersection(*map(set, itrs))

def union(*itrs: _t.Iterable) -> set:
    return set().union(*itrs)


# other

_C = _t.TypeVar('C', str, list)
def remove(container: _C, *elems) -> _C:
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
    """Finds the index or slice of `a` if `a` has __len__ method"""

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
                       default_values: tuple = ()) -> _t.Callable\
        :
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


class AttrDict(_collections.OrderedDict, _t.MutableMapping[str, _T_co],
               _t.Sequence[_T_co]):
    """Attribute-access mapping - OrderedDict + namedtuple

    A dictionary which can be accessed and edited through the attribute notation,
    hence `ad['x'] is ad.x`. Works for getting, setting and deleting. Used as
      `return AttrDict(k1=v1, k2=v2) -> res.k1 OR res[0] OR res['k1']`
    in place of:
    * `return collections.namedtuple(name, keys)(*values)` -> res.k1 OR res[0],
    * `return dict(k1=v1, k2=v2) -> res['k1']`
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

    __slots__ = ()

    class KeyAttrError(KeyError, AttributeError):
        "Exception which inherits from both KeyError and AttributeError"
        pass

    def __init__(self, *args, **kwargs):
        # too complicated to do parsing ourselves, use OrderedDict's
        setup_d = _collections.OrderedDict(*args, **kwargs)
        for key in setup_d.keys():
            self._test(key)
        super().__init__(setup_d)

    # don't override __repr__ for recursion reasons
    def __str__(self):
        # Will not be ordered in py_ver < 3.5
        # noinspection PyCallByClass
        return (f'{_cls.name(self)}(\n' +
                ',\n'.join(f' {k}={v!r}' for k, v in self.items()) +
                '\n)')

    def __iter__(self) -> _t.Iterator[_T_co]:
        return iter(self.values())

    def __reversed__(self) -> _t.Iterator[_T_co]:
        return reversed(self.values())

    @_t.overload
    def __getitem__(self, key: slice) -> _t.Tuple[_T_co, ...]:
        pass

    def __getitem__(self, key: _t.Union[int, str]) -> _T_co:

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
            # noinspection PyTypeChecker
            return tuple(self)[key]
        else:
            msg = "key ({!r}) must be type str, int or slice; not {}"
            raise self.KeyAttrError(msg.format(key, key.__class__.__name__))

    # namedtuple/dict-like methods
    # noinspection PyMethodOverriding
    def __setitem__(self, key: str, value: _T_co):
        self._test(key)
        super().__setitem__(key, value)

    def __getattr__(self, attr: str) -> _T_co:
        try:
            return self[attr]
        except KeyError:
            raise self.KeyAttrError(attr)

    def __setattr__(self, attr: str, value: _T_co):
        self[attr] = value

    def __delattr__(self, attr: str):
        try:
            del self[attr]
        except KeyError:
            pass
        try:
            super().__delattr__(attr)
        except AttributeError:
            raise self.KeyAttrError(attr)

    def _test(self, key: str) -> None:
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

class Node(_t.Generic[_T_co]):

    __slots__ = ('value', 'next')

    value: _T_co
    next: '_t.Optional[Node[_T_co]]'

    # Don't define next as generic
    def __init__(self, value: _T_co, next: 'Node' = None):
        self.value = value
        self.next = next

    def __repr__(self):
        next_id = 'None' if self.next is None else f'<Node at {hex(id(self.next))}>'
        return f'Node({self.value}, {next_id})'

    def __eq__(self, other: 'Node[_T_co]'):
        if isinstance(other, Node):
            return self is other
        return NotImplemented

    def copy(self) -> 'Node[_T_co]':
        return self.__class__(self.value, self.next)


class LinkedList(_t.MutableSequence[_T_co]):
    """
    A linked list implementation for faster appending and popping to the front
    and end of a list.
    """

    __slots__ = ('_first', '_last', '_length')

    _first: _t.Optional[Node[_T_co]]
    _last: _t.Optional[Node[_T_co]]
    _length: int

    def __init__(self):
        self._first = None
        self._last = None
        self._length = 0

    def clear(self) -> None:
        self.__init__()

    def append(self, x: _T_co) -> None:
        if self._first is None:
            self._first = Node(x, None)
            self._last = self._first
        elif self._last is self._first:
            self._last = Node(x, None)
            self._first.next = self._last
        else:
            self._last.next = Node(x, None)
            self._last = self._last.next
        self._length += 1

    def insert(self, index: int, value: _T_co) -> None:
        if index == len(self):
            self.append(value)
        elif index == 0:
            self.append_left(value)
        else:
            self._assert_index(index)
            node = Node(value, self._nth_node(index))
            self._nth_node(index - 1).next = node
            self._length += 1

    def pop(self, index: int = -1) -> _T_co:
        if not len(self):
            raise IndexError("pop from empty list")
        if index == -1:
            return self.pop(len(self) - 1)
        elif index == 0:
            cur = self._first
            self._first = self._first.next
        else:
            self._assert_index(index)
            prev = self._nth_node(index - 1)
            cur = prev.next
            prev.next = cur.next
        self._length -= 1
        return cur.value

    def append_left(self, value: _T_co) -> None:
        node = Node(value, self._first)
        self._first = node
        self._length += 1

    def pop_first(self) -> _T_co:
        return self.pop(0)

    def pop_last(self) -> _T_co:
        return self.pop()

    def __len__(self):
        return self._length

    def _iter_nodes(self) -> _t.Iterator[Node[_T_co]]:
        current = self._first
        if current is None:
            return
        while current.next is not None:
            yield current
            current = current.next
        yield current

    def _nth_node(self, index: int) -> Node[_T_co]:
        self._assert_index(index)
        return _iters.nth(self._iter_nodes(), index)

    def _assert_index(self, index: int) -> None:
        if not isinstance(index, int):
            raise TypeError(
                    f"index must be integer, not {index.__class__.__name__}")
        if not 0 <= index < self._length:
            raise IndexError(f"list index ({index}) out of range(0, {len(self)})")

    def __iter__(self) -> _t.Iterator[_T_co]:
        for node in self._iter_nodes():
            yield node.value

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}({str(self)})'

    def __str__(self):
        return f'[{_string.join(self, ", ")}]'

    def __getitem__(self, index: int) -> _t.Union[_T_co, 'LinkedList[_T_co]']:


        if isinstance(index, int):
            return self._nth_node(index).value

        if isinstance(index, slice):
            start: int = index.start if index.start is not None else 0
            stop: int= index.stop if index.stop is not None else len(self)

            if index.step not in (1, None) or stop < start:
                raise IndexError

            new_ll = self.__class__()
            if start == stop:
                return new_ll

            new_ll._first = self._nth_node(start)
            if stop == len(self):
                new_ll._last = self._last
            else:
                new_ll._last = self._nth_node(stop - 1)

            return new_ll

        raise TypeError

    def __delitem__(self, index: int):
        self._assert_index(index)
        if len(self) == 0:
            self.clear()
        elif index == 0:
                self._first = self._first.next
        else:
            prev = self._nth_node(index - 1)
            prev.next = prev.next.next
            if prev.next is None:
                self._last = prev
        self._length -= 1

    def __setitem__(self, index: int, value: _T_co) -> None:
        self._nth_node(index).value = value

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
