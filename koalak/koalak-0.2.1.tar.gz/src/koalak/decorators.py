import functools

# TODO: create ObjectStore to store attributes in object with a specific namespace
import inspect
import logging

logger = logging.getLogger("pff")
logger.setLevel(logging.DEBUG)
logger.setLevel(logging.CRITICAL)


class ObjectStore:
    def __init__(self):
        pass

    def has(self, attribute):
        pass

    def get(self):
        pass

    def set(self):
        pass


def factory_dispatcher__init__(cls):
    # Create the new __init__
    # we will call functools.wraps after
    def dispatcher__init__(self, *args, **kwargs):
        for __init__ in cls.__inits__:
            __init__(self, *args, **kwargs)

        for __post_init__ in cls.__post_inits__:
            __post_init__(self)

    # Wraps functions for signature
    # if the cls use the object.__init__ we have
    # to replace it signature with a signature without *args, **kwargs
    if cls.__init__ == object.__init__:

        def dummy__init__(self):
            pass

        wrapped_signature = dummy__init__
    else:
        wrapped_signature = cls.__init__
    dispatcher__init__ = functools.wraps(wrapped_signature)(dispatcher__init__)
    return dispatcher__init__


def add_post_init(post_init):
    """A decorator for class to add a function to be called
    after init.
    The decorator will create an __init__ if doesn't exist
    if an __init__ exist it will replace it with a an other one
    called __dispatcher_init__ that will call the old __init__
    - possible to have many post_inits

    Example:
        def addx(self):
            self.x = True

        @add_post_init(addx)
        class A:
        def __init__():
            self.a = True

        assert a.a is True
        assert a.x is True

    Args:
        post_init: function with one positional argument (self)

    # TODO: check that when creating an init (cls don't have one)
    # we create a init with a simple signature not *args, **kwargs
    names: in the cls class (TODO: change it in a namespace for this package)
        - __inits__
        - __post_inits__
    """
    # TODO: support multiple functions at once *init_functions
    def decorator(cls):
        if not hasattr(cls, "__inits__"):
            # create a new __init__
            dispatcher__init__ = factory_dispatcher__init__(cls)
            # replace the original __init__ by the dispathcer__init__
            cls.__inits__ = [cls.__init__]
            cls.__post_inits__ = []
            cls.__init__ = dispatcher__init__
        # add the post_init function
        # this function will be called by the dispathcer__init__
        cls.__post_inits__.append(post_init)

        return cls

    return decorator


# TODO: add order
def addinit(added__init__, *added__inits__, runfirst=False):
    # TODO: test this class
    # TOOD: use the factory dispatcher__init__
    # TODO: test addinit with add_postinit
    added__inits__ = [added__init__, *added__inits__]

    def dispatcher__init__(self, *args, **kwargs):
        for __init__ in dispatcher__init__.__inits__:
            __init__(self, *args, **kwargs)

    def decorator(cls):
        try:
            # Check if addinit was already called or not
            # if addinit is called, the __init__ will
            # have the attributes __inits__
            # Warning: check the __init__ of the class (__dict__['__init__'])
            # not the __init__ cls.__init__ (it could be the parent __init__)
            __inits__ = cls.__dict__["__init__"].__inits__
        except (KeyError, AttributeError):
            # if it's the first time we call addinit
            # we dynamically add __inits__ in cls.__init__
            __inits__ = [cls.__init__]
            dispatcher__init__.__inits__ = __inits__
            cls.__init__ = dispatcher__init__

        # Handle the order of execution
        if runfirst:
            __inits__ = added__inits__ + __inits__
        else:
            __inits__ += added__inits__
        return cls

    return decorator


# TODO: add way to specify runfirst
def persistent_addinit(added_init, runfirst=False):
    def added_init_decorator(cls):
        return addinit(added_init)(cls)

    return added_init_decorator


def defaultdecorator(_addattr=None, *, decorated=None, firstarg=None):
    """Decorator for decorators to allow them to be called with or without
    arguments.

    Example:
        @defaultdecorator
        def decorator(obj, msg="Hello"):
            print(msg)
            return obj

        # Now decorator can be called with (@decorator(msg="somthing")) or
        # without arguments (@decorator)

        @decorator
        class A:
            pass

        @decorator(msg="Good Bye")
        class A:
            pass

    This decorator itself can be called with or without arguments.

    By default only keyword arguments are allowed for the decorated decorator
    to enable positional arguments you have to specify either the type of
    the first argument or the type of the decorated object (by the decorated
    decorator) to resolve ambiguity.



    Args:
        decorated: type of the expected decorated object (by the decorated decorator)
            to resolve ambiguity
        firstarg: type of the first argument of the decorated decorator to resolve
            ambiguity

    """
    if _addattr is not None:
        # defaultdecorator called without kwargs. Example
        #  @defaultdecorator
        #  def f():
        #      pass
        @functools.wraps(_addattr)
        def new_addattr(obj=None, **kwargs):
            # no *args, the decorator must be called with kwargs only
            if obj is None:
                # obj is None => @decorator(a=2, x=3)
                print("obj is None => @decorator(a=2, x=3)")

                def deco1(cls):
                    return _addattr(cls, **kwargs)

                return deco1
            else:
                # obj is not None => @decorator without args
                print("obj is not None => @decorator")
                return _addattr(obj, **kwargs)

        return new_addattr
    else:
        # defaultdecorator called with kwargs to enable positional arguments

        if decorated is not None and firstarg is not None:
            raise TypeError(f"You can't use both 'decorated' and 'firstarg' keyword")

        if decorated is not None:
            # Normalize decorated to a tuple
            if not isinstance(decorated, tuple):
                decorated = tuple([decorated])

            def isarg_for_decorator(decorated_obj):
                return not isinstance(decorated_obj, decorated)

            print("arg decorated", decorated)

        elif firstarg is not None:
            # Normalize decorated to a tuple
            if not isinstance(firstarg, tuple):
                firstarg = tuple([firstarg])

            def isarg_for_decorator(decorated_obj):
                """Tell if the argument is for the decorator or if
                it's the object to decorate"""
                return isinstance(decorated_obj, firstarg)

            print("arg firstarg", firstarg)

        else:
            pass
            print("NOTHING GIVEN PROBLEM")
            raise TypeError()
            # TODO: raise error?

        def _defaultdecorator(_addattr):
            @functools.wraps(_addattr)
            def new_addattr(obj_or_arg=None, *args, **kwargs):
                if isarg_for_decorator(obj_or_arg):
                    # obj is None => @decorator(a=2, x=3)
                    print("obj is None => @decorator(a=2, x=3)")
                    if obj_or_arg:
                        args = [obj_or_arg] + list(args)
                    print("args", args)
                    print("kwargs", kwargs)

                    def deco1(cls):
                        return _addattr(cls, *args, **kwargs)

                    return deco1
                else:
                    # obj is not None => @decorator without args
                    print("obj is not None => @decorator")
                    print("args", args)
                    print("kwargs", kwargs)
                    return _addattr(obj_or_arg, *args, **kwargs)

            return new_addattr

        return _defaultdecorator


