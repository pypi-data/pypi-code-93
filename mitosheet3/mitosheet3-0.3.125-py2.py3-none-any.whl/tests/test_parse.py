#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

import pytest

from mitosheet.errors import EditError
from mitosheet.parser import parse_formula, safe_replace, safe_contains

CONSTANT_TEST_CASES = [
    (
        '=100',
        'B',
        'df[\'B\'] = 100',
        set([]),
        set([])
    ),
    (
        '=True',
        'B',
        'df[\'B\'] = True',
        set([]),
        set([])
    ),
    (
        '=\'StringSingleQuotes\'',
        'B',
        'df[\'B\'] = \'StringSingleQuotes\'',
        set([]),
        set([])
    ),
    (
        '=\"StringDoubleQuotes\"',
        'B',
        'df[\'B\'] = \"StringDoubleQuotes\"',
        set([]),
        set([])
    ), 
    (
        '=\"String Double Quotes\"',
        'B',
        'df[\'B\'] = \"String Double Quotes\"',
        set([]),
        set([])
    ), 
    (
        '=FUNC(\"String Double Quotes\")',
        'B',
        'df[\'B\'] = FUNC(\"String Double Quotes\")',
        set(['FUNC']),
        set([])
    ),
    (
        '=FUNC(\"DIFF_FUNC(A)\")',
        'B',
        'df[\'B\'] = FUNC(\"DIFF_FUNC(A)\")',
        set(['FUNC']),
        set([])
    ),
    (
        '=\"String One FUNC(A)\" + \"STRING TWO FUNC(A)\"',
        'B',
        'df[\'B\'] = \"String One FUNC(A)\" + \"STRING TWO FUNC(A)\"',
        set([]),
        set([])
    ),
    (
        '=\'String One FUNC(A)\' + \'STRING TWO FUNC(A)\'',
        'B',
        'df[\'B\'] = \'String One FUNC(A)\' + \'STRING TWO FUNC(A)\'',
        set([]),
        set([])
    ),
    (
        '=FUNC1(\'String One FUNC(A)\') + FUNC2(\'STRING TWO FUNC(A)\')',
        'B',
        'df[\'B\'] = FUNC1(\'String One FUNC(A)\') + FUNC2(\'STRING TWO FUNC(A)\')',
        set(['FUNC1', 'FUNC2']),
        set([])
    )
]

# Tests cases to ensure operators are parsed correctly
OPERATOR_TEST_CASES = [
    # Simple add operation
    (
        '=A + B',
        'C',
        'df[\'C\'] = df[\'A\'] + df[\'B\']',
        set(),
        set(['A', 'B'])
    ),
    # Simple subtract operation
    (
        '=A - B',
        'C',
        'df[\'C\'] = df[\'A\'] - df[\'B\']',
        set(),
        set(['A', 'B'])
    ),
    # Simple multiply operation
    (
        '=A * B',
        'C',
        'df[\'C\'] = df[\'A\'] * df[\'B\']',
        set(),
        set(['A', 'B'])
    ),
    # Simple divide operation
    (
        '=A / B',
        'C',
        'df[\'C\'] = df[\'A\'] / df[\'B\']',
        set(),
        set(['A', 'B'])
    ),
    # Handles multi-char columns
    (
        '=AAA + BBB + CCC + DDD',
        'E',
        'df[\'E\'] = df[\'AAA\'] + df[\'BBB\'] + df[\'CCC\'] + df[\'DDD\']',
        set(),
        set(['AAA', 'BBB', 'CCC', 'DDD'])
    ),
    # Maintains parens and constants
    (
        '=(A + B) / C + A * 100',
        'D',
        'df[\'D\'] = (df[\'A\'] + df[\'B\']) / df[\'C\'] + df[\'A\'] * 100',
        set(),
        set(['A', 'B', 'C'])
    ),
    # Operator in functions
    (
        '=FUNC(A + B / C + A * 100)',
        'D',
        'df[\'D\'] = FUNC(df[\'A\'] + df[\'B\'] / df[\'C\'] + df[\'A\'] * 100)',
        set(['FUNC']),
        set(['A', 'B', 'C'])
    )
]

