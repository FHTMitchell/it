#!/usr/bin/env python3
# it/helpers.py
"""
Things generally in other languages that are missing from python or other misc
objects / functions.
"""

import functools as _functools
import operator as _op
import typing as _t

from . import cls as _cls

try:
    import pandas as pd
except ImportError:
    pass

_T = _t.TypeVar('T')

### singletons and lazy ###

# noinspection PyCallingNonCallable
def singleton(obj: _t.Type[_T]) -> _T:
    """ Decorator which initialises a class with a single instance
    of the same name
    """
    return obj()


def lazy(func: _t.Callable[[], _T]) -> _t.Callable[[], _T]:
    """ Decorator which only actually runs a function the first time it is
    called and stores the result.

    Note that for properties and methods `self` can actually change.
    Use functools.lru_cache instead.
    """
    FLAG = object()
    result = FLAG
    @_functools.wraps(func)
    def inner():
        nonlocal result
        if result is FLAG:
            result = func()
        return result
    return inner


def cache(func: _t.Callable[..., _T]) -> _t.Callable[..., _T]:
    """ Decorator which caches all arguments and keyword argument calls to
        func unlike functools.lru_cache which only caches the first argument.

    Note that any unhashable types passed as a keyword argument to func will
    result in a skipping of any cache processing.
    """
    results = {}
    @_functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            frozen_kwargs = frozenset(kwargs.items())
        except TypeError:
            return func(*args, **kwargs)

        if (args, frozen_kwargs) in results:
            return results[inner]

        result = func(*args, **kwargs)
        results[args, frozen_kwargs] = result
        return result

    return inner


### better assert statement: asrt() ###

class _Assert:
    """Singleton class. See `__call__`."""

    on: bool

    def __init__(self, on=True):
        self.on = bool(on)

    def __repr__(self):
        return f'<_Assert: on={self.on}>'

    def __call__(self, test_, **kwargs):
        """
        Better assert statement

        Same as `assert test` except each kwarg is printed out as a
        key value pair for debugging.

        >>> a = 0
        >>> b = 3
        >>> asrt(a < 4 < b, a=a, b=b)
        AssertionError:
            a: int = 0
            b: int = 3

        Can turn off all asrt checks by setting `asrt.on` to `False`.
        """
        if self.on and not test_:
            msgs = [f'{k}: {v.__class__.__name__} = {v!r}'
                    for k, v in kwargs.items()]
            msg = ('\n\t' if len(msgs) > 1 else '') + '\n\t'.join(msgs)
            raise AssertionError(msg)

asrt = _Assert()  # instance to interact with _Assert

# sanitised input

def sanitised_input(prompt: str, type_: _t.Type[_T] = str, min_: float = None,
                    max_: float = None, range_: range = None) -> _T:
    """
    """

    if min_ is not None and max_ is not None and max_ < min_:
        raise ValueError("min_ must be less than or equal to max_.")

    while True:

        ui = input(prompt)

        if type_ is not str:
            try:
                # noinspection PyCallingNonCallable
                ui = type_(ui)
            except ValueError:
                print("Input type must be {0}.".format(type_.__name__))
                continue

        if max_ is not None and ui > max_:
            print("Input must be less than or equal to {0}.".format(max_))
        elif min_ is not None and ui < min_:
            print("Input must be greater than or equal to {0}.".format(min_))
        elif range_ is not None and ui not in range_:
            if isinstance(range_, range):
                print(f"Input must be between {range_.start} and {range_.stop}.")
            else:
                print(f"Input must be in {set(range_)}.")
        else:
            return ui

# None aware functions

class NoneError(TypeError):
    pass


def assert_not_none(obj: _t.Optional[_T]) -> _T:
    if obj is None:
        raise NoneError()
    return obj


def none_or(a: _t.Optional[_T], b: _T) -> _T:
    """Return a if it is not None otherwise b"""
    return a if a is not None else b


def none_getattr(obj: _t.Optional, *attrs: str):
    """Return a None-Safe `obj.attrs[0].attrs[1].....attrs[N]`

    If any attribute in chain is None, return None rather than throwing an
    AttributeError
    """
    current = obj
    for attr in attrs:
        current = getattr(current, attr, None)
        if current is None:
            break
    return current


def none_getitem(obj: _t.Optional, *items: _t.Any):
    """Return a None-safe `obj[items[0]][items[1]]......[items[N]]`

    If any value in chain is None, return None rather than throwing an
    IndexError or KeyError.
    """
    current = obj
    for item in items:
        try:
            current = current[item]
        except (IndexError, KeyError):
            current = None
        if current is None:
            break
    return current


# Flag

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

# switch / case

class switch(_t.Generic[_T]):
    """
    Simple switch - case statements. Use as follows

    with switch(obj) as case:
        if case(a):
            do_a()
        elif case(b, op='in'):
            do_in_b()
        elif case(c, d):
            do_c_or_d()
        ...
        else:  # can also be `elif case.default:`
            do_default()

    valid operators are currently:
        ==, isinstance, issubclass, in, is, <, <=, >, <=, !=
    """

    default = True  # const - just a wrapper for True
    valid_ops = {
                '==': _op.eq,
                'isinstance': isinstance,
                'issubclass': issubclass,
                'in': _op.contains,
                'is': _op.is_,
                '<': _op.lt,
                '<=': _op.le,
                '>': _op.gt,
                '>=': _op.gt,
                '!=': _op.ne,
            }

    def __init__(self, obj: _T):
        """obj - object to be compared"""
        self.obj = obj

    def __repr__(self):
        return _cls.class_repr(self, 'obj')

    def __call__(self, *values: _t.Union[_T, type], op: str = '==') -> bool:

        if len(values) == 0:
            return False

        if op in {'isinstance', 'issubclass'}:
            return self.valid_ops[op](values)
        elif op in self.valid_ops:
            f = self.valid_ops[op]
            return any(f(self.obj, value) for value in values)
        else:
            msg = f'op ({op}) not valid: {list(self.valid_ops.keys())}'
            raise ValueError(msg)

    def __bool__(self):
        return bool(self.obj)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


_StrList = _t.Union[str, _t.List[str]]
def pd2latex(df: 'pd.DataFrame', cols: _StrList = None, *,
             fmts: _StrList = '.2f', names: _StrList = None) -> str:
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
