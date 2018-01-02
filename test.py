# Auto-generated objects for testing

from __future__ import print_function as _, division as _

import collections as _col
from functools import total_ordering as _to

from . import rand as _rand
from . import repl as _repl
from . import cls as _cls


def remake():
    global l, s, d, t, st, fst, a, m, nt, od, c

    l = [_rand.rint() for _ in range(6)]
    s = _rand.rstr(30, spaces=6)
    d = {w: len(w) for w in "these are some words".split()}
    t = tuple(d.keys())
    st = set(l)
    fst = frozenset(l)

    a = _rand.rint(6)
    m = _rand.rint((3, 3))

    nt = NT(*_rand.rint(2, low=-9))
    od = _repl.odict(d, bykey=False)

    c = C(*l[0:_rand.rint(None, 1, 3)])  # half chance of supplying a mangled


NT = _col.namedtuple("NT", "x y")


def f(*args, **kwargs):
    "docstring"
    return args, kwargs


def g(size=5):
    "docstring"
    for i in _rand.rint(size):
        yield i


@_to
class C(object):
    "class docstring"

    classvar = _rand.rstr(3, spaces=False)

    def __init__(self, x, mangled=0):
        "inst docstring"
        self.x = x
        self.__mangled = mangled

    def __repr__(self):
        return _cls.class_repr(self, 'x')

    def __eq__(self, other):
        if not isinstance(other, C):
            return NotImplemented
        return self.x == other.x

    def __lt__(self, other):
        if not isinstance(other, C):
            return NotImplemented
        return self.x < other.x

    @property
    def mangled(self):
        "mangled docstring"
        return self.__mangled

    @mangled.setter
    def mangled(self, value):
        self.__mangled = value

    @mangled.deleter
    def mangled(self, value):
        del self.__mangled

    def method(self, y=''):
        "method docstring"
        print('inst', self, y)

    @classmethod
    def clsmethod(cls, y=''):
        "clsmethod docstring"
        print('cls', cls, y)

    @staticmethod
    def static(y=''):
        "static(method) docstring"
        print('static', y)


remake()
