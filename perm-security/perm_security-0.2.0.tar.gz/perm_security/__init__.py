def validate(a, b) -> bool:
    """Determines if a class is valid against another"""
    return a.__validate__(b)


from .MemberAdapter import *
from .Permission import *
from .TokenStrategy import *
from .Token import Token
