"Mathematical related scripts"

from functools import reduce as _reduce
from operator import mul as _mul
import collections as _collections
import itertools as _itertools
import functools as _functools
import numbers as _n
import typing as _t

import numpy as _np

from .timers import Timer as _Timer
from .boxes import default_namedtuple as _default_namedtuple

# noinspection PyUnresolvedReferences
from math import pi, e

_T = _t.TypeVar('T')

__all__ = ['apply']

# helper functions with numpy

def apply(func: _t.Callable, array: _np.ndarray, dtype: _np.dtype = None) \
        -> _np.ndarray:
    array = _np.asarray(array)
    if dtype is None:
        dtype = array.dtype
    return _np.fromiter(map(func, array), dtype, count=len(array))



_Array = _t.TypeVar('Array', _np.ndarray, _n.Real)
Ball = _default_namedtuple('Ball', ('max', 'min'), (1, 0))
def scale(x: _Array, inrange: Ball, outrange: Ball) -> _Array:
    """ Returns x scaled from
        [inrange.min, inrange.max] -> [outrange.min, outrange.max]
    """
    in_ = Ball(inrange)
    out = Ball(outrange)
    return (x - in_.min) * ((out.max - out.min)/(in_.max - in_.min)) + out.min





# functions involving primes

def isprime(n: int) -> bool:
    """Returns True if n is prime.

    NOTE: Floats will always return True. In order to check input, use
    isprime.safe.
    """
    # No assertion or conversion: had significant impact!
    if n < 4:
        if n < 2:
            return False
        return True
    if n%2 == 0 or n%3 == 0:
        return False
    for i in range(5, _rootp1(n), 6):
        if n%i == 0 or n%(i + 2) == 0:
            return False
    return True


def _safe_isprime(n: int) -> bool:
    "Safe version of isprime which checks if n is an integer"
    if not isinstance(n, _n.Integral):
        raise ValueError('n is not an integral type: {!r}'.format(type(n).__name__))
    return isprime(n)
isprime.safe  =_safe_isprime


def primelist(n: int) -> _t.List[int]:
    """Returns a list of all primes less than n.

    Use primelist.memeff for a memory efficient alternative and
    primelist.verbose to run in a verbose manner"""
    if n <= 2:
        return []
    nums = [True]*(n - 2)
    for num in range(2, _rootp1(n)):
        counter = num
        while True:
            product = counter*num
            if product >= n:
                break
            nums[product - 2] = False
            counter += 1
    return [index for index, val in enumerate(nums, 2) if val]


def _memeff_primelist(n: int) -> _t.List[int]:
    """Return a list of all primes less than n in a more memory efficient
    manner than primelist (and faster for small values of n)."""
    if n <= 2:
        return []
    primes = []  # Add 2 in at the end, don't need to check non-even
    for i in range(3, int(n), 2):
        for p in primes:
            if i%p == 0:  # non-prime
                break
            if p*p > i:  # no factors bigger than sqrt(i)
                primes.append(i)
                break
        else:
            primes.append(i)  # only for i == 3
    primes.insert(0, 2)
    return primes
primelist.memeff = _memeff_primelist


def factorize(n: int) -> _collections.Counter:
    """Returns the prime factors of `n`. Returns a Counter of factors.

    Use `list(factorize(n).elements())` to get a list.
    Use factorize.verbose for a verbose run.
    """
    assert isinstance(n, _n.Integral)

    possible_primes = primelist(_rootp1(n))  # <=sqrt(n) highest prime possible other than n
    m = n
    p_factors = []

    while m != 1:
        if m in possible_primes:
            # quick check to see if m is prime
            p_factors.append(m)
            break
        for prime in _itertools.takewhile(lambda x: x < _rootp1(m), possible_primes):
            if m%prime == 0:
                m //= prime
                p_factors.append(prime)
                break
        else:
            # will only occur if n is prime
            p_factors.append(m)
            break

    # noinspection PyArgumentList
    return _collections.Counter(p_factors)


def num_divisors(n: int) -> int:  # Not very efficient
    """Gives the number of divisors n has.

    See http://mathschallenge.net/library/number/number_of_divisors
    """
    return prod(f[1] + 1 for f in factorize(n))






# functions involving sums and products

def prod(itr: _t.Iterable[_T]) -> _T:
    """Return the product of an iterable"""
    return _reduce(_mul, itr)
    # _mul replaces lambda x, y: x * y


def factorial(n: int) -> int:
    """factorial: Uses a generator"""
    if n > 1:
        return prod(range(1, n + 1))
    assert isinstance(n, _n.Integral)
    return 1


def _recursive_factorial(n: int) -> int:
    """factorial: Uses recursion (innefficient)"""
    assert isinstance(n, _n.Integral)
    if n <= 1:
        return 1
    return n * _recursive_factorial(n - 1)
