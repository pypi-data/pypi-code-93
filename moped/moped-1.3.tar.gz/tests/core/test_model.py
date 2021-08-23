import io
import unittest
import unittest.mock as mock

from moped import Compound, Model, Reaction

import numpy as np


class MiscModelTests(unittest.TestCase):
    def test_str_and_repr(self):
        m = Model()
        self.assertEqual(repr(m), "Model: Model\n    compounds: 0\n    reactions: 0\n")
        self.assertEqual(str(m), "Model: Model\n    compounds: 0\n    reactions: 0\n")

        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compound(Compound(base_id="cpd1", compartment="c"))
        m.add_compound(Compound(base_id="cpd2", compartment="c"))
        m.add_reaction(Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        self.assertEqual(repr(m), "Model: Model\n    compounds: 2\n    reactions: 1\n")
        self.assertEqual(str(m), "Model: Model\n    compounds: 2\n    reactions: 1\n")

    def test_str_and_repr_name(self):
        m = Model(name="My model name")
        self.assertEqual(repr(m), "Model: My model name\n    compounds: 0\n    reactions: 0\n")
        self.assertEqual(str(m), "Model: My model name\n    compounds: 0\n    reactions: 0\n")

        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compound(Compound(base_id="cpd1", compartment="c"))
        m.add_compound(Compound(base_id="cpd2", compartment="c"))
        m.add_reaction(Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        self.assertEqual(repr(m), "Model: My model name\n    compounds: 2\n    reactions: 1\n")
        self.assertEqual(str(m), "Model: My model name\n    compounds: 2\n    reactions: 1\n")

    def test_copy(self):
        m1 = Model()
        m1.add_compartment(compartment_id="c", compartment_suffix="c")
        m1.add_compound(Compound(base_id="cpd1", compartment="c"))
        m1.add_compound(Compound(base_id="cpd2", compartment="c"))
        m1.add_reaction(Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        m2 = m1.copy()
        self.assertTrue(m1 is not m2)
        self.assertTrue(m1.compounds == m2.compounds)
        self.assertTrue(m1.reactions == m2.reactions)
        self.assertTrue(m1.compounds["cpd1_c"] is not m2.compounds["cpd1_c"])
        self.assertTrue(m1.compounds["cpd2_c"] is not m2.compounds["cpd2_c"])
        self.assertTrue(m1.reactions["rxn1"] is not m2.reactions["rxn1"])

    def test_context_manager_copy(self):
        m1 = Model()
        m1.add_compartment(compartment_id="c", compartment_suffix="c")
        m1.add_compound(Compound(base_id="cpd1", compartment="c"))
        m1.add_compound(Compound(base_id="cpd2", compartment="c"))
        m1.add_reaction(Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        with m1 as m2:
            self.assertTrue(m1 is not m2)
            self.assertTrue(m1.compounds == m2.compounds)
            self.assertTrue(m1.reactions == m2.reactions)
            self.assertTrue(m1.compounds["cpd1_c"] is not m2.compounds["cpd1_c"])
            self.assertTrue(m1.compounds["cpd2_c"] is not m2.compounds["cpd2_c"])
            self.assertTrue(m1.reactions["rxn1"] is not m2.reactions["rxn1"])

    def test_context_manager_restore_changes(self):
        m1 = Model()
        m1.add_compartment(compartment_id="c", compartment_suffix="c")
        m1.add_compound(Compound(base_id="cpd1", compartment="c"))
        m1.add_compound(Compound(base_id="cpd2", compartment="c"))
        m1.add_reaction(Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        with m1:
            m1.add_compound(Compound(base_id="cpd3", compartment="c"))
        self.assertEqual(tuple(m1.compounds.keys()), ("cpd1_c", "cpd2_c"))

    def test_create_submodel(self):
        m1 = Model()
        m1.add_compartment(compartment_id="c", compartment_suffix="c")
        m1.add_compound(Compound(base_id="cpd1", compartment="c"))
        m1.add_compound(Compound(base_id="cpd2", compartment="c"))
        m1.add_compound(Compound(base_id="cpd3", compartment="c"))
        m1.add_reaction(Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        m1.add_reaction(Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}))

        m2 = m1.create_submodel(reaction_ids=["rxn1"])
        self.assertEqual(m2.name, "Model submodel")
        self.assertEqual(set(m2.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(
            set(m2.reactions.keys()),
            {
                "rxn1",
            },
        )

        m2 = m1.create_submodel(reaction_ids=["rxn1"], name="test")
        self.assertEqual(m2.name, "test")


class ModelCompartmentTests(unittest.TestCase):
    def test_add_compartment_suffix(self):
        m = Model()
        m.add_compartment(compartment_id="cytosol", compartment_suffix="c")
        m.add_compound(Compound(base_id="cpd1", compartment="cytosol"))
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c",))

    def test_add_compartment_suffix_empty(self):
        m = Model()
        m.add_compartment(compartment_id="cytosol", compartment_suffix="")
        m.add_compound(Compound(base_id="cpd1", compartment="cytosol"))
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1",))

    def test_add_compartment_compound_variant_id(self):
        m = Model()
        m.add_compartments(compartments={"cytosol": "c", "extracellular": "e"})
        m.add_compound(Compound(base_id="cpd1", compartment="cytosol"))
        new_cpd = m.add_compartment_compound_variant(compound_id="cpd1_c", compartment_id="extracellular")
        self.assertEqual(new_cpd.base_id, "cpd1")
        self.assertEqual(new_cpd.id, "cpd1_e")
        self.assertEqual(new_cpd.in_reaction, set())
        self.assertEqual(new_cpd.compartment, "extracellular")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c", "cpd1_e"))

    def test_add_compartment_compound_variant_base_id(self):
        m = Model()
        m.add_compartments(compartments={"cytosol": "c", "extracellular": "e"})
        m.add_compound(Compound(base_id="cpd1", compartment="cytosol"))
        new_cpd = m.add_compartment_compound_variant(compound_id="cpd1", compartment_id="extracellular")

        self.assertEqual(new_cpd.base_id, "cpd1")
        self.assertEqual(new_cpd.id, "cpd1_e")
        self.assertEqual(new_cpd.in_reaction, set())
        self.assertEqual(new_cpd.compartment, "extracellular")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c", "cpd1_e"))


class ModelCompoundTests(unittest.TestCase):
    def test_add_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c",))

    def test_compound_independence(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        compound = Compound(base_id="cpd1", compartment="CYTOSOL")
        m1 = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m2 = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m1.add_compound(compound)
        m2.add_compound(compound)
        m2.compounds["cpd1_c"].in_reaction.add("rxn1_c")
        self.assertEqual(m1.compounds["cpd1_c"].in_reaction, set())
        self.assertEqual(m2.compounds["cpd1_c"].in_reaction, {"rxn1_c"})

    def test_add_compound_nonsense_input_str(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        with self.assertRaises(TypeError):
            m.add_compound("cpd")

    def test_add_compound_nonsense_input_int(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        with self.assertRaises(TypeError):
            m.add_compound(1)

    def test_add_compound_nonsense_input_float(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        with self.assertRaises(TypeError):
            m.add_compound(1.0)

    def test_add_compound_nonsense_input_none(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        with self.assertRaises(TypeError):
            m.add_compound(None)

    def test_add_compound_nonsense_input_list(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        cpd1 = Compound(base_id="cpd1", compartment="CYTOSOL")
        with self.assertRaises(TypeError):
            m.add_compound([cpd1])

    def test_add_compound_nonsense_input_set(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        cpd1 = Compound(base_id="cpd1", compartment="CYTOSOL")
        with self.assertRaises(TypeError):
            m.add_compound({cpd1})

    def test_add_compound_nonsense_input_dict(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        cpd1 = Compound(base_id="cpd1", compartment="CYTOSOL")
        with self.assertRaises(TypeError):
            m.add_compound({"key": cpd1})

    def test_add_compound_nonsense_input_dict2(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        cpd1 = Compound(base_id="cpd1", compartment="CYTOSOL")
        with self.assertRaises(TypeError):
            m.add_compound({cpd1: "value"})

    def test_add_compounds(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c", "cpd2_c"))

    def test_add_compartment_compound_variant_extracellular(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_compartment_compound_variant("cpd1_c", "EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.compounds["cpd1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["cpd1_e"].compartment, "EXTRACELLULAR")

    def test_add_compartment_compound_variant_in_reaction(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(Reaction(id="rxn1_c", base_id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        m.add_compartment_compound_variant("cpd1_c", "EXTRACELLULAR")
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, set(["rxn1_c"]))
        self.assertEqual(m.compounds["cpd1_e"].in_reaction, set())

    def test_add_compartment_compound_missing_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        with self.assertRaises(KeyError):
            m.add_compartment_compound_variant("cpd1_c", "EXTRACELLULAR")

    def test_set_compound_property(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        cpd1 = Compound(base_id="cpd1", compartment="CYTOSOL")
        m.add_compound(cpd1)
        m.set_compound_property(
            "cpd1_c",
            {
                "id": "cpd1_c",
                "name": "cpd2_c",
                "formula": {"C": 1, "H": 4},
                "charge": 5,
                "gibbs0": 4,
                "compartment": "_p",
                "smiles": "CH4",
                "types": ["Some type"],
                "in_reaction": ["rxn1_c"],
            },
        )
        self.assertEqual(m.compounds["cpd1_c"].id, "cpd1_c")
        self.assertEqual(m.compounds["cpd1_c"].name, "cpd2_c")
        self.assertEqual(m.compounds["cpd1_c"].formula, {"C": 1, "H": 4})
        self.assertEqual(m.compounds["cpd1_c"].charge, 5)
        self.assertEqual(m.compounds["cpd1_c"].gibbs0, 4)
        self.assertEqual(m.compounds["cpd1_c"].compartment, "_p")
        self.assertEqual(m.compounds["cpd1_c"].smiles, "CH4")
        self.assertEqual(m.compounds["cpd1_c"].types, ["Some type"])
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, ["rxn1_c"])

    def test_set_compound_property_wrong_key(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        cpd1 = Compound(base_id="cpd1", compartment="CYTOSOL")
        m.add_compound(cpd1)
        with self.assertRaises(KeyError):
            m.set_compound_property("cpd1_c", {"bogus-key": "bogus-value"})

    def test_remove_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.remove_compound("cpd1_c")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd2_c",))

    def test_remove_compounds_tuple(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.remove_compounds(("cpd1_c", "cpd3_c"))
        self.assertEqual(tuple(m.compounds.keys()), ("cpd2_c",))

    def test_remove_compounds_list(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.remove_compounds(["cpd1_c", "cpd3_c"])
        self.assertEqual(tuple(m.compounds.keys()), ("cpd2_c",))

    def test_remove_compounds_set(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.remove_compounds({"cpd1_c", "cpd3_c"})
        self.assertEqual(tuple(m.compounds.keys()), ("cpd2_c",))

    def test_remove_compounds_dict(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.remove_compounds({"cpd1_c": 1, "cpd3_c": 1})
        self.assertEqual(tuple(m.compounds.keys()), ("cpd2_c",))

    def test_remove_compound_types(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", types=["type1"]),
                Compound(base_id="cpd2", compartment="CYTOSOL", types=["type1"]),
            )
        )
        m.remove_compound(compound_id="cpd1_c")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd2_c",))
        self.assertEqual(m._compound_types, {"type1": {"cpd2_c"}})
        m.remove_compound(compound_id="cpd2_c")
        self.assertFalse(bool(m.compounds))
        self.assertFalse(bool(m._compound_types))

    def test_remove_nonexistant_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        with self.assertRaises(KeyError):
            m.remove_compound("cpd3")

    def test_get_reactions_of_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        v1 = Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1})
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(v1)
        self.assertEqual(m.get_reactions_of_compound("cpd1_c"), set(["v1"]))
        self.assertEqual(m.get_reactions_of_compound("cpd2_c"), set(["v1"]))

    def test_get_compounds_of_compartment(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m.add_compounds(
            (
                Compound(base_id="cpd0", compartment="CYTOSOL"),
                Compound(base_id="cpd1", compartment="PERIPLASM"),
                Compound(base_id="cpd2", compartment="EXTRACELLULAR"),
            )
        )
        self.assertEqual(m.get_compounds_of_compartment(compartment_id="CYTOSOL"), ["cpd0_c"])
        self.assertEqual(m.get_compounds_of_compartment(compartment_id="PERIPLASM"), ["cpd1_p"])
        self.assertEqual(m.get_compounds_of_compartment(compartment_id="EXTRACELLULAR"), ["cpd2_e"])
        with self.assertRaises(KeyError):
            m.get_compounds_of_compartment(compartment_id="GARBAGE")

    def test_compound_getters(self):
        m = Model()
        m.add_compartment(compartment_id="cytosol", compartment_suffix="c")
        m.add_compound(
            compound=Compound(
                base_id="cpd1",
                formula={"C": 6, "H": 12, "O": 6},
                charge=1,
                compartment="cytosol",
                gibbs0=1,
                name="Compound One",
                smiles="ABCDEFG",
                types=["type1", "type2"],
                in_reaction=["rxn1"],
                database_links={"kegg": "some-cpd-id"},
            )
        )

        self.assertEqual(m.get_compound_compartment_variants(compound_base_id="cpd1"), {"cpd1_c"})
        self.assertEqual(m.get_compound_base_id(compound_id="cpd1_c"), "cpd1")
        self.assertEqual(m.get_compound_compartment(compound_id="cpd1_c"), "cytosol")
        self.assertEqual(m.get_compound_formula(compound_id="cpd1_c"), {"C": 6, "H": 12, "O": 6})
        self.assertEqual(m.get_compound_charge(compound_id="cpd1_c"), 1)
        self.assertEqual(m.get_compound_gibbs0(compound_id="cpd1_c"), 1)
        self.assertEqual(
            m.get_compound_database_links(compound_id="cpd1_c"),
            {"kegg": "some-cpd-id"},
        )
        self.assertEqual(m.get_compounds_of_type(compound_type="type1"), {"cpd1_c"})
        self.assertEqual(m.get_base_compound_ids(), {"cpd1"})
        self.assertEqual(m.get_compound_type_ids(), {"type2", "type1"})
        self.assertEqual(m.get_compounds_of_compartment(compartment_id="cytosol"), ["cpd1_c"])


class ModelReactionTests(unittest.TestCase):
    def test_add_reaction(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        self.assertEqual(tuple(m.reactions.keys()), ("v1",))
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, {"v1"})
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, {"v1"})

    def test_add_reaction_var(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(
            Reaction(
                id="v1__var__0_c",
                base_id="v1",
                stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
            )
        )
        self.assertEqual(set(m.reactions.keys()), {"v1__var__0_c"})
        self.assertEqual(m.variant_reactions["v1"], {"v1__var__0_c"})
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, {"v1__var__0_c"})
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, {"v1__var__0_c"})

    def test_add_reaction_fail_on_wrong_type(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        with self.assertRaises(TypeError):
            m.add_reaction("v1")

    def test_set_reaction_property(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        m.set_reaction_property(
            "v1",
            {
                "id": "v1",
                "name": "v1",
                "stoichiometries": {"cpd1_c": 1, "cpd2_c": -1},
                "bounds": (-1000, 1000),
                "reversible": True,
                "gibbs0": 5,
                "ec": "5.4.123.2",
                "pathways": ["pwy-101"],
            },
        )
        self.assertEqual(m.reactions["v1"].id, "v1")
        self.assertEqual(m.reactions["v1"].name, "v1")
        self.assertEqual(m.reactions["v1"].stoichiometries, {"cpd1_c": 1, "cpd2_c": -1})
        self.assertEqual(m.reactions["v1"].bounds, (-1000, 1000))
        self.assertEqual(m.reactions["v1"].reversible, True)
        self.assertEqual(m.reactions["v1"].gibbs0, 5)
        self.assertEqual(m.reactions["v1"].ec, "5.4.123.2")
        self.assertEqual(m.reactions["v1"].pathways, ["pwy-101"])

    def test_set_reaction_property_wrong_key(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}))
        with self.assertRaises(KeyError):
            m.set_reaction_property("v1", {"bogus-key": "bogus-value"})

    def test_remove_reaction(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
            )
        )
        m.remove_reaction("v1")
        self.assertEqual(tuple(m.reactions.keys()), ("v2",))

    def test_remove_reaction_var(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    pathways={"PWY101"},
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    pathways={"PWY101"},
                ),
            )
        )
        self.assertEqual(m.pathways["PWY101"], {"rxn1__var__1_c", "rxn1__var__0_c"})
        self.assertEqual(m.variant_reactions["rxn1"], {"rxn1__var__1_c", "rxn1__var__0_c"})
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, {"rxn1__var__1_c", "rxn1__var__0_c"})
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, {"rxn1__var__1_c", "rxn1__var__0_c"})

        m.remove_reaction("rxn1__var__0_c")
        self.assertEqual(m.pathways["PWY101"], {"rxn1__var__1_c"})
        self.assertEqual(m.variant_reactions["rxn1"], {"rxn1__var__1_c"})
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, {"rxn1__var__1_c"})
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, {"rxn1__var__1_c"})

        m.remove_reaction("rxn1__var__1_c")
        with self.assertRaises(KeyError):
            m.pathways["PWY101"]
        with self.assertRaises(KeyError):
            m.variant_reactions["rxn1"]
        with self.assertRaises(KeyError):
            m.compounds["cpd1_c"]
        with self.assertRaises(KeyError):
            m.compounds["cpd2_c"]

    def test_remove_reaction_compound_in_reaction(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
            )
        )
        m.remove_reaction("v1")
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, set(["v2"]))
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, set(["v2"]))

    def test_remove_reaction_types(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="v1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    types=["type1"],
                ),
                Reaction(
                    id="v2",
                    stoichiometries={"cpd1_c": 1, "cpd2_c": -1},
                    types=["type1"],
                ),
            )
        )
        m.remove_reaction("v1")
        self.assertEqual(m._reaction_types["type1"], {"v2"})
        m.remove_reaction("v2")
        self.assertFalse(bool(m._reaction_types))

    def test_remove_reactions_tuple(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
                Reaction(id="v3", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
            )
        )
        m.remove_reactions(("v1", "v3"))
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, set(["v2"]))
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, set(["v2"]))

    def test_remove_reactions_list(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
                Reaction(id="v3", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
            )
        )
        m.remove_reactions(["v1", "v3"])
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, set(["v2"]))
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, set(["v2"]))

    def test_remove_reactions_set(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
                Reaction(id="v3", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
            )
        )
        m.remove_reactions({"v1", "v3"})
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, set(["v2"]))
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, set(["v2"]))

    def test_remove_reactions_dict(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
                Reaction(id="v3", stoichiometries={"cpd1_c": 1, "cpd2_c": -1}),
            )
        )
        m.remove_reactions({"v1": 1, "v3": 1})
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, set(["v2"]))
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, set(["v2"]))

    def test_reaction_getters(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compound(Compound(base_id="cpd1", compartment="c"))
        m.add_compound(Compound(base_id="cpd2", compartment="c"))

        reaction = Reaction(
            id="rxn1",
            base_id="rxn1",
            name="Reaction One",
            stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
            compartment="c",
            bounds=(-1000, 1000),
            reversible=True,
            gibbs0=1,
            ec="1.0.0.0",
            types=["type-1"],
            pathways={"pwy-1"},
            sequences={"monomer-1": "ABC"},
            monomers={"enzrxn-1": {"monomer-1"}},
            enzrxns={"enzrxn-1": {"km": {"cpd1": "1", "cpd2": "2"}}},
            database_links={"kegg": "some-id"},
            transmembrane=False,
        )
        m.add_reaction(reaction=reaction)

        self.assertEqual(m.get_reaction_compartment_variants(reaction_base_id="rxn1"), {"rxn1"})
        self.assertEqual(m.get_reaction_base_id(reaction_id="rxn1"), "rxn1")
        self.assertEqual(m.get_reaction_compartment(reaction_id="rxn1"), "c")
        self.assertEqual(m.get_reaction_gibbs0(reaction_id="rxn1"), 1)
        self.assertEqual(m.get_reaction_bounds(reaction_id="rxn1"), (-1000, 1000))
        self.assertEqual(m.get_reaction_reversibility(reaction_id="rxn1"), True)
        self.assertEqual(m.get_reaction_pathways(reaction_id="rxn1"), {"pwy-1"})
        self.assertEqual(m.get_reaction_sequences(reaction_id="rxn1"), {"monomer-1": "ABC"})
        self.assertEqual(m.get_reaction_types(reaction_id="rxn1"), ["type-1"])
        self.assertEqual(m.get_reaction_database_links(reaction_id="rxn1"), {"kegg": "some-id"})

        self.assertEqual(m.get_base_reaction_ids(), {"rxn1"})
        self.assertEqual(m.get_reaction_type_ids(), {"type-1"})

    def test_get_reaction_variants(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compound(Compound(base_id="cpd1", compartment="c"))
        m.add_compound(Compound(base_id="cpd2", compartment="c"))
        m.add_reaction(Reaction(id="rnx1", base_id="rxn1"))
        m.add_reaction(Reaction(id="rnx1__var__0", base_id="rxn1"))

        self.assertEqual(m.get_reaction_variants(base_reaction_id="rxn1"), {"rnx1__var__0"})

    def test_get_reactions_of_compartment(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compartment(compartment_id="e", compartment_suffix="e")
        m.add_compound(Compound(base_id="cpd1", compartment="c"))
        m.add_compound(Compound(base_id="cpd2", compartment="c"))
        m.add_compound(Compound(base_id="cpd2", compartment="e"))
        m.add_reaction(
            Reaction(
                id="rxn1",
                base_id="rxn1",
                stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                transmembrane=False,
            )
        )
        m.add_reaction(
            Reaction(
                id="rxn1_trans",
                base_id="rxn1_trans",
                compartment="e",
                stoichiometries={"cpd2_e": -1, "cpd2_c": 1},
                transmembrane=True,
            )
        )
        self.assertEqual(
            m.get_reactions_of_compartment(compartment_id="c", include_transporters=False),
            {"rxn1"},
        )
        self.assertEqual(
            m.get_reactions_of_compartment(compartment_id="c", include_transporters=True),
            {"rxn1", "rxn1_trans"},
        )

    def test_get_reversible_reactions(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v_irrev", reversible=False),
                Reaction(id="v_rev", reversible=True),
            )
        )
        self.assertEqual(m.get_reversible_reactions(), ["v_rev"])

    def test_get_irreversible_reactions(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v_irrev", reversible=False),
                Reaction(id="v_rev", reversible=True),
            )
        )
        self.assertEqual(m.get_irreversible_reactions(), ["v_irrev"])

    def test_add_pathway(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v1"),
                Reaction(id="v2"),
                Reaction(id="v3"),
            )
        )
        m.add_pathway(pathway_id="pwy-101", pathway_reactions=["v2", "v3"])
        self.assertEqual(m.pathways, {"pwy-101": {"v2", "v3"}})
        self.assertFalse(bool(m.reactions["v1"].pathways))
        self.assertEqual(m.reactions["v2"].pathways, {"pwy-101"})
        self.assertEqual(m.reactions["v3"].pathways, {"pwy-101"})

    def test_remove_pathway(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v1"),
                Reaction(id="v2"),
                Reaction(id="v3"),
            )
        )
        m.add_pathway(pathway_id="pwy-101", pathway_reactions=["v2", "v3"])
        m.remove_pathway(pathway_id="pwy-101")
        self.assertFalse(bool(m.pathways))
        self.assertFalse(bool(m.reactions["v1"].pathways))
        self.assertFalse(bool(m.reactions["v2"].pathways))
        self.assertFalse(bool(m.reactions["v3"].pathways))

    def test_add_pathway_reaction_attribute(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v1"),
                Reaction(id="v2"),
                Reaction(id="v3"),
            )
        )
        m.add_pathway("pwy-101", ["v2", "v3"])
        self.assertEqual(m.reactions["v1"].pathways, set())
        self.assertEqual(m.reactions["v2"].pathways, {"pwy-101"})
        self.assertEqual(m.reactions["v3"].pathways, {"pwy-101"})

    def test_get_reactions_of_pathway(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v1"),
                Reaction(id="v2"),
                Reaction(id="v3"),
            )
        )
        m.add_pathway("pwy-101", ["v2", "v3"])
        self.assertEqual(m.get_reactions_of_pathway("pwy-101"), {"v2", "v3"})

    def test_get_pathway_ids(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_reactions(
            (
                Reaction(id="v1"),
                Reaction(id="v2"),
                Reaction(id="v3"),
            )
        )
        m.add_pathway("pwy-101", ["v2", "v3"])
        self.assertEqual(m.get_pathway_ids(), ("pwy-101",))

    def test_add_transport_reaction_c_p(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_transport_reaction(compound_id="cpd1_c", compartment_id="PERIPLASM")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c", "cpd1_p"))
        self.assertEqual(m.reactions["TR_cpd1_c_p"].stoichiometries, {"cpd1_c": -1, "cpd1_p": 1})

    def test_add_transport_reaction_p_c(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="PERIPLASM"))
        m.add_transport_reaction(compound_id="cpd1_p", compartment_id="CYTOSOL")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_p", "cpd1_c"))
        self.assertEqual(m.reactions["TR_cpd1_p_c"].stoichiometries, {"cpd1_p": -1, "cpd1_c": 1})

    def test_add_transport_reaction_c_e(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_transport_reaction(compound_id="cpd1_c", compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["TR_cpd1_c_e"].stoichiometries, {"cpd1_c": -1, "cpd1_e": 1})

    def test_add_transport_reaction_e_c(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_transport_reaction(compound_id="cpd1_e", compartment_id="CYTOSOL")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_e", "cpd1_c"))
        self.assertEqual(m.reactions["TR_cpd1_e_c"].stoichiometries, {"cpd1_e": -1, "cpd1_c": 1})

    def test_add_transport_reaction_p_e(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="PERIPLASM"))
        m.add_transport_reaction(compound_id="cpd1_p", compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_p", "cpd1_e"))
        self.assertEqual(m.reactions["TR_cpd1_p_e"].stoichiometries, {"cpd1_p": -1, "cpd1_e": 1})

    def test_add_transport_reaction_e_p(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_transport_reaction(compound_id="cpd1_e", compartment_id="PERIPLASM")
        self.assertEqual(tuple(m.compounds.keys()), ("cpd1_e", "cpd1_p"))
        self.assertEqual(m.reactions["TR_cpd1_e_p"].stoichiometries, {"cpd1_e": -1, "cpd1_p": 1})

    def test_add_influx_base_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_influx("cpd1", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, False)

    def test_add_efflux_base_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_efflux("cpd1", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (0, 1000))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, False)

    def test_add_medium_base_compound(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_medium_component("cpd1", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (-1000, 1000))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, True)

    def test_add_influx_cytosol(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_influx("cpd1_c", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, False)

    def test_add_efflux_cytosol(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_efflux("cpd1_c", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (0, 1000))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, False)

    def test_add_medium_cytosol(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_medium_component("cpd1_c", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd1_e"))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (-1000, 1000))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, True)

    def test_add_influx_extracellular(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_influx("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_e",))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, False)

    def test_add_efflux_extracellular(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_efflux("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_e",))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (0, 1000))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, False)

    def test_add_medium_extracellular(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_medium_component("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        self.assertEqual(tuple(m.compounds), ("cpd1_e",))
        self.assertEqual(m.reactions["EX_cpd1_e"].stoichiometries, {"cpd1_e": -1})
        self.assertEqual(m.reactions["EX_cpd1_e"].bounds, (-1000, 1000))
        self.assertEqual(m.reactions["EX_cpd1_e"].reversible, True)

    def test_remove_influx_base_compound(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_influx("cpd1", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_influx(compound_id="cpd1")
        self.assertEqual(tuple(m.compounds), ("cpd1_c",))
        self.assertFalse(bool(m.reactions))

    def test_remove_efflux_base_compound(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_efflux("cpd1", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_efflux(compound_id="cpd1")
        self.assertEqual(tuple(m.compounds), ("cpd1_c",))
        self.assertFalse(bool(m.reactions))

    def test_remove_medium_base_compound(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_medium_component("cpd1", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_medium_component(compound_id="cpd1")
        self.assertEqual(tuple(m.compounds), ("cpd1_c",))
        self.assertFalse(bool(m.reactions))

    def test_remove_influx_cytosol(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_influx("cpd1_c", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_influx(compound_id="cpd1_c")
        self.assertEqual(tuple(m.compounds), ("cpd1_c",))
        self.assertFalse(bool(m.reactions))

    def test_remove_efflux_cytosol(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_efflux("cpd1_c", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_efflux(compound_id="cpd1_c")
        self.assertEqual(tuple(m.compounds), ("cpd1_c",))
        self.assertFalse(bool(m.reactions))

    def test_remove_medium_cytosol(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="CYTOSOL"))
        m.add_medium_component("cpd1_c", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_medium_component(compound_id="cpd1_c")
        self.assertEqual(tuple(m.compounds), ("cpd1_c",))
        self.assertFalse(bool(m.reactions))

    def test_remove_influx_extracellular(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_influx("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_influx(compound_id="cpd1_e")
        self.assertFalse(tuple(m.compounds))
        self.assertFalse(bool(m.reactions))

    def test_remove_efflux_extracellular(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_efflux("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_efflux(compound_id="cpd1_e")
        self.assertFalse(tuple(m.compounds))
        self.assertFalse(bool(m.reactions))

    def test_remove_medium_extracellular(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_medium_component("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        m.remove_medium_component(compound_id="cpd1_e")
        self.assertFalse(tuple(m.compounds))
        self.assertFalse(bool(m.reactions))

    def test_remove_influx_missing(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_influx("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.remove_influx(compound_id="garbage")

    def test_remove_efflux_missing(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_efflux("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.remove_efflux(compound_id="garbage")

    def test_remove_medium_missing(self):
        compartments = {"CYTOSOL": "c", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compound(Compound(base_id="cpd1", compartment="EXTRACELLULAR"))
        m.add_medium_component("cpd1_e", extracellular_compartment_id="EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.remove_medium_component(compound_id="garbage")


class ObjectiveTests(unittest.TestCase):
    def test_set_objective_single(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
        )
        reactions = (Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.set_objective({"v1": 1})
        self.assertEqual(m.objective, {"v1": 1})

    def test_set_objective_multiple(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="v2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.set_objective({"v1": 1, "v2": 2})
        self.assertEqual(m.objective, {"v1": 1, "v2": 2})

    def test_set_objective_fail_on_missing(self):
        m = Model()
        with self.assertRaises(KeyError):
            m.set_objective(objective={"v1": 1})

    def test_init_objective(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="v2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        objective = {"v1": 1, "v2": 2}
        m = Model(
            compounds=compounds,
            reactions=reactions,
            compartments=compartments,
            objective=objective,
        )
        self.assertEqual(m.objective, {"v1": 1, "v2": 2})


class StoichiometricMatrixTests(unittest.TestCase):
    def test_get_stoichiometric_matrix(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
            )
        )
        self.assertTrue(
            np.all(
                np.equal(
                    m.get_stoichiometric_matrix(),
                    np.array([[-1.0, 0.0], [1.0, -1.0], [0.0, 1.0]]),
                )
            )
        )

    def test_get_stoichiometric_df(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
            )
        )
        df = m.get_stoichiometric_df()
        self.assertEqual(tuple(df.index), ("cpd1_c", "cpd2_c", "cpd3_c"))
        self.assertEqual(tuple(df.columns), ("v1", "v2"))


class StructuralDuplicationTests(unittest.TestCase):
    def test_reversibility_duplication(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v_default", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(
                    id="v_irrev",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=False,
                ),
                Reaction(
                    id="v_rev",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=True,
                ),
            )
        )
        m.reversibility_duplication()
        self.assertEqual(tuple(m.reactions.keys()), ("v_default", "v_irrev", "v_rev", "v_rev__rev__"))
        self.assertEqual(m.reactions["v_rev"].stoichiometries, {"cpd1_c": -1, "cpd2_c": 1})
        self.assertEqual(m.reactions["v_rev__rev__"].stoichiometries, {"cpd1_c": 1, "cpd2_c": -1})

    def test_remove_reversibility_duplication(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(id="v_default", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
                Reaction(
                    id="v_irrev",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=False,
                ),
                Reaction(
                    id="v_rev",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=True,
                ),
            )
        )
        m.reversibility_duplication()
        m.remove_reversibility_duplication()
        self.assertEqual(tuple(m.reactions.keys()), ("v_default", "v_irrev", "v_rev"))
        self.assertEqual(m.reactions["v_rev"].stoichiometries, {"cpd1_c": -1, "cpd2_c": 1})

    def test_cofactor_duplication(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="v0",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                ),
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "ATP_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": -1, "cpd2_c": 1, "ADP_c": 1}),
            )
        )
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_duplication()
        self.assertEqual(
            tuple(m.compounds),
            (
                "cpd1_c",
                "cpd2_c",
                "ATP_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            ),
        )
        self.assertEqual(tuple(m.reactions), ("v0", "v1", "v2", "v0__cof__"))
        self.assertEqual(
            m.reactions["v0"].stoichiometries,
            {"cpd1_c": -1, "cpd2_c": 1, "ATP_c": -1, "ADP_c": 1},
        )
        self.assertEqual(m.reactions["v1"].stoichiometries, {"cpd1_c": -1, "ATP_c": -1, "cpd2_c": 1})
        self.assertEqual(m.reactions["v2"].stoichiometries, {"cpd1_c": -1, "cpd2_c": 1, "ADP_c": 1})
        self.assertEqual(
            m.reactions["v0__cof__"].stoichiometries,
            {"cpd1_c": -1, "cpd2_c": 1, "ATP_c__cof__": -1, "ADP_c__cof__": 1},
        )

    def test_remove_cofactor_duplication(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="v0",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                ),
                Reaction(id="v1", stoichiometries={"cpd1_c": -1, "ATP_c": -1, "cpd2_c": 1}),
                Reaction(id="v2", stoichiometries={"cpd1_c": -1, "cpd2_c": 1, "ADP_c": 1}),
            )
        )
        m.cofactor_duplication()
        m.remove_cofactor_duplication()
        self.assertEqual(tuple(m.compounds), ("cpd1_c", "cpd2_c", "ATP_c", "ADP_c"))
        self.assertEqual(tuple(m.reactions), ("v0", "v1", "v2"))
        self.assertEqual(
            m.reactions["v0"].stoichiometries,
            {"cpd1_c": -1, "cpd2_c": 1, "ATP_c": -1, "ADP_c": 1},
        )
        self.assertEqual(m.reactions["v1"].stoichiometries, {"cpd1_c": -1, "ATP_c": -1, "cpd2_c": 1})
        self.assertEqual(m.reactions["v2"].stoichiometries, {"cpd1_c": -1, "cpd2_c": 1, "ADP_c": 1})


class QualityControlTests(unittest.TestCase):
    def test_charge_balance_both_zero(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=0),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=0),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertTrue(m.check_charge_balance("v1"))

    def test_charge_balance_both_one(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertTrue(m.check_charge_balance("v1"))

    def test_charge_balance_substrate_stoichiometry(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=2),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -2, "cpd2_c": 1}),))
        self.assertTrue(m.check_charge_balance("v1"))

    def test_charge_balance_product_stoichiometry(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=2),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 2}),))
        self.assertTrue(m.check_charge_balance("v1"))

    def test_charge_balance_fail_on_opposite_signs(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=-1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertFalse(m.check_charge_balance("v1"))

    def test_charge_balance_fail_on_opposite_signs2(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=-1),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertFalse(m.check_charge_balance("v1"))

    def test_check_charge_balance_verbose(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            m.check_charge_balance("v1", verbose=True)
            self.assertEqual(
                mock_stdout.getvalue().split("\n"),
                ["Substrate charge: 1", "Product charge: 1", ""],
            )

    def test_mass_balance_single_atom(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", formula={"C": 1}),
                Compound(base_id="cpd2", compartment="CYTOSOL", formula={"C": 1}),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertTrue(m.check_mass_balance("v1"))

    def test_check_mass_balance_verbose(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", formula={"C": 1}),
                Compound(base_id="cpd2", compartment="CYTOSOL", formula={"C": 1}),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            m.check_mass_balance("v1", verbose=True)
            self.assertEqual(
                mock_stdout.getvalue().split("\n"),
                ["{'C': 1}", "{'C': 1}", ""],
            )

    def test_mass_balance_multiple_atoms(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
                Compound(
                    base_id="cpd2",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertTrue(m.check_mass_balance("v1"))

    def test_check_mass_balance_missing_atom(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
                Compound(
                    base_id="cpd2",
                    compartment="CYTOSOL",
                    formula={
                        "C": 6,
                        "H": 12,
                    },
                ),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),))
        self.assertFalse(m.check_mass_balance(reaction_id="v1"))

    def test_mass_balance_multiple_compounds(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
                Compound(
                    base_id="cpd2",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
                Compound(base_id="cpd3", compartment="CYTOSOL", formula={"C": 6}),
                Compound(base_id="cpd4", compartment="CYTOSOL", formula={"C": 6}),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="v1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "cpd3_c": -2,
                        "cpd2_c": 1,
                        "cpd4_c": 2,
                    },
                ),
            )
        )
        self.assertTrue(m.check_mass_balance("v1"))

    def test_mass_balance_multiple_atoms_substrate_stoichiometry(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 3, "H": 6, "O": 3},
                ),
                Compound(
                    base_id="cpd2",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -2, "cpd2_c": 1}),))
        self.assertTrue(m.check_mass_balance("v1"))

    def test_mass_balance_multiple_atoms_product_stoichiometry(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 6, "H": 12, "O": 6},
                ),
                Compound(
                    base_id="cpd2",
                    compartment="CYTOSOL",
                    formula={"C": 3, "H": 6, "O": 3},
                ),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 2}),))
        self.assertTrue(m.check_mass_balance("v1"))

    def test_mass_balance_fail_on_missing_substrate_formula(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", formula={}),
                Compound(
                    base_id="cpd2",
                    compartment="CYTOSOL",
                    formula={"C": 3, "H": 6, "O": 3},
                ),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 2}),))
        self.assertFalse(m.check_mass_balance("v1"))

    def test_mass_balance_fail_on_missing_product_formula(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 3, "H": 6, "O": 3},
                ),
                Compound(base_id="cpd2", compartment="CYTOSOL", formula={}),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 2}),))
        self.assertFalse(m.check_mass_balance("v1"))

    def test_mass_balance_fail_on_missing_substrate_atom(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", formula={"C": 1}),
                Compound(base_id="cpd2", compartment="CYTOSOL", formula={"C": 1, "H": 1}),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 2}),))
        self.assertFalse(m.check_mass_balance("v1"))

    def test_mass_balance_fail_on_missing_product_atom(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", formula={"C": 1, "H": 1}),
                Compound(base_id="cpd2", compartment="CYTOSOL", formula={"C": 1}),
            )
        )
        m.add_reactions((Reaction(id="v1", stoichiometries={"cpd1_c": -1, "cpd2_c": 2}),))
        self.assertFalse(m.check_mass_balance("v1"))


