import sys
from antlr4 import *
from .AFMLexer import AFMLexer
from .AFMParser import AFMParser


def get_tree(argv):
    input_stream = FileStream(argv)
    lexer = AFMLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = AFMParser(stream)
    tree = parser.feature_model()
    return tree


get_tree("test.afm")
