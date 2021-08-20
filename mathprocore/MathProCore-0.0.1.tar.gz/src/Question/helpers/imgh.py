"""
Contains a number of helper functions for dealing with Image objects.
"""

import re, sympy
from Question.helpers.csympy.printing.latex import latex as clatex
from Question import image
from Question.helpers import exprh

latex_params = {
    "order": "none",
    "inv_trig_style": "power"
}

def to_sympy(img):
    """Mutates the image such that self.expressions is a list of sympy objects. img initially stores expression strings
    strings in self.expressions.
    A sympy string is any string that can be evaluated to produce a sympy object or objects. 
    To store multiple expressions in a sympy string, delimit them with '{' and '}'. Note that this
    function will not throw an error if the image's expressions are already sympy objects.

    :param img: An image object whose expressions are expression strings.
    :type img: image.Image
    """
    if img is image.Image.none:
        return img
    exprs = []
    for e in img.expressions:
        if type(e) == str:
            e = exprh.to_sympy(e.replace("{", "").replace("}", ""))
        exprs.append(e)
    img.expressions = exprs
    img.update(exprh.to_sympy)

def get_expr_strs_as_sympy(img):
    """Returns all expressions in an image storing expression strings as sympy objects.
    An expression is defined as either the entire expression string, or any
    substrings delimited by '{' and '}'.
    Note that this function does not mutate the img object.

    Ex. identifies a in y = {a} * x + b
        identifies the entire (y = a * x + b)

    :param img: An image object whose expressions are or include expression strings.
    :type img: image.Image
    :returns: A list of sympy objects representing the expression strings in the original image.
    :rtype: list
    """
    if img is image.Image.none:
        return []
    exprs = []
    for expr in img.expressions:
        if "{" in expr and "}" in expr:
            exprs.extend(re.findall(r"{(.*?)}", expr))
        else:
            exprs.append(expr)
    exprs = [ exprh.to_sympy(e) for e in exprs ]
    return exprs

def to_latex(img, vars=[]):
    """Mutates the image such that self.expressions is a list of latex strings. img initially stores 
    sympy objects in self.expressions.

    Some variables in the sympy object have not been replaced with values yet! For these 
    variables, we delimit them by '@' symbols which can be easily
    replaced later on (by a call to subs_latex).

    :param img: An image object containing sympy expressions.
    :type img: image.Image
    :param vars: A list of variables in the sympy expression.
    :type vars: list, optional
    :returns: An image object whose expressions are latex strings.
    :rtype: image.Image
    """
    if img is image.Image.none:
        return img
    substitutions = { var: sympy.symbols("@"+str(var)+"@") for var in vars }
    img.expressions = [ expr_as_latex(expr, substitutions) for expr in img.expressions ]

def expr_as_latex(expr, substitutions):
    """Converts a sympy expression in an image object into a latex expression.
    Subsitutions are made into the sympy object based on the substitutions dict passed to the function.
    The latex expression that is returned is of the specific form required by the Desmos API. This function can handle
    piecewise functions, points, as well as regular sympy expressions.

    :param expr: A sympy object.
    :type expr: sympy
    :param substitutions: A dictionary that associates sympy symbols in the expression with values.
        Note that the keys must be sympy objects.
    :type substitutions: dict
    :returns: A latex string of the original expression including the given substitutions.
    :rtype: str
    """
    # base case
    if type(expr) == str:
        return expr
    # equations
    if isinstance(expr, sympy.Rel):
        lhs, rhs = expr.args
        if isinstance(lhs, sympy.Piecewise):
            lhs = piecewise_as_latex(lhs, substitutions)
        if isinstance(rhs, sympy.Piecewise):
            rhs = piecewise_as_latex(rhs, substitutions)
        oper = "=" if expr.rel_op == "==" else expr.rel_op
        return expr_as_latex(lhs, substitutions) + " " + oper + " " + expr_as_latex(rhs, substitutions)
    # points
    if isinstance(expr, sympy.Point):
        return "\\left(" + ", ".join([expr_as_latex(arg, substitutions) for arg in expr.args]) + "\\right)"
    # generic sympy expressons
    sympy_expr = exprh.subs(
        expr,
        substitutions
    )
    return exprh.replace(clatex(sympy_expr, **latex_params))

def piecewise_as_latex(expr, substitutions):
    """Converts a sympy.Piecewise object in an image into a latex expression.
    Subsitutions are made into the sympy object based on the substitutions dict passed to the function.
    The latex expression that is returned is of the specific form required by the Desmos API.

    :param expr: A sympy.Piecewise object.
    :type expr: sympy
    :param substitutions: A dictionary that associates sympy symbols in the expression with values.
        Note that the keys must be sympy objects.
    :type substitutions: dict
    :returns: A latex string of the original expression including the given substitutions.
    :rtype: str
    """
    pieces = []
    for ex, eq in expr.args:
        pieces.append(expr_as_latex(eq, substitutions) + ":" + expr_as_latex(ex, substitutions))
    return "{" + ", ".join(pieces) + "}"

def subs_latex(img, substitutions):
    """Substitutes values from a dictionary into the latex strings stored in an image.
    Assumes the variables in the image's expressions have been delimited with '@' symbols.
    Should be called on an image object after `as_latex()` has been called.

    :param img: An image storing latex expressions.
    :type img: image.Image
    :param substitutions: A dictionary that associates sympy symbols or strings in the expression with values.
    :type substitutions: dict
    :returns: A new image object with the given subsitutions applied to its expressions.
    :rtype: image.Image
    """
    if img is image.Image.none:
        return img
    img = img.copy()
    image_subs = { "@"+str(key)+"@": value for key, value in substitutions.items() }
    img.expressions = [ exprh.replace(subs_latex_expr(expr, image_subs)) for expr in img.expressions ]
    img.update(exprh.subs, substitutions)
    return img

def subs_latex_expr(expr, substitutions):
    """
    Substitutes values from a dictionary into a latex string.

    :param expr: A latex string.
    :type expr: string
    :param substitutions: A dictionary that associates sympy symbols or strings in the expression with values.
    :type substitutions: dict
    :returns: A latex string of the original expression including the given substitutions.
    :rtype: str
    """
    for key in substitutions:
        expr = expr.replace(key, "(" + clatex(substitutions[key]) + ")")
    return expr
