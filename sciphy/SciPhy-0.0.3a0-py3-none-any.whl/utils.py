from physics.errors import *


def classify(obj: object) -> str:
    return f"'{str(type(obj))[8:-2].split('.')[-1]}'"

def numerator(unit: str) -> str:
    if not isinstance(unit, str):
        raise TypeError(f"Argument 'unit' must be of type 'str'")
    return unit.split('/')[0]

def denominator(unit: str) -> str:
    if not isinstance(unit, str):
        raise TypeError(f"Argument 'unit' must be of type 'str'")
    return unit.split('/')[-1]