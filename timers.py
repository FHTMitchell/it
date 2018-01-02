# it/timers.py

from __future__ import print_function as _, division as _

import time
import warnings


def timestamp(unix_time=None, show_zone=True):
    """Show time (current if None) in the format 'yyyy-mm-dd HH:MM:SS [TZ]'"""
    if unix_time is None:
        unix_time = time.time()
    fmt = '%Y-%m-%d %H:%M:%S'
    if show_zone:
        fmt += ' %z'
    return time.strftime(fmt, time.localtime(unix_time))


def time_diff_repr(unix_start, unix_end=0, unit=None, sig=1, pad=0):
    """
    Returns a string of the absolute difference between two times given in 
    appropriate units. The unit selection can be overridden with one of the 
    following arguments passed to `unit`:
        e: seconds (scientific notation)
        s: seconds
        m: minutes
        h: hours
        d: days
        y: years
    `sig` is the number of digits after the decimal point to display whilst 
    `pad` is the minimum size of the numeric value to be returned padded to 
    the right with spaces.
    """
    fmt = '>{}.{}'.format(pad, sig)
    unit_dict = {
        'e': lambda t: '{1:{0}e} seconds'.format(fmt, t),
        's': lambda t: '{1:{0}f} seconds'.format(fmt, t),
        'm': lambda t: '{1:{0}f} minutes'.format(fmt, t/60),
        'h': lambda t: '{1:{0}f} hours'.format(fmt, t/3600),
        'd': lambda t: '{1:{0}f} days'.format(fmt, t/(3600*24)),
        'y': lambda t: '{1:{0}f} years'.format(fmt, t/(3600*24*365.25))
    }

    diff = abs(unix_end - unix_start)

    if unit is None:
        repr_dict = {
            0.1: 'e',
            120: 's',
            120*60: 'm',
            48*3600: 'h',
            365*24*3600: 'd'
        }
        for key, value in repr_dict.items():
            if diff < key:
                return unit_dict[value](diff)
        else:
            return unit_dict['y'](diff)
    else:
        try:
            return unit_dict[unit[0]](diff)
        except KeyError:
            print('Valid keys are {}.'.format(tuple(unit_dict.keys())))
            raise

            
### Classes ###

class Clock(object):
    time = staticmethod(time.time)  # python really can be beautiful

    @staticmethod
    def ftime(show_zone=True):
        return timestamp(show_zone=show_zone)

    def __repr__(self):
        return "<{}: time=`{}`>".format(self.__class__.__name__,
                                        self.ftime())


class Stopwatch(Clock):
    """
    A stopwatch, starts counting from first instancing and upon restart().
    Call an instance to find the time in seconds since timer started/restarted.
    Call str to print how much time has past in reasonable units.
    """

    def __init__(self):
        self._tic = time.time()

    def restart(self):
        self._tic = time.time()

    @property
    def tic(self):
        return self._tic

    @property
    def toc(self):
        return time.time() - self._tic  # faster to check _tic than tic

    def __call__(self, unit=None, sig=1, pad=0):
        """
        Depreciated - Saved for legacy reasons.
        """
        msg = "Will no longer be callable. Use __format__ instead."
        warnings.warn(msg, DeprecationWarning)
        return self.ftoc(unit, sig, pad)

    def ftoc(self, unit=None, sig=1, pad=0):
        """
        Time since (re)start in a given unit to sig significant places. 
        If unit is None an appropriate unit is chosen.
        """
        return time_diff_repr(time.time(), self.tic, unit, sig, pad)

    def __repr__(self):
        return '<{}: tic=`{}`>'.format(self.__class__.__name__,
                                       timestamp(self.tic))

    def __str__(self):
        return self.ftoc()

    def __format__(self, fmt):
        """
        Format specifier for Stopwatch. Can specifiy a right pad, precision and
        unit (see time_diff_repr). "f" and "g" use default unit.
        """
        clsname = self.__class__.__name__

        if any((c in fmt) for c in '<=^'):
            msg = "{} only supports right alligned pad".format(clsname)
            raise ValueError(msg)

        if '>' in fmt:

            index = fmt.index('>')
            if index == 0:
                pass
            elif index == 1:
                if fmt[0] != ' ':
                    msg = "Only valid padding character for {} is ' '"
                    raise ValueError(msg.format(clsname))
            else:
                msg = "Invalid format specifier for {}".format(clsname)
                raise ValueError(msg)
            pad = ''

            for char in fmt[index + 1:]:
                if not char.isnumeric():
                    break
                pad += char
            fmt = fmt[index + len(pad) + 1:]
            pad = int(pad) if pad else 0
        else:
            pad = 0

        if '.' in fmt:
            index = fmt.index('.')
            if index != 0:
                msg = "Invalid format spec {!r} for {}"
                raise ValueError(msg.format(fmt[:index], clsname))
            sig = ''
            for char in fmt[index + 1:]:
                if not char.isnumeric():
                    break
                sig += char
            if not sig:
                raise ValueError('Format specifier missing precision')
            fmt = fmt[index + len(sig) + 1:]
            sig = int(sig)
        else:
            sig = 1

        if len(fmt) > 1:
            msg = "Invalid format specifier {} for {}"
            raise ValueError(msg.format(fmt, clsname))

        if fmt in 'fgFG':  # includes ''
            fmt = None
        else:
            fmt = fmt.lower()

        return self.ftoc(unit=fmt, sig=sig, pad=pad)


class Timer(Stopwatch):
    def __init__(self, checktime=5):
        super(Timer, self).__init__()
        self.checktime = checktime
        self.checker = Stopwatch()

    def __repr__(self):
        msg = '<{}: tic=`{}`, checktime={}>'
        return msg.format(self.__class__.__name__,
                          timestamp(self.tic),
                          self.checktime)

    def check(self):
        "Checks if self.checktime has passed since self.check returned True"
        if self.checker.toc > self.checktime:
            self.checker.restart()
            return True
        return False

    def check2(self, time):
        "As check but takes a time (in seconds) argument instead"
        if self.checker.toc > time:
            self.checker.restart()
            return True
        return False
