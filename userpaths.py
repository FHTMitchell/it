#! /usr/bin/env python3
# userpaths.py
# NOT TO BE COMMITED

try:
    from pathlib import Path  # > 3.5
except ImportError:
    from .script import Path

# Paths of interest
conda = Path(r'C:\ProgramData\Anaconda3')
it = conda / 'it'
code = Path(r'C:\Users\FMitchell\Code')
py3 = code / 'Py3'
scripts = py3 / 'scripts'
projects = py3 / 'projects'

__default__ = (py3, scripts, projects)