# Tests proper function parsing
FUNCTION_TEST_CASES = [
    # Simple, singular function call
    (
        '=FUNC(A)',
        'B',
        'df[\'B\'] = FUNC(df[\'A\'])',
        set(['FUNC']),
        set(['A'])
    ),
    # Simple, singular function call that has the name of a column
    (
        '=C(A)',
        'B',
        'df[\'B\'] = C(df[\'A\'])',
        set(['C']),
        set(['A'])
    ),
    # Nested functions with different names
    (
        '=FUNCA(FUNCB(FUNCC(FUNCD(FUNCE(FUNCF(FUNCG(FUNCH(A))))))))',
        'B',
        'df[\'B\'] = FUNCA(FUNCB(FUNCC(FUNCD(FUNCE(FUNCF(FUNCG(FUNCH(df[\'A\']))))))))',
        set(['FUNCA', 'FUNCB', 'FUNCC', 'FUNCD', 'FUNCE', 'FUNCF', 'FUNCG', 'FUNCH']),
        set(['A'])
    ),
    # Nested functions with basic operators
    (
        '=RIGHT(A, LEN(B) - 10)',
        'C',
        'df[\'C\'] = RIGHT(df[\'A\'], LEN(df[\'B\']) - 10)',
        set(['RIGHT', 'LEN']),
        set(['A', 'B'])
    ),
    # More nested functions with columns
    (
        '=FUNC(A, FUNC(B, FUNC(C)))',
        'D',
        'df[\'D\'] = FUNC(df[\'A\'], FUNC(df[\'B\'], FUNC(df[\'C\'])))',
        set(['FUNC']),
        set(['A', 'B', 'C'])
    ),
    # Lots of column references
    (
        '=FUNC(A, B, C, D, E, F, G, H, I)',
        'J',
        'df[\'J\'] = FUNC(df[\'A\'], df[\'B\'], df[\'C\'], df[\'D\'], df[\'E\'], df[\'F\'], df[\'G\'], df[\'H\'], df[\'I\'])',
        set(['FUNC']),
        set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])
    ),
    # Lots of column references to columns with numbers
    (
        '=FUNC(column1, column2)',
        'J',
        'df[\'J\'] = FUNC(df[\'column1\'], df[\'column2\'])',
        set(['FUNC']),
        set(['column1', 'column2'])
    ),
    # Test references to columns with underscores
    (
        '=FUNC(column_1, column_2)',
        'J',
        'df[\'J\'] = FUNC(df[\'column_1\'], df[\'column_2\'])',
        set(['FUNC']),
        set(['column_1', 'column_2'])
    ),
    # Test references to columns that are lookups
    (
        '=FUNC(LOOKUP, XLOOKUP, VLOOKUP, HLOOKUP)',
        'J',
        'df[\'J\'] = FUNC(df[\'LOOKUP\'], df[\'XLOOKUP\'], df[\'VLOOKUP\'], df[\'HLOOKUP\'])',
        set(['FUNC']),
        set(['LOOKUP', 'XLOOKUP', 'VLOOKUP', 'HLOOKUP'])
    ) 
]


"""
PARSE_TESTS contains a variety of tests that make sure
formula parsing is working properly; it is passed as 
a parameter into the test_parse test below.

Order of params is: formula, address, python_code, functions, columns

See documentation here: https://docs.pytest.org/en/latest/parametrize.html#parametrize-basics
"""
PARSE_TESTS = CONSTANT_TEST_CASES + OPERATOR_TEST_CASES + FUNCTION_TEST_CASES
@pytest.mark.parametrize("formula,address,python_code,functions,columns", PARSE_TESTS)
def test_parse(formula, address, python_code, functions, columns):
    assert parse_formula(formula, address) == \
        (
            python_code, 
            functions, 
            columns
        )


PARSE_TEST_ERRORS = [
    ('=LOOKUP(100, A)', 'B', 'invalid_formula_error', 'LOOKUP'),
    ('=VLOOKUP(100, A)', 'B', 'invalid_formula_error', 'VLOOKUP'),
    ('=HLOOKUP(100, A)', 'B', 'invalid_formula_error', 'HLOOKUP'),
    ('=XLOOKUP(100, A)', 'B', 'invalid_formula_error', 'XLOOKUP'),
    ('=A <> 100', 'B', 'invalid_formula_error', '<>'),
    ('=SUM(A', 'B', 'invalid_formula_error', 'parentheses'),
]
@pytest.mark.parametrize("formula, address, error_type, to_fix_substr", PARSE_TEST_ERRORS)
def test_parse_errors(formula, address, error_type, to_fix_substr):
    with pytest.raises(EditError) as e_info:
        parse_formula(formula, address)
    assert e_info.value.type_ == error_type
    if to_fix_substr is not None:
        assert to_fix_substr in e_info.value.to_fix


SAFE_REPLACE_TESTS = [
    ('=A', 'A', 'B', '=B'),
    ('=A + A', 'A', 'B', '=B + B'),
    ('=A + B', 'A', 'B', '=B + B'),
    ('=A + B + A', 'A', 'B', '=B + B + B'),
    ('=A + B + \"A\"', 'A', 'B', '=B + B + \"A\"'),
    ('=A + B + \'A\'', 'A', 'B', '=B + B + \'A\''),
    ('=A + B + \'A\'', 'A', 'B', '=B + B + \'A\''),
    ('=FUNC(A, B, A) + TEST(FUNC(A, \'A\', \'B\')) + \'A\'', 'A', 'B', '=FUNC(B, B, B) + TEST(FUNC(B, \'A\', \'B\')) + \'A\''),
    ('=APPLE(A, B, A) + AARON(AAA(A, \'A\', \'B\')) + \'A\'', 'A', 'B', '=APPLE(B, B, B) + AARON(AAA(B, \'A\', \'B\')) + \'A\''),
]

@pytest.mark.parametrize('formula,old_text,new_text,new_formula', SAFE_REPLACE_TESTS)
def test_safe_replace(formula, old_text, new_text, new_formula):
    assert safe_replace(formula, old_text, new_text) == new_formula


SAFE_CONTAINS_TESTS = [
    ('=A', 'A', True),
    ('=A + B', 'B', True),
    ('=A + "B"', 'B', False),
    ('=A & "B"', '&', True),
    ('=A - +  "&"', '&', False),
    ('=A - +  \'&\'', '&', False),
]

@pytest.mark.parametrize('formula,substring,contains', SAFE_CONTAINS_TESTS)
def test_safe_contains(formula, substring, contains):
    assert safe_contains(formula, substring) == contains