#!/usr/bin/env python3
# coding:utf-8
from .error import ParsecError
from . import Parsec, oneOf
from io import StringIO
from . import skip, skip1


def string(s, case_sensitive=True):
    @Parsec
    def call(st):
        buffer = StringIO()
        segment = s if case_sensitive else s.lower()
        for chr in segment:
            c = st.next()
            if (chr != c and case_sensitive) or (not case_sensitive and chr != c.lower()):
                raise ParsecError(st, "Expect '{0}' but got {1}".format(s, c))
            else:
                buffer.write(c)
        else:
            return buffer.getvalue()

    return call


def textIn(t, case_sensitive=True):
    check = set(x.lower for x in t) if case_sensitive else t
    return oneOf(check)


@Parsec
def space(state):
    c = state.next()
    if c.isspace():
        return c
    raise ParsecError(state, "Expect a space but got {0}".format(c))


@Parsec
def noSpace(state):
    c = state.next()
    if c.isspace():
        raise ParsecError(state, "Expect any no space but got {0}".format(c))
    return c


@Parsec
def digit(state):
    c = state.next()
    if c.isdigit():
        return c
    else:
        raise ParsecError(state, "Expect a space but got {0}".format(c))


@Parsec
def skipSpaces(state):
    return skip(space)(state)


@Parsec
def skip1Spaces(state):
    return skip1(space)(state)


def mkString(txt):
    @Parsec
    def call(state):
        return "".join(txt)

    return call


def join():
    def binder(txt):
        @Parsec
        def call(state):
            return "".join(txt)

        return call

    return binder
