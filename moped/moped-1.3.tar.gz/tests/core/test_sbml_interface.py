import unittest

from moped import Compound, Model, Reaction
from moped.utils import get_temporary_directory

import cobra


class SBMLInterfaceTests(unittest.TestCase):
    def create_minimal_toy_model(self):
        compounds = (
            Compound(base_id="S", compartment="CYTOSOL", formula={"C": 1}, charge=0),
            Compound(base_id="E", compartment="CYTOSOL", formula={"E": 1}, charge=0),
            Compound(base_id="SE", compartment="CYTOSOL", formula={"C": 1, "E": 1}, charge=0),
            Compound(base_id="P", compartment="CYTOSOL", formula={"C": 1}, charge=0),
        )
        reactions = (
            Reaction(
                id="v1_c",
                base_id="v1",
                stoichiometries={"S_c": -1, "E_c": -1, "SE_c": 1},
                bounds=(-10, 1000),
                sequences={"MONOMER-001": {"GATC"}},
            ),
            Reaction(
                id="v2_c",
                base_id="v2",
                stoichiometries={"SE_c": -1, "P_c": 1, "E_c": 1},
                bounds=(0, 1000),
                sequences={"MONOMER-002": {"GATC"}},
            ),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_transport_reaction(compound_id="S_c", compartment_id="EXTRACELLULAR", bounds=(-1000, 0))
        m.add_influx("S_c", extracellular_compartment_id="EXTRACELLULAR")
        m.add_transport_reaction(compound_id="P_c", compartment_id="EXTRACELLULAR", bounds=(0, 1000))
        m.add_efflux("P_c", extracellular_compartment_id="EXTRACELLULAR")
        m.set_objective({"v1_c": 1, "v2_c": 1})
        return m.copy()

    def test_to_sbml(self):
        m = self.create_minimal_toy_model()
        sbml_file = str(get_temporary_directory(subdirectory="unittests") / "test.sbml")
        m.to_sbml(filename=sbml_file)
        _, errors = cobra.io.validate_sbml_model(filename=sbml_file)
        self.assertFalse(bool(errors["SBML_FATAL"]))
        self.assertFalse(bool(errors["SBML_ERROR"]))
        self.assertFalse(bool(errors["SBML_SCHEMA_ERROR"]))
        self.assertFalse(bool(errors["SBML_WARNING"]))
        self.assertFalse(bool(errors["COBRA_FATAL"]))
        self.assertFalse(bool(errors["COBRA_ERROR"]))
        self.assertFalse(bool(errors["COBRA_WARNING"]))
        self.assertFalse(bool(errors["COBRA_CHECK"]))

    def test_to_sbml_and_back(self):
        m = self.create_minimal_toy_model()
        sbml_file = str(get_temporary_directory(subdirectory="unittests") / "test.sbml")
        m.to_sbml(filename=sbml_file)
        m2 = Model()
        m2.read_from_sbml(sbml_file=sbml_file)

        self.assertEqual(m.compounds, m2.compounds)
        self.assertEqual(m.reactions, m2.reactions)

        for reaction in m.reactions:
            self.assertEqual(
                m.reactions[reaction].stoichiometries,
                m.reactions[reaction].stoichiometries,
            )
            self.assertEqual(
                m.reactions[reaction].bounds,
                m.reactions[reaction].bounds,
            )
