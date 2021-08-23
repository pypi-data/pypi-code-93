""" A module where types, interfaces, and classes are defined """
from abc import ABCMeta, abstractmethod
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")

RCode = str


class Tor(metaclass=ABCMeta):
    """
    Support conversion from python code to R code.
    """
    @abstractmethod
    def tor(self) -> RCode:
        pass


class Join(Tor):
    """
    Support combining two R codes.
    """
    @abstractmethod
    def __add__(self, other: "Join") -> "Join":
        pass


class Show(metaclass=ABCMeta):
    """
    Support graphic display with `ggplot2`.
    """
    @abstractmethod
    def show(self):
        pass
