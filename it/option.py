#! /usr/bin/env python3
"""
it -- option.py

author  - fmitchell
created - 2018-Oct-23
"""

import dataclasses as dc
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable, Any

from .helpers import singleton

__all__ = ['NilError', 'Option', 'Some', 'Nil', 'Result', 'Ok', 'Err']

T = TypeVar('T', covariant=True)
E = TypeVar('E', covariant=True, bound=Exception)
R = TypeVar('R')

class NilError(Exception):
    pass

### Option[T] -> Some[T] or Nil

class Option(ABC, Generic[T]):

    @abstractmethod
    def issome(self) -> bool:
        pass

    def isnil(self) -> bool:
        return not self.issome()

    @abstractmethod
    def expect(self) -> T:
        pass

    @abstractmethod
    def map(self, func: Callable[[T], R]) -> 'Option[R]':
        pass

    @abstractmethod
    def get(self, default: T) -> T:
        pass

    @abstractmethod
    def __and__(self, other: 'Option[T]') -> 'Option[T]':
        pass

    @abstractmethod
    def __or__(self, other: 'Option[T]') -> 'Option[T]':
        pass


@dc.dataclass(frozen=True)
class Some(Option[T]):

    value: T

    def expect(self):
        return self.value

    def issome(self):
        return True

    def map(self, func):
        return Some(func(self.value))

    def get(self, default):
        return self.value

    def __and__(self, other):
        return other

    def __or__(self, other):
        return self

@singleton
class Nil(Option[Any]):

    def __repr__(self):
        return 'Nil'

    def issome(self):
        return False

    def expect(self):
        raise NilError()

    def map(self, func):
        return self

    def get(self, default):
        return default

    def __and__(self, other):
        return self

    def __or__(self, other):
        return other
Nil: Nil  # singleton


### Result[T, E] -> Ok[T] or Err[E]

class Result(ABC, Generic[T, E]):

    @abstractmethod
    def isok(self):
        pass

    def iserr(self):
        return not self.isok()

    @abstractmethod
    def expect(self) -> T:
        pass

    @abstractmethod
    def map(self, func: Callable[[T], R]) -> 'Result[R]':
        pass

    @abstractmethod
    def get(self, default: T) -> T:
        pass

    @abstractmethod
    def __and__(self, other: 'Option[T]') -> 'Result[T]':
        pass

    @abstractmethod
    def __or__(self, other: 'Option[T]') -> 'Result[T]':
        pass


@dc.dataclass(frozen=True)
class Ok(Result[E, Any]):

    value: T

    def isok(self):
        return True

    def expect(self):
        return self.value

    def map(self, func):
        return Ok(func(self.value))

    def get(self, default):
        return self.value

    def __and__(self, other):
        return other

    def __or__(self, other):
        return self


@dc.dataclass(frozen=True)
class Err(Result[Any, E]):

    error: E

    def isok(self):
        return False

    def expect(self):
        raise self.error

    def map(self, func):
        return self

    def get(self, default):
        return default

    def __and__(self, other):
        return self

    def __or__(self, other):
        return other
