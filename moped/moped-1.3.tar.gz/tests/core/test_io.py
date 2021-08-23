import unittest
from pathlib import Path

from moped import Model

import cobra

FILEPATH = str(Path(__file__).parent / "data" / "dummy-model.sbml")
FILEPATH_BIGG = str(Path(__file__).parent / "data" / "dummy-model-bigg.xml")


class ReadTests(unittest.TestCase):
    def test_read_cobra(self):
        cm = cobra.io.read_sbml_model(filename=FILEPATH)
        m = Model()
        m.read_from_cobra(cobra_model=cm)
        # compartments
        self.assertEqual(m.compartments, {"CYTOSOL": "c", "EXTRACELLULAR": "e"})
        # compounds
        self.assertEqual(set(m.compounds), {"SE_c", "S_e", "P_c", "P_e", "S_c", "E_c"})
        self.assertEqual(m.compounds["S_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["S_c"].formula, {"C": 1})
        self.assertEqual(m.compounds["S_c"].charge, 1)
        self.assertEqual(m.compounds["S_c"].in_reaction, {"TR_S_c_e", "v1_c"})
        self.assertEqual(m.compounds["S_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["S_e"].formula, {"C": 1})
        self.assertEqual(m.compounds["S_e"].charge, 1)
        self.assertEqual(m.compounds["S_e"].in_reaction, {"EX_S_e", "TR_S_c_e"})
        # reactions
        self.assertEqual(
            set(m.reactions),
            {"EX_P_e", "EX_S_e", "TR_P_c_e", "TR_S_c_e", "v1_c", "v2_c"},
        )
        self.assertEqual(m.reactions["v1_c"].stoichiometries, {"S_c": -1, "E_c": -1, "SE_c": 1})
        self.assertEqual(m.reactions["v1_c"].transmembrane, False)
        self.assertEqual(m.reactions["v1_c"].bounds, (-10, 1000))
        self.assertEqual(m.reactions["v1_c"].reversible, True)
        self.assertEqual(m.reactions["EX_S_e"].stoichiometries, {"S_e": -1})
        self.assertEqual(m.reactions["EX_S_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["EX_S_e"].reversible, False)
        self.assertEqual(m.reactions["TR_S_c_e"].stoichiometries, {"S_c": -1, "S_e": 1})
        self.assertEqual(m.reactions["TR_S_c_e"].transmembrane, True)
        self.assertEqual(m.reactions["TR_S_c_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["TR_S_c_e"].reversible, False)
        # objective
        self.assertEqual(m.objective, {"v1_c": 1, "v2_c": 1})

    def test_read_sbml(self):
        m = Model()
        m.read_from_sbml(sbml_file=FILEPATH)
        # compartments
        self.assertEqual(m.compartments, {"CYTOSOL": "c", "EXTRACELLULAR": "e"})
        # compounds
        self.assertEqual(set(m.compounds), {"SE_c", "S_e", "P_c", "P_e", "S_c", "E_c"})
        self.assertEqual(m.compounds["S_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["S_c"].formula, {"C": 1})
        self.assertEqual(m.compounds["S_c"].charge, 1)
        self.assertEqual(m.compounds["S_c"].in_reaction, {"TR_S_c_e", "v1_c"})
        self.assertEqual(m.compounds["S_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["S_e"].formula, {"C": 1})
        self.assertEqual(m.compounds["S_e"].charge, 1)
        self.assertEqual(m.compounds["S_e"].in_reaction, {"EX_S_e", "TR_S_c_e"})
        # reactions
        self.assertEqual(
            set(m.reactions),
            {"EX_P_e", "EX_S_e", "TR_P_c_e", "TR_S_c_e", "v1_c", "v2_c"},
        )
        self.assertEqual(m.reactions["v1_c"].stoichiometries, {"S_c": -1, "E_c": -1, "SE_c": 1})
        self.assertEqual(m.reactions["v1_c"].transmembrane, False)
        self.assertEqual(m.reactions["v1_c"].bounds, (-10, 1000))
        self.assertEqual(m.reactions["v1_c"].reversible, True)
        self.assertEqual(m.reactions["EX_S_e"].stoichiometries, {"S_e": -1})
        self.assertEqual(m.reactions["EX_S_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["EX_S_e"].reversible, False)
        self.assertEqual(m.reactions["TR_S_c_e"].stoichiometries, {"S_c": -1, "S_e": 1})
        self.assertEqual(m.reactions["TR_S_c_e"].transmembrane, True)
        self.assertEqual(m.reactions["TR_S_c_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["TR_S_c_e"].reversible, False)
        # objective
        self.assertEqual(m.objective, {"v1_c": 1, "v2_c": 1})

    def test_read_bigg(self):
        m = Model()
        m.read_from_bigg(bigg_sbml_file=FILEPATH_BIGG)
        # compartments
        self.assertEqual(m.compartments, {"CYTOSOL": "c", "EXTRACELLULAR": "e"})
        # compounds
        self.assertEqual(
            set(m.compounds),
            {
                "SE_c",
                "S_e",
                "P_c",
                "P_e",
                "S_c",
                "E_c",
                "trdrd_c",
                "adp_c",
                "accoa_c",
                "coa_c",
                "methf_c",
                "pcrd_c",
                "etfrd_c",
                "trdox_c",
                "atp_c",
                "fdxrd_c",
                "gtp_c",
                "nadph_c",
                "nad_c",
                "gdp_c",
                "etfox_c",
                "pcox_c",
                "nadh_c",
                "thf_c",
                "nadp_c",
                "10fthf_c",
                "fdxox_c",
            },
        )
        self.assertEqual(m.compounds["S_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["S_c"].formula, {"C": 1})
        self.assertEqual(m.compounds["S_c"].charge, 1)
        self.assertEqual(m.compounds["S_c"].in_reaction, {"TR_S_c_e", "v1_c"})
        self.assertEqual(m.compounds["S_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["S_e"].formula, {"C": 1})
        self.assertEqual(m.compounds["S_e"].charge, 1)
        self.assertEqual(m.compounds["S_e"].in_reaction, {"EX_S_e", "TR_S_c_e"})
        # reactions
        self.assertEqual(
            set(m.reactions),
            {"EX_P_e", "EX_S_e", "TR_P_c_e", "TR_S_c_e", "v1_c", "v2_c"},
        )
        self.assertEqual(m.reactions["v1_c"].stoichiometries, {"S_c": -1, "E_c": -1, "SE_c": 1})
        self.assertEqual(m.reactions["v1_c"].transmembrane, False)
        self.assertEqual(m.reactions["v1_c"].bounds, (-10, 1000))
        self.assertEqual(m.reactions["v1_c"].reversible, True)
        self.assertEqual(m.reactions["EX_S_e"].stoichiometries, {"S_e": -1})
        self.assertEqual(m.reactions["EX_S_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["EX_S_e"].reversible, False)
        self.assertEqual(m.reactions["TR_S_c_e"].stoichiometries, {"S_c": -1, "S_e": 1})
        self.assertEqual(m.reactions["TR_S_c_e"].transmembrane, True)
        self.assertEqual(m.reactions["TR_S_c_e"].bounds, (-1000, 0))
        self.assertEqual(m.reactions["TR_S_c_e"].reversible, False)
        # objective
        self.assertEqual(m.objective, {"v1_c": 1, "v2_c": 1})
        self.assertEqual(
            m.cofactor_pairs,
            {
                "atp_c": "adp_c",
                "gtp_c": "gdp_c",
                "nadh_c": "nad_c",
                "nadph_c": "nadp_c",
                "10fthf_c": "thf_c",
                "methf_c": "thf_c",
                "fdxrd_c": "fdxox_c",
                "trdrd_c": "trdox_c",
                "etfrd_c": "etfox_c",
                "accoa_c": "coa_c",
                "pcrd_c": "pcox_c",
            },
        )
