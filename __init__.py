# it
"""
Interactive Tools (it) -
Tools for (* implies attributes can be imported directly from it):
    repl*   - help in using REPL as shell
    cls     - simplifying class development
    math    - mathematical functions
    boxes   - functions and classes relating to containers
    path    - functions and class for dealing with OS paths
    string  - functions for string handling and writing to stdout
    rand*   - functions for generating random arrays and lists
    timers  - classes for measuring and formatting time
    helpers - misc functions and classes for use in projects
    test    - a bunch of initialised stdlib and numpy objects for testing

A bunch of commands for python 3.6 and up

No longer will support python 2.7 - 3.5 because I can no longer be bothered
"""

from warnings import warn as _warn
from sys import version_info as ver

if ver <= (3, 6):
    _warn("Python version 3.6.0 or greater is expected, not %d.%d.%d" % ver[:3])

try:
    from .it.repl import *
    from .it import (helpers, timers, cls, iters as ers, string, test, math, \
                      boxes, path, rand, arrays)
    from .it.rand import *
except ImportError as e:
    _warn("Unable to load module: {!s}".format(e))
    raise
