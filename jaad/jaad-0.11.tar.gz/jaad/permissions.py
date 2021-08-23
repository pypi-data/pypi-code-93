from functools import wraps


def authentication(*authentication_classes):
    def add_authentication(view):
        view.authentication_classes = authentication_classes
        return view

    return add_authentication


def restricted(check):
    def restricted_decorator(handler):
        @wraps(handler)
        def wrapper(view, request, *args):
            check(request, *args)
            return handler(view, request, *args)

        return wrapper

    return restricted_decorator
