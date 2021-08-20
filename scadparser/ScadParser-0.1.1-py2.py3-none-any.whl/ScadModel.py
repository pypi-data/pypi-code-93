from __future__ import annotations

import os
import tatsu
from tatsu.ast import AST

symbol_table = {}

def store(id, val):
    symbol_table[id] = val

def lookup(id):
    if not id in symbol_table:
        return id
    else:
        return symbol_table[id]


class ScadSemantics(object):

    def include(self, ast):
        print("CWD" + str(os.getcwd()))
        grammar = open('grammar/scad.tatsu').read()
        incfile = os.path.join('scad', ast.file)
        prog = open(incfile).read()
        parser = tatsu.compile(grammar)
        ast = parser.parse(prog,
            trace=False, colorize=True, semantics=ScadSemantics())
        return ast

    def int(self, ast):
        return int(ast)

    def fract(self, ast):
        return float(ast)

    def ident(self, ast):
        return lookup(ast)

    def declaration(self, ast):
        store(ast.id, ast.value)
        return ast

    def addition(self, ast):
        return ast.left + ast.right

    def subtraction(self, ast):
        return ast.left - ast.right

    def multiplication(self, ast):
        return ast.left * ast.right

    def division(self, ast):
        return ast.left / ast.right


