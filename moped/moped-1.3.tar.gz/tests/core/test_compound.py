import unittest

from moped import Compound


class CompoundTests(unittest.TestCase):
    def test_initialization(self):
        cpd = Compound("CPD001")
        self.assertEqual(cpd.base_id, "CPD001")
        self.assertEqual(cpd.compartment, None)

    def test_initialization_cytosol(self):
        cpd = Compound("CPD001", compartment="CYTOSOL")
        self.assertEqual(cpd.base_id, "CPD001")
        self.assertEqual(cpd.compartment, "CYTOSOL")

    def test_initialization_compartment_periplasm(self):
        cpd = Compound("CPD001", compartment="PERIPLASM")
        self.assertEqual(cpd.base_id, "CPD001")
        self.assertEqual(cpd.compartment, "PERIPLASM")

    def test_initialization_compartment_extracellular(self):
        cpd = Compound("CPD001", compartment="EXTRACELLULAR")
        self.assertEqual(cpd.base_id, "CPD001")
        self.assertEqual(cpd.compartment, "EXTRACELLULAR")

    def test_initialize_name(self):
        c = Compound("CPD001", name="compound")
        self.assertEqual(c.name, "compound")

    def test_initialize_formula(self):
        c = Compound("CPD001", formula={"C": 1})
        self.assertEqual(c.formula, {"C": 1})

    def test_initialize_charge(self):
        c = Compound("CPD001", charge=1)
        self.assertEqual(c.charge, 1)

    def test_initialize_gibbs0(self):
        c = Compound("CPD001", gibbs0=1)
        self.assertEqual(c.gibbs0, 1)

    def test_initialize_smiles(self):
        c = Compound("CPD001", smiles="CN=C=O")
        self.assertEqual(c.smiles, "CN=C=O")

    def test_initialize_types(self):
        c = Compound("CPD001", types=["small-molecule"])
        self.assertEqual(c.types, ["small-molecule"])

    def test_initialize_in_reaction(self):
        c = Compound("CPD001", in_reaction={"rxn-1"})
        self.assertEqual(c.in_reaction, {"rxn-1"})

    def test_comparisons(self):
        c1 = Compound(base_id="CPD1")
        c1.id = "CDP1_c"
        c2 = Compound(base_id="CPD2")
        c2.id = "CDP2_c"

        self.assertTrue(c1 == c1)
        self.assertTrue(c1 != c2)
        self.assertTrue(c1 < c2)
        self.assertTrue(c1 <= c2)
        self.assertTrue(c2 > c1)
        self.assertTrue(c2 >= c1)

    def test_iter(self):
        c = Compound(
            base_id="CPD001",
            name="CPD001",
            formula={"C": 1},
            charge=1,
            gibbs0=1,
            compartment="CYTOSOL",
            smiles="CN=C=O",
            types=["small-molecule"],
            in_reaction={"rxn-1"},
        )
        self.assertEqual(
            dict(c),
            {
                "base_id": "CPD001",
                "name": "CPD001",
                "formula": {"C": 1},
                "charge": 1,
                "gibbs0": 1,
                "compartment": "CYTOSOL",
                "smiles": "CN=C=O",
                "types": ["small-molecule"],
                "in_reaction": {"rxn-1"},
            },
        )

    def test_str(self):
        c = Compound(
            base_id="CPD001",
            name="CPD001",
            formula={"C": 1},
            charge=1,
            gibbs0=1,
            compartment="CYTOSOL",
            smiles="CN=C=O",
            types=["small-molecule"],
            in_reaction={"rxn-1"},
        )
        c.id = "CPD001_c"

        self.assertEqual(
            str(c).split("\n"),
            [
                "Compound <CPD001_c>",
                "    base_id: CPD001",
                "    id: CPD001_c",
                "    name: CPD001",
                "    compartment: CYTOSOL",
                "    formula: {'C': 1}",
                "    charge: 1",
                "    gibbs0: 1",
                "    smiles: CN=C=O",
                "    types: ['small-molecule']",
                "    in_reaction: {'rxn-1'}",
            ],
        )

    def test_repr(self):
        c = Compound(
            base_id="CPD001",
            name="CPD001",
            formula={"C": 1},
            charge=1,
            gibbs0=1,
            compartment="CYTOSOL",
            smiles="CN=C=O",
            types=["small-molecule"],
            in_reaction={"rxn-1"},
        )
        c.id = "CPD001_c"
        self.assertEqual(
            repr(c).split(", "),
            [
                "Compound(base_id='CPD001'",
                "id='CPD001_c'",
                "name='CPD001'",
                "compartment='CYTOSOL'",
                "formula={'C': 1}",
                "charge=1",
                "gibbs0=1",
                "smiles='CN=C=O'",
                "types=['small-molecule']",
                "in_reaction={'rxn-1'})",
            ],
        )

    def test_formula_to_string(self):
        c = Compound("CPD001", formula={"C": 1})
        self.assertEqual(c.formula_to_string(), "C1")

    def test_formula_to_string_two_atoms(self):
        c = Compound("CPD001", formula={"C": 1, "H": 12})
        self.assertEqual(c.formula_to_string(), "C1H12")
