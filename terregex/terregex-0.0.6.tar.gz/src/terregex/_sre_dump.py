"""Convert the parse tree created by sre_parse.parse back into a string

This library is borrowed from http://www.dalkescientific.com/Python/sre_dump.html
There are some modifications for python3 support and bug fixes.

Originally written in 2003 by Andrew Dalke <dalke@dalkescientific.com>,
Updated in 2021 by Mikihito Matsuura <me@mikit.dev>

SPDX-License-Identifier: Apache-2.0
"""
import sre_parse
from sre_constants import *
import string

__all__ = ["dump", "dump_and_offsets", "pprint", "pformat"]

_categories = {
    CATEGORY_DIGIT: "\\d",
    CATEGORY_NOT_DIGIT: "\\D",
    CATEGORY_WORD: "\\w",
    CATEGORY_NOT_WORD: "\\W",
    CATEGORY_SPACE: "\\s",
    CATEGORY_NOT_SPACE: "\\S",
    # are there more?
    }

_at_symbols = {
    AT_BEGINNING: "^",
    AT_END: "$",
    AT_BEGINNING_STRING: r"\A",
    AT_END_STRING: r"\Z",
    AT_BOUNDARY: r"\b",
    AT_NON_BOUNDARY: r"\B",
    }

# [AB\]C] to match any of A, B, ] and C
# [AB\-D] matches any one of A, B, -, and D
def _escape_in_char(i):
    c = chr(i)
    if c in ']-':
        return '\\' + c
    return c

# [--A] means from "-" to "A"
def _escape_in_range(i):
    c = chr(i)
    if c in ']':
        return '\\' + c
    return c

def _dump_in(av):
    # XXX is this proper escaping?
    words = []
    emit = words.append
    first_flg = 1
    for x in av:
        if x[0] == NEGATE:
            if first_flg == 1:
                emit("^")
            else:
                raise AssertionError("negate not first?")
        elif x[0] == LITERAL:
            if first_flg and x[1] == ord("^"):
                emit("\\^")
            else:
                emit(_escape_in_char(x[1]))
        elif x[0] == RANGE:
            emit(_escape_in_range(x[1][0]) + "-" +
                 _escape_in_range(x[1][1]))
        elif x[0] == CATEGORY:
            emit(_categories[x[1]])
        else:
            raise NotImplementedError(x[0])
        first_flg = 0
    return "[" + "".join(words) + "]"
        

# I could use sre.escape but I don't like that it
# escapes "<", ">", and some other characters
_escape_table = {"\000": "\\000"}  # special-case 0
for i in range(256):
    _escape_table[i] = "\\" + chr(i)
for c in string.ascii_letters + string.digits + "<>: /":
    _escape_table[ord(c)] = c
del c, i


def _dump(pattern, groupdict):
    pos = [0]
    offsets = []
    words = []
    def emit(s):
        words.append(s)
        pos[0] = pos[0] + len(s)

    def include(suboffsets):
        x = pos[0]
        for e, i, j in suboffsets:
            offsets.append( (e, i+x, j+x) )

    start = pos[0]
    
    for term in pattern:
        op, av = term
        
        if op == LITERAL:
            emit(_escape_table[av])
        elif op == NOT_LITERAL:
            emit("[^%s]" % chr(av))
        elif op == IN:
            emit(_dump_in(av))
        elif op in (MAX_REPEAT, MIN_REPEAT):
            i, j, subtree = av
            s, suboffsets = _dump(subtree, groupdict)
            include(suboffsets)
            emit(s)
            if j == MAXREPEAT:
                if i == 0:
                    emit("*")
                elif i == 1:
                    emit("+")
                else:
                    emit("{%d,}" % i)
            else:
                if i == 0 and j == 1:
                    emit("?")
                elif i == j:
                    emit("{%d}" % i)
                else:
                    emit("{%d,%d}" % (i, j))
            if op == MIN_REPEAT:
                emit("?")
        elif op == SUBPATTERN:
            groupnum, _, _, subtree = av
            s, suboffsets = _dump(subtree, groupdict)
            if groupnum in groupdict:
                name = groupdict[groupnum]
                emit("(?P<%s>" % (name,))  #")  emacs cruft
            elif groupnum is None:
                emit("(?:")  #")  emacs cruft
            else:
                emit("(")
            include(suboffsets) 
            emit("%s)" % s)
            
        elif op == ASSERT:
            dir, subtree = av
            dir = {1:"", -1:"<"}[dir]
            s, suboffsets = _dump(subtree, groupdict)
            emit("(?%s=" % dir)  #")
            include(suboffsets)
            emit("%s)" % s)
        elif op == ASSERT_NOT:
            dir, subtree = av
            dir = {1:"", -1:"<"}[dir]
            s, suboffsets = _dump(subtree, groupdict)
            emit("(?%s!" % dir)
            include(suboffsets)
            emit("%s)" % s)
                       
        elif op == BRANCH:
            # av[0] is always None
            emit("(?:")
            for x in av[1][:-1]:
                s, suboffsets = _dump(x, groupdict)
                include(suboffsets)
                emit(s)
                emit("|")
            s, suboffsets = _dump(av[1][-1], groupdict)
            include(suboffsets)
            emit(s)
            emit(")")
        elif op == ANY:
            emit(".")
        elif op == AT:
            emit(_at_symbols[av])
        elif op == GROUPREF:
            if av in groupdict:
                emit("(?P=%s)" % groupdict[av])
            else:
                emit("\\%d" % av)
        else:
            raise NotImplementedError(op)

        # These are added in creation order, inner before outer.
        offsets.append( (term, start, pos[0]) )
        start = pos[0]

    return "".join(words), offsets

