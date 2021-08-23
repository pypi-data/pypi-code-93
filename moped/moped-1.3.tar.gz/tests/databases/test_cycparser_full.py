import unittest
import unittest.mock as mock

from moped.core.model import Model
from moped.databases.cyc import CompoundParser, ReactionParser, Repairer

COMPARTMENT_MAP = {
    "CYTOSOL": "CYTOSOL",
    "IN": "CYTOSOL",
    "UNKNOWN-SPACE": "CYTOSOL",
    "SIDE-1": "CYTOSOL",
    "SIDE-2": "EXTRACELLULAR",
    "EXTRACELLULAR": "EXTRACELLULAR",
    "CHL-THY-MEM": "PERIPLASM",
    "CHLOR-STR": "CYTOSOL",
    "CHROM-STR": "CYTOSOL",
    "GOLGI-LUM": "CYTOSOL",
    "LYS-LUM": "CYTOSOL",
    "MIT-IM-SPC": "CYTOSOL",
    "MIT-IMEM": "PERIPLASM",
    "MIT-LUM": "CYTOSOL",
    "OUTER-MEM": "PERIPLASM",
    "PERI-BAC": "PERIPLASM",
    "PERI-BAC-GN": "PERIPLASM",
    "PERIPLASM": "PERIPLASM",
    "PEROX-LUM": "CYTOSOL",
    "PLASMA-MEM": "PERIPLASM",
    "PLAST-IMEM": "PERIPLASM",
    "PLASTID-STR": "PERIPLASM",
    "PM-ANIMAL": "PERIPLASM",
    "PM-BAC-ACT": "PERIPLASM",
    "PM-BAC-NEG": "PERIPLASM",
    "PM-BAC-POS": "PERIPLASM",
    "RGH-ER-LUM": "CYTOSOL",
    "RGH-ER-MEM": "PERIPLASM",
    "THY-LUM-CYA": "CYTOSOL",
    "VAC-LUM": "CYTOSOL",
    "VAC-MEM": "PERIPLASM",
    "VESICLE": "PERIPLASM",
    "OUT": "PERIPLASM",
}


class IntegrationParserTests(unittest.TestCase):
    def read_mock_compounds(self, file):
        with mock.patch(
            "moped.databases.cyc._open_file_and_remove_comments",
            mock.Mock(return_value=("", 0)),
        ):
            CP = CompoundParser("")
            CP.file = file
            return CP.parse()

    def read_mock_reactions(self, file):
        with mock.patch(
            "moped.databases.cyc._open_file_and_remove_comments",
            mock.Mock(return_value=("", 0)),
        ):
            RP = ReactionParser("")
            RP.file = file
            return RP.parse()

    def mock_parsing(self, compound_file, reaction_file):
        """CAUTION: manual additions are set to {}"""
        compounds, compound_types = self.read_mock_compounds(compound_file)
        reactions = self.read_mock_reactions(reaction_file)
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.manual_additions = {}
        compounds, reactions, compartments = r.repair()
        with mock.patch("moped.core.model.Cyc", mock.Mock()) as MockCyc:
            MockCyc.return_value.parse.return_value = (
                compounds,
                reactions,
                compartments,
            )
            m = Model()
            m.read_from_pgdb(pgdb_path="")
        return m


class IntegrationParserTestsNoInfo(IntegrationParserTests):
    def test_no_compartment_info(self):
        """We assume the cytosol as the default location"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "RIGHT - CPD2",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]


class IntegrationParserTestsAllIn(IntegrationParserTests):
    def test_no_location_all_in(self):
        """We assume the cytosol as the default location"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_single_location_cytosol_all_in(self):
        """This should stay in the cytosol"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, {"CPD1_c": -1, "CPD2_c": 1})
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_single_location_periplasm_all_in(self):
        """This should only be in the periplasm"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-PERIPLASM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        self.assertEqual(m.compounds["CPD1_p"].compartment, "PERIPLASM")
        self.assertEqual(m.compounds["CPD2_p"].compartment, "PERIPLASM")
        self.assertFalse(m.reactions["RXN_p"].transmembrane)
        stoich = {"CPD1_p": -1, "CPD2_p": 1}
        self.assertEqual(m.reactions["RXN_p"].stoichiometries, stoich)
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_single_location_extracellular_all_in(self):
        """This should only be extracellular"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        self.assertFalse(m.reactions["RXN_e"].transmembrane)
        stoich = {"CPD1_e": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_e"].stoichiometries, stoich)

    def test_multiple_locations_cytosol_periplasm_all_in(self):
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-CYTOSOL",
            "RXN-LOCATIONS - CCO-PERIPLASM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm
        self.assertEqual(m.compounds["CPD1_p"].compartment, "PERIPLASM")
        self.assertEqual(m.compounds["CPD2_p"].compartment, "PERIPLASM")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_p": -1, "CPD2_p": 1}
        self.assertEqual(m.reactions["RXN_p"].stoichiometries, stoich)
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_multiple_locations_cytosol_extracellular_all_in(self):
        """This should give both cytosolic and extracellular"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-CYTOSOL",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, {"CPD1_c": -1, "CPD2_c": 1})
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        self.assertFalse(m.reactions["RXN_e"].transmembrane)
        stoich = {"CPD1_e": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_e"].stoichiometries, stoich)

    def test_fake_transmembrane_location_all_in(self):
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR-CCO-CYTOSOL",  # out - in
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]


