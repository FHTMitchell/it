"""
For use in the interactive REPL interpreter
"""

# imports for funcs
import sys as _sys
import os as _os
import collections as _collections
import pprint as _pprint
import typing as _t

from warnings import warn as _warn

from .boxes import AttrDict
from .helpers import Flag as _Flag
from .path import Path

# Imports a reload function  -- leave for ease of converting
try:
    from importlib import reload as _r  # 3.6
except ImportError:
    try:
        from imp import reload as _r  # 3.0
    except ImportError:
        # noinspection PyUnboundLocalVariable,PyUnresolvedReferences
        _r = reload  # 2.7 - sets it._r

# paths

"""
User paths are held in userpaths.py - use the following format

# Any imports can be used, only strings and Path objects will be used
import os
from pathlib import Path

# paths - order doesn't matter
a_path = r'a/path'                         # can be str
another_path = Path(r'another/path/too')   # can be Path
sub_path = os.path.join(a_path, 'subdir')  # can be combined
non_path = another_path / '^^^'            # nonexistant paths will be ignored

# macros
__cd__ = 'path/to/start/python/in'   # will CD to here upon importing it

__default__ = (a_path, sub_path)     # defaults for it.path
"""



try:
    from it import userpaths as _user_paths
except ImportError:
    paths: AttrDict[Path] = AttrDict()
    default_paths = ()
else:
    paths = {key: Path(value) for key, value in _user_paths.__dict__.items() if
                isinstance(value, (str, Path))
                and _os.path.isdir(str(value))
                and key not in ('__default__', '__cd__')
            }
    paths: AttrDict[Path] = AttrDict(paths)

    default_paths = _user_paths.__dict__.get('__default__', ())
    if isinstance(default_paths, str):
        default_paths = (default_paths,)

    try:
        # noinspection PyUnresolvedReferences
        _nwd = _user_paths.__cd__
        _os.chdir(_nwd)
        print('Changed CWD to {!s}'.format(_nwd))
    except AttributeError:
        pass
    except OSError as err:
        _warn(err)
    else:
        del _nwd

    del _user_paths

# For use in interpreter
def setpath(paths: _t.Reversible[Path] = None, *, verbose: bool = True) -> None:
    """
    Adds all paths in path_tuple to sys.path. If None will add every path in
    `def_paths`.
    """
    if paths is None:
        paths = default_paths
    elif isinstance(paths, (str, Path)):
        paths = (paths,)  # don't iter over str (or Path)

    for path in reversed(paths):
        path = str(path)
        if path not in _sys.path:
            _sys.path.insert(0, path)
            if verbose:
                print('{} added to sys.path'.format(path))


def reload(*modules) -> tuple:
    """Reload modules"""
    return tuple(map(_r, modules))


def odict(d: dict, bykey: bool = True, reverse: bool = False) \
        -> _collections.OrderedDict:
    """
    Returns a collections.OrderedDict which is automatically sorted from a dict,
    `d`. Sorts by key if `bykey` is True else by value and in ascending order
    if not `reverse` else descending.
    """
    index = 0 if bykey else 1
    items = sorted(d.items(), key=lambda x: x[index], reverse=reverse)
    return _collections.OrderedDict(items)


def pp(obj, ret: bool = False) -> _t.Union[_t.List[str], None]:
    """
    Shortcut for pprint.pprint(obj) except that since numpy arrays have their
    own pretty __str__ method, simply prints those.
    """
    if type(obj).__name__ == 'ndarray':  # avoids importing numpy
        printout = str(obj)
    elif isinstance(int, float):
        printout = com(obj)
    else:
        printout = _pprint.pformat(obj)
    if ret:
        return printout
    print(printout)


# Formatting fancy classes
_FLAG = _Flag('FMT')
class _Fmt(object):
    """
    Class for quick formatting.
    USE it.fmt / obj / fmt_spec
    OR  it.fmt - obj - fmt_spec
    """
    _name = 'fmt'
    _fmtbase = _FLAG

    def __init__(self, obj=_FLAG, fmt=None):
        self.obj = obj
        self.fmt = fmt if fmt is not None else self._fmtbase

    def __repr__(self):
        if self.obj == _FLAG:
            return "<{} constructor>".format(self._name)
        if self.fmt == _FLAG:
            return "<{} {!r}>".format(self._name, self.obj)
        return format(self.obj, self.fmt)

    def __call__(self, obj, fmt=None):
        if fmt is None and self.obj is not _FLAG:
            obj, fmt = self.obj, obj
        return self.__class__(obj, fmt)

    def __truediv__(self, other):
        return self(other)

    def __sub__(self, other):
        return self(other)

    # could do something with // (__floordiv__)?


class _Com(_Fmt):
    """Class for quick formatting (defaults to ',' format spec)"""
    _name = 'com'
    _fmtbase = ','

    def __init__(self, obj=_FLAG, fmt=None):
        super(_Com, self).__init__(obj, fmt)

# visible instances
fmt = _Fmt()
com = _Com()

