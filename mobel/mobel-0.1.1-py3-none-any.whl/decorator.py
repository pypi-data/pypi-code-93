from typing import Callable, Optional, TypeVar, Union, overload, Protocol
import inspect
from functools import wraps

from .common import ANNOTATION_DIR

__all__ = "makeDecorator"

TA = TypeVar("TA")
TB = TypeVar("TB")
TC = TypeVar("TC")
TD = TypeVar("TD")
TE = TypeVar("TE")
TF = TypeVar("TF")
TG = TypeVar("TG")
TH = TypeVar("TH")
TI = TypeVar("TI")
TJ = TypeVar("TJ")

F = TypeVar("F", bound=Callable, contravariant=True)

RV = TypeVar("RV", bound=Callable, covariant=True)

Decorator = Callable[[F], RV]
NoArgsDecoratorFactory = Callable[[], Decorator]


class DecoratorFactory(Protocol[F, RV]):
    @overload
    def __call__(self) -> Callable[[F], RV]: ...
    @overload
    def __call__(self, f: F) -> RV: ...


PA = Callable[[F, TA], RV]
DA = Union[Callable[[TA], Decorator], DecoratorFactory[F, RV]]

PB = Callable[[F, TA, TB], RV]
DB = Union[Callable[[TA, TB], Decorator], DecoratorFactory[F, RV]]

PC = Callable[[F, TA, TB, TC], RV]
DC = Union[Callable[[TA, TB, TC], Decorator], DecoratorFactory[F, RV]]

PD = Callable[[F, TA, TB, TC, TD], RV]
DD = Union[Callable[[TA, TB, TC, TD], Decorator], DecoratorFactory[F, RV]]

PE = Callable[[F, TA, TB, TC, TD, TE], RV]
DE = Union[Callable[[TA, TB, TC, TD, TE], Decorator], DecoratorFactory[F, RV]]


@overload
def makeDecorator(decoratorPrototype: Decorator) -> NoArgsDecoratorFactory:
    ...  # pragma: no cover


@overload
def makeDecorator(decoratorPrototype: PA) -> DA:
    ...  # pragma: no cover


@overload
def makeDecorator(decoratorPrototype: PB) -> DB:
    ...  # pragma: no cover


@overload
def makeDecorator(decoratorPrototype: PC) -> DC:
    ...  # pragma: no cover


@overload
def makeDecorator(decoratorPrototype: PD) -> DD:
    ...  # pragma: no cover


@overload
def makeDecorator(decoratorPrototype: PE) -> DE:
    ...  # pragma: no cover


def makeDecorator(decoratorPrototype):
    """Converts a prototype function into a decorator and/or decorator factory
        the generated decorator can only have keyword arguments
        if the prototype has positional_or_keyword arguments they'll be converted to keyword

    Args:
        decoratorPrototype (Callable): decorator prototype

    Raises:
        ValueError: The decorator prototype has no arguments
        ValueError: The decorator prototype has positional only arguments

    Returns:
        Callable: the decorator/decorator factory
    """
    function_signature = inspect.signature(decoratorPrototype)

    if len(function_signature.parameters.values()) == 0:
        raise ValueError("decorator prototype must have at least one argument")

    if functionHasPositionalOnlyArguments(function_signature):
        raise ValueError(
            "decorator prototype can't have positional only arguments")

    def decoratorOrFactory(functionToDecorate: Optional[Callable] = None, /, **kwargs):
        if functionToDecorate is None:
            def decorator(functionToDecorate):
                return wrapFunction(functionToDecorate, decoratorPrototype(functionToDecorate, **kwargs))
            return decorator
        return wrapFunction(functionToDecorate, decoratorPrototype(functionToDecorate))
    return decoratorOrFactory


def functionHasPositionalOnlyArguments(function_signature: inspect.Signature) -> bool:
    """ Checks whether the function signature provided contains positional only arguments
        other than the argument representing the function to decorate

    Args:
        function_signature (Signature): function signature

    Returns:
        bool: True if the provided signature has unwanted positional only arguments
    """
    arguments = iter(function_signature.parameters.values())
    next(arguments)  # skip the first argument which is the function to decorate
    try:
        first_argument = next(arguments)
        return first_argument.kind == first_argument.POSITIONAL_ONLY
    except StopIteration:
        return False


Func = TypeVar("Func", bound=Callable)


def wrapFunction(sourceFunction: Func, targetFunction: Func) -> Func:
    """Function that preserves the signature of the sourceFunction into the targetFunction
        and copies attibutes used by Mobel such as Annotations

    Args:
        sourceFunction (Callable): function to copy properties from
        targetFunction (Callable): function to copy properties to

    Returns:
        Callable: wrapped target function
    """
    wrappedFunction = wraps(sourceFunction)(targetFunction)
    if hasattr(sourceFunction, ANNOTATION_DIR):
        sourceAnnotations = getattr(sourceFunction, ANNOTATION_DIR)
        setattr(wrappedFunction, ANNOTATION_DIR, sourceAnnotations)
    return wrappedFunction
