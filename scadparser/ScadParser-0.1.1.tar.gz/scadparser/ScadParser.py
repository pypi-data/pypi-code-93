import tatsu
from pprint import pprint
from ScadModel import ScadSemantics


class ScadParser(object):

    def __init__(self):
        self.grammar = open('grammar/scad.tatsu').read()
        self.parser = tatsu.compile(self.grammar, asmodel=False)

    def parse(self, code):
        ast = self.parser.parse(code, semantics = ScadSemantics())
        print('# AST')
        pprint(ast, width=20, indent=4)
        print()

if __name__ == '__main__':
    scp = ScadParser()
    test = open('scad/model.scad').read()
    scp.parse(test)


