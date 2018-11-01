#!/usr/bin/env python3
# it/path.py

import typing as _t
from pathlib import Path
from . import iters as _it

class Directory(_t.NamedTuple):
    path: Path
    dirs: _t.List[Path]
    files: _t.List[Path]


def iterdirs(path: Path) -> _t.Iterator[Path]:
    """ Iterate through all the directories in path """
    return filter(Path.is_dir, path.iterdir())


def iterfiles(path: Path) -> _t.Iterator[Path]:
    """ Iterate through all files in path """
    return filter(Path.is_file, path.iterdir())


def iternotdirs(path: Path) -> _t.Iterator[Path]:
    """ Iterate over all objects in path that are not directories """
    return _it.filterfalse(Path.is_dir, path.iterdir())


def walk(path: _t.Union[Path, str], verbose: bool = False)  \
        -> _t.Iterator[Directory]:
    """ Copy of os.path.walk but for Path objects """

    if not isinstance(path, Path):  # don't optimise -- takes nanoseconds
        path = Path(path)

    try:
        # Better to put them into RAM rather than iterating 3 times
        # and allowing errors to bubble up.
        files, dirs = map(list, _it.partition(Path.is_dir, path.iterdir()))
        yield Directory(path, dirs, files)
    except PermissionError as e:
        if verbose:
            print(e, '(Skipping)')
        return

    for subwalk in map(walk, dirs, _it.repeat(verbose)):
        yield from subwalk



#
# class Path(str):
#     """
#     Barebones replacement for pathlib.Path in py_ver < 3.3.
#
#     Has most of the same methods, should work as a replacement.
#     Nb. subclass of str so some errors may be suppressed.
#     """
#     sep = os.path.sep
#
#     def __new__(cls, *s):
#         # noinspection PyTypeChecker
#         return str.__new__(cls, os.path.normpath(os.path.join(*s)))
#
#     def __repr__(self):
#         return "it.Path({!r})".format(self.as_posix())
#
#     # def __fspath__(self):
#     #    # don't use in order to test in 3.6 (subclass of str so unneeded)
#     #    return str(self)
#
#     def __truediv__(self, other):
#         return self.joinpath(other)
#
#     def __rtruediv__(self, other):
#         return self.__class__(other)/self
#
#     def joinpath(self, *others):
#         return self.__class__(os.path.join(self, *others))
#
#     def iterdir(self):
#         for item in os.listdir(self):
#             yield self.__class__(self, item)  # or just `yield from os.lisdir(self)`
#
#     def as_posix(self):
#         return '/'.join(self.parts)
#
#     def absolute(self):
#         return self.__class__(os.path.abspath(self))
#
#     def open(self):
#         return open(self)
#
#     def rename(self, target):
#         os.rename(self, target)
#
#     @classmethod
#     def cwd(cls):
#         return cls(os.getcwd())
#
#     @property
#     def parts(self):
#         return self.split(self.sep)
#
#     @property
#     def suffix(self):
#         return os.path.splitext(self)[1]
#
#     @property
#     def name(self):
#         return os.path.split(self)[1]
#
#     @property
#     def parent(self):
#         return self.__class__(os.path.split(self)[0])
#
#     @property
#     def parents(self):
#         p = self.parent
#         if p == self:
#             return []
#         return [p] + p.parents
#
#     def exists(self):
#         return os.path.exists(self)
#
#     def is_absolute(self):
#         return os.path.isabs(self)
#
#     def is_dir(self):
#         return os.path.isdir(self)
#
#     def is_file(self):
#         return os.path.isfile(self)
