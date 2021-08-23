import inspect
from abc import ABCMeta
from functools import partial, wraps
from typing import List

VALID_RULES = ["before", "after", "wrap", "setup"]


def _check_rule(rule: str):
    if rule not in VALID_RULES:
        raise ValueError(
            "Invalid rule! Must be one of the following: {}".format(VALID_RULES)
        )


class Callback(metaclass=ABCMeta):
    def class_setup(self, cls):
        pass

    def function_setup(self, f):
        pass

    def setup(self, wrapped_class, f, *args, **kwargs):
        pass

    def before(self, wrapped_class, f, *args, **kwargs):
        pass

    def after(self, prev_output, wrapped_class, f, *args, **kwargs):
        return prev_output

    def in_class(self, f):
        return "self" in inspect.signature(f).parameters

    def get_wrapped_class(self, f, args):
        if self.in_class(f):
            return args[0]
        return None

    def handle_exception(self, exception: Exception):
        return exception

    def _run(self, f, *args, **kwargs):
        wrapped_class = self.get_wrapped_class(f, args)
        self.before(wrapped_class, f, *args, **kwargs)
        try:
            out = f(*args, **kwargs)
        except Exception as e:
            ex = self.handle_exception(e)
            if ex is None:
                ex = e
            raise ex
        after_out = self.after(out, wrapped_class, f, *args, **kwargs)
        if after_out is None:
            after_out = out
        return after_out

    def wrap(self, f):
        @wraps(f)
        def _inner(*args, **kwargs):
            return self._run(f, *args, **kwargs)

        _inner.__signature__ = inspect.signature(f)
        return _inner

    def wrap_setup(self, f):
        @wraps(f)
        def _inner(*args, **kwargs):
            wrapped_class = self.get_wrapped_class(f, args)
            self.setup(wrapped_class, f, *args, **kwargs)
            return f(*args, **kwargs)

        _inner.__signature__ = inspect.signature(f)
        return _inner

    def wrap_before(self, f):
        @wraps(f)
        def _inner(*args, **kwargs):
            wrapped_class = self.get_wrapped_class(f, args)
            self.before(wrapped_class, f, *args, **kwargs)
            return f(*args, **kwargs)

        _inner.__signature__ = inspect.signature(f)
        return _inner

    def wrap_after(self, f):
        @wraps(f)
        def _inner(*args, **kwargs):
            wrapped_class = self.get_wrapped_class(f, args)
            try:
                out = f(*args, **kwargs)
            except Exception as e:
                self.handle_exception(e)
                raise e
            after_out = self.after(out, wrapped_class, f, *args, **kwargs)
            if after_out is None:
                after_out = out
            return after_out

        _inner.__signature__ = inspect.signature(f)
        return _inner

    def __call__(self, f, *args, **kwargs):
        return self._run(f, *args, **kwargs)


def _callback_function(func, callbacks, rule: str):
    _check_rule(rule)

    @wraps(func)
    def _inner(*args, **kwargs):
        wrapped = func
        for callback in callbacks:
            if rule == "wrap":
                wrapped = callback.wrap(wrapped)
            elif rule == "before":
                wrapped = callback.wrap_before(wrapped)
            elif rule == "after":
                wrapped = callback.wrap_after(wrapped)
            elif rule == "setup":
                wrapped = callback.wrap_setup(wrapped)
        return wrapped(*args, **kwargs)

    return _inner


def callback_class(
    cls, callbacks, functions: List[str] = ["_all_"], rule: str = "wrap"
):
    _check_rule(rule)
    # https://stackoverflow.com/a/17019983/190597 (jamylak)
    for name, m in inspect.getmembers(
        cls, lambda x: inspect.isfunction(x) or inspect.ismethod(x)
    ):
        if name in functions or "_all_" in functions:
            setattr(cls, name, _callback_function(m, callbacks, rule))
    return cls


def callback(callbacks, functions: List[str] = ["_all_"], rule: str = "wrap"):
    _check_rule(rule)

    def callback_wrapper(obj):
        if inspect.isclass(obj):
            for c in callbacks:
                c.class_setup(obj)
            return callback_class(obj, callbacks, functions, rule)
        for c in callbacks:
            c.function_setup(obj)
        return _callback_function(obj, callbacks, rule)

    return callback_wrapper


def set_method_callback(class_instance, method_name, callbacks, rule: str = "wrap"):
    c_back = callback(callbacks, [method_name], rule)
    return c_back(class_instance)


before = partial(callback, rule="before")
after = partial(callback, rule="after")
setup_callback = partial(callback, rule="setup")