def addattr(obj=None, *, attr="x", value=5):
    def payload(obj):
        setattr(obj, attr, value)
        return obj

    if obj is None:
        # called with args @addattr() @addattr(x=2)
        def decorator(obj):
            return payload(obj)

        return decorator
    else:
        # called without args @addattr
        return payload(obj)


def is_future_method(function):
    """Tell if this function will be a method based on if it's first argument is named 'self'"""
    # this function is used in "optionalargs"
    try:
        return inspect.getfullargspec(function).args[0] == "self"
    except IndexError:
        return False


def optionalargs(decorator_to_decorate, *, firstarg=None):
    # TODO: decorator as a class
    # TODO: yassmine: add option to disable "ismethod" guessing, and to tell that it's a method
    """Decorator for decorators to allow them to be called with or without
    arguments.

    Example:
        ```
        @optionalargs
        def decorator(obj, msg="Hello"):
            print(msg)
            return obj

        # Now the decorator can be called with or without arguments

        # without arguments:
        @decorator
        def f():
            pass

        # with arguments
        @decorator(msg="Good Bye")
        def f():
            pass
        ```
    optionalargs can be called with or without arguments.

    By default only keyword arguments are allowed for the decorated decorator
    to enable positional arguments you have to specify either the type of
    the first argument or the type of the decorated object (by the decorated
    decorator) to resolve ambiguity.



    Args:
        decorated: type of the expected decorated object (by the decorated decorator)
            to resolve ambiguity
        firstarg: type of the first argument of the decorated decorator to resolve
            ambiguity

    """
    logger.error(
        "optionalargs called with decorator=%s firstarg=%r",
        decorator_to_decorate,
        firstarg,
    )

    obj_is_method = is_future_method(decorator_to_decorate)

    def _refactored(obj_or_arg, args, kwargs, self=None):
        pre_args = []
        if self:
            pre_args.append(self)

        # There are 3 possibility for the first argument
        #  None => decorator called with brackets =>
        if obj_or_arg is None or (
            firstarg is not None and isinstance(obj_or_arg, firstarg)
        ):
            logger.error(
                "decorator %s called with brackets", decorator_to_decorate.__name__
            )
            logger.error("obj_or_arg %r args %s kwargs %s", obj_or_arg, args, kwargs)
            # decorator called with brackets
            #  @decorateme()
            #  def f():
            #      pass
            # or:
            #  @decorateme(arg=value)
            #  def f():
            #      pass
            arg = obj_or_arg
            del obj_or_arg

            if arg is not None:
                args = (arg, *args)

            def decorator(obj):
                return decorator_to_decorate(*pre_args, obj, *args, **kwargs)

            return decorator
        else:
            # decorator called without braketcs. Example
            #  @decorateme
            #  def f():
            #      pass
            obj = obj_or_arg
            del obj_or_arg

            logger.error(
                "decorator %s called without brackets", decorator_to_decorate.__name__
            )
            return decorator_to_decorate(*pre_args, obj)

    if obj_is_method:
        # if it's a method we must add self in the signature
        @functools.wraps(decorator_to_decorate)
        def decorated_decorate_me(self, obj_or_arg=None, *args, **kwargs):
            return _refactored(obj_or_arg, args, kwargs, self=self)

    else:

        @functools.wraps(decorator_to_decorate)
        def decorated_decorate_me(obj_or_arg=None, *args, **kwargs):
            return _refactored(obj_or_arg, args, kwargs)

    return decorated_decorate_me


# decorate optionalargs with itself
optionalargs = optionalargs(optionalargs)
logger.error("after init optionalargs")


"""
@optionalargs
def decorateme_addattr(obj, *, attr="x", value=5):
    setattr(obj, attr, value)
    return obj

@decorateme_addattr
class A:
    pass


assert A.x == 5


@addattr(attr="y", value=2)
class A:
    pass


assert A.y == 2




def addattr(*, attr="x", value=5):
    def decorator(obj):
        setattr(obj, attr, value)
        return obj
    return decorator
"""