class UpdateFromReferenceTests(unittest.TestCase):
    def test_add_cpd_from_ref_new(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compound(
            Compound(
                base_id="cpd1",
                compartment="CYTOSOL",
                formula={"C": 1},
                charge=1,
                gibbs0=10,
                smiles="abc",
                types=["cpd"],
            )
        )
        m.add_compound_from_reference(db, "cpd1_c")
        cpd = m.compounds["cpd1_c"]
        self.assertEqual(cpd.id, "cpd1_c")
        self.assertEqual(cpd.formula, {"C": 1})
        self.assertEqual(cpd.charge, 1)
        self.assertEqual(cpd.gibbs0, 10)
        self.assertEqual(cpd.smiles, "abc")
        self.assertEqual(cpd.types, ["cpd"])
        self.assertEqual(cpd.in_reaction, set())

    def test_add_cpd_from_ref_existing(self):
        """Should keep the in_reaction attribute"""
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)

        db.add_compounds(
            (
                Compound(
                    base_id="cpd1",
                    compartment="CYTOSOL",
                    formula={"C": 1},
                    charge=1,
                    gibbs0=10,
                    smiles="abc",
                    types=["cpd"],
                    in_reaction={"rxn2_c"},
                ),
            )
        )
        m.add_compounds((Compound(base_id="cpd1", compartment="CYTOSOL", in_reaction={"rxn1_c"}),))
        m.add_compound_from_reference(db, "cpd1_c")
        cpd = m.compounds["cpd1_c"]
        self.assertEqual(cpd.id, "cpd1_c")
        self.assertEqual(cpd.formula, {"C": 1})
        self.assertEqual(cpd.charge, 1)
        self.assertEqual(cpd.gibbs0, 10)
        self.assertEqual(cpd.smiles, "abc")
        self.assertEqual(cpd.types, ["cpd"])
        self.assertEqual(cpd.in_reaction, {"rxn1_c"})

    def test_add_reaction_from_ref_new(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
                Reaction(
                    id="rxn2_c",
                    base_id="rxn2",
                    stoichiometries={"cpd2_c": -1, "cpd3_c": 1},
                ),
                Reaction(
                    id="rxn3_c",
                    base_id="rxn3",
                    stoichiometries={"cpd1_c": -1, "cpd3_c": 1},
                    pathways={"pwy1"},
                ),
            ),
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
                Reaction(
                    id="rxn2_c",
                    base_id="rxn2",
                    stoichiometries={"cpd2_c": -1, "cpd3_c": 1},
                ),
            )
        )
        m.add_reaction_from_reference(db, "rxn3_c")
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, {"rxn1_c", "rxn3_c"})
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, {"rxn1_c", "rxn2_c"})
        self.assertEqual(m.compounds["cpd3_c"].in_reaction, {"rxn2_c", "rxn3_c"})
        self.assertEqual(dict(m.pathways), {"pwy1": {"rxn3_c"}})

    def test_add_reaction_replacing(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            ),
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
                Reaction(
                    id="rxn2_c",
                    base_id="rxn2",
                    stoichiometries={"cpd2_c": -1, "cpd3_c": 1},
                ),
                Reaction(
                    id="rxn3_c",
                    base_id="rxn3",
                    stoichiometries={"cpd1_c": -1, "cpd3_c": 1},
                    reversible=True,
                    pathways={"pwy0"},
                ),
            ),
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="cpd3", compartment="CYTOSOL"),
            ),
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
                Reaction(
                    id="rxn2_c",
                    base_id="rxn2",
                    stoichiometries={"cpd2_c": -1, "cpd3_c": 1},
                ),
                Reaction(
                    id="rxn3_c",
                    base_id="rxn3",
                    stoichiometries={"cpd2_c": -2, "cpd3_c": 2},
                    reversible=False,
                    pathways={"pwy1"},
                ),
            )
        )
        m.add_reaction_from_reference(db, "rxn3_c")
        self.assertEqual(m.compounds["cpd1_c"].in_reaction, {"rxn1_c", "rxn3_c"})
        self.assertEqual(m.compounds["cpd2_c"].in_reaction, {"rxn1_c", "rxn2_c"})
        self.assertEqual(m.compounds["cpd3_c"].in_reaction, {"rxn2_c", "rxn3_c"})

        self.assertEqual(m.reactions["rxn3_c"].stoichiometries, {"cpd1_c": -1, "cpd3_c": 1})
        self.assertTrue(m.reactions["rxn3_c"].reversible)
        self.assertEqual(dict(m.pathways), {"pwy0": {"rxn3_c"}})

    def test_add_from_reference(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c"})

    def test_add_reaction_from_reference_missing_in_reference(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compartments=compartments)
        m = Model(compartments=compartments)
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        m.add_reaction(
            Reaction(
                id="rxn1_c",
                base_id="rxn1",
                stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
            )
        )
        with self.assertRaises(KeyError):
            m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")

    def test_add_multiple_from_reference(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
                Reaction(
                    id="rxn2_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_reactions_from_reference(reference_model=db, reaction_ids=["rxn1_c", "rxn2_c"])
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn2_c"})

    def test_add_from_reference_cof_removal_afterwards(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"ATP_c": -1, "ADP_c": 1},
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(set(m.compounds.keys()), {"ATP_c", "ATP_c__cof__", "ADP_c__cof__", "ADP_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__cof__"})
        m.remove_cofactor_duplication()
        self.assertEqual(set(m.compounds.keys()), {"ATP_c", "ADP_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c"})

    def test_add_from_reference_cof_removal_afterwards_2(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"ATP_c": -1, "ADP_c": 1},
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c__cof__")
        self.assertEqual(set(m.compounds.keys()), {"ATP_c", "ATP_c__cof__", "ADP_c__cof__", "ADP_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__cof__"})
        m.remove_cofactor_duplication()
        self.assertEqual(set(m.compounds.keys()), {"ATP_c", "ADP_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c"})

    def test_add_from_reference_rev_removal_afterwards(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=True,
                ),
            )
        )
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__rev__"})
        m.remove_reversibility_duplication()
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c"})

    def test_add_from_reference_rev_removal_afterwards_2(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=True,
                ),
            )
        )
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c__rev__")
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__rev__"})
        m.remove_reversibility_duplication()
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c"})

    def test_add_from_reference_cof(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__cof__"})

    def test_add_from_reference_rev(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=True,
                ),
            )
        )
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__rev__"})

    def test_add_from_reference_cof_and_rev(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1_c", "rxn1_c__rev__", "rxn1_c__cof____rev__", "rxn1_c__cof__"},
        )

    def test_add_from_reference_var_base_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(
            set(m.compounds.keys()),
            {"cpd1_c", "ATP_c", "cpd2_c", "ADP_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1__var__0_c", "rxn1__var__1_c"},
        )

    def test_add_from_reference_var_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c")
        self.assertEqual(
            set(m.compounds.keys()),
            {"cpd1_c", "ATP_c", "cpd2_c", "ADP_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1__var__0_c", "rxn1__var__1_c"},
        )

    def test_add_from_reference_var_cof_rev_base_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(
            set(m.compounds.keys()),
            {"ATP_c__cof__", "ADP_c__cof__", "ADP_c", "cpd2_c", "ATP_c", "cpd1_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof____rev__",
                "rxn1__var__1_c",
                "rxn1__var__1_c__cof__",
                "rxn1__var__1_c__rev__",
                "rxn1__var__1_c__cof____rev__",
            },
        )

    def test_add_from_reference_var_cof_rev_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c")
        self.assertEqual(
            set(m.compounds.keys()),
            {"ATP_c__cof__", "ADP_c__cof__", "ADP_c", "cpd2_c", "ATP_c", "cpd1_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof____rev__",
                "rxn1__var__1_c",
                "rxn1__var__1_c__cof__",
                "rxn1__var__1_c__rev__",
                "rxn1__var__1_c__cof____rev__",
            },
        )

    def test_replace_from_reference(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_old_c": -1, "cpd2_old_c": 1},
                ),
            )
        )
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1_c")
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c"})

    def test_replace_from_reference_cof(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "cpd2_c",
                "ATP_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__cof__"})

    def test_replace_from_reference_rev(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_old_c": -1, "cpd2_old_c": 1},
                    reversible=True,
                ),
            )
        )
        db.reversibility_duplication()
        m.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(set(m.compounds.keys()), {"cpd1_c", "cpd2_c"})
        self.assertEqual(set(m.reactions.keys()), {"rxn1_c", "rxn1_c__rev__"})

    def test_replace_from_reference_cof_and_rev(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1_c", "rxn1_c__rev__", "rxn1_c__cof____rev__", "rxn1_c__cof__"},
        )

    def test_replace_from_reference_var_base_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(
            set(m.compounds.keys()),
            {"cpd1_c", "ATP_c", "cpd2_c", "ADP_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1__var__0_c", "rxn1__var__1_c"},
        )

    def test_replace_from_reference_var_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c")
        self.assertEqual(
            set(m.compounds.keys()),
            {"cpd1_c", "ATP_c", "cpd2_c", "ADP_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1__var__0_c", "rxn1__var__1_c"},
        )

    def test_replace_from_reference_var_cof_rev_base_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_duplication()
        m.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1")
        self.assertEqual(
            set(m.compounds.keys()),
            {"ATP_c__cof__", "ADP_c__cof__", "ADP_c", "cpd2_c", "ATP_c", "cpd1_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof____rev__",
                "rxn1__var__1_c",
                "rxn1__var__1_c__cof__",
                "rxn1__var__1_c__rev__",
                "rxn1__var__1_c__cof____rev__",
            },
        )

    def test_replace_from_reference_var_cof_rev_id(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_duplication()
        m.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c")
        self.assertEqual(
            set(m.compounds.keys()),
            {"ATP_c__cof__", "ADP_c__cof__", "ADP_c", "cpd2_c", "ATP_c", "cpd1_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__cof____rev__",
                "rxn1__var__1_c",
                "rxn1__var__1_c__rev__",
                "rxn1__var__1_c__cof__",
                "rxn1__var__1_c__cof____rev__",
            },
        )

    def test_add_from_reference_rev_input(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c__rev__")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__cof____rev__",
            },
        )

    def test_add_from_reference_cof_input(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c__cof__")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__cof____rev__",
            },
        )

    def test_replace_from_reference_rev_input(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_duplication()
        m.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c__rev__")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__cof____rev__",
            },
        )

    def test_replace_from_reference_cof_input(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
                Compound(base_id="ATP", compartment="CYTOSOL"),
                Compound(base_id="ADP", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        db.reversibility_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_duplication()
        m.reversibility_duplication()
        m.add_reaction_from_reference(reference_model=db, reaction_id="rxn1__var__0_c__cof__")
        self.assertEqual(
            set(m.compounds.keys()),
            {
                "cpd1_c",
                "ATP_c",
                "cpd2_c",
                "ADP_c",
                "ATP_c__cof__",
                "ADP_c__cof__",
            },
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {
                "rxn1__var__0_c",
                "rxn1__var__0_c__rev__",
                "rxn1__var__0_c__cof__",
                "rxn1__var__0_c__cof____rev__",
            },
        )

    def test_update_from_reference_var(self):
        compounds = (
            Compound(base_id="ATP", compartment="CYTOSOL"),
            Compound(base_id="ADP", compartment="CYTOSOL"),
        )
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL"),
                Compound(base_id="cpd2", compartment="CYTOSOL"),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
                Reaction(
                    id="rxn1__var__1_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_c": -1,
                        "ATP_c": -1,
                        "cpd2_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1_old", compartment="CYTOSOL"),
                Compound(base_id="cpd2_old", compartment="CYTOSOL"),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1__var__0_c",
                    base_id="rxn1",
                    stoichiometries={
                        "cpd1_old_c": -1,
                        "ATP_c": -1,
                        "cpd2_old_c": 1,
                        "ADP_c": 1,
                    },
                    reversible=True,
                ),
            )
        )
        m.update_from_reference(reference_model=db)
        self.assertEqual(
            set(m.compounds.keys()),
            {"cpd1_c", "ATP_c", "cpd2_c", "ADP_c"},
        )
        self.assertEqual(
            set(m.reactions.keys()),
            {"rxn1__var__0_c", "rxn1__var__1_c"},
        )

    def test_update_model_remove_unbalanced(self):
        compounds = {}
        reactions = {}
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1_c",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=2),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn2",
                    base_id="rxn2",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
            )
        )
        m.update_from_reference(db)
        self.assertEqual(m.reactions, {})

    def test_update_model_remove_unmapped_unbalanced(self):
        """Remove reactions that are unbalanced after the update of a compound"""
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compartments=compartments)
        m = Model(compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=2),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
                Reaction(
                    id="rxn2",
                    base_id="rxn2",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
            )
        )
        m.update_from_reference(db)
        self.assertEqual(set(m.reactions), {"rxn1"})

    def test_update_model_remove_unmapped_unbalanced_mass_verbose(self):
        """Remove reactions that are unbalanced after the update of a compound"""
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compartments=compartments)
        m = Model(compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=2, formula={"C": 1}),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1, formula={"C": 1}),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=2, formula={"C": 2}),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1, formula={"C": 1}),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
                Reaction(
                    id="rxn2",
                    base_id="rxn2",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
            )
        )
        m.update_from_reference(reference_model=db, verbose=True)
        self.assertEqual(set(m.reactions), {"rxn1"})

    def test_update_model_remove_unmapped_unbalanced_charge_verbose(self):
        """Remove reactions that are unbalanced after the update of a compound"""
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        db = Model(compartments=compartments)
        m = Model(compartments=compartments)
        db.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=1, formula={"C": 2}),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1, formula={"C": 1}),
            )
        )
        db.add_reactions(
            (
                Reaction(
                    id="rxn1",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 1},
                ),
            )
        )
        m.add_compounds(
            (
                Compound(base_id="cpd1", compartment="CYTOSOL", charge=2, formula={"C": 2}),
                Compound(base_id="cpd2", compartment="CYTOSOL", charge=1, formula={"C": 1}),
            )
        )
        m.add_reactions(
            (
                Reaction(
                    id="rxn1",
                    base_id="rxn1",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
                Reaction(
                    id="rxn2",
                    base_id="rxn2",
                    stoichiometries={"cpd1_c": -1, "cpd2_c": 2},
                ),
            )
        )
        m.update_from_reference(reference_model=db, verbose=True)
        self.assertEqual(set(m.reactions), {"rxn1"})


class StructuralTests(unittest.TestCase):
    def test_get_biomass_template(self):
        expected = {
            "TRP_c": -0.055234,
            "GLT_c": -0.255712,
            "MALONYL-COA_c": -3.1e-05,
            "GTP_c": -0.209121,
            "NADP_c": -0.000112,
            "WATER_c": -48.752916,
            "LEU_c": -0.437778,
            "ASN_c": -0.234232,
            "L-ASPARTATE_c": -0.234232,
            "L-ALPHA-ALANINE_c": -0.499149,
            "ARG_c": -0.28742,
            "TYR_c": -0.133993,
            "THR_c": -0.246506,
            "CTP_c": -0.129799,
            "SER_c": -0.209684,
            "ATP_c": -54.119975,
            "GLN_c": -0.255712,
            "MET_c": -0.149336,
            "LYS_c": -0.333448,
            "ACETYL-COA_c": -0.000279,
            "CYS_c": -0.088988,
            "HIS_c": -0.092056,
            "VAL_c": -0.411184,
            "UTP_c": -0.140101,
            "ILE_c": -0.282306,
            "NADPH_c": -0.000335,
            "NAD_c": -0.001787,
            "PRO_c": -0.214798,
            "PHE_c": -0.180021,
            "GLY_c": -0.595297,
            "Pi_c": 53.945874,
            "PROTON_c": 51.472,
            "ADP_c": 53.95,
        }
        m = Model()
        biomass = m.get_biomass_template(organism="ecoli")
        self.assertEqual(biomass, expected)

    def test_get_biomass_template_fail_on_missing(self):
        m = Model()
        with self.assertRaises(KeyError):
            m.get_biomass_template(organism="garbage")

    def test_add_cofactor_pair(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compound(Compound(base_id="ATP", compartment="c"))
        m.add_compound(Compound(base_id="ADP", compartment="c"))
        m.add_cofactor_pair(strong_cofactor_base_id="ATP", weak_cofactor_base_id="ADP")
        self.assertEqual(m.cofactor_pairs, {"ATP_c": "ADP_c"})

    def test_add_cofactor_pair_multiple_compartments(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compartment(compartment_id="e", compartment_suffix="e")
        m.add_compound(Compound(base_id="ATP", compartment="c"))
        m.add_compound(Compound(base_id="ADP", compartment="c"))
        m.add_compound(Compound(base_id="ATP", compartment="e"))
        m.add_compound(Compound(base_id="ADP", compartment="e"))
        m.add_cofactor_pair(strong_cofactor_base_id="ATP", weak_cofactor_base_id="ADP")
        self.assertEqual(m.cofactor_pairs, {"ATP_c": "ADP_c", "ATP_e": "ADP_e"})

    def test_get_weak_cofactors(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compartment(compartment_id="e", compartment_suffix="e")
        m.add_compound(Compound(base_id="ATP", compartment="c"))
        m.add_compound(Compound(base_id="ADP", compartment="c"))
        m.add_compound(Compound(base_id="ATP", compartment="e"))
        m.add_compound(Compound(base_id="ADP", compartment="e"))
        m.add_cofactor_pair(strong_cofactor_base_id="ATP", weak_cofactor_base_id="ADP")
        self.assertEqual(set(m.get_weak_cofactors()), set(["ADP_c", "ADP_e"]))

    def test_get_strong_cofactors(self):

        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compartment(compartment_id="e", compartment_suffix="e")
        m.add_compound(Compound(base_id="ATP", compartment="c"))
        m.add_compound(Compound(base_id="ADP", compartment="c"))
        m.add_compound(Compound(base_id="ATP", compartment="e"))
        m.add_compound(Compound(base_id="ADP", compartment="e"))
        m.add_cofactor_pair(strong_cofactor_base_id="ATP", weak_cofactor_base_id="ADP")
        self.assertEqual(set(m.get_strong_cofactors()), set(["ATP_c", "ATP_e"]))

    def test_get_strong_cofactor_duplications(self):
        m = Model()
        m.add_compartment(compartment_id="c", compartment_suffix="c")
        m.add_compartment(compartment_id="e", compartment_suffix="e")
        m.add_compound(Compound(base_id="ATP", compartment="c"))
        m.add_compound(Compound(base_id="ADP", compartment="c"))
        m.add_compound(Compound(base_id="ATP", compartment="e"))
        m.add_compound(Compound(base_id="ADP", compartment="e"))
        m.add_cofactor_pair(strong_cofactor_base_id="ATP", weak_cofactor_base_id="ADP")
        self.assertEqual(
            set(m.get_strong_cofactor_duplications()),
            set(["ATP_c__cof__", "ATP_e__cof__"]),
        )

    def test_add_minimal_seed(self):
        m = Model()
        m.add_minimal_seed(compound_ids=("a", "b", "c"))
        self.assertEqual(m.minimal_seed, {"a", "b", "c"})

    def test_get_minimal_seed(self):
        m = Model()
        m.add_minimal_seed(compound_ids=("a", "b", "c"))
        self.assertEqual(m.get_minimal_seed(carbon_source_id="GLC"), {"GLC", "a", "b", "c"})

    def test_get_minimal_seed_fail_without_supplied(self):
        m = Model()
        with self.assertRaises(ValueError):
            m.get_minimal_seed(carbon_source_id="GLC")


class MetaCycTests(unittest.TestCase):
    def test_move_electron_transport_cofactors_to_cytosol(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p"}
        compounds = (
            Compound(base_id="ATP", compartment="CYTOSOL"),
            Compound(base_id="ATP", compartment="PERIPLASM"),
            Compound(base_id="ADP", compartment="CYTOSOL"),
            Compound(base_id="ADP", compartment="PERIPLASM"),
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd1", compartment="PERIPLASM"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="PERIPLASM"),
        )
        reactions = (
            Reaction(
                id="transporter",
                stoichiometries={"ATP_p": -1, "cpd1_p": -1, "ADP_p": 1, "cpd1_c": 1},
                transmembrane=True,
                compartment=("CYTOSOL", "PERIPLASM"),
                types=["Electron-Transfer-Reactions"],
            ),
            Reaction(
                id="only-cofactors-periplasm",
                stoichiometries={"ATP_p": -1, "cpd1_c": -1, "ADP_p": 1, "cpd2_c": 1},
                transmembrane=True,
                compartment=("CYTOSOL", "PERIPLASM"),
                types=["Electron-Transfer-Reactions"],
            ),
            Reaction(
                id="all-periplasm",
                stoichiometries={"ATP_p": -1, "cpd1_p": -1, "ADP_p": 1, "cpd2_p": 1},
                transmembrane=True,
                compartment=("PERIPLASM",),
                types=["Electron-Transfer-Reactions"],
            ),
        )
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m._move_electron_transport_cofactors_to_cytosol()

        self.assertEqual(m.reactions["transporter_c_p"].id, "transporter_c_p")
        self.assertEqual(
            m.reactions["transporter_c_p"].stoichiometries,
            {"cpd1_p": -1, "cpd1_c": 1, "ATP_c": -1, "ADP_c": 1},
        )
        self.assertEqual(m.reactions["transporter_c_p"].transmembrane, True)
        self.assertEqual(m.reactions["transporter_c_p"].compartment, ("CYTOSOL", "PERIPLASM"))

        self.assertEqual(m.reactions["only-cofactors-periplasm_c"].id, "only-cofactors-periplasm_c")
        self.assertEqual(
            m.reactions["only-cofactors-periplasm_c"].stoichiometries,
            {"cpd1_c": -1, "cpd2_c": 1, "ATP_c": -1, "ADP_c": 1},
        )
        self.assertEqual(m.reactions["only-cofactors-periplasm_c"].transmembrane, False)
        self.assertEqual(m.reactions["only-cofactors-periplasm_c"].compartment, "CYTOSOL")

        self.assertEqual(m.reactions["all-periplasm_c_p"].id, "all-periplasm_c_p")
        self.assertEqual(
            m.reactions["all-periplasm_c_p"].stoichiometries,
            {"cpd1_p": -1, "cpd2_p": 1, "ATP_c": -1, "ADP_c": 1},
        )
        self.assertEqual(m.reactions["all-periplasm_c_p"].transmembrane, True)
        self.assertEqual(m.reactions["all-periplasm_c_p"].compartment, ("CYTOSOL", "PERIPLASM"))

    def test_repair_photosynthesis_reactions(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p"}

        compounds = (
            Compound(base_id="Light", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
            Compound(base_id="PLASTOQUINONE-9", compartment="CYTOSOL"),
            Compound(base_id="OXYGEN-MOLECULE", compartment="CYTOSOL"),
            Compound(base_id="CPD-12829", compartment="CYTOSOL"),
            Compound(base_id="PROTON", compartment="PERIPLASM"),
            Compound(base_id="PROTON", compartment="CYTOSOL"),
            Compound(base_id="Oxidized-Plastocyanins", compartment="CYTOSOL"),
            Compound(base_id="CPD-12829", compartment="CYTOSOL"),
            Compound(base_id="Plastocyanin-Reduced", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(
                id="PSII-RXN__var__0_c_p",
                base_id="PSII-RXN",
                stoichiometries={
                    "Light_c": -1,
                    "WATER_c": -2.0,
                    "PLASTOQUINONE-9_c": -2.0,
                    "OXYGEN-MOLECULE_c": 1,
                    "CPD-12829_c": 2.0,
                    "PROTON_c": 4.0,
                    "PROTON_p": -4.0,
                },
                compartment=("CYTOSOL", "PERIPLASM"),
                pathways={"PWY-101"},
                transmembrane=True,
            ),
            Reaction(
                id="PLASTOQUINOL--PLASTOCYANIN-REDUCTASE-RXN__var__0_c_p",
                base_id="PLASTOQUINOL--PLASTOCYANIN-REDUCTASE-RXN",
                stoichiometries={
                    "Oxidized-Plastocyanins_c": -2.0,
                    "CPD-12829_c": -1,
                    "Plastocyanin-Reduced_c": 2.0,
                    "PLASTOQUINONE-9_c": 1,
                    "PROTON_c": 4.0,
                    "PROTON_p": -2.0,
                },
                compartment=("CYTOSOL", "PERIPLASM"),
                pathways={"PWY-101"},
                transmembrane=True,
            ),
        )

        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m._repair_photosynthesis_reactions()
        self.assertEqual(
            m.reactions["PSII-RXN__var__0_c_p"].stoichiometries,
            {
                "Light_c": -1,
                "WATER_c": -2.0,
                "PLASTOQUINONE-9_c": -2.0,
                "OXYGEN-MOLECULE_c": 1,
                "CPD-12829_c": 2.0,
                "PROTON_p": 4.0,
                "PROTON_c": -4.0,
            },
        )
        self.assertEqual(
            m.reactions["PLASTOQUINOL--PLASTOCYANIN-REDUCTASE-RXN__var__0_c_p"].stoichiometries,
            {
                "Oxidized-Plastocyanins_c": -2.0,
                "CPD-12829_c": -1,
                "Plastocyanin-Reduced_c": 2.0,
                "PLASTOQUINONE-9_c": 1,
                "PROTON_p": 4.0,
                "PROTON_c": -2.0,
            },
        )

    def test_repair_photosynthesis_reactions_isolation(self):
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p"}

        compounds = (
            Compound(base_id="PROTON", compartment="PERIPLASM"),
            Compound(base_id="PROTON", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(
                id="rxn1",
                stoichiometries={
                    "PROTON_c": -1.0,
                    "PROTON_p": 2.0,
                },
                compartment=("CYTOSOL", "PERIPLASM"),
                pathways={"PWY-101"},
                transmembrane=True,
            ),
            Reaction(
                id="rxn2",
                stoichiometries={
                    "PROTON_p": 2.0,
                },
                compartment=("CYTOSOL", "PERIPLASM"),
                pathways={"PWY-101"},
                transmembrane=True,
            ),
            Reaction(
                id="rxn3",
                stoichiometries={
                    "PROTON_c": -1.0,
                },
                compartment=("CYTOSOL", "PERIPLASM"),
                pathways={"PWY-101"},
                transmembrane=True,
            ),
        )

        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m._repair_photosynthesis_reactions()
        self.assertEqual(m.reactions["rxn1"].stoichiometries, {"PROTON_p": -1.0, "PROTON_c": 2.0})
        self.assertEqual(m.reactions["rxn2"].stoichiometries, {"PROTON_c": 2.0})
        self.assertEqual(m.reactions["rxn3"].stoichiometries, {"PROTON_p": -1.0})
