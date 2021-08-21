import sympy, random
from .matrix import Matrix

class Interval:
    """A class that represents numeric intervals in different domains. 

    :param domain: A string representing the parent set of the specified interval. Accepted values: ["Integer", "Real", "Natural", "Rational", "Finite"]
    :type domain: str
    :param \*vals: Intervals for numbers generated
    :param \*\*default: A function that takes no arguments and returns a sympy number
    :param \*\*zero: determines if 0 is included in the given interval. Defaults to True.
    :param \*\*zero: bool, optional
    :type default: function
    """

    domains = {
        "Integer",
        "Real",
        "Natural",
        "Rational",
        "Finite"
    }
    kwargs = { "default", "units", "exclude" }
    none = []

    def __init__(self, domain, *vals, **kwargs):
        """Constructor method."""
        assert domain in Interval.domains, f"Invalid value for domain. Accepted values: {Interval.domains}"
        assert len(vals) != 0
        uargs = set(kwargs.keys()) - Interval.kwargs
        assert not uargs, f"Invalid keyword arguments: {uargs}"

        self.set = domain
        self.default = kwargs.get("default", self.rand)
        self.units = kwargs.get("units", "")
        self.exclude = kwargs.get("exclude", [])
        if self.units != "":
            self.units = sympy.sympify(self.units)
        self.values = list(vals)
        if self.set != "Finite":
            self.values.sort()
        if self.set == "Finite":
            self.values = self.values[0]

    def rand(self, attempt=0):
        """Generate a random sympy number that satisfies `self.min` <= value <= `self.max` and is in the `self.domain` set.
        Default random method for `Interval` instances.
        """
        random.seed()
        if self.set == "Integer":
            # self.values[0] is min and self.values[1] is max
            value = random.randint(
                self.values[0],
                self.values[1]
            )
        elif self.set == "Real":
            value = random.uniform(
                self.values[0],
                self.values[1]
            )
        elif self.set == "Natural":
            # natural numbers are integers >= 0
            value = random.randint(
                max(0, self.values[0]),
                self.values[1]
            )
        elif self.set == "Rational":
            value = round(
                random.uniform(
                    self.values[0],
                    self.values[1]
                ),
                2 # todo: 2 digits of accuracy is still arbitrary
            )
        elif self.set == "Finite":
            value = random.choice(self.values)
        value = sympy.sympify(
            value,
            rational=(self.set == "Rational"),
            evaluate=False
        )
        if self.units != "":
            value = value * self.units
        if value not in self.exclude:
            return value
        if attempt > 100:
            raise RuntimeError(f"Maximum attempts exceeded to draw number from {self.set} set in the range {self.values}.")
        return self.rand(attempt=attempt+1)
        
    def __call__(self):
        """Call method."""
        return self.default()

class Relation:
    """A class that defines a relationship between a given symbol and other symbols in a system.

    :param var: A sympy object representing the symbol that has a relation.
    :type var: sympy.core.symbol.Symbol or str
    :param default_interval: An ``Interval`` instance to default to if the variable passed is
        determined 'free' under the system of relations.
    :type default_interval: :class:`Interval`
    :param expr: A keyword argument that takes a mathematical expression
        that relates a variable to others in the system.
    :type expr: str
    """

    reserved = ["degrees", "_zero", "_one"]

    def __init__(self, var, default_interval=Interval.none, expr='', matrix=None):
        """Constructor method."""
        assert var not in Relation.reserved, f"The variable name {var} is a reserved name and cannot be used in a `Relation` object."
        assert callable(default_interval) or default_interval is Interval.none, "The default_interval argument must be callable."
        self.var = sympy.sympify(var, evaluate=False)
        self.interval = default_interval
        self.expr = ""
        self.matrix = matrix
        if matrix is not None:
            self.interval = matrix
            if type(matrix) is Matrix:
                self.interval = matrix.to_sympy
        if expr != "":
            self.expr = sympy.sympify(expr)

    def default(self):
        return self.interval()

radians = Interval(
    "Finite",
    [
        sympy.pi / 6,
        sympy.pi / 4,
        sympy.pi / 3,
        sympy.pi / 2,
        sympy.pi * 2 / 3,
        sympy.pi * 3 / 4,
        sympy.pi * 5 / 6,
        sympy.pi,
        sympy.pi * 7 / 6,
        sympy.pi * 5 / 4,
        sympy.pi * 4 / 3,
        sympy.pi * 3 / 2,
        sympy.pi * 5 / 3,
        sympy.pi * 7 / 4,
        sympy.pi * 11 / 6,
        sympy.pi * 2
    ]
)

degrees = Interval(
    "Finite",
    [
        "30",
        "45",
        "60",
        "90",
        "120",
        "135",
        "150",
        "180",
        "210",
        "225",
        "240",
        "270",
        "300",
        "315",
        "330",
        "360"
    ],
    units="degrees"
)
