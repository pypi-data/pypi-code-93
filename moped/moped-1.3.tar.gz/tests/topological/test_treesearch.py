import unittest

from moped import Compound, Model, Reaction
from moped.topological.treesearch import _split_stoichiometries, metabolite_tree_search


class ScopePreparationTests(unittest.TestCase):
    def test_split_stoichiometries(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
        )
        reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        compartments = {"CYTOSOL": "c"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        self.assertEqual(
            _split_stoichiometries(m),
            {"rxn1": {"substrates": {"cpd1_c": -1}, "products": {"cpd2_c": 1}}},
        )

    def test_split_stoichiometries_exclude_medium_reactions(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
        )
        reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1}),)
        compartments = {"CYTOSOL": "c"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        self.assertEqual(_split_stoichiometries(m), {})

    def test_fail_on_wrong_search_type(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()

        with self.assertRaises(ValueError):
            metabolite_tree_search(
                model=m,
                start_compound_id="cpd1_c",
                end_compound_id="cpd3_c",
                max_iterations=50,
                ignored_reaction_ids=None,
                ignored_compound_ids=None,
                search_type="nonsense",
            )


class TreesearchTests(unittest.TestCase):
    def test_fail_on_missing_metabolite(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()
        with self.assertRaises(KeyError):
            m.depth_first_search(
                start_compound_id="cpd1_c",
                end_compound_id="cpd4_c",
                max_iterations=50,
            )

    def test_fail_on_no_solution(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),)
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()
        with self.assertRaises(ValueError):
            m.depth_first_search(
                start_compound_id="cpd1_c",
                end_compound_id="cpd3_c",
                max_iterations=50,
            )

    def test_fail_on_max_iterations(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()

        with self.assertRaises(ValueError):
            m.depth_first_search(
                start_compound_id="cpd1_c",
                end_compound_id="cpd3_c",
                max_iterations=1,
            )

    def test_depth_first_search(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()

        cpds, rxns = m.depth_first_search(
            start_compound_id="cpd1_c",
            end_compound_id="cpd3_c",
            max_iterations=50,
        )
        self.assertEqual(cpds, ["cpd1_c", "cpd2_c", "cpd3_c"])
        self.assertEqual(rxns, ["rxn1", "rxn2"])

    def test_breadth_first_search(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()

        cpds, rxns = m.breadth_first_search(
            start_compound_id="cpd1_c",
            end_compound_id="cpd3_c",
            max_iterations=50,
        )
        self.assertEqual(cpds, ["cpd1_c", "cpd2_c", "cpd3_c"])
        self.assertEqual(rxns, ["rxn1", "rxn2"])

    def test_metabolite_search_ignore_reactions(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}, reversible=True),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
            Reaction(id="rxn3", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}, reversible=True),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()

        cpds, rxns = m.depth_first_search(
            start_compound_id="cpd1_c",
            end_compound_id="cpd3_c",
            max_iterations=50,
            ignored_reaction_ids=["rxn2"],
        )
        self.assertEqual(cpds, ["cpd1_c", "cpd2_c", "cpd3_c"])
        self.assertEqual(rxns, ["rxn1", "rxn3"])

    def test_metabolite_search_ignore_compounds(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2.1", compartment="CYTOSOL"),
            Compound(base_id="cpd2.2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        reactions = (
            Reaction(
                id="rxn1.1",
                stoichiometries={"cpd1_c": -1, "cpd2.1_c": 1},
                reversible=True,
            ),
            Reaction(
                id="rxn1.2",
                stoichiometries={"cpd1_c": -1, "cpd2.2_c": 1},
                reversible=True,
            ),
            Reaction(
                id="rxn2.1",
                stoichiometries={"cpd2.1_c": -1, "cpd3_c": 1},
                reversible=True,
            ),
            Reaction(
                id="rxn2.2",
                stoichiometries={"cpd2.2_c": -1, "cpd3_c": 1},
                reversible=True,
            ),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.reversibility_duplication()

        cpds, rxns = m.depth_first_search(
            start_compound_id="cpd1_c",
            end_compound_id="cpd3_c",
            max_iterations=50,
            ignored_compound_ids=["cpd2.1_c"],
        )
        self.assertEqual(cpds, ["cpd1_c", "cpd2.2_c", "cpd3_c"])
        self.assertEqual(rxns, ["rxn1.2", "rxn2.2"])
