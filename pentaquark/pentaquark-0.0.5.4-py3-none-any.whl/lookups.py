import collections.abc

from pentaquark.exceptions import PentaQuarkValidationError
from pentaquark.registry import Registry

LOOKUPS = []
LOOKUP_REGISTRY = Registry()


def register(klass):
    """Register lookup"""
    LOOKUP_REGISTRY.add(klass.name, klass)
    LOOKUPS.append(klass.name)
    return klass


class Lookup:
    name = ""
    cypher_expr = ""

    def _check_expr(self, exp):
        return exp

    def _check_right_expr(self, right):
        return self._check_expr(right)

    def _check_left_expr(self, left):
        return self._check_expr(left)

    def to_cypher(self, left, right, param_store):
        left_expr = self._check_left_expr(left)
        right_expr = self._check_right_expr(right)
        param_name = param_store.add(left, right_expr)
        return f"{left_expr} {self.cypher_expr} ${param_name}"


@register
class EqualLookup(Lookup):
    name = "eq"
    cypher_expr = "="


@register
class NotEqualLookup(Lookup):
    name = "neq"
    cypher_expr = "<>"


@register
class GreaterThanLookup(Lookup):
    name = "gt"
    cypher_expr = ">"


@register
class GreaterThanOrEqualToLookup(Lookup):
    name = "gte"
    cypher_expr = ">="


@register
class LessThanLookup(Lookup):
    name = "lt"
    cypher_expr = "<"


@register
class LessThanOrEqualToLookup(Lookup):
    name = "lte"
    cypher_expr = "<="


@register
class RegMatchLookup(Lookup):
    name = "regmatch"
    cypher_expr = "=~"


@register
class IsNullLookup(Lookup):
    """Usage:
    x__isnull=True  => x IS NULL
    x__isnull=False => x IS NOT NULL
    """
    name = "isnull"

    def _check_right_expr(self, right):
        if isinstance(right, bool):
            return right
        raise PentaQuarkValidationError(f"Invalid left argument {right}, expected bool")

    def to_cypher(self, left, right, param_store):
        right_exp = self._check_right_expr(right)
        left_exp = self._check_left_expr(left)
        if right_exp:
            return f"{left_exp} IS NULL"
        return f"{left_exp} IS NOT NULL"


@register
class StartsWithLookup(Lookup):
    name = "startswith"
    cypher_expr = "STARTS WITH"


@register
class EndsWithLookup(Lookup):
    name = "endswith"
    cypher_expr = "ENDS WITH"


@register
class StrContainsLookup(Lookup):
    name = "contains"
    cypher_expr = "CONTAINS"


@register
class InLookup(Lookup):
    """
    Check that the Cypher property is within a list
    """
    name = "in"
    cypher_expr = "IN"

    def _check_right_expr(self, right):
        if isinstance(right, collections.abc.MutableSequence):
            return right
        raise PentaQuarkValidationError(f"Invalid left argument {right}, expected list")


@register
class InvInLookup(Lookup):
    """
    Inverse IN:
    Check that the right hand side is contained into the cypher list property
    """
    name = "inv_in"
    cypher_expr = "IN"

    def to_cypher(self, left, right, param_store):
        left_expr = self._check_left_expr(left)
        right_expr = self._check_right_expr(right)
        param_name = param_store.add(left, right_expr)
        return f"${param_name} {self.cypher_expr} {left_expr}"


class FunctionLookup(Lookup):
    function = ""

    def to_cypher(self, left, right=None, param_store=None):
        if right:
            return f"{self.function}({left}) = {right}"
        return f"{self.function}({left})"


class Exists(FunctionLookup):
    name = "exists"
    function = "EXISTS"


@register
class Label(Lookup):
    name = "label"
    function = "labels"

    def to_cypher(self, left, right, param_store):
        param_name = param_store.add(left, right)
        return f"${param_name} IN {self.function}({left})"