class IntegrationParserTestsAllOut(IntegrationParserTests):
    def test_no_location_all_out(self):
        """We assume the extracellular as the default location"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        self.assertFalse(m.reactions["RXN_e"].transmembrane)
        stoich = {"CPD1_e": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_e"].stoichiometries, stoich)

    def test_single_location_cytosol_all_out(self):
        """This should stay in the cytosol"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_single_location_periplasm_all_out(self):
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm - the compounds will be created, but the reaction should not
        self.assertEqual(m.compounds["CPD1_p"].compartment, "PERIPLASM")
        self.assertEqual(m.compounds["CPD2_p"].compartment, "PERIPLASM")
        self.assertFalse(m.reactions["RXN_p"].transmembrane)
        stoich = {"CPD1_p": -1, "CPD2_p": 1}
        self.assertEqual(m.reactions["RXN_p"].stoichiometries, stoich)
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_single_location_extracellular_all_out(self):
        """This should stay in the extracellular"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        self.assertFalse(m.reactions["RXN_e"].transmembrane)
        stoich = {"CPD1_e": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_e"].stoichiometries, stoich)

    def test_multiple_locations_cytosol_periplasm_all_out(self):
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CYTOSOL",
            "RXN-LOCATIONS - CCO-PERIPLASM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm - the compounds will be created, but the reaction should not
        self.assertEqual(m.compounds["CPD1_p"].compartment, "PERIPLASM")
        self.assertEqual(m.compounds["CPD2_p"].compartment, "PERIPLASM")
        self.assertFalse(m.reactions["RXN_p"].transmembrane)
        stoich = {"CPD1_p": -1, "CPD2_p": 1}
        self.assertEqual(m.reactions["RXN_p"].stoichiometries, stoich)
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]

    def test_multiple_locations_cytosol_extracellular_all_out(self):
        """This should give both cytosolic and extracellular"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CYTOSOL",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        self.assertFalse(m.reactions["RXN_e"].transmembrane)
        stoich = {"CPD1_e": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_e"].stoichiometries, stoich)

    def test_fake_transmembrane_location_all_out(self):
        """This should give only extracelluar, regardless of the location.
        It just doesn't make any sense to have a transmembrane string
        for just CCO-OUT annotation
        """
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR-CCO-CYTOSOL",  # out - in
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        self.assertFalse(m.reactions["RXN_e"].transmembrane)
        stoich = {"CPD1_e": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_e"].stoichiometries, stoich)


class IntegrationParserTestsInOut(IntegrationParserTests):
    def test_no_location_in_out(self):
        """Should yield _c_e"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_p"]
        # Cytosol - Extracellular
        stoich = {"CPD1_c": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_c_e"].stoichiometries, stoich)
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]

    def test_single_location_cytosol_in_out(self):
        """This one is a bit debatable. It will be mapped to
        CCO-CYTOSOL-CCO-CYTOSOL, so it will loose its transmembrane
        information
        Should yield _c
        """
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        stoich = {"CPD1_c": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_c"].stoichiometries, stoich)
        self.assertFalse(m.reactions["RXN_c"].transmembrane)
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_p"]
        # Cytosol - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_e"]
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]

    def test_single_location_periplasm_in_out(self):
        """Should yield _c_e"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        self.assertEqual(m.compounds["CPD2_p"].compartment, "PERIPLASM")
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        stoich = {"CPD1_c": -1, "CPD2_p": 1}
        self.assertEqual(m.reactions["RXN_c_p"].stoichiometries, stoich)
        self.assertTrue(m.reactions["RXN_c_p"].transmembrane)
        # Cytosol - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_e"]
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]

    def test_single_location_extracellular_in_out(self):
        """Should yield _c_e"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_p"]
        # Cytosol - Extracellular
        stoich = {"CPD1_c": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_c_e"].stoichiometries, stoich)
        self.assertTrue(m.reactions["RXN_c_e"].transmembrane)
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]

    def test_transmembrane_locations_cytosol_periplasm_in_out(self):
        """ Should yield _c_p"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.compounds["CPD1_2"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        self.assertEqual(m.compounds["CPD2_p"].compartment, "PERIPLASM")
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        stoich = {"CPD1_c": -1, "CPD2_p": 1}
        self.assertEqual(m.reactions["RXN_c_p"].stoichiometries, stoich)
        self.assertTrue(m.reactions["RXN_c_p"].transmembrane)
        # Cytosol - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_e"]
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]

    def test_transmembrane_locations_cytosol_extracellular_in_out(self):
        """Should yield _c_e"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        self.assertEqual(m.compounds["CPD1_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.compounds["CPD2_c"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        self.assertEqual(m.compounds["CPD2_e"].compartment, "EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_p"]
        # Cytosol - Extracellular
        stoich = {"CPD1_c": -1, "CPD2_e": 1}
        self.assertEqual(m.reactions["RXN_c_e"].stoichiometries, stoich)
        self.assertTrue(m.reactions["RXN_c_e"].transmembrane)
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]

    def test_transmembrane_locations_periplasm_cytosol_in_out(self):
        """Should yield _p_c"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CYTOSOL-CCO-PERIPLASM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        self.assertEqual(m.compounds["CPD1_p"].compartment, "PERIPLASM")
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        with self.assertRaises(KeyError):
            m.compounds["CPD1_e"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_p"]
        # Cytosol - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_e"]
        # Periplasm - Cytosol
        stoich = {"CPD1_p": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_p_c"].stoichiometries, stoich)
        self.assertTrue(m.reactions["RXN_p_c"].transmembrane)
        # Extracellular - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_c"]
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]

    def test_transmembrane_locations_extracellular_cytosol_in_out(self):
        """Should yield _e_c"""
        compound_file = [
            "UNIQUE-ID - CPD1",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
            "UNIQUE-ID - CPD2",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (C 1)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN",
            "LEFT - CPD1",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - CPD2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CYTOSOL-CCO-EXTRACELLULAR",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        # Cytosol
        with self.assertRaises(KeyError):
            m.compounds["CPD1_c"]
        self.assertEqual(m.compounds["CPD2_c"].compartment, "CYTOSOL")
        with self.assertRaises(KeyError):
            m.reactions["RXN_c"]
        # Periplasm
        with self.assertRaises(KeyError):
            m.compounds["CPD1_p"]
        with self.assertRaises(KeyError):
            m.compounds["CPD2_p"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_p"]
        # Extracellular
        self.assertEqual(m.compounds["CPD1_e"].compartment, "EXTRACELLULAR")
        with self.assertRaises(KeyError):
            m.compounds["CPD2_e"]
        with self.assertRaises(KeyError):
            m.reactions["RXN_e"]
        # Cytosol - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_p"]
        # Cytosol - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_c_e"]
        # Periplasm - Cytosol
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_c"]
        # Extracellular - Cytosol
        stoich = {"CPD1_e": -1, "CPD2_c": 1}
        self.assertEqual(m.reactions["RXN_e_c"].stoichiometries, stoich)
        self.assertTrue(m.reactions["RXN_e_c"].transmembrane)
        # Extracellular - Periplasm
        with self.assertRaises(KeyError):
            m.reactions["RXN_e_p"]
        # Periplasm - Extracellular
        with self.assertRaises(KeyError):
            m.reactions["RXN_p_e"]


class IntegrationParserTestsPhotosynthesisReactions(IntegrationParserTests):
    """The photosynthesis functions tend to be annotated in a way that we
    can't work with them. So extra care is needed that they are parsed correctly"""

    def test_psii_rxn(self):
        compound_file = [
            "UNIQUE-ID - Plastoquinols",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - OXYGEN-MOLECULE",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Light",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - PLASTOQUINONE",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - WATER",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - PSII-RXN",
            "TYPES - Chemical-Reactions",
            "TYPES - Electron-Transfer-Reactions",
            "TYPES - Small-Molecule-Reactions",
            "IN-PATHWAY - PWY-101",
            "LEFT - Plastoquinols",
            "^COEFFICIENT - 2",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "LEFT - OXYGEN-MOLECULE",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - PHYSIOL-RIGHT-TO-LEFT",
            "RIGHT - Light",
            "^COMPARTMENT - CCO-CYTOSOL",
            "RIGHT - PLASTOQUINONE",
            "^COEFFICIENT - 2",
            "RIGHT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - WATER",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-CHL-THY-MEM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["PSII-RXN_c_p"]
        stoich = {
            "Light_c": -1,
            "PLASTOQUINONE_c": -2.0,
            "PROTON_c": -4.0,
            "WATER_c": -2.0,
            "Plastoquinols_c": 2.0,
            "PROTON_p": 4.0,
            "OXYGEN-MOLECULE_c": 1,
        }
        self.assertEqual(rxn.stoichiometries, stoich)

    def test_1_18_1_2_rxn(self):
        compound_file = [
            "UNIQUE-ID - NADP",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Reduced-ferredoxins",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Oxidized-ferredoxins",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - NADPH",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - 1.18.1.2-RXN",
            "TYPES - Electron-Transfer-Reactions",
            "TYPES - Protein-Modification-Reactions",
            "IN-PATHWAY - PWY-101",
            "LEFT - NADP",
            "^COMPARTMENT - CCO-OUT",
            "LEFT - PROTON",
            "^COMPARTMENT - CCO-OUT",
            "LEFT - Reduced-ferredoxins",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - Oxidized-ferredoxins",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RIGHT - NADPH",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-SIDE-2-CCO-SIDE-1",
            "RXN-LOCATIONS - CCO-EXTRACELLULAR-CCO-CYTOSOL",
            "RXN-LOCATIONS - CCO-CHLOR-STR-CCO-THY-LUM-CYA",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["1.18.1.2-RXN_c"]
        stoich = {
            "NADP_c": -1,
            "PROTON_c": -1,
            "Reduced-ferredoxins_c": -2.0,
            "Oxidized-ferredoxins_c": 2.0,
            "NADPH_c": 1,
        }
        self.assertEqual(rxn.stoichiometries, stoich)

    def test_rxn_15479(self):
        compound_file = [
            "UNIQUE-ID - Oxidized-Plastocyanins",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Light",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Reduced-ferredoxins",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Oxidized-ferredoxins",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Plastocyanin-Reduced",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN-15479",
            "TYPES - Electron-Transfer-Reactions",
            "TYPES - Protein-Modification-Reactions",
            "IN-PATHWAY - PWY-101",
            "LEFT - Oxidized-Plastocyanins",
            "^COMPARTMENT - CCO-IN",
            "LEFT - Reduced-ferredoxins",
            "^COMPARTMENT - CCO-OUT",
            "REACTION-DIRECTION - PHYSIOL-RIGHT-TO-LEFT",
            "RIGHT - Light",
            "^COMPARTMENT - CCO-CYTOSOL",
            "RIGHT - Plastocyanin-Reduced",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - Oxidized-ferredoxins",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-CHL-THY-MEM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN-15479_c"]
        stoich = {
            "Light_c": -1,
            "Plastocyanin-Reduced_c": -1,
            "Oxidized-ferredoxins_c": -1,
            "Oxidized-Plastocyanins_c": 1,
            "Reduced-ferredoxins_c": 1,
        }
        self.assertEqual(rxn.stoichiometries, stoich)

    def test_plastoquionol_plastocyanin_reductase_rxn(self):
        compound_file = [
            "UNIQUE-ID - Plastoquinols",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Oxidized-Plastocyanins",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - PLASTOQUINONE",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
            "UNIQUE-ID - Plastocyanin-Reduced",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - PLASTOQUINOL--PLASTOCYANIN-REDUCTASE-RXN",
            "TYPES - Electron-Transfer-Reactions",
            "TYPES - Protein-Modification-Reactions",
            "IN-PATHWAY - PWY-101",
            "LEFT - Plastoquinols",
            "LEFT - Oxidized-Plastocyanins",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-IN",
            "LEFT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "REACTION-DIRECTION - LEFT-TO-RIGHT",
            "RIGHT - PLASTOQUINONE",
            "RIGHT - Plastocyanin-Reduced",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-IN",
            "RIGHT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "RXN-LOCATIONS - CCO-CHL-THY-MEM",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["PLASTOQUINOL--PLASTOCYANIN-REDUCTASE-RXN_c_p"]
        stoich = {
            "Plastoquinols_c": -1,
            "Oxidized-Plastocyanins_c": -2.0,
            "PROTON_c": -2.0,
            "PLASTOQUINONE_c": 1,
            "Plastocyanin-Reduced_c": 2.0,
            "PROTON_p": 4.0,
        }
        self.assertEqual(rxn.stoichiometries, stoich)


class IntegrationParserTestsPeriplasmReactions(IntegrationParserTests):
    """To allow periplasm proton gradients to form and disallow infeasible loops
    only certain types of reactions are allowed to transport protons to the periplasm"""

    def test_no_type(self):
        """Expect stoichiometry to be switched"""
        compound_file = [
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN1",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN1_c_p"]
        stoich = {
            "PROTON_p": -2,
            "PROTON_c": 4,
        }
        self.assertEqual(rxn.stoichiometries, stoich)
        self.assertEqual(rxn.bounds, (0, 1000))
        self.assertFalse(rxn.reversible)

    def test_tr12(self):
        """Disallowed reaction
        reaction type TR-12: Transport Energized by the Membrane Electrochemical Gradient
        Expect stoichiometry to be switched and bounds to be (0, 1000)
        """
        compound_file = [
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN1",
            "TYPES - TR-12",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN1_c_p"]
        stoich = {
            "PROTON_p": -2,
            "PROTON_c": 4,
        }
        self.assertEqual(rxn.stoichiometries, stoich)
        self.assertEqual(rxn.bounds, (0, 1000))
        self.assertFalse(rxn.reversible)

    def test_tr13(self):
        """Allowed reaction
        reaction type TR-13: Transport Energized by Phosphoanhydride-Bond Hydrolysis
        """
        compound_file = [
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN1",
            "TYPES - TR-13",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN1_c_p"]
        stoich = {
            "PROTON_c": -4,
            "PROTON_p": 2,
        }
        self.assertEqual(rxn.stoichiometries, stoich)
        self.assertEqual(rxn.bounds, (-1000, 1000))
        self.assertTrue(rxn.reversible)

    def test_tr15(self):
        """Allowed reaction
        reaction type TR-15: Transport Energized by Decarboxylation
        """
        compound_file = [
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN1",
            "TYPES - TR-15",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN1_c_p"]
        stoich = {
            "PROTON_c": -4,
            "PROTON_p": 2,
        }
        self.assertEqual(rxn.stoichiometries, stoich)
        self.assertEqual(rxn.bounds, (-1000, 1000))
        self.assertTrue(rxn.reversible)

    def test_etr(self):
        """Allowed reaction"""
        compound_file = [
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN1",
            "TYPES - Electron-Transfer-Reactions",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN1_c_p"]
        stoich = {
            "PROTON_c": -4,
            "PROTON_p": 2,
        }
        self.assertEqual(rxn.stoichiometries, stoich)
        self.assertEqual(rxn.bounds, (-1000, 1000))
        self.assertTrue(rxn.reversible)

    def test_mpmr(self):
        """Allowed reaction"""
        compound_file = [
            "UNIQUE-ID - PROTON",
            "ATOM-CHARGES - (0 0)",
            "CHEMICAL-FORMULA - (X 0)",
        ]
        reaction_file = [
            "UNIQUE-ID - RXN1",
            "TYPES - Membrane-Protein-Modification-Reactions",
            "LEFT - PROTON",
            "^COEFFICIENT - 4",
            "^COMPARTMENT - CCO-IN",
            "REACTION-DIRECTION - REVERSIBLE",
            "RIGHT - PROTON",
            "^COEFFICIENT - 2",
            "^COMPARTMENT - CCO-OUT",
            "RXN-LOCATIONS - CCO-PERIPLASM-CCO-CYTOSOL",
        ]
        m = self.mock_parsing(compound_file=compound_file, reaction_file=reaction_file)
        rxn = m.reactions["RXN1_c_p"]
        stoich = {
            "PROTON_c": -4,
            "PROTON_p": 2,
        }
        self.assertEqual(rxn.stoichiometries, stoich)
        self.assertEqual(rxn.bounds, (-1000, 1000))
        self.assertTrue(rxn.reversible)
