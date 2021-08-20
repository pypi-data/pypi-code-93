import math

def sympify_interaction(i, symbolic_lr=False, include_weights=True):
    import sympy
    mname = lambda s: s.replace(" ","_").replace('_', '')
    num_rep = lambda n: n+'_in' if n.isdigit() else n
    cat_rep = lambda c: c+'_cat'
    fmt = lambda s: f"{s:.{15}e}"

    if i.spec == "in:linear(f)->i":
        num_str = num_rep(mname(i.name))
        s = f"{num_str} * {fmt(i.state.scale)} * {fmt(i.state.w)} + {fmt(i.state.bias)}" if include_weights else num_str
    elif i.spec== "in:cat(c)->i":
        cat_str = cat_rep(mname(i.name))
        s = f"{cat_str} + {fmt(i.state.bias)}" if include_weights else cat_str
    elif i.spec=="cell:multiply(i,i)->i":
        s = "__x0__ * __x1__"
    elif i.spec=="cell:add(i,i)->i":
        s = "__x0__ + __x1__"
    elif i.spec=="cell:linear(i)->i":
        s = f"{fmt(i.state.w0)} * __x0__ + {fmt(i.state.bias)}" if include_weights else '__x0__'
    elif i.spec=="cell:tanh(i)->i":
        s = "tanh(__x0__)"
    elif i.spec=="cell:inverse(i)->i":
        s = "1/__x0__"
    elif i.spec=="cell:log(i)->i":
        s = "log(__x0__)"
    elif i.spec=="cell:exp(i)->i":
        s = "exp(__x0__)"
    elif i.spec=="cell:gaussian(i,i)->i":
        s = "exp(-(__x0__**2 / .5 +__x1__**2 / .5))" if include_weights else "exp(-(__x0__**2 +__x1__**2))"
    elif i.spec=="cell:gaussian(i)->i":
        s = "exp(-(__x0__**2 / .5))" if include_weights else "exp(-(__x0__**2))"
    elif i.spec=="cell:sqrt(i)->i":
        s = "sqrt(__x0__)"
    elif i.spec=="cell:squared(i)->i":
        s = "__x0__**2"
    elif i.spec=="out:linear(i)->f":
        s = f"{fmt(i.state.scale)} * ({fmt(i.state.w)} * __x0__ + {fmt(i.state.bias)})" if include_weights else '__x0__'
    elif i.spec=="out:lr(i)->b":
        output = f"{fmt(i.state.w)} * __x0__ + {fmt(i.state.bias)}" if include_weights else '__x0__'
        if symbolic_lr:
            s = f"1/(1+exp(-({output})))"
        else:
            s = f"logreg({output})"
    else:
        raise ValueError("Unsupported %s"%i.spec)
    return sympy.sympify(s)

def _signif(x, digits):
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)

def _round_expression(expr, digits):
    import sympy
    for a in sympy.preorder_traversal(expr):
        if isinstance(a, sympy.Float):
            expr = expr.subs(a, _signif(a, digits))

    return expr

def sympify_model(m, signif=6, symbolic_lr=False, include_weights=True):
    exprs = [sympify_interaction(i, symbolic_lr=symbolic_lr, include_weights=include_weights) for i in m]
    for ix, i in enumerate(m):
        if len(i.sources)>0:
            exprs[ix] = exprs[ix].subs({"__x0__": exprs[i.sources[0]]})
        if len(i.sources)>1:
            exprs[ix] = exprs[ix].subs({"__x1__": exprs[i.sources[1]]})
    return _round_expression(exprs[-1], signif)
