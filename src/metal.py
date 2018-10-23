#! /usr/bin/env python3
"""
it -- metal.py

Functions for working "down to the metal" of the computer -- i.e. low level

author  - fmitchell
created - 2018-Oct-08
"""

import struct as _struct
import typing as _t


class BinaryFloat:

    sign: _t.List[int]
    exponent: _t.List[int]
    fraction: _t.List[int]

    def _from_float(self, num: float, sign_length: int, exponent_length: int,
                    fraction_length: int) -> None:

        bytes_ = _struct.pack('!f', num)
        bits = ''.join(f'{byte:0>8b}' for byte in bytes_)
        assert len(bits) == sign_length + exponent_length + fraction_length, len(bits)

        self.sign = bits[0:sign_length]
        self.exponent = [int(b) for b in bits[sign_length : sign_length+fraction_length]]
        self.fraction = [int(b) for b in bits[sign_length+fraction_length : ]]


    def to_value(self) -> float:
        sgn  = 2 ** self.sign[0] if self.is_signed() else 1
        exp = sum(bit * 2**i for i, bit in enumerate(reversed(self.exponent)))
        frac = sum(bit * 2**-i for i, bit in enumerate(self.fraction))
        return sgn * exp * frac

    def is_signed(self) -> bool:
        return bool(self.sign)

    @staticmethod
    def bits2str(bits: _t.List[int]) -> str:
        assert all(bit in {0, 1} for bit in bits)
        return ''.join(map(str, bits)) if bits else '[]'

    @property
    def full(self):
        return list(self.sign + self.exponent + self.fraction)

    def __repr__(self):
        cls_name = self.__class__.__name__
        sgn = self.bits2str(self.sign)
        exp = self.bits2str(self.exponent)
        frac = self.bits2str(self.fraction)
        return f'<{cls_name}: sign={sgn} exponent={exp} fraction={frac}>'

    def __str__(self):
        return self.bits2str(self.full)


class SingleFloat(BinaryFloat):

    sign_length = 1
    exponent_length = 8
    fraction_length = 23

    def __init__(self, num: float):
        self._from_float(num, self.sign_length, self.exponent_length,
                         self.fraction_length)


class DoubleFloat(BinaryFloat):

    sign_length = 1
    exponent_length = 11
    fraction_length = 52

    def __init__(self, num: float):
        self._from_float(num, self.sign_length, self.exponent_length,
                         self.fraction_length)
