def compose(apply: bool = True, *funcs, **kwargs):
    f = funcs[0]
    for func in funcs[1:]:
        f = func(f)
    return f(**kwargs) if apply else f


def composer(*funcs, **kw):
    f = funcs[0](**kw)
    if len(funcs) == 1:
        return f
    for func in funcs[1:]:
        f = func(f, **kw)
    return f
