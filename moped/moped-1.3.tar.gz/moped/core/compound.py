"""Compound abstraction."""

import reprlib
from copy import deepcopy


class Compound:
    """A compound abstraction.

    This is written with slots to keep the memory footprint low
    and also to keep users from making mistakes in the naming
    of the possible fields.

    Attributes
    ----------
    base_id: str
    id: str
    name: str
    formula: dict(str: float)
    charge: float
    gibbs0: float
    compartment: str
    smiles: str
    types: list(str)
        Corresponds to the compound classes this compound belongs to.
        The order of the list equals the order of the classes written
        in the flatfiles and thus increases in specificity. So the last
        element is the most important one.
    in_reaction: set(str)
        Set of the reactions in which this compound takes part. This
        only makes sense if the Compounds is part of a Model and should
        otherwise be empty.
    database_links: dict(str: str)
        Links of identifiers etc. to other databases.
    """

    __slots__ = [
        "base_id",
        "id",
        "name",
        "formula",
        "charge",
        "gibbs0",
        "compartment",
        "smiles",
        "types",
        "in_reaction",
        "database_links",
    ]

    def __init__(
        self,
        base_id,
        formula=None,
        charge=None,
        compartment=None,
        gibbs0=None,
        name=None,
        smiles=None,
        types=None,
        in_reaction=None,
        database_links=None,
        id=None,
        *args,
        **kwargs,
    ):
        """Create a model compound.

        Necessary information to pass charge and mass balance tests are the charge and formula attributes.

        Parameters
        ----------
        id : str
        formula : dict(str : int), optional
        charge : int, optional
        compartment : str, optional
        gibbs0 : int, optional
        smiles : str, optional
        types : list, optional
            Compound types this compound is part of
        in_reaction : set, optional
            Set of reactions this compound occurs in (in a model context)
        name : str, optional
        """
        self.base_id = base_id
        self.id = id
        self.compartment = compartment
        self.formula = formula if formula is not None else {}
        self.charge = charge
        self.name = name
        self.gibbs0 = gibbs0
        self.smiles = smiles
        self.database_links = database_links if database_links is not None else {}
        if types is None:
            self.types = []
        else:
            self.types = list(types)
        if in_reaction is None:
            self.in_reaction = set()
        else:
            self.in_reaction = set(in_reaction)

    def __hash__(self):
        """Hash the compound id."""
        return hash(self.id)

    def __eq__(self, other):
        """Compare compound id with another compound id."""
        return self.id == other.id

    def __ne__(self, other):
        """Compare compound id with another compound id."""
        return self.id != other.id

    def __lt__(self, other):
        """Compare compound id with another compound id."""
        return self.id < other.id

    def __le__(self, other):
        """Compare compound id with another compound id."""
        return self.id <= other.id

    def __gt__(self, other):
        """Compare compound id with another compound id."""
        return self.id > other.id

    def __ge__(self, other):
        """Compare compound id with another compound id."""
        return self.id >= other.id

    def __iter__(self):
        """Return tuple of certain attributes and their value."""
        return (
            (i, getattr(self, i))
            for i in [
                "base_id",
                "id",
                "name",
                "compartment",
                "formula",
                "charge",
                "gibbs0",
                "smiles",
                "types",
                "in_reaction",
                "database_links",
            ]
            if bool(getattr(self, i))
        )

    def __str__(self):
        """Return string representation."""
        s = f"Compound <{self.id}>"
        for k, v in dict(self).items():
            s += f"\n    {k}: {v}"
        return s

    def __repr__(self):
        """Return representation."""
        args = ", ".join(f"{k}={reprlib.repr(v)}" for k, v in dict(self).items())
        return f"Compound({args})"

    def copy(self):
        """Create a deepcopy of the compound.

        While this is more costly than shallow copies, it takes away
        the hassle of always keeping track if a shallow copy is what
        you want at the moment. So it's mostly for me not getting
        confused ;)

        Returns
        -------
        cpd: Compound
        """
        return deepcopy(self)

    def formula_to_string(self):
        """Create a string variant of the formula dict.

        Examples
        --------
        >>> Compound(formula={"C": 1, "H": 1}).formula_to_string()
        "C1H1"

        Returns
        -------
        formula_string: str
            The compound formula as a string representation
        """
        return "".join([str(k) + str(v) for k, v in self.formula.items()])
