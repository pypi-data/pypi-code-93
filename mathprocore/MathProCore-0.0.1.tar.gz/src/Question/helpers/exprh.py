"""
Contains a number of helper functions for sympy expressions represented as strings, sympy objects, or even latex.
"""

import re
import sympy
from Question.helpers.csympy.parsing.sympy_parser import parse_expr as cparse_expr

transforms = (
    sympy.parsing.sympy_parser.standard_transformations
)
ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def subs(sympy_obj, substitutions):
    """Substitutes values from a dictionary into a sympy object without applying any automatic simplifications.

    :param sympy_obj: A sympy object.
    :type sympy_obj: sympy
    :param substitutions: Two dictionary of key value pairs that associate sympy symbols in the sympy object with values.
        Note that the keys must be sympy objects.
    :type substitutions: dict
    :returns: A sympy object with symbols replaced by values specified in subsitutions.
    :rtype: sympy.core.expr.Expr
    """
    # substitution
    if isinstance(sympy_obj, (sympy.Symbol, sympy.Number)):
        return substitutions.get(sympy_obj, sympy_obj)
    # matrices
    if isinstance(sympy_obj, sympy.Matrix):
        matrix = sympy_obj.copy()
        for i in range(len(matrix)):
            matrix[i] = subs(matrix[i], substitutions)
        return matrix
    args = [ subs(arg, substitutions) for arg in sympy_obj.args ]
    # addition
    if type(sympy_obj) == sympy.core.add.Add:
        args = [ arg for arg in args if arg != 0 ]
    # multiplication
    if type(sympy_obj) == sympy.core.mul.Mul:
        if len(args) == 2 and type(args[1]) == sympy.core.power.Pow and args[1].args[1] == -1: # division
            string1 = str(args[0])
            string2 = str(args[1].args[0])
            if isinstance(args[0], sympy.Symbol):
                string1 = f"Symbol('{string1}')"
            if isinstance(args[1].args[0], sympy.Symbol):
                string2 = f"Symbol('{string2}')"
            return cparse_expr(string1 + " / " + string2, evaluate=False)
        args = [ arg for arg in args if arg != 1 ] # simplify multplication by one
    try:
        return type(sympy_obj)(*args, evaluate=False)
    except Exception:
        return type(sympy_obj)(*args)

def replace(latex):
    """A janky function that makes final substitutions on a latex string.
    A lazy solution to a complex problem.

    :param latex: A latex string.
    :type latex: str
    :returns: The cleaner version of the original latex.
    :rtype: str
    """
    reps = {
        "degrees": r"^{\circ}",
        "^{1}": "",
        "--": "+",
        "- -": "+", # fix this for strings that start with "--b"
        "1^{-1}": "1",
        "+ 0\\right)": "\\right)",
        "+ 0 \\right)": "\\right)",
        "+0\\right)": "\\right)",
        "_zero": "0",
        "_one": "1",
        "Point2D": "",
        "Point3D": "",
    }

    for pattern, rep in reps.items():
        latex = latex.replace(pattern, rep)
    latex = re.sub(r'\\frac{(.*?)}\{1\}', lambda m: m.group(1), latex)
    return latex

def final_replace(latex):
    """An even jankier function that makes the most final substitutions on a latex string.
    A lazy solution to a complex problem.

    :param latex: A latex string.
    :type latex: str
    :returns: The cleaner version of the original latex.
    :rtype: str
    """
    reps = {
        "--": "+",
        "- -": "+"
    }
    latex = latex.replace(" \\text{} ", "")
    latex = latex.replace("\\text{} ", "")
    latex = latex.replace("\\text{}", "")
    for pattern, rep in reps.items():
        latex = latex.replace(pattern, rep)
    return latex

START, STOP = "á", "é"
def pre_secure(expr):
    """Changes the parenthesis surrounding function calls (i.e sqrt(expr)) to special characters.
    They will be changed back during a call to secure().

    :param expr: A string that can be used to produce a sympy object by a call to `to_sympy`.
    :type expr: str
    :returns: The original string with important function calls secured.
    :rtype: str
    """
    functions = [
        "sqrt",
        "tan",
        "sin",
        "cos",
        "log"
    ]
    tks = list(expr)
    for func in functions:
        indices = [ m.start() + len(func) for m in re.finditer(func, expr) ]
        for i in indices:
            tks[i] = START
            start, stop = 1, 0
            while start != stop:
                i += 1
                if tks[i] == "(":
                    start += 1
                if tks[i] == ")":
                    stop += 1
            tks[i] = STOP
    return "".join(tks)

