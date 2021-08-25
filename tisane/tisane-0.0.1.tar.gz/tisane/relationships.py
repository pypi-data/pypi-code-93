from tisane.variable import AbstractVariable

"""
Class for Has relationships
"""


class Has():
    variable: "AbstractVariable"
    measure: "AbstractVariable"
    repetitions: int
    # repetitions: 'AbstractVariable'

    # Default is between subjects, only once
    def __init__(
        self,
        variable: "AbstractVariable",
        measure: "AbstractVariable",
        repetitions: int,
    ):
        self.variable = variable
        self.measure = measure
        self.repetitions = repetitions
