# iters.py

import collections as _collections
import operator as _operator
import random as _random
import typing as _t
from itertools import *

from .helpers import Flag as _Flag

_NO_DEFAULT = _Flag('NO_DEFAULT')

_T = _t.TypeVar('T')
_U = _t.TypeVar('U')
_V = _t.TypeVar('V')
_Iin = _t.Iterable
_Iout = _t.Iterator

# Mine

def isiterable(obj: _t.Any, *, include_str=True, include_bytes=True) -> bool:
    """Returns true if obj is iterable"""
    if not include_str and isinstance(obj, str):
        return False
    if not include_bytes and isinstance(obj, bytes):
        return False
    return hasattr(obj, '__iter__')


def flatten(a: _Iin) -> _Iout:
    """generator of flattened n-deep iterable (excluding str) a."""
    for elem in a:
        if not isinstance(elem, str):
            try:
                yield from flatten(elem)
            except TypeError:
                yield elem
        else:
            yield elem


def _flatten_fast(a: _Iin) -> _Iout:
    """generator of flattened n-deep iterable a (types are not checked).

    WARNING: Will have infinite recursion if any element is str object
    """
    for elem in a:
        try:
            yield from _flatten_fast(elem)
        except TypeError:
            yield elem
flatten.fast = _flatten_fast


def grouper_with_prev(iterable: _Iin[_T], n: int, include_first: bool = False) \
        -> _Iout[_t.Tuple[_T, ...]]:
    """
    Returns n size chuncks of iterable with the previous n-1 elements

        grouper_with_prev('ABCDE', 3) -> ABC, BCD, CDE
    If include_first is True, will return
        grouper_with_prev('ABCDE', 3, True) -> A, AB, ABC, BCD, CDE
    """
    d = _collections.deque(maxlen=n)

    for elem in iterable:
        d.append(elem)
        if len(d) == n or include_first:
            yield tuple(d)


def repeat_each(iterable: _Iin[_T], n: int) -> _Iout[_T]:
    """ Repeate each element of iterable n times

        repeat_each('ABC', 3) --> AAABBBCCC
    """
    return flatten1deep(repeat(i, n) for i in iterable)


def argmap(func: _t.Callable[..., _V], iterable: _Iin[_U], *args: _t.Any) \
        -> _Iout[_t.Tuple[_U, _V]]:
    """Yield each element of iterable and func applied to that element as a tuple

        argmap(bool, range(3)) -> (0, False), (1, True), (2, True)
    """
    itr1, itr2 = tee(iterable, 2)
    return zip(itr1, map(func, itr2, *args))


# itertools recipes (edited)

def nth(iterable: _Iin[_T], n: int, default: _U = _NO_DEFAULT) \
        -> _t.Union[_T, _U]:
    """Returns the nth item or a default value

    If no default set, raises an error
    """
    try:
        return next(islice(iterable, n, None))
    except StopIteration:
        if default is _NO_DEFAULT:
            raise IndexError('Index out of range')
        return default


def flatten1deep(list_of_lists: _Iin[_Iin[_T]]) -> _Iout[_T]:
    "Flatten one level of nesting"
    return chain.from_iterable(list_of_lists)
flatten.one_deep = flatten1deep


# itertools recpes (as given)

def take(n: int, iterable: _Iin[_T]) -> _t.List[_T]:
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def tabulate(function: _t.Callable[[int], _T], start: int = 0) -> _Iout[_T]:
    "Return function(0), function(1), ..."
    return map(function, count(start))


def tail(n: int, iterable: _Iin[_T]) -> _Iout[_T]:
    """Return an iterator over the last n items
    # tail(3, 'ABCDEFG') --> E F G
    """
    return iter(_collections.deque(iterable, maxlen=n))


def consume(iterator: _Iin, n: int) -> None:
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        _collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)



def all_equal(iterable: _Iin) -> bool:
    "Returns True if all the elements are equal to each other"
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def quantify(iterable: _Iin[_T], pred: _t.Callable[[_T], bool] = bool) -> int:
    "Count how many times the predicate is true"
    return sum(map(pred, iterable))


