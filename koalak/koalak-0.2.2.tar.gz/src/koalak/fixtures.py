import inspect

fixtures = {}


def register_fixture(f):
    global fixtures
    fixtures[f.__name__] = f
    return f


@register_fixture
def one():
    return 1


@register_fixture
def two():
    return 2


print(fixtures)


def callfixture(f):
    params = inspect.signature(f).parameters
    args = []
    for param_name, param in params.items():
        if param_name in fixtures:
            args.append(fixtures[param_name])
        else:
            raise ValueError(f"fixture {param_name} unknown")

    def new_f():
        n_args = [arg() for arg in args]
        return f(*n_args)

    return new_f


@callfixture
def hey(one, two):
    return one + two


@register_fixture
def extra():
    return "Whaaaat"


@callfixture
def f(extra, one):
    print(extra)
    print(one)
    return extra * 2


print(f())
print(hey())
