# Class related scripts
from __future__ import print_function as _, division as _


def name(inst, this=False):
    if this:
        return inst.__name__
    return inst.__class__.__name__


def class_repr(inst, *attrs, codelike=True, sep=', ', colon=False):
    """
    For simple class repr formatting. If codelike then gives output of:
        cls_name(attr1=value1, attr2=value2)
    If not then:
        <cls_name attr1=value1 attr2=value2>

    Use as follows:

    >>> import cls
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
    return repr_str.format(inst.__class__.__name__ + colon_s, attrs_repr)


def class_equal(inst, other, *attrs, raise_miss_attr=True, force_same_cls=False):
    """
    Checks if all the attrs given are equal for both inst and other.
    If `raise_miss_attr` an exception is raised if `other` does not have any of
    the attrs else the function just returns False.
    If `force_same_cls` then if one of `inst` and `other`s classes is not a
    subclass of the other, then an exception is raised.
    """
    if force_same_cls:
        if not (isinstance(inst, other.__class__) or isinstance(other, inst.__class__)):
            raise TypeError("Types {!r} and {!r} cannot be compared"
                            .format(inst.__class__.__name__, other.__class__.__name__))

    if len(attrs) == 1 and not isinstance(attrs[0], str):
        attrs = attrs[0]

    for attr in attrs:
        if not hasattr(other, attr):
            if not raise_miss_attr:
                return False
            raise ValueError("{} does not have attribute {!r}".format(other, attr))

    return all(getattr(inst, attr) == getattr(other, attr) for attr in attrs)


try:
    import numpy as _np
except ImportError:
    pass
else:
    class Array(_np.ndarray):
        def __new__(cls, array):
            return _np.asarray(array).view(cls)


    class Coord(Array):
        coords = {'x': 0, 'y': 1, 'z': 2}

        def __init__(self, array):
            assert isinstance(self.coords, dict) and self.coords, repr(self.coords)
            if self.shape != (len(self.coords),):
                msg = "{}.shape should be {}, not {}"
                raise ValueError(msg.format(name(self), (len(self.coords),), self.shape))

        def __getattr__(self, attr):
            if attr in self.coords:
                return self[self.coords[attr]]
            return super().__getattr__(attr)

        def __setattr__(self, attr, value):
            if attr in self.coords:
                self[self.coords[attr]] = value
            else:
                super().__setattr__(attr, value)
