"""This module extends the predicate class to enable the comparison between two predicates."""
from typing import Tuple, List, Optional

from pddl.pddl import Predicate, Type


class ComparablePredicate(Predicate):
    """Class that extends the basic predicate to enable comparison."""

    name: str
    signature: List[Tuple[str, Tuple[Type]]]

    def __init__(self, name: Optional[str] = None,
                 signature: Optional[List[Tuple[str, Tuple[Type]]]] = None,
                 predicate: Optional[Predicate] = None):
        if predicate:
            super(ComparablePredicate, self).__init__(predicate.name, predicate.signature)

        else:
            super(ComparablePredicate, self).__init__(name, signature)

    @staticmethod
    def is_sub_type(this_type: Type, other_type: Type) -> bool:
        """Checks if a type a subtype of the other.

        :param this_type: the checked type.
        :param other_type: the type that is checked to se if the first is subtype of.
        :return: whether or not the first is a subtype of the other.
        """
        ancestors_type_names = [this_type.name]
        compared_type = this_type
        while compared_type.parent is not None:
            ancestors_type_names.append(compared_type.parent.name)
            compared_type = compared_type.parent

        return other_type.name in ancestors_type_names

    @staticmethod
    def extract_types(signature: List[Tuple[str, Tuple[Type]]]) -> List[Type]:
        """Extract the type of the object from the signature format.

        :param signature: the signature of the predicate.
        :return: the types that were extracted from the signature.
        """
        types = []
        for _, param_type in signature:
            if type(param_type) is tuple or type(param_type) is list:
                types.append(param_type[0])
            else:
                types.append(param_type)
        return types

    def __eq__(self, other: Predicate):
        self_signature_params_name = [name for name, _ in self.signature]
        other_signature_params_name = [name for name, _ in other.signature]
        return \
            (self.name == other.name and self_signature_params_name ==
             other_signature_params_name and
             all([self.is_sub_type(this_type, other_type) for this_type, other_type in
                  zip(self.extract_types(self.signature), self.extract_types(other.signature))]))

    def __str__(self):
        return f"{self.name}{str(self.signature)}".strip("\n")

    def __hash__(self):
        return hash(str(self))

    def __copy__(self):
        return ComparablePredicate(self.name, self.signature)
