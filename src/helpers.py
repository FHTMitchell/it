#!/usr/bin/env python3
# it/helpers.py

import typing as _t

from src import cls as _cls

try:
    import pandas as pd
except ImportError:
    pass

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