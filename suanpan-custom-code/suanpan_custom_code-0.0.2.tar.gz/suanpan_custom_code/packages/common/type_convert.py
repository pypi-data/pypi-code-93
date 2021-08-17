from types import FunctionType


def cast(f: FunctionType):
    def wrapper(*args, **kwargs):
        # check args
        args = list(args)
        keys = tuple(f.__annotations__.keys())
        for ar in enumerate(args):
            function_type = None
            if len(keys) > ar[0]:
                function_type = f.__annotations__.get(keys[ar[0]])
            if function_type is not None:
                try:
                    args[ar[0]] = function_type(ar[1])
                except TypeError:
                    print(f"cannot convert {ar[1]} to {function_type}")

        # check kwargs
        for k, v in kwargs.items():
            function_type = f.__annotations__.get(k)
            if function_type is not None:
                try:
                    kwargs[k] = function_type(v)
                except TypeError:
                    print(f"cannot convert {v} to {function_type}")
        args = tuple(args)
        return f(*args, **kwargs)

    return wrapper