def secure(expr):
    """Secures an expression string by helping prevent automatic simplifications being applied by
    a later call to `to_sympy`. Works by adding parentheses and adding zero to important expressions.
    These expressions are also raised to the power 1.

    :param expr: A string that can be used to produce a sympy object by a call to `to_sympy`.
    :type expr: str
    :returns: The original string with important expressions secured.
    :rtype: str
    """
    expr = pre_secure(expr)
    if "," in expr:
        return expr
    tks = list(expr.replace(" ", ""))
    i, division = 0, False
    while i < len(tks):
        if tks[i] == ")":
            # ugly-fuck conditional (it is what it is)
            if not division and (len(tks) == i+1 or tks[i+1] in ["+", "-"] or (tks[i+1] == "*" and (len(tks) == i+2 or tks[i+2] != "*"))):
                tks.insert(i, "+_zero")
                tks.insert(i+2, "**(_one)")
                i += 2
            division = len(tks) > i+1 and tks[i+1] == "/"
        i += 1
    return "".join(tks).replace(START, "(").replace(STOP, ")")

def to_sympy(expr):
    """Converts an expression string into a sympy object. Superior to sympy.sympify because `to_sympy`
    can handle normal expressions as well as relations.

    :param expr: A string that can be parsed into a sympy object.
    :type expr: str
    :returns: The sympy object associated with the given string.
    :rtype: sympy
    """
    if type(expr) != str:
        return expr
    expr = secure(expr)
    # find if there's a relation in the prompt and what/where it is
    locs = [(expr.find(rel), rel) for rel in ['>=', '<=', '!=', '=', '<', '>']]
    relation = any([loc[0] != -1 for loc in locs])
    # if there is a relation
    if relation:
        # get sympy objects for the left/right hand sides
        loc, relation = min([loc for loc in locs if loc[0] != -1], key=lambda loc: loc[0])
        left = cparse_expr(
            expr[:loc],
            evaluate=False,
            transformations=transforms
        )
        right = cparse_expr(
            expr[loc+len(relation):],
            evaluate=False,
            transformations=transforms
        )
        # and stick em' together by their relation
        expr = sympy.Rel(left, right, '==' if relation == '=' else relation)
    else:
        # if there's no relation, then it's an expression and we can just `sympify` it directly
        expr = cparse_expr(
            expr,
            evaluate=False,
            transformations=transforms
        )
    if type(expr) == tuple:
        return sympy.Point(expr)
    return expr

def seperate(prompt):
    """Seperates a prompt string into a list of text and a list of expression strings. Expressions
    in the prompt must be delimited by '{' and '}'. Note, to prevent latex expressions from being
    incorrectly parsed, they must be delimited by '$' symbols. For intance 'The angle is $\\frac{\\pi}\{2\}$'
    would be valid.

    :param prompt: A string containing text and expressions within it.
    :type prompt: str
    :returns: A list of text and a list of expression strings.
    :rtype: tuple(list, list)
    """
    # store and remove symbols
    symbols = re.findall(r"\$(.*?)\$", prompt)
    for symb in symbols:
        prompt = prompt.replace("$"+symb+"$", "$$", 1)
    # seperate expressions from the string
    expressions = re.findall(r"{(.*?)}", prompt)
    if not expressions:
        return ["", ""], [prompt]
    for expr in expressions:
        prompt = prompt.replace("{"+expr+"}", "•", 1)
    # return symbols to there original positions
    for symb in symbols:
        prompt = prompt.replace("$$", "} " + symb + " \\text{", 1)
    text = [ "\\text{"+p+"}" for p in prompt.split("•") ]
    return text, expressions

def process_prompt(prompt, matrices):
    """Uses a number of helper functions to split the text from a prompt string and
    parse the remaining expression strings into sympy objects.

    :param prompt: A string containing text and expressions within it.
    :type prompt: str
    :returns: A list containing the text and expressions from the original prompt string.
    :rtype: list(list, list)
    """
    # split the text from the sympy expressions in the prompt
    text, expressions = seperate(prompt)
    prompt = [text, []]
    matrix_symbols = sorted([ str(m.var) for m in matrices ], key=len, reverse=True)
    # loop through the expressions
    for expr in expressions:
        for symb in matrix_symbols:
            if symb in expr:
                index = expr.index(symb)
                pre = index == 0 or expr[index - 1] not in ALPHABET
                post = index + len(symb) == len(expr) or expr[index + len(symb)] not in ALPHABET
                if pre and post:
                    expr = expr.replace(symb, f"MatrixSymbol('{symb}', 0, 0)")
        prompt[1].append(to_sympy(expr))
    return prompt