################################## ld ##########################################
class ld(object):
    """
    ld - list dir

    List the attributes and methods of an object with the following filters
    entered as a character in the mode string:

    (attributes beginning with a lowercase letter will always be shown)
    a   - all:    show all attrs
    c   - caps:   show attrs beginning with a capital
    s/_ - sunder: show attrs beginning with a single underscore
    d   - dunder: show attrs beginning with a double underscore
    __  - show method beginning with either a single or a double underscore

    Additional information can be shown (only one of these can be provided)
    t  - types: also show the type of each attribute
    v  - vals:  also show the value of each attribute
    """

    modes = {
        'a': 'all',
        'v': 'vals',
        't': 'types',
        'c': 'caps',
        's': 'sunder',
        'd': 'dunder',
        '__': 'dunder',  # will automatically include sunder
        '_': 'sunder'
    }

    def __init__(self, obj, mode='c'):
        not_in_modes = ''.join(filter(lambda m: m not in self.modes, mode))
        assert not not_in_modes, repr(not_in_modes)
        assert not all(m in mode for m in 'vt'), repr(mode)

        self._obj = obj
        self._mode = mode

    def __repr__(self):
        return _pprint.pformat(self.ret())  # also works for str/print

    def __format__(self, format_spec):
        return self.__class__(self._obj, format_spec)

    def __call__(self):
        return self  # so it.ld(obj).all == it.ld(obj).all()

    def __iter__(self):
        ms = {self.modes[m] for m in self._mode}

        attrs = sorted(dir(self._obj), key=self.dir_sort)
        if not 'all' in ms:
            if not 'sunder' in ms:
                attrs = [a for a in attrs if
                         (not a.startswith('_')) or a.startswith('__')]
            if not 'dunder' in ms:
                attrs = [a for a in attrs if not a.startswith('__')]
            if not 'caps' in ms:
                # needs to be this way since '_'.upper() == '_'
                attrs = [a for a in attrs if a[0] == a[0].lower()]

        isdict = True
        if 'types' in ms:
            attrs = {a: type(getattr(self._obj, a)).__name__ for a in attrs}
        elif 'vals' in ms:
            attrs = {a: getattr(self._obj, a) for a in attrs}
        else:
            isdict = False

        return iter(attrs if not isdict else attrs.items())

    @property
    def _fmter(self):
        return dict if any(m in self._mode for m in 'vt') else list

    def ret(self):
        return self._fmter(self)

    def _pass(self, addmode):
        return self.__class__(self._obj, self._mode + addmode)

    @property
    def all(self):
        return self._pass('a')

    @property
    def vals(self):
        return self._pass('v')

    @property
    def types(self):
        return self._pass('t')

    @property
    def caps(self):
        return self._pass('c')

    @property
    def sunder(self):
        return self._pass('s')

    @property
    def dunder(self):
        return self._pass('d')
        
    @staticmethod
    def dir_sort(s: str) -> _t.Tuple[bool, bool, str]:
        "Sorts objects by all no_leading_underscore -> all sunder -> all dunder"
        return s.startswith('__'), s[0] == '_', s


############################## pwd, cd, ls #####################################

# path navigation tools, designed to mimic bash using fancy classes

_PathType = _t.Union[Path, str]

class _PWD(object):
    def __repr__(self):  # also makes __str__
        return _os.getcwd()

    def __call__(self):  # ret for consistency with ls()
        return self

    def __eq__(self, other):
        if isinstance(other, (str, Path)):
            return str(self) == str(other)
        return NotImplemented

    def __fspath__(self):
        return str(self)

    @property
    def path(self):
        return Path(self)


class _CD(_PWD):  # __repr__ taken from pwd
    def __call__(self, path: _PathType = '.') -> '_CD':
        try:
            _os.chdir(path)
        except TypeError:
            if isinstance(path, Path):
                _os.chdir(str(path))
            else:
                raise
        return self

    def __getattr__(self, attr):
        if (len(attr) == 1) and (attr.lower() != attr):  # ie. it.cd('C')
            try:
                self(attr)
            except OSError:
                self("{}:/".format(attr))
        elif '_' in attr:  # attempt to take '_' as ' '
            try:
                self(attr)
            except OSError:
                self(attr.replace('_', ' '))
        else:
            self(attr)
        return self  # so attrs can be chained

    def __getitem__(self, key):
        self(_os.listdir('.')[key])
        return self

    def __truediv__(self, other):
        return self(other)

    def __floordiv__(self, other):
        # from root
        return (+self) / other

    def __neg__(self):
        return self('..')

    def __pos__(self):
        return self('/')

    @property
    def _(self):
        # shortcut for parent dir
        return self('..')

    up = _
    # it = _IT()


class _IT(object):
    def __repr__(self):
        return "<Special method. Use it.cd/'it' (rel) or it.cd.it.it (abs)>"

    def __getattr__(self, key):
        return cd(paths[key])


class _LS(object):

    def __init__(self, _path='.'):
        self._path: Path = Path(_path)

    def __repr__(self):

        lst = list(self)
        if not lst:
            return '<empty>'

        return "\n".join(
            "{:>2} {}{}".format(index, elem, self._pathtype(elem))
            for index, elem in enumerate(lst)
        )

    def __call__(self, path: _PathType = '.') -> '_LS':

        if path == '.': # so _LS objects can have non-'.' defaults
            path = self._path

        return self.__class__(path)

    def __iter__(self):
        yield from self._path.iterdir()

    def __len__(self):
        return len(list(iter(self)))  # need iter to stop inf recursion

    def __getitem__(self, key):
        return list(self)[key]

    def files(self, path: _PathType = '.') -> _t.List[Path]:
        return [p for p in self(path) if p.is_file()]

    def dirs(self, path: _PathType = '.') -> _t.List[Path]:
        return [p for p in self(path) if p.is_dir()]

    def _pathtype(self, obj: _PathType) -> str:
        elem = self._path / obj
        if elem.is_file():
            return ''
        elif elem.is_dir():
            return '/'
        elif elem.is_symlink():
            return '@'
        else:
            return '?'


# and the visible instances
pwd = cwd = _PWD()
cd = _CD()
ls = _LS()
cd.it = _IT()