def pad(iterable: _Iin[_T], obj: _U = None) -> _Iout[_t.Union[_T, _U]]:
    """Returns the sequence elements and then returns obj indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return chain(iterable, repeat(obj))


def ncycles(iterable: _Iin[_T], n: int) -> _Iout[_T]:
    "Returns the sequence elements n times"
    return chain.from_iterable(repeat(tuple(iterable), n))


def dotproduct(vec1, vec2):
    return sum(map(_operator.mul, vec1, vec2))


def repeatfunc(func: _t.Callable[..., _T], times: int = None, *args: _t.Any) \
        -> _Iout[_T]:
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))


def pairwise(iterable: _Iin[_T]) -> _Iout[_t.Tuple[_T, _T]]:
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def grouper(iterable: _Iin[_T], n: int, fillvalue: _T = None) \
        -> _Iout[_t.Tuple[_T, ...]]:
    """Collect data into fixed-length chunks or blocks
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    """
    args = [iter(iterable)]*n
    return zip_longest(*args, fillvalue=fillvalue)


def roundrobin(*iterables: _Iin[_T]) -> _Iout[_T]:
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))


def partition(pred: _t.Callable[[_T], bool], iterable: _Iin[_T])\
        -> _t.Tuple[_Iout[_T], _Iout[_T]]:
    """Use a predicate to partition entries into false entries and true entries
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    """
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)


def powerset(iterable: _Iin[_T]) -> _Iout[_Iout[_T]]:
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def unique_everseen(iterable: _Iin[_T], key: _t.Callable[[_T], _t.Any] = None)\
        -> _Iout[_T]:
    """List unique elements, preserving order. Remember all elements ever seen.
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def unique_justseen(iterable: _Iin[_T], key: _t.Callable[[_T], _t.Any] = None)\
        -> _Iout[_T]:
    """List unique elements, preserving order. Remember only the element just seen.
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBCcAD', str.lower) --> A B C A D
    """
    # had to add `operator.`
    return map(next, map(_operator.itemgetter(1), groupby(iterable, key)))


def iter_except(func: _t.Callable[[], _T], exception: Exception,
                first: _t.Callable[[], _T] = None) -> _Iout[_T]:
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like builtins.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    ``first`` - For database APIs needing an initial cast to db.first()

    Examples:
        iter_except(functools.partial(heappop, h), IndexError)   # priority queue iterator
        iter_except(d.popitem, KeyError)                         # non-blocking dict iterator
        iter_except(d.popleft, IndexError)                       # non-blocking deque iterator
        iter_except(q.get_nowait, Queue.Empty)                   # loop over a producer Queue
        iter_except(s.pop, KeyError)                             # non-blocking set iterator

    """
    try:
        if first is not None:
            yield first()
        while True:
            yield func()
    except exception:
        pass


def first_true(iterable: _Iin[_T], default: _T = False,
               pred: _t.Callable[[_T], bool] = None) -> _T:
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    """
    return next(filter(pred, iterable), default)


def random_product(*args: _T, repeat: int = 1) -> _t.Tuple[_T, ...]:
    "Random selection from itertools.product(*args, **kwds)"
    pools = [tuple(pool) for pool in args]*repeat
    return tuple(_random.choice(pool) for pool in pools)


def random_permutation(iterable: _Iin[_T], r: int = None) -> _t.Tuple[_T, ...]:
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(_random.sample(pool, r))


def random_combination(iterable: _Iin[_T], r: int = None) -> _t.Tuple[_T, ...]:
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(_random.sample(range(n), r))
    return tuple(pool[i] for i in indices)


def random_combination_with_replacement(iterable: _Iin[_T], r: int = None) \
        -> _t.Tuple[_T, ...]:
    "Random selection from itertools.combinations_with_replacement(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(_random.randrange(n) for i in range(r))
    return tuple(pool[i] for i in indices)
