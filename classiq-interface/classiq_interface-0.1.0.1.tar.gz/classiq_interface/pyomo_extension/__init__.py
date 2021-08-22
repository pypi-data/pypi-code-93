import pyomo
from pyomo import core

from classiq_interface.pyomo_extension import (
    inequality_expression,
    equality_expression,
    set_pprint,
)

pyomo.core.expr.logical_expr.InequalityExpression.getname = (
    inequality_expression.getname
)

pyomo.core.expr.logical_expr.EqualityExpression.getname = equality_expression.getname

pyomo.core.base.set.Set._pprint_members = set_pprint._pprint_members