factorial.recursive = _recursive_factorial


def weighted_sum(iterable, weights = None) -> float:
    """
    For a list of the form [(amount, weight), ...] returns the sum of each 
    amount multiplied by it's weight, which is then divided by the total weight.
    
    If weights is not None, it is used as the list of weights instead, with
    iterable just being the amounts.
    """

    iterable = list(iterable)
    if weights is None:
        assert all(len(x) == 2 for x in iterable)
    else:
        weights = list(weights)
        iterable = list(zip(iterable, weights))
        assert len(iterable) == len(weights)

    numerator = sum(x[0]*x[1] for x in iterable)
    denominator = sum(x[1] for x in iterable)
    return numerator/denominator


# functions involving factors
def gcd(a: int, b: int, *, verbose=False):
    """The greatest common denominator of a and b."""
    while b:
        a, b = b, a%b
        if verbose: print(a, b)
    return a


# functions involving averages
def mean(vector) -> float:
    "Returns the mean of vector"
    return sum(vector)/len(vector)


def median(vector):
    "Returns the median of vector"
    vector = sorted(vector)
    size = len(vector)
    if size%2 != 0:
        return vector[size//2]
    return mean(vector[size//2: (size//2) + 2])


def mode(vector, singleton=True):
    """
    Finds the mode of vector. If `singleton` is True, .
    """
    vec_count = _collections.Counter(vector).most_common()

    for index, (value, count) in enumerate(vec_count):
        if count != vec_count[0][1]:
            ans = vec_count[:index]
            break
    else:
        ans = vec_count

    if singleton:
        if len(ans) == 1:
            return ans[0][0]
        raise ValueError("More than one mode found (set singlton to False)")
    return {v[0] for v in ans}






# functions involving logarithms

ln = _np.log

def log(n: _n.Real, base: int = 10) -> float:
    """The log of n in a given base"""
    if base is None:
        return ln(n)
    return ln(n)/ln(base)






# functions involving vectors / linear algebra

def unit(v) -> _np.ndarray:
    "Gives the unit vector (the direction) of v"
    return _np.divide(v, _np.linalg.norm(v))


def rotmat(angle: float, axis: str = None, direction: str = 'ccw',
           ndim: int = 3) -> _np.ndarray:
    """
    Calculates the rotation matrix for the given number of dimensions (2 or 3).
    For the three dimensional version, an axis must be specified (either 'x',
    'y' or 'z'). The direction must be either clockwise ('cw') or counter-
    clockwise ('ccw', default). 'cw' is equivalent to entering a negative argument.
    """
    if direction.lower() == 'cw':
        angle = -angle  # flip direction
    elif direction.lower() not in ('ccw', 'acw'):
        msg = 'direction must be "cw" or "ccw", not {!r}.'.format(direction)
        raise ValueError(msg)

    cost = _np.cos(angle)
    sint = _np.sin(angle)
    if ndim == 2:
        assert axis is None, 'No axis is required for 2 dimensions'
        return _np.array([[cost, -sint], [sint, cost]])
    if ndim == 3:
        if axis in {'x', 'X', 0}:
            R = [[1, 0, 0], [0, cost, -sint], [0, sint, cost]]
        elif axis in {'y', 'Y', 1}:
            R = [[cost, 0, sint], [0, 1, 0], [-sint, 0, cost]]
        elif axis in {'z', 'Z', 2}:
            R = [[cost, -sint, 0], [sint, cost, 0], [0, 0, 1]]
        else:
            raise ValueError('axis must be "x", "y" or "z", not {!r}'.format(axis))
        return _np.array(R)
    raise ValueError('ndim must be either 2 or 3, not {!r}'.format(ndim))


def diagonalise(M, imaglim=1e6, maxcond=1e5, debug=False):
    """ 
    TODO: PROBABLY DOESN'T WORK!!
    
    Diagonalise M. 
    
    if all the imaginary elements of the diagonalised matrix are less than 
    imaglim, will return just the real components. Set to None / 0 to ignore.
    
    Will raise an AssertionError if the condition of the 
    eigenvectors of M is greater than maxcond (cond(V) = 10**n where n is the
    the number of digits of accuracy for a V). Set to None to ignore.
    """
    evals, evecs = _np.linalg.eig(M)
    evecs_inv = _np.linalg.inv(evecs)
    D = evecs_inv@M@evecs
    if debug:
        print("M =\n{}\nD =\n{}\nevecs= \n{}\ncond(evecs) = {}"
              .format(M, D, evecs, _np.linalg.cond(evecs)))
    if maxcond:
        assert abs(_np.linalg.cond(evecs)) <= maxcond, "M is probably not diagonalisable"
    if imaglim:
        # noinspection PyTypeChecker
        if _np.all(abs(D.imag) <= imaglim):
            return D.real
    return D






# degree trig
def _use_deg(f: _t.Callable, arc: bool = False) -> _t.Callable:
    """Convert a trignometric which uses radians to degrees

    If an `arc` function, make sure `arc` is set to True
    """

    if not arc:
        def df(*args, **kwargs):
            # Need to convert all numeric input types to degrees
            args = list(args)
            for index, value in enumerate(args):
                try:
                    args[index] = _np.deg2rad(value)
                except TypeError:
                    pass
            for key, value in kwargs.items():
                if key == 'out':
                    continue  # ignore
                try:
                    kwargs[key] = _np.deg2rad(value)
                except TypeError:
                    pass
            # and return
            return f(*args, **kwargs)

    else:
        def df(*args, **kwargs):
            return _np.rad2deg(f(*args, **kwargs))

    return _functools.wraps(f)(df)


sind = _use_deg(_np.sin)
cosd = _use_deg(_np.cos)
tand = _use_deg(_np.tan)
arcsind = _use_deg(_np.arcsin, True)
arccosd = _use_deg(_np.arccos, True)
arctand = _use_deg(_np.arctan, True)
arctan2d = _use_deg(_np.arctan2, True)






# Generators

def fib(a: int = 1, b: int = 1) -> _t.Iterator[int]:
    "Generator for the Fibonacci sequence."
    a, b = sorted((a, b))
    yield a
    yield b
    while True:
        b, a = a + b, b
        yield b


def triangles(n: int = 2, stop: int = None) -> _t.Iterator[int]:
    "Generates the (first `stop`) nth dimensional triangle numbers."
    if n == 1:
        if stop is None:
            yield from _itertools.count()
        else:
            yield from range(stop)
    else:
        total = 0
        for t in triangles(n - 1, stop):
            total += t
            yield total







# Misc functions

def ispalindrome(n) -> bool:
    return str(n) == str(n)[::-1]


def precision(x: _n.Real) -> int:
    """The precision of x"""
    if isinstance(x, float):
        decimal_part = repr(x).split('.')[1]
        return len(decimal_part) if decimal_part != '0' else 0
    elif isinstance(x, int):
        return 0
    else:
        msg = 'x must be a real number, not {}'.format(type(x).__name__)
        raise TypeError(msg)


def _rootp1(n: float) -> int:
    'returns the truncated square root of n plus 1 for use in range'
    return int(n**0.5) + 1







# Verbose versions - might put in separate namespace

def _verbose_primelist(n: int) -> _t.List[int]:
    """Return a list of all primes less than n in a more memory efficient 
    manner than primelist. Also faster for small values of n]."""
    # VERBOSE SETUP
    timer = _Timer(5)
    print('Finding primes up to {:,}'.format(n))

    if n <= 2:
        return []
    primes = []  # Add 2 in at the end, don't need to check non-even
    for i in range(3, int(n), 2):
        for p in primes:
            # VERBOSE BIT
            if timer.check():
                msg = "Time taken: {}, found {:,} primes up to {:,}."
                print(msg.format(timer(pad=4), len(primes), i - 1))
            if i%p == 0:  # non-prime
                break
            if p*p > i:  # no factors bigger than sqrt(i)
                primes.append(i)
                break
        else:
            primes.append(i)  # only for i == 3
    primes.insert(0, 2)

    # VERBOSE END
    print("Found {:,} primes in {}".format(len(primes), timer))
    return primes


def _verbose_factorize(n: int) -> _collections.Counter:
    """
    Verbose form of factorize
    """
    assert isinstance(n, _n.Integral)
    # VERBOSE SETUP
    timer = _Timer(5)
    print("Finding prime factors of {:,}".format(n))

    possible_primes = _verbose_primelist(_rootp1(n))  # <=sqrt(n) highest prime possible other than n
    m = n
    p_factors = []

    while m != 1:
        if m in possible_primes:
            # quick check to see if m is prime
            p_factors.append(m)
            break
        for prime in _itertools.takewhile(lambda x: x < _rootp1(m), possible_primes):
            # VERBOSE BIT
            if timer.check():
                msg = 'Time taken: {}, found {:,} prime factors up to m = {:,}.'
                print(msg.format(timer(pad=4), len(p_factors), m))
            if m%prime == 0:
                m //= prime
                p_factors.append(prime)
                break
        else:
            # will only occur if n is prime
            p_factors.append(m)
            break

    # VERBOSE END
    print("Found {:,} prime factors in {}".format(len(p_factors), timer))
    # noinspection PyArgumentList
    return _collections.Counter(p_factors)


primelist.verbose = _verbose_primelist
factorize.verbose = _verbose_factorize