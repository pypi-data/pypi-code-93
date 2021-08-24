from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp


def get_expr_sql(x):
    if issubclass(type(x), BaseScalarOp):
        return f"({x.get_sql()})"
    else:
        return x.get_sql()
