# Class related scripts

import abc as _abc
import typing as _t

def name(inst: _t.Any) -> str:
    """
    Return the class name of an instance of that class

    >>> name(1) == 'int'
    >>> name("hello") == 'str'
    >>> name(object) == 'type'
    """
    try:
        return inst.__class__.__qualname__
    except AttributeError:
        return inst.__class__.__name__


def class_repr(inst: _t.Any, *attrs: str, codelike: bool = True,
               sep: str = ', ', colon: bool = False) -> str:
    """ Format an instance of a class using attributes `attrs`

    For simple class repr formatting. If codelike then gives output of:
        cls_name(attr1=value1, attr2=value2)
    If not then:
        <cls_name attr1=value1 attr2=value2>

    Use as follows:

    >>> from src import cls
    >>> class Example:
    ...     def __init__(self, *attrs):
    ...         self.att1, self.attr2 = attrs
    ...     def __repr__(self):
    ...         return classtools.class_repr(self, *attrs, codelike=False)
    ...     def __str__(self): # example of codelike=False and non-default 'sep'
    ...         return classtools.class_repr(self, *attrs, codelike=True,
                                             sep=' ', colon=True)

    >>> Example(1,'hi')
    'Example(attr1=1, attr2="hi")'
    >>> print(Example(1,'hi'))
    <Example: attr1=1 attr2="hi">
    """
    attrs_repr = sep.join('{0}={1!r}'.format(attr, getattr(inst, attr))
                          for attr in attrs)
    repr_str = '{}({})' if codelike else '<{} {}>'
    colon_s = ':' if (colon and not codelike) else ''
    return repr_str.format(name(inst) + colon_s, attrs_repr)


def class_equal(inst: _t.Any, other: _t.Any, *attrs: str,
                raise_miss_attr: bool = True, force_same_cls: bool = True) \
        -> bool:
    """ Check that two instances are equal dependent on attrs

    Checks if all the attrs given are equal for both inst and other.
    If `raise_miss_attr` an exception is raised if `other` does not have any of
    the attrs else the function just returns False.
    If `force_same_cls` then if one of `inst` and `other`s classes is not a
    subclass of the other, then an exception is raised.
    """
    if force_same_cls:
        if not (isinstance(inst, other.__class__)
                or isinstance(other, inst.__class__)):
            return NotImplemented

    # in case we are passed an iterable of strings
    if len(attrs) == 1 and not isinstance(attrs[0], str):
        attrs = attrs[0]

    try:
        return all(getattr(inst, attr) == getattr(other, attr) for attr in attrs)
    except AttributeError:
        if not raise_miss_attr:
            return False
        raise


class GetAttrBase(_abc.ABC):
    """
    Base class which can be used to produce a good error message when attribute
    does not exist
    """

    def _raise_no_attribute(self, attr: str) -> None:
        msg = "'{}' object has not attribute '{}'"
        raise AttributeError(msg.format(name(self), attr))

    def __getattr__(self, attr: str) -> None:
        self._raise_no_attribute(attr)
