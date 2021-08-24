#########################################
#         OPERATORS FOR V1 TREES        #
#########################################

OPERATORS_V1 = {
    "IS": "is",
    "IN_INTERVAL": "[in[",
    "GTE": ">=",
    "LT": "<",
}


def LT(a, b):
    return a < b


def GTE(a, b):
    return a >= b


OPERATORS_FUNCTION_V1 = {
    OPERATORS_V1["IS"]: lambda context, value: context == value,
    OPERATORS_V1["GTE"]: lambda context, value: safe_op(context, value, GTE),
    OPERATORS_V1["LT"]: lambda context, value: safe_op(context, value, LT),
    OPERATORS_V1["IN_INTERVAL"]: lambda context, value: safe_op(context, value[0], GTE)
    and safe_op(context, value[1], LT)
    if safe_op(value[0], value[1], LT)
    else safe_op(context, value[0], GTE) or safe_op(context, value[1], LT),
}


def safe_op(context, value, func):
    if context is not None and context != {}:
        return func(context, value)
    return False


#########################################
#         OPERATORS FOR V2 TREES        #
#########################################

# The operators for V2 tree are simply an extension of V1 operators

OPERATORS_V2 = OPERATORS_V1.copy()
OPERATORS_FUNCTION_V2 = OPERATORS_FUNCTION_V1.copy()

OPERATORS_V2.update({"IN_MULTI": "in"})

OPERATORS_FUNCTION_V2.update(
    {OPERATORS_V2["IN_MULTI"]: lambda context, value: context in value}
)

#########################################
#           DEFAULT OPERATORS           #
#########################################

OPERATORS = OPERATORS_V2
OPERATORS_FUNCTION = OPERATORS_FUNCTION_V2
