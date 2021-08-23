"""The main reaction file."""

import reprlib
from copy import deepcopy


class Reaction:
    """Reaction abstraction.

    Uses slots to keep the memory footprint low and to help
    users by not allowing to set wrong attributes.
    """

    __slots__ = (
        "base_id",
        "id",
        "name",
        "stoichiometries",
        "compartment",
        "bounds",
        "reversible",
        "gibbs0",
        "ec",
        "types",
        "pathways",
        "sequences",
        "monomers",
        "enzrxns",
        "database_links",
        "transmembrane",
    )

    def __init__(
        self,
        id,
        stoichiometries=None,
        compartment=None,
        bounds=None,
        reversible=None,
        gibbs0=None,
        ec=None,
        types=None,
        pathways=None,
        sequences=None,
        monomers=None,
        enzrxns=None,
        database_links=None,
        transmembrane=None,
        name=None,
        base_id=None,
        *args,
        **kwargs,
    ):
        """Initialise a reaction object.

        Parameters
        ----------
        id : str
        stoichiometries : dict, optional
            Stoichiometries of the reaction
        bounds : tuple(float, float), optional
            (lower_bound, upper_bound)
        reversible : bool, optional
        gibbs0 : float, optional
        ec : str, optional
        pathways : set, optional
        enzymes : set, optional
        name : str, optional
        base_id : str, optional
            Base id in the case of a variant reaction
        """
        self.base_id = base_id if base_id is not None else id
        self.id = id
        self.name = name
        self.stoichiometries = stoichiometries if stoichiometries is not None else {}
        self.compartment = compartment
        self.bounds = bounds
        if reversible is None:
            if bounds is not None:
                if bounds[0] < 0 and bounds[1] > 0:
                    self.reversible = True
                else:
                    self.reversible = False
            else:
                self.reversible = False
        else:
            self.reversible = reversible
        self.gibbs0 = gibbs0
        self.ec = ec
        self.types = types if types is not None else list()
        if transmembrane is None:
            compound_compartments = set()
            for i in self.stoichiometries:
                try:
                    compartment = i.rsplit("_", maxsplit=1)[1]
                except IndexError:
                    pass
                else:
                    compound_compartments.add(compartment)
            if len(compound_compartments) > 1:
                transmembrane = True
            else:
                transmembrane = False
        self.transmembrane = transmembrane
        self.pathways = pathways if pathways is not None else set()
        self.sequences = sequences if sequences is not None else {}
        self.monomers = monomers if monomers is not None else {}
        self.enzrxns = enzrxns if enzrxns is not None else {}
        self.database_links = database_links if database_links is not None else {}

    def __hash__(self):
        """Hash the id."""
        return hash(self.id)

    def __eq__(self, other):
        """Compare ids."""
        return self.id == other.id

    def __ne__(self, other):
        """Compare ids."""
        return self.id != other.id

    def __lt__(self, other):
        """Compare ids."""
        return self.id < other.id

    def __le__(self, other):
        """Compare ids."""
        return self.id <= other.id

    def __gt__(self, other):
        """Compare ids."""
        return self.id > other.id

    def __ge__(self, other):
        """Compare ids."""
        return self.id >= other.id

    def __iter__(self):
        """Iterate over select attributes."""
        return (
            (i, getattr(self, i))
            for i in (
                "id",
                "base_id",
                "name",
                "stoichiometries",
                "transmembrane",
                "compartment",
                "bounds",
                "reversible",
                "gibbs0",
                "ec",
                "types",
                "pathways",
                "sequences",
                "monomers",
                "enzrxns",
                "database_links",
            )
            if bool(getattr(self, i))
        )

    def __str__(self):
        """Create a string representation of the reaction attributes."""
        s = f"Reaction <{self.id}>"
        for k, v in dict(self).items():
            s += f"\n    {k}: {v}"
        return s

    def __repr__(self):
        """Create a string representation of the reaction."""
        args = ", ".join(f"{k}={reprlib.repr(v)}" for k, v in dict(self).items())
        return f"Reaction({args})"

    def copy(self):
        """Create a deepcopy of the reaction.

        While this is more costly than shallow copies, it takes away
        the hassle of always keeping track if a shallow copy is what
        you want at the moment. So it's mostly for me not getting
        confused ;)

        Returns
        -------
        rxn: Reaction
        """
        return deepcopy(self)

    def _split_stoichiometries(self):
        """Split the reaction stoichiometries into substrates and products.

        This is mostly used in structural analyses, such as the scope algorithm.

        Returns
        -------
        substrates: dict(str: float)
        products: dict(str: float)
        """
        substrates, products = {}, {}
        for k, v in self.stoichiometries.items():
            if v < 0:
                substrates[k] = v
            else:
                products[k] = v
        return substrates, products

    def replace_compound(self, old_compound, new_compound):
        """Replace a compound with another, keeping the stoichiometries.

        Parameters
        ----------
        old_compound : str
            Id of the compound to be replaced
        new_compound : str
            Id of the replacing compound
        """
        stoich = self.stoichiometries.pop(old_compound)
        self.stoichiometries[new_compound] = stoich

    def reverse_stoichiometry(self):
        """Reverses the stoichiometry of the reaction.

        This also reverses the bounds and gibbs0
        """
        self.stoichiometries = {k: -v for k, v in self.stoichiometries.items()}
        if self.gibbs0 is not None:
            self.gibbs0 = -self.gibbs0
        if self.bounds is not None:
            self.bounds = (-self.bounds[1], -self.bounds[0])

    def make_reversible(self):
        """Make the reaction reversible."""
        lb, ub = self.bounds
        # Check if it is not really irreversible in the first place
        if lb < 0 and ub > 0:
            pass
        elif lb < 0:
            self.bounds = (lb, -lb)
        else:
            self.bounds = (-ub, ub)
        self.reversible = True

    def make_irreversible(self):
        """Make the reaction irreversible."""
        lb, ub = self.bounds
        if lb < 0 and ub > 0:
            self.bounds = (0, ub)
        # Maybe it was annotated wrong
        elif ub > 0:
            self.bounds = (0, ub)
        else:
            self.bounds = (lb, 0)
        self.reversible = False
