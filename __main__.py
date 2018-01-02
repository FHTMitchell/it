# it/__main__.py
from __future__ import print_function as _

"""
Will copy all it/*.py files into a copy subdirectory.
"""

import os
import sys
import time
import shutil
# todo: update to use glob instead?

if __name__ == '__main__':  # isn't this always true?

    moddir = os.path.abspath(os.path.dirname(sys.argv[0]))
    now = time.strftime('%Y%m%d')
    subdir = os.path.join(moddir, 'Copy' + now)

    if os.path.exists(subdir):
        shutil.rmtree(subdir)
        is_new = False
    else:
        is_new = True

    os.mkdir(subdir)

    for file in os.listdir(moddir):
        oldpath = os.path.join(moddir, file)
        if os.path.splitext(oldpath)[-1] == '.py':
            newpath = os.path.join(subdir, file)
            shutil.copy(oldpath, newpath)

    if is_new:
        print('Created new `it` copy at {!r}'.format(subdir))
    else:
        print('Modified latest `it` copy at {!r}'.format(subdir))
