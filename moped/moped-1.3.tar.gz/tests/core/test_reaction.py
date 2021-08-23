import unittest

from moped import Reaction


class ReactionTests(unittest.TestCase):
    def test_initialize_id(self):
        self.assertEqual(Reaction("RXN001").id, "RXN001")

    def test_initialize_name(self):
        rxn = Reaction("RXN001", name="Reaction")
        self.assertEqual(rxn.name, "Reaction")

    def test_initialize_stoichiometries(self):
        rxn = Reaction("RXN001", stoichiometries={"X": -1, "Y": 1})
        self.assertEqual(rxn.stoichiometries, {"X": -1, "Y": 1})

    def test_initialize_bounds(self):
        rxn = Reaction("RXN001", bounds=(-1000, 1000))
        self.assertEqual(rxn.bounds, (-1000, 1000))

    def test_initialize_reversible_default(self):
        rxn = Reaction("RXN001")
        self.assertEqual(rxn.reversible, False)

    def test_initialize_reversible_true(self):
        rxn = Reaction("RXN001", reversible=True)
        self.assertEqual(rxn.reversible, True)

    def test_initialize_reversible_false(self):
        rxn = Reaction("RXN001", reversible=False)
        self.assertEqual(rxn.reversible, False)

    def test_initialize_gibbs0(self):
        rxn = Reaction("RXN001", gibbs0=1)
        self.assertEqual(rxn.gibbs0, 1)

    def test_initialize_ec(self):
        rxn = Reaction("RXN001", ec="123")
        self.assertEqual(rxn.ec, "123")

    def test_initialize_pathways(self):
        rxn = Reaction("RXN001", pathways=["PWY-101"])
        self.assertEqual(rxn.pathways, ["PWY-101"])

    def test_transmembrane_both_none(self):
        rxn = Reaction(
            id="RXN001_c",
            base_id="RXN001",
            stoichiometries={"X": -1, "Y": 1},
        )
        self.assertFalse(rxn.transmembrane)

    def test_transmembrane_both_cytosol(self):
        rxn = Reaction(
            id="RXN001_c",
            base_id="RXN001",
            stoichiometries={"X_c": -1, "Y_c": 1},
        )
        self.assertFalse(rxn.transmembrane)

    def test_transmembrane_different_compartments(self):
        rxn = Reaction(
            id="RXN001_c",
            base_id="RXN001",
            stoichiometries={"X_c": -1, "Y_p": 1},
        )
        self.assertTrue(rxn.transmembrane)

    def test_iter(self):
        rxn = Reaction(
            id="RXN001_c",
            base_id="RXN001",
            stoichiometries={"X_c": -1, "Y_c": 1},
            bounds=(-1000, 1000),
            reversible=True,
            gibbs0=1,
            ec="123",
            pathways=["PWY-101"],
        )
        self.assertEqual(
            dict(rxn),
            {
                "id": "RXN001_c",
                "base_id": "RXN001",
                "stoichiometries": {"X_c": -1, "Y_c": 1},
                "bounds": (-1000, 1000),
                "reversible": True,
                "gibbs0": 1,
                "ec": "123",
                "pathways": ["PWY-101"],
            },
        )

    def test_hash(self):
        rxn = Reaction(id="RXN001_c")
        self.assertEqual(hash(rxn), hash("RXN001_c"))

    def test_comparisons(self):
        rxn1 = Reaction(id="RXN001_c")
        rxn2 = Reaction(id="RXN002_c")
        self.assertTrue(rxn1 == rxn1)
        self.assertTrue(rxn1 != rxn2)
        self.assertTrue(rxn1 <= rxn2)
        self.assertTrue(rxn1 < rxn2)
        self.assertTrue(rxn2 >= rxn1)
        self.assertTrue(rxn2 > rxn1)

    def test_str(self):
        rxn = Reaction(
            id="RXN001_c",
            base_id="RXN001",
            stoichiometries={"X_c": -1, "Y_c": 1},
            bounds=(-1000, 1000),
            reversible=True,
            gibbs0=1,
            ec="123",
            pathways=["PWY-101"],
        )

        self.assertEqual(
            str(rxn).split("\n"),
            [
                "Reaction <RXN001_c>",
                "    id: RXN001_c",
                "    base_id: RXN001",
                "    stoichiometries: {'X_c': -1, 'Y_c': 1}",
                "    bounds: (-1000, 1000)",
                "    reversible: True",
                "    gibbs0: 1",
                "    ec: 123",
                "    pathways: ['PWY-101']",
            ],
        )

    def test_repr(self):
        rxn = Reaction(
            id="RXN001_c",
            base_id="RXN001",
            stoichiometries={"X_c": -1, "Y_c": 1},
            bounds=(-1000, 1000),
            reversible=True,
            gibbs0=1,
            ec="123",
            pathways=["PWY-101"],
        )

        self.assertEqual(
            repr(rxn).split(", "),
            [
                "Reaction(id='RXN001_c'",
                "base_id='RXN001'",
                "stoichiometries={'X_c': -1",
                "'Y_c': 1}",
                "bounds=(-1000",
                "1000)",
                "reversible=True",
                "gibbs0=1",
                "ec='123'",
                "pathways=['PWY-101'])",
            ],
        )

    def test_reverse_stoichiometries_stoichiometries(self):
        rxn = Reaction("RXN001", stoichiometries={"X": -1, "Y": 1})
        rxn.reverse_stoichiometry()
        self.assertEqual(rxn.stoichiometries, {"X": 1, "Y": -1})

    def test_reverse_stoichiometries_bounds(self):
        rxn = Reaction("RXN001", stoichiometries={"X": -1, "Y_e": 1}, bounds=(-50, 100))
        rxn.reverse_stoichiometry()
        self.assertEqual(rxn.bounds, (-100, 50))

    def test_reverse_stoichiometries_gibbs0(self):
        rxn = Reaction("RXN001", stoichiometries={"X": -1, "Y_e": 1}, gibbs0=-1)
        rxn.reverse_stoichiometry()
        self.assertEqual(rxn.gibbs0, 1)

    def test_replace_substrate(self):
        v = Reaction("v", stoichiometries={"x": -1, "y": 1})
        v.replace_compound("x", "x1")
        self.assertEqual(v.stoichiometries, {"x1": -1, "y": 1})

    def test_replace_product(self):
        v = Reaction("v", stoichiometries={"x": -1, "y": 1})
        v.replace_compound("y", "y1")
        self.assertEqual(v.stoichiometries, {"x": -1, "y1": 1})

    def test_reaction_reversibility_from_bounds_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 1000))
        self.assertTrue(r.reversible)

    def test_reaction_reversibility_from_bounds_upper_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1, 1))
        self.assertTrue(r.reversible)

    def test_reaction_reversibility_from_bounds_lower_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1, 1))
        self.assertTrue(r.reversible)

    def test_reaction_reversibility_from_bounds_upper_zero(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 0))
        self.assertFalse(r.reversible)

    def test_reaction_reversibility_from_bounds_lower_zero(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(0, 1000))
        self.assertFalse(r.reversible)

    def test_reaction_make_reversible_upper_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(0, 1000))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1000, 1000))

    def test_reaction_make_reversible_lower_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 0))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1000, 1000))

    def test_reaction_make_reversible_upper_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(0, 1))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1, 1))

    def test_reaction_make_reversible_lower_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1, 0))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1, 1))

    def test_reaction_make_reversible_already_reversible_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 1000))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1000, 1000))

    def test_reaction_make_reversible_already_reversible_lower_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1, 1000))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1, 1000))

    def test_reaction_make_reversible_already_reversible_upper_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 1))
        r.make_reversible()
        self.assertTrue(r.reversible)
        self.assertEqual(r.bounds, (-1000, 1))

    def test_reaction_make_irreversible_upper_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(0, 1000))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (0, 1000))

    def test_reaction_make_irreversible_lower_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 0))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (-1000, 0))

    def test_reaction_make_irreversible_upper_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(0, 1))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (0, 1))

    def test_reaction_make_irreversible_lower_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1, 0))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (-1, 0))

    def test_reaction_make_irreversible_reversible_max(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 1000))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (0, 1000))

    def test_reaction_make_irreversible_reversible_lower_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1, 1000))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (0, 1000))

    def test_reaction_make_irreversible_reversible_upper_one(self):
        r = Reaction(id="rxn", stoichoimetries={"x": -1, "y": 1}, bounds=(-1000, 1))
        r.make_irreversible()
        self.assertFalse(r.reversible)
        self.assertEqual(r.bounds, (0, 1))