class NoGroupNames:
    def __getitem__(self, i):
        assert i < 100,  "that would be silly"
        return "group_%d" % i
    def __contains__(self, i):
        return 0

def dump_and_offsets(tree):
    # You really should pass in a SubTree, but I'll let you
    # get away with a couple common variations
    if isinstance(tree, list):
        # used when building a list by hand; ignore group names
        d = NoGroupNames()
    elif isinstance(tree, tuple) and len(tree) == 2:
        # an (op, av) 2-pl element in the tree
        tree = [tree]
        d = NoGroupNames()
    else:
        if isinstance(tree, str):
            # pass in a string and I'll convert it for you
            tree = sre_parse.parse(tree)
        
        # need the reverse mapping to get the names
        d = {}
        for k, v in list(tree.state.groupdict.items()):
            d[v] = k

    return _dump(tree, d)

def dump(tree):
    return dump_and_offsets(tree)[0]


def pprint(tree, stream=None):
    s, offsets = dump_and_offsets(tree)
    print(s, file=stream)
    for expr, i, j in offsets:
        print(" "*i + "-"*(j-i) + " " *(len(s)-j+1) + s[i:j], file=stream)

def pformat(tree):
    import io as StringIO
    sio = StringIO.StringIO()
    pprint(tree, sio)
    return sio.getvalue()

def _do_test(input, expected = None):
    if expected is None:
        expected = input
    tree = sre_parse.parse(input)
    try:
        output, offsets = dump_and_offsets(tree)
    except (NotImplementedError, KeyError) as msg:
        import traceback
        print("   ===== Cannot compute =====")
        print("Input was", repr(input))
        print("Exception mesage:", msg)
        traceback.print_exc()
        return False
        
    if output != expected:
        print("   ===== Different =====")
        print("Input was", repr(input))
        print("Expected:", repr(expected))
        print("Output is", repr(output))
        print(tree)
        return False

    # Check the offsets are generated correctly
    for expr, i, j in offsets:
        a = output[i:j]
        # Use the SubPattern to get the pattern names correct.
        b = dump(sre_parse.SubPattern(tree.pattern, [expr]))
        if a != b:
            print("   ===== bad substrings =====")
            print("Input was", repr(input))
            print("Excepcted", repr(a))
            print("Redump is", repr(b))
            return False
    return True
                       

def test():
    # Some of these taken from 'perlre', some from AMK's docs
    # and many I just made up
    test_values = r"""
A AB ABC [^A] [^ABC] A+ A* A? AA* A{2} A{2,4} A{9,12} A{2,} A{,9}
[\d] [^\d] [A-Za-z0-9_]+ . .*
AB|CD AB|CD|EF|GH (AB|CD)*
(a??) a*? a{3,}? ab{4,7}?
(?P<test>ABC*) (?P<a>x)|(?P<b>y)
[b:]+ (b)|(:+) a|(b)
(?:Q)(Q) ^A*$
(?:(?P<a1>a)|(?P<b2>b))(?P<c3>c)?
(?=AB)C (?!CD)DC AB(?<=CD) AB(?<!CD)
[ABC]+(?=D).*$ <.*?>
(?P<name>[a-zA-Z]+)(?P=name)
[AB\]C] [--A] [ABC\-D] [\^ABC]
""".split()
    passed = True
    for input in test_values:
        passed = passed and _do_test(input)

    # sre_parse does some optimization so I
    # have to allow variant forms
    special_values = r"""
      \d [\d]
      \d+ [\d]+
      \w [\w]
      \W [\W]
      \s [\s]
      \S [\S]
      A|B [AB]
      A|B|C|D [ABCD]
      (?:a|b|c) (?:[abc])
      .*\..*$ .*\..*$
      .*\.([^b]..|.[^a].|..[^t])$ .*\.([^b]..|.[^a].|..[^t])$
      .*\.([^b].?.?|.[^a]?.?|..?[^t]?) .*\.([^b].?.?|.[^a]?.?|..?[^t]?)
      .*\.(?!bat$).*$ .*\.(?!bat$).*$
      .*\.(?!bat$|exe$) .*\.(?!bat$|exe$)
      """.split("\n")[1:-1]
    for x in special_values:
        if not x.strip():
            continue
        input, expected = x.split()
            
        
        passed = passed and _do_test(input, expected)

    # issues with spaces
    others = [
        r"^([^ ]*) *([^ ]*)",
        r"(.)\1",
        r"/Time: (..):(..):(..)/",
        r"\Aabc",
        r"abc\b",
        r"abc\Bqwe",
        r"qwerty\Z",
        (r"\n", "\\\n"),
        ]
    for x in others:
        if isinstance(x, str):
            passed = passed and _do_test(x)
        else:
            input, output = x
            passed = passed and _do_test(input, output)


    s = pformat("(AB*|C?D){2,3}((?P<name>\d+)(?:a|b))+")

    if passed:
        print("All tests passed.")
    else:
        print("Test failure.")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        test()
    else:
        in_s = sys.argv[1]
        x = sre_parse.parse(in_s)
        out_s = dump(x)
        print("Input :", repr(in_s))
        print("Output:", repr(out_s))

