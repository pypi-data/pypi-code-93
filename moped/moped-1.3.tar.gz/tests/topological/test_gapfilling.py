import io
import unittest
import unittest.mock as mock

from moped import Compound, Model, Reaction


class GapFillingSeedTests(unittest.TestCase):
    def test_fail_on_wrong_seed_num(self):
        m = Model()
        db = Model()
        with self.assertRaises(TypeError):
            m.get_gapfilling_reactions(reference_model=db, seed=0, targets=["cpd3_c"], verbose=False)

    def test_fail_on_wrong_seed_list_num(self):
        m = Model()
        db = Model()
        with self.assertRaises(TypeError):
            m.get_gapfilling_reactions(reference_model=db, seed=[0], targets=["cpd3_c"], verbose=False)


class GapFillingTests(unittest.TestCase):
    def test_linear_chain(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        self.assertEqual(
            ["rxn2"],
            m.get_gapfilling_reactions(
                reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False
            ),
        )

    def test_linear_chain_gapfilling(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)

        gapfilling_reactions = m.get_gapfilling_reactions(
            reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False
        )
        m2 = m.copy()
        m2.gapfilling(reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False)
        self.assertEqual(set(m.reactions) | set(gapfilling_reactions), set(m2.reactions))

    def test_linear_chain_str_seed(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        self.assertEqual(
            ["rxn2"],
            m.get_gapfilling_reactions(reference_model=db, seed="cpd1_c", targets=["cpd3_c"], verbose=False),
        )

    def test_linear_chain_verbose(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            m.get_gapfilling_reactions(reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=True)
        self.assertEqual(
            mock_stdout.getvalue().split("\n"),
            [
                "Searching for ['cpd3_c'] in reference database",
                "Could produce all compounds in reference database",
                "Found 1 essential reaction(s)",
                "",
            ],
        )

    def test_linear_chain_gapfilling_verbose(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "cpd3_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            m.gapfilling(reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=True)
        self.assertEqual(
            mock_stdout.getvalue().split("\n"),
            [
                "Searching for ['cpd3_c'] in reference database",
                "Could produce all compounds in reference database",
                "Found 1 essential reaction(s)",
                "Adding reactions ['rxn2']",
                "",
            ],
        )

    def test_linear_chain_fail_verbose(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with self.assertWarns(UserWarning):
                m.get_gapfilling_reactions(
                    reference_model=m, seed=["cpd1_c"], targets=["cpd3_c"], verbose=True
                )
        self.assertEqual(
            mock_stdout.getvalue().split("\n"),
            [
                "Searching for ['cpd3_c'] in reference database",
                "Could produce [] in reference database",
                "Found 0 essential reaction(s)",
                "",
            ],
        )

    def test_linear_chain_fail_on_missing(self):
        model_compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        db_compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        m = Model(
            compounds=model_compounds,
            reactions=model_reactions,
            compartments=compartments,
        )
        db = Model(compounds=db_compounds, reactions=db_reactions, compartments=compartments)
        with self.assertWarns(UserWarning):
            m.get_gapfilling_reactions(reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False)

    def test_linear_chain_water_addition(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="cpd4", compartment="CYTOSOL"),
            Compound(base_id="WATER", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction("rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd2_c": -1, "WATER_c": -1, "cpd3_c": 1}),
            Reaction(id="rxn3", stoichiometries={"cpd3_c": -1, "cpd4_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        reaction_ids = m.get_gapfilling_reactions(
            reference_model=db,
            seed=["cpd1_c", "WATER_c"],
            targets=["cpd4_c"],
            verbose=False,
        )
        self.assertEqual(set(reaction_ids), set(["rxn3", "rxn2"]))

    def test_linear_reversible_duplication(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd3_c": -1, "cpd2_c": 1}, reversible=True),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        db.reversibility_duplication()
        self.assertEqual(
            ["rxn2__rev__"],
            m.get_gapfilling_reactions(
                reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False
            ),
        )

    def test_linear_chain_fail_on_reverse(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd3_c": -1, "cpd2_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        self.assertEqual(
            [],
            m.get_gapfilling_reactions(
                reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False
            ),
        )

    def test_linear_chain_fail_on_reverse_with_duplication(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(id="rxn2", stoichiometries={"cpd3_c": -1, "cpd2_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        db.reversibility_duplication()
        self.assertEqual(
            [],
            m.get_gapfilling_reactions(
                reference_model=db, seed=["cpd1_c"], targets=["cpd3_c"], verbose=False
            ),
        )

    def test_linear_chain_cofactor_duplicated(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="cpd4", compartment="CYTOSOL"),
            Compound(base_id="ATP", compartment="CYTOSOL"),
            Compound(base_id="ADP", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(
                id="rxn2",
                stoichiometries={"cpd2_c": -1, "ADP_c": -1, "cpd3_c": 1, "ATP_c": 1},
            ),
            Reaction(id="rxn3", stoichiometries={"cpd3_c": -1, "cpd4_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        reaction_ids = m.get_gapfilling_reactions(
            reference_model=db,
            seed=["cpd1_c"] + m.get_weak_cofactor_duplications(),
            targets=["cpd4_c"],
            verbose=False,
        )
        self.assertEqual(set(reaction_ids), set(["rxn2__cof__", "rxn3"]))

    def test_linear_chain_include_cofactor_duplicated(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="cpd4", compartment="CYTOSOL"),
            Compound(base_id="ATP", compartment="CYTOSOL"),
            Compound(base_id="ADP", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(
                id="rxn2",
                stoichiometries={"cpd2_c": -1, "ADP_c": -1, "cpd3_c": 1, "ATP_c": 1},
            ),
            Reaction(id="rxn3", stoichiometries={"cpd3_c": -1, "cpd4_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        m.add_cofactor_pair(strong_cofactor_base_id="ATP_c", weak_cofactor_base_id="ADP_c")
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        db.cofactor_duplication()
        m.cofactor_pairs = {"ATP_c": "ADP_c"}
        reaction_ids = m.get_gapfilling_reactions(
            reference_model=db,
            seed=["cpd1_c"],
            targets=["cpd4_c"],
            include_weak_cofactors=True,
            verbose=False,
        )
        self.assertEqual(set(reaction_ids), set(["rxn2__cof__", "rxn3"]))

    def test_linear_chain_cofactor_duplicated_fail_without_duplication(self):
        compounds = (
            Compound(base_id="cpd1", compartment="CYTOSOL"),
            Compound(base_id="cpd2", compartment="CYTOSOL"),
            Compound(base_id="cpd3", compartment="CYTOSOL"),
            Compound(base_id="cpd4", compartment="CYTOSOL"),
            Compound(base_id="ATP", compartment="CYTOSOL"),
            Compound(base_id="ADP", compartment="CYTOSOL"),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        model_reactions = (Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),)
        db_reactions = (
            Reaction(id="rxn1", stoichiometries={"cpd1_c": -1, "cpd2_c": 1}),
            Reaction(
                id="rxn2",
                stoichiometries={"cpd2_c": -1, "ADP_c": -1, "cpd3_c": 1, "ATP_c": 1},
            ),
            Reaction(id="rxn3", stoichiometries={"cpd3_c": -1, "cpd4_c": 1}),
        )
        m = Model(compounds=compounds, reactions=model_reactions, compartments=compartments)
        db = Model(compounds=compounds, reactions=db_reactions, compartments=compartments)
        db.cofactor_pairs = {"ATP_c": "ADP_c"}
        m.cofactor_pairs = {"ATP_c": "ADP_c"}

        reaction_ids = m.get_gapfilling_reactions(
            reference_model=db,
            seed=["cpd1_c"] + m.get_weak_cofactor_duplications(),
            targets=["cpd4_c"],
            verbose=False,
        )

        self.assertEqual(reaction_ids, [])
