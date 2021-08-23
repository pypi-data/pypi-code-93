import unittest
import unittest.mock as mock
from pathlib import Path

from moped.databases.cyc import (
    CompoundParser,
    Cyc,
    EnzymeParser,
    ReactionParser,
    Repairer,
    SequenceParser,
    _check_for_monomer,
    _get_enzrnx_to_monomer_mapping,
    _get_enzrnx_to_sequence_mapping,
    _map_reactions_to_kinetic_parameters,
    _map_reactions_to_sequences,
    _remove_top_comments,
    _rename,
)

TESTCYC_PATH = str(Path(__file__).parent / "testcyc")
TESTCYC_WO_SEQ_PATH = str(Path(__file__).parent / "testcyc_without_sequences")

COMPARTMENT_MAP = {
    "CYTOSOL": "CYTOSOL",
    "IN": "CYTOSOL",
    "UNKNOWN-SPACE": "CYTOSOL",
    "SIDE-1": "CYTOSOL",
    "SIDE-2": "PERIPLASM",
    "EXTRACELLULAR": "EXTRACELLULAR",
    "CHL-THY-MEM": "PERIPLASM",
    "CHLOR-STR": "PERIPLASM",
    "CHROM-STR": "PERIPLASM",
    "GOLGI-LUM": "CYTOSOL",
    "LYS-LUM": "CYTOSOL",
    "MIT-IM-SPC": "PERIPLASM",
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
    "OUT": "EXTRACELLULAR",
}


class ParserUniversalTests(unittest.TestCase):
    def test_remove_top_comments(self):
        file = [
            "# Species: MetaCyc",
            "# Database: MetaCyc",
            "# Version: 23.0",
            "# File Name: reactions.dat",
            "# Date and time generated: November 20, 2018, 14:01:26",
            "#",
            "# Attributes:",
            "#    UNIQUE-ID",
            "#    TYPES",
            "#    COMMON-NAME",
            "#    ATOM-MAPPINGS",
            "#    SYSTEMATIC-NAME",
            "#    TAXONOMIC-RANGE",
            "#",
            "UNIQUE-ID - RXN-19177",
        ]

        file, idx = _remove_top_comments(file)
        self.assertEqual(["UNIQUE-ID - RXN-19177"], file)
        self.assertEqual(idx, 14)

    def test_rename(self):
        self.assertEqual("O-methylbergaptol", _rename("<i>O</i>-methylbergaptol"))
        self.assertEqual("N2-acetyl-ornithine", _rename("<i>N<sup>2</sup></i>-acetyl-ornithine"))
        self.assertEqual("SePO3", _rename("SePO<sub>3</sub>"))
        self.assertEqual(
            "UDP-2,4-diacetamido-2,4,6-trideoxy-alpha-D-glucopyranose",
            _rename("UDP-2,4-diacetamido-2,4,6-trideoxy-&alpha;-D-glucopyranose"),
        )
        self.assertEqual("Glucopyranose", _rename("|Glucopyranose|"))


class CompoundParserTests(unittest.TestCase):
    def read_mock_file(self, file):
        with mock.patch(
            "moped.databases.cyc._open_file_and_remove_comments",
            mock.Mock(return_value=("", 0)),
        ):
            CP = CompoundParser("")
            CP.file = file
            cpds, types = CP.parse()
            return cpds, types

    def test_create_compound(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1"])
        self.assertEqual(cpds["cpd1_c"]["id"], "cpd1_c")

    def test_create_default_compartment(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1"])
        self.assertEqual(cpds["cpd1_c"]["compartment"], "CYTOSOL")

    def test_create_default_charge(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1"])
        self.assertEqual(cpds["cpd1_c"]["charge"], 0)

    def test_add_cpd_type_single(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1", "TYPES - LIGNAN"])
        self.assertEqual(cpds["cpd1_c"]["types"], ["LIGNAN"])
        self.assertEqual(types, {"LIGNAN_c": ["cpd1_c"]})

    def test_add_cpd_type_double(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1", "TYPES - LIGNAN", "TYPES - Toxins"])
        self.assertEqual(cpds["cpd1_c"]["types"], ["LIGNAN", "Toxins"])
        self.assertEqual(types, {"Toxins_c": ["cpd1_c"]})

    def test_atom_charges_neg(self):
        cpds, types = self.read_mock_file(
            [
                "UNIQUE-ID - cpd1",
                "ATOM-CHARGES - (0 -1)",
            ]
        )
        self.assertEqual(cpds["cpd1_c"]["charge"], -1.0)

    def test_atom_charges_pos(self):
        cpds, types = self.read_mock_file(
            [
                "UNIQUE-ID - cpd1",
                "ATOM-CHARGES - (0 1)",
            ]
        )
        self.assertEqual(cpds["cpd1_c"]["charge"], 1.0)

    def test_atom_charges_pos_and_neg(self):
        cpds, types = self.read_mock_file(
            [
                "UNIQUE-ID - cpd1",
                "ATOM-CHARGES - (0 -1)",
                "ATOM-CHARGES - (1 1)",
            ]
        )
        self.assertEqual(cpds["cpd1_c"]["charge"], 0)

    def test_formula_single(self):
        cpds, types = self.read_mock_file(
            [
                "UNIQUE-ID - cpd1",
                "CHEMICAL-FORMULA - (C 1)",
            ]
        )
        self.assertEqual(cpds["cpd1_c"]["formula"], {"C": 1})

    def test_formula_multiple(self):
        cpds, types = self.read_mock_file(
            [
                "UNIQUE-ID - cpd1",
                "CHEMICAL-FORMULA - (C 6)",
                "CHEMICAL-FORMULA - (H 12)",
                "CHEMICAL-FORMULA - (O 6)",
            ]
        )
        self.assertEqual(cpds["cpd1_c"]["formula"], {"C": 6, "H": 12, "O": 6})

    def test_formula_two_letters(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1", "CHEMICAL-FORMULA - (He 1)"])
        self.assertEqual(cpds["cpd1_c"]["formula"], {"He": 1})

    def test_formula_multiple_two_letters(self):
        cpds, types = self.read_mock_file(
            [
                "UNIQUE-ID - cpd1",
                "CHEMICAL-FORMULA - (C 6)",
                "CHEMICAL-FORMULA - (He 12)",
                "CHEMICAL-FORMULA - (O 6)",
            ]
        )
        self.assertEqual(cpds["cpd1_c"]["formula"], {"C": 6, "He": 12, "O": 6})

    def test_smiles(self):
        cpds, types = self.read_mock_file(["UNIQUE-ID - cpd1", "SMILES - COC1"])
        self.assertEqual(
            cpds["cpd1_c"]["smiles"],
            "COC1",
        )


class ReactionParserTests(unittest.TestCase):
    def read_mock_file(self, file):
        with mock.patch(
            "moped.databases.cyc._open_file_and_remove_comments",
            mock.Mock(return_value=("", 0)),
        ):
            RP = ReactionParser("")
            RP.file = file
            rxns = RP.parse()
            return rxns

    def test_create_reaction(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001"])
        self.assertEqual(rxns["RXN001"]["id"], "RXN001")

    def test_set_ec_number(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "EC-NUMBER - EC-3.5.4.32"])
        self.assertEqual(rxns["RXN001"]["ec"], "EC-3.5.4.32")

    def test_add_single_pathway(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "IN-PATHWAY - PWY-7623"])
        self.assertEqual(rxns["RXN001"]["pathways"], {"PWY-7623"})

    def test_add_multiple_pathways(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "IN-PATHWAY - PWY-0001", "IN-PATHWAY - PWY-0002"])
        self.assertEqual(rxns["RXN001"]["pathways"], {"PWY-0001", "PWY-0002"})

    def test_add_single_enzyme(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "ENZYMATIC-REACTION - ENZRXN-23486"])
        self.assertEqual(rxns["RXN001"]["enzymes"], {"ENZRXN-23486"})

    def test_default_reversibility(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001"])
        self.assertEqual(rxns["RXN001"]["reversible"], False)

    def test_irreversible(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "REACTION-DIRECTION - LEFT-TO-RIGHT"])
        self.assertEqual(rxns["RXN001"]["reversible"], False)

    def test_reversible(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "REACTION-DIRECTION - REVERSIBLE"])
        self.assertEqual(rxns["RXN001"]["reversible"], True)

    def test_default_direction(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001"])
        self.assertEqual(rxns["RXN001"]["direction"], "LEFT-TO-RIGHT")

    def test_set_direction_left_to_right(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "REACTION-DIRECTION - LEFT-TO-RIGHT"])
        self.assertEqual(rxns["RXN001"]["direction"], "LEFT-TO-RIGHT")

    def test_set_direction_right_to_left(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "REACTION-DIRECTION - RIGHT-TO-LEFT"])
        self.assertEqual(rxns["RXN001"]["direction"], "RIGHT-TO-LEFT")

    def test_set_direction_reversible(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "REACTION-DIRECTION - REVERSIBLE"])
        self.assertEqual(rxns["RXN001"]["direction"], "REVERSIBLE")

    def test_add_direction_reversible(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "REACTION-DIRECTION - REVERSIBLE"])
        self.assertEqual(rxns["RXN001"]["direction"], "REVERSIBLE")

    def test_add_location_default(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001"])
        self.assertEqual(rxns["RXN001"]["locations"], [])

    def test_add_location_cytosol(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RXN-LOCATIONS - CCO-CYTOSOL"])
        self.assertEqual(rxns["RXN001"]["locations"], ["CCO-CYTOSOL"])

    def test_add_location_extracellular(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RXN-LOCATIONS - CCO-EXTRACELLULAR"])
        self.assertEqual(rxns["RXN001"]["locations"], ["CCO-EXTRACELLULAR"])

    def test_add_location_periplasm(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RXN-LOCATIONS - CCO-PERIPLASM"])
        self.assertEqual(rxns["RXN001"]["locations"], ["CCO-PERIPLASM"])

    def test_add_location_cci(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RXN-LOCATIONS - CCI-PERIPLASM"])
        self.assertEqual(rxns["RXN001"]["locations"], ["CCO-PERIPLASM"])

    def test_add_location_nil(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RXN-LOCATIONS - NIL"])
        self.assertEqual(rxns["RXN001"]["locations"], [])

    def test_add_location_other(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RXN-LOCATIONS - CCO-SIDE1"])
        self.assertEqual(rxns["RXN001"]["locations"], ["CCO-SIDE1"])

    def test_add_substrate_default_stoichiometry(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxns["RXN001"]["products"], {})

    def test_add_multiple_substrates(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "LEFT - cpd2"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -1, "cpd2_c": -1})
        self.assertEqual(rxns["RXN001"]["products"], {})

    def test_add_product_default_stoichiometry(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1"])
        self.assertEqual(rxns["RXN001"]["substrates"], {})
        self.assertEqual(rxns["RXN001"]["products"], {"cpd1_c": 1})

    def test_add_multiple_products(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "RIGHT - cpd2"])
        self.assertEqual(rxns["RXN001"]["substrates"], {})
        self.assertEqual(rxns["RXN001"]["products"], {"cpd1_c": 1, "cpd2_c": 1})

    def test_add_substrates_and_products(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "RIGHT - cpd1"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxns["RXN001"]["products"], {"cpd1_c": 1})

    def test_set_substrate_coefficient_one(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COEFFICIENT - 1"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -1.0})
        self.assertEqual(rxns["RXN001"]["products"], {})

    def test_set_substrate_coefficient_two(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COEFFICIENT - 2"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -2.0})
        self.assertEqual(rxns["RXN001"]["products"], {})

    def test_set_substrate_coefficient_variable(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COEFFICIENT - n"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -1.0})
        self.assertEqual(rxns["RXN001"]["products"], {})

    def test_set_product_coefficient_one(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COEFFICIENT - 1"])
        self.assertEqual(rxns["RXN001"]["substrates"], {})
        self.assertEqual(rxns["RXN001"]["products"], {"cpd1_c": 1.0})

    def test_set_product_coefficient_two(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COEFFICIENT - 2"])
        self.assertEqual(rxns["RXN001"]["substrates"], {})
        self.assertEqual(rxns["RXN001"]["products"], {"cpd1_c": 2.0})

    def test_set_product_coefficient_variable(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COEFFICIENT - n"])
        self.assertEqual(rxns["RXN001"]["substrates"], {})
        self.assertEqual(rxns["RXN001"]["products"], {"cpd1_c": 1.0})

    def test_set_substrate_compartment_default(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1"])
        self.assertEqual(rxns["RXN001"]["substrates"], {"cpd1_c": -1.0})
        self.assertEqual(rxns["RXN001"]["substrate_compartments"], {"cpd1_c": "CCO-IN"})

    def test_set_substrate_compartment_in(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COMPARTMENT - CCO-IN"])
        self.assertEqual(rxns["RXN001"]["substrate_compartments"], {"cpd1_c": "CCO-IN"})

    def test_set_substrate_compartment_out(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COMPARTMENT - CCO-OUT"])
        self.assertEqual(rxns["RXN001"]["substrate_compartments"], {"cpd1_c": "CCO-OUT"})

    def test_set_substrate_compartment_middle(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COMPARTMENT - CCO-MIDDLE"])
        self.assertEqual(rxns["RXN001"]["substrate_compartments"], {"cpd1_c": "CCO-OUT"})

    def test_set_substrate_compartment_other(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "LEFT - cpd1", "^COMPARTMENT - UNKNOWN"])
        self.assertEqual(rxns["RXN001"]["substrate_compartments"], {"cpd1_c": "CCO-IN"})

    def test_set_product_compartment_default(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1"])
        self.assertEqual(rxns["RXN001"]["product_compartments"], {"cpd1_c": "CCO-IN"})

    def test_set_product_compartment_in(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COMPARTMENT - CCO-IN"])
        self.assertEqual(rxns["RXN001"]["product_compartments"], {"cpd1_c": "CCO-IN"})

    def test_set_product_compartment_out(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COMPARTMENT - CCO-OUT"])
        self.assertEqual(rxns["RXN001"]["product_compartments"], {"cpd1_c": "CCO-OUT"})

    def test_set_product_compartment_middle(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COMPARTMENT - CCO-MIDDLE"])
        self.assertEqual(rxns["RXN001"]["product_compartments"], {"cpd1_c": "CCO-OUT"})

    def test_set_product_compartment_other(self):
        rxns = self.read_mock_file(["UNIQUE-ID - RXN001", "RIGHT - cpd1", "^COMPARTMENT - UNKNOWN"])
        self.assertEqual(rxns["RXN001"]["product_compartments"], {"cpd1_c": "CCO-IN"})


class EnzymeParserTests(unittest.TestCase):
    def read_mock_file(self, file):
        with mock.patch(
            "moped.databases.cyc._open_file_and_remove_comments",
            mock.Mock(return_value=("", 0)),
        ):
            EP = EnzymeParser("")
            EP.file = file
            return EP.parse()

    def test_read_single(self):
        enzrxns = self.read_mock_file(["UNIQUE-ID - ENZRXN-13149", "ENZYME - MONOMER-17831"])
        self.assertEqual(enzrxns["ENZRXN-13149"], {"enzyme": "MONOMER-17831"})


class SequenceParserTests(unittest.TestCase):
    def read_mock_file(self, file):
        with mock.patch("builtins.open", mock.mock_open(read_data="")):
            SP = SequenceParser("")
            SP.file = file
            return SP.parse()

    def test_read_multiple(self):
        sequences = self.read_mock_file(
            [
                ">gnl|META|HS10525-MONOMER Serine--pyruvate aminotransferase (Homo sapiens)",
                "MASHED",
                ">gnl|META|HS10520-MONOMER alpha-(1,3)-fucosyltransferase 9 (Homo sapiens)",
                "POTATOES",
            ]
        )
        self.assertEqual(sequences["HS10525-MONOMER"], "MASHED")
        self.assertEqual(sequences["HS10520-MONOMER"], "POTATOES")


class RepairerTests(unittest.TestCase):
    def test_reverse_stoichiometry(self):
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-IN"},
            "gibbs0": -10,
        }
        Repairer.reverse_stoichiometry(rxn)
        self.assertEqual(rxn["substrates"], {"cpd2_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd1_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], 10)

    def test_unify_direction_left_to_right(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], -10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_unify_direction_physiol_left_to_right(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "PHYSIOL-LEFT-TO-RIGHT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], -10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_unify_direction_irrev_left_to_right(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-LEFT-TO-RIGHT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], -10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_unify_direction_reversible(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "REVERSIBLE",
                "reversible": True,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], -10)
        self.assertEqual(rxn["reversible"], True)
        self.assertEqual(rxn["bounds"], (-1000, 1000))

    def test_unify_direction_right_to_left(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd2_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd1_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], 10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_unify_direction_physiol_right_to_left(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "PHYSIOL-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd2_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd1_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], 10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_unify_direction_irrev_right_to_left(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd2_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd1_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], 10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_unify_direction_garbage(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "GARBAGE",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        with self.assertWarns(UserWarning):
            r.unify_reaction_direction(reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})
        self.assertEqual(rxn["gibbs0"], -10)
        self.assertEqual(rxn["reversible"], False)
        self.assertEqual(rxn["bounds"], (0, 1000))

    def test_compound_existence(self):
        compounds = {"cpd1_c": {}, "cpd2_c": {}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_compound_existence(r.reactions["RXN1"]))

    def test_missing_substrate(self):
        compounds = {"cpd2_c": {}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_compound_existence(r.reactions["RXN1"]))

    def test_missing_product(self):
        compounds = {"cpd1_c": {}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_compound_existence(r.reactions["RXN1"]))

    def test_charge_balance_wrong_type_left(self):
        compounds = {"cpd1_c": {"charge": 1}, "cpd2_c": {"charge": 1}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": "-1"},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_charge_balance(r.reactions["RXN1"]))

    def test_charge_balance_wrong_type_right(self):
        compounds = {"cpd1_c": {"charge": 1}, "cpd2_c": {"charge": 1}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": "1"},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_charge_balance(r.reactions["RXN1"]))

    def test_charge_balance_both_zero(self):
        compounds = {"cpd1_c": {"charge": 0}, "cpd2_c": {"charge": 0}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_charge_balance(r.reactions["RXN1"]))

    def test_charge_balance_both_one(self):
        compounds = {"cpd1_c": {"charge": 1}, "cpd2_c": {"charge": 1}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_charge_balance(r.reactions["RXN1"]))

    def test_charge_balance_substrate_stoichiometry(self):
        compounds = {"cpd1_c": {"charge": 1}, "cpd2_c": {"charge": 2}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -2},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_charge_balance(r.reactions["RXN1"]))

    def test_charge_balance_product_stoichiometry(self):
        compounds = {"cpd1_c": {"charge": 2}, "cpd2_c": {"charge": 1}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 2},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_charge_balance(r.reactions["RXN1"]))

    def test_charge_balance_opposite_signs(self):
        compounds = {"cpd1_c": {"charge": -1}, "cpd2_c": {"charge": 1}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_charge_balance(r.reactions["RXN1"]))

    def test_mass_balance_single_atom(self):
        compounds = {"cpd1_c": {"formula": {"C": 1}}, "cpd2_c": {"formula": {"C": 1}}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_multiple_atoms(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 6, "H": 12, "O": 6}},
            "cpd2_c": {"formula": {"C": 6, "H": 12, "O": 6}},
        }
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_multiple_compounds(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 6, "H": 12, "O": 6}},
            "A": {"formula": {"C": 6}},
            "cpd2_c": {"formula": {"C": 6, "H": 12, "O": 6}},
            "B": {"formula": {"C": 6}},
        }
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1, "A": -2},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1, "B": 2},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_multiple_atoms_substrate_stoichiometry(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 3, "H": 6, "O": 3}},
            "cpd2_c": {"formula": {"C": 6, "H": 12, "O": 6}},
        }
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -2},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_multiple_atoms_product_stoichiometry(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 6, "H": 12, "O": 6}},
            "cpd2_c": {"formula": {"C": 3, "H": 6, "O": 3}},
        }
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 2},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertTrue(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_missing_substrate_formula(self):
        compounds = {"cpd1_c": {"formula": {}}, "cpd2_c": {"formula": {"C": 1}}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_missing_product_formula(self):
        compounds = {"cpd1_c": {"formula": {"C": 1}}, "cpd2_c": {"formula": {}}}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_missing_substrate_atom(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}},
            "cpd2_c": {"formula": {"C": 1, "H": 1}},
        }
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_mass_balance(r.reactions["RXN1"]))

    def test_mass_balance_missing_product_atom(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1, "H": 1}},
            "cpd2_c": {"formula": {"C": 1}},
        }
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "IRREVERSIBLE-RIGHT-TO-LEFT",
                "reversible": False,
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertFalse(r.check_mass_balance(r.reactions["RXN1"]))

    def test_variants_no_variants(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}, "charge": 1},
            "cpd2_c": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1"]
        self.assertEqual(rxn["id"], "RXN1")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})

    def test_variants_empty(self):
        compounds = {
            "A1": {"formula": {"C": 1}, "charge": 1},
            "A2": {"formula": {"C": 1}, "charge": 1},
            "B1": {"formula": {"C": 1}, "charge": 1},
            "B2": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": [], "T2": []}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        self.assertEqual(r.reactions, {})

    def test_variants_one_substrate(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}, "charge": 1},
            "cpd2_c": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["cpd1_c"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]

        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})

    def test_variants_two_substrates(self):
        compounds = {
            "X1": {"formula": {"C": 1}, "charge": 1},
            "X2": {"formula": {"C": 1}, "charge": 1},
            "cpd2_c": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["X1", "X2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"X1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"X1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})

        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"X2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"X2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})

    def test_variants_one_product(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}, "charge": 1},
            "cpd2_c": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T2": ["cpd2_c"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})

    def test_variants_two_products(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}, "charge": 1},
            "Y1": {"formula": {"C": 1}, "charge": 1},
            "Y2": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T2": ["Y1", "Y2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"Y1": 1})
        self.assertEqual(rxn["product_compartments"], {"Y1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"Y2": 1})
        self.assertEqual(rxn["product_compartments"], {"Y2": "CCO-IN"})

    def test_variants_one_substrate_one_product(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}, "charge": 1},
            "cpd2_c": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["cpd1_c"], "T2": ["cpd2_c"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN"})

    def test_variants_two_substrates_two_products(self):
        compounds = {
            "X1": {"formula": {"C": 1}, "charge": 1},
            "X2": {"formula": {"C": 1}, "charge": 1},
            "Y1": {"formula": {"C": 1}, "charge": 1},
            "Y2": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["X1", "X2"], "T2": ["Y1", "Y2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"X1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"X1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"Y1": 1})
        self.assertEqual(rxn["product_compartments"], {"Y1": "CCO-IN"})

        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"X1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"X1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"Y2": 1})
        self.assertEqual(rxn["product_compartments"], {"Y2": "CCO-IN"})

        rxn = r.reactions["RXN1__var__2"]
        self.assertEqual(rxn["id"], "RXN1__var__2")
        self.assertEqual(rxn["substrates"], {"X2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"X2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"Y1": 1})
        self.assertEqual(rxn["product_compartments"], {"Y1": "CCO-IN"})

        rxn = r.reactions["RXN1__var__3"]
        self.assertEqual(rxn["id"], "RXN1__var__3")
        self.assertEqual(rxn["substrates"], {"X2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"X2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"Y2": 1})
        self.assertEqual(rxn["product_compartments"], {"Y2": "CCO-IN"})

    def test_variants_two_substrates_two_products_one_normal(self):
        compounds = {
            "cpd1_c": {"formula": {"C": 1}, "charge": 1},
            "A1": {"formula": {"C": 1}, "charge": 1},
            "A2": {"formula": {"C": 1}, "charge": 1},
            "cpd2_c": {"formula": {"C": 1}, "charge": 1},
            "B1": {"formula": {"C": 1}, "charge": 1},
            "B2": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["A1", "A2"], "T2": ["B1", "B2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1, "T1": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN", "T1": "CCO-IN"},
            "products": {"cpd2_c": 1, "T2": 1},
            "product_compartments": {"cpd2_c": "CCO-IN", "T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1, "A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN", "A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1, "B1": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN", "B1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1, "A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN", "A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1, "B2": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN", "B2": "CCO-IN"})
        rxn = r.reactions["RXN1__var__2"]
        self.assertEqual(rxn["id"], "RXN1__var__2")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1, "A2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN", "A2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1, "B1": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN", "B1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__3"]
        self.assertEqual(rxn["id"], "RXN1__var__3")
        self.assertEqual(rxn["substrates"], {"cpd1_c": -1, "A2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"cpd1_c": "CCO-IN", "A2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"cpd2_c": 1, "B2": 1})
        self.assertEqual(rxn["product_compartments"], {"cpd2_c": "CCO-IN", "B2": "CCO-IN"})

    def test_variants_charge_matching(self):
        compounds = {
            "A1": {"formula": {"C": 1}, "charge": 1},
            "A2": {"formula": {"C": 1}, "charge": 0},
            "B1": {"formula": {"C": 1}, "charge": 1},
            "B2": {"formula": {"C": 1}, "charge": 0},
        }
        compound_types = {"T1": ["A1", "A2"], "T2": ["B1", "B2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B1": 1})
        self.assertEqual(rxn["product_compartments"], {"B1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"A2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B2": 1})
        self.assertEqual(rxn["product_compartments"], {"B2": "CCO-IN"})

    def test_variants_formula_matching(self):
        compounds = {
            "A1": {"formula": {"C": 1, "H": 1}, "charge": 1},
            "A2": {"formula": {"C": 1}, "charge": 1},
            "B1": {"formula": {"C": 1, "H": 1}, "charge": 1},
            "B2": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["A1", "A2"], "T2": ["B1", "B2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B1": 1})
        self.assertEqual(rxn["product_compartments"], {"B1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"A2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B2": 1})
        self.assertEqual(rxn["product_compartments"], {"B2": "CCO-IN"})

    def test_variants_missing_substrate(self):
        compounds = {
            "A1": {"formula": {"C": 1}, "charge": 1},
            "B1": {"formula": {"C": 1}, "charge": 1},
            "B2": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["A1", "A2"], "T2": ["B1", "B2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B1": 1})
        self.assertEqual(rxn["product_compartments"], {"B1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B2": 1})
        self.assertEqual(rxn["product_compartments"], {"B2": "CCO-IN"})

    def test_variants_missing_product(self):
        compounds = {
            "A1": {"formula": {"C": 1}, "charge": 1},
            "A2": {"formula": {"C": 1}, "charge": 1},
            "B1": {"formula": {"C": 1}, "charge": 1},
        }
        compound_types = {"T1": ["A1", "A2"], "T2": ["B1", "B2"]}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"T1": -1},
            "substrate_compartments": {"T1": "CCO-IN"},
            "products": {"T2": 1},
            "product_compartments": {"T2": "CCO-IN"},
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.create_reaction_variants("RXN1", r.reactions["RXN1"])
        rxn = r.reactions["RXN1__var__0"]
        self.assertEqual(rxn["id"], "RXN1__var__0")
        self.assertEqual(rxn["substrates"], {"A1": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A1": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B1": 1})
        self.assertEqual(rxn["product_compartments"], {"B1": "CCO-IN"})
        rxn = r.reactions["RXN1__var__1"]
        self.assertEqual(rxn["id"], "RXN1__var__1")
        self.assertEqual(rxn["substrates"], {"A2": -1})
        self.assertEqual(rxn["substrate_compartments"], {"A2": "CCO-IN"})
        self.assertEqual(rxn["products"], {"B1": 1})
        self.assertEqual(rxn["product_compartments"], {"B1": "CCO-IN"})

    def test_split_location_string(self):
        compounds = {}
        compound_types = {}
        reactions = {}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        self.assertEqual(
            r.split_location_string("CCO-CYTOSOL"),
            {"CCO-OUT": "CYTOSOL", "CCO-IN": "CYTOSOL"},
        )
        self.assertEqual(
            r.split_location_string("CCO-EXTRACELLULAR"),
            {"CCO-OUT": "EXTRACELLULAR", "CCO-IN": "CYTOSOL"},
        )
        self.assertEqual(
            r.split_location_string("CCO-EXTRACELLULAR-CCO-CYTOSOL"),
            {"CCO-OUT": "EXTRACELLULAR", "CCO-IN": "CYTOSOL"},
        )
        self.assertEqual(
            r.split_location_string("CCO-CYTOSOL-CCO-EXTRACELLULAR"),
            {"CCO-OUT": "CYTOSOL", "CCO-IN": "EXTRACELLULAR"},
        )

    def test_fix_compartments_both_in(self):
        compounds = {
            "cpd1_c": {
                "base_id": "cpd1",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
            "cpd2_c": {
                "base_id": "cpd2",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
        }
        compound_types = {}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-IN"},
            "locations": [],
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.fix_reaction_compartments("RXN1")
        self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.reactions["RXN1_c"]["substrates"], {"cpd1_c": -1})
        self.assertEqual(r.reactions["RXN1_c"]["products"], {"cpd2_c": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1_c"]["substrate_compartments"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_c"]["product_compartments"]

    def test_fix_compartments_both_out(self):
        compounds = {
            "cpd1_c": {
                "base_id": "cpd1",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
            "cpd2_c": {
                "base_id": "cpd2",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
        }
        compound_types = {}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-OUT"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-OUT"},
            "locations": [],
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.fix_reaction_compartments("RXN1")
        self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd1_e"]["compartment"], "EXTRACELLULAR")
        self.assertEqual(r.compounds["cpd2_e"]["compartment"], "EXTRACELLULAR")
        self.assertEqual(r.reactions["RXN1_e"]["substrates"], {"cpd1_e": -1})
        self.assertEqual(r.reactions["RXN1_e"]["products"], {"cpd2_e": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_e"]["substrate_compartments"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_e"]["product_compartments"]

    def test_fix_compartments_in_out(self):
        compounds = {
            "cpd1_c": {
                "base_id": "cpd1",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
            "cpd2_c": {
                "base_id": "cpd2",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
        }
        compound_types = {}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-IN"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-OUT"},
            "locations": [],
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.fix_reaction_compartments("RXN1")
        self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd2_e"]["compartment"], "EXTRACELLULAR")
        self.assertEqual(r.reactions["RXN1_c_e"]["substrates"], {"cpd1_c": -1})
        self.assertEqual(r.reactions["RXN1_c_e"]["products"], {"cpd2_e": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_c_e"]["substrate_compartments"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_c_e"]["product_compartments"]

    def test_fix_compartments_out_in(self):
        compounds = {
            "cpd1_c": {
                "base_id": "cpd1",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
            "cpd2_c": {
                "base_id": "cpd2",
                "formula": {"C": 1},
                "charge": 1,
                "compartment": "CYTOSOL",
            },
        }
        compound_types = {}
        rxn = {
            "id": "RXN1",
            "base_id": None,
            "substrates": {"cpd1_c": -1},
            "substrate_compartments": {"cpd1_c": "CCO-OUT"},
            "products": {"cpd2_c": 1},
            "product_compartments": {"cpd2_c": "CCO-IN"},
            "locations": [],
        }
        reactions = {"RXN1": rxn}
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        r.fix_reaction_compartments("RXN1")
        self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
        self.assertEqual(r.compounds["cpd1_e"]["compartment"], "EXTRACELLULAR")
        self.assertEqual(r.reactions["RXN1_c_e"]["substrates"], {"cpd1_e": -1})
        self.assertEqual(r.reactions["RXN1_c_e"]["products"], {"cpd2_c": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_c_e"]["substrate_compartments"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1_c_e"]["product_compartments"]

    def test_fix_compartments_periplasm(self):
        locations = [
            "CCO-CHL-THY-MEM",
            "CCO-CHLOR-STR",
            "CCO-MIT-IM-SPC",
            "CCO-MIT-IMEM",
            "CCO-OUTER-MEM",
            "CCO-PERI-BAC",
            "CCO-PERI-BAC-GN",
            "CCO-PERIPLASM",
            "CCO-PLASMA-MEM",
            "CCO-PLAST-IMEM",
            "CCO-PM-ANIMAL",
            "CCO-PM-BAC-ACT",
            "CCO-PM-BAC-NEG",
            "CCO-PM-BAC-POS",
            "CCO-RGH-ER-MEM",
            "CCO-VAC-MEM",
        ]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_p"]["compartment"], "PERIPLASM")
            self.assertEqual(r.reactions["RXN1_c_p"]["substrates"], {"cpd1_c": -1})
            self.assertEqual(r.reactions["RXN1_c_p"]["products"], {"cpd2_p": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_p"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_p"]["product_compartments"]

    def test_fix_compartments_extracellular(self):
        locations = ["CCO-EXTRACELLULAR"]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_e"]["compartment"], "EXTRACELLULAR")
            self.assertEqual(r.reactions["RXN1_c_e"]["substrates"], {"cpd1_c": -1})
            self.assertEqual(r.reactions["RXN1_c_e"]["products"], {"cpd2_e": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_e"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_e"]["product_compartments"]

    def test_fix_compartments_transporters_c_c(self):
        locations = [
            "CCO-CYTOSOL-CCO-MIT-LUM",
            "CCO-CYTOSOL-CCO-VAC-LUM",
            "CCO-MIT-LUM-CCO-CYTOSOL",
            "CCO-PEROX-LUM-CCO-CYTOSOL",
            "CCO-RGH-ER-LUM-CCO-CYTOSOL",
            "CCO-CYTOSOL",
            "CCO-IN",
            "CCO-LYS-LUM",
            "CCO-MIT-LUM",
            "CCO-GOLGI-LUM",
            "CCO-PEROX-LUM",
            "CCO-RGH-ER-LUM",
        ]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.reactions["RXN1_c"]["substrates"], {"cpd1_c": -1})
            self.assertEqual(r.reactions["RXN1_c"]["products"], {"cpd2_c": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c"]["product_compartments"]

    def test_fix_compartments_transporters_c_p(self):
        locations = [
            "CCO-CHLOR-STR-CCO-CYTOSOL",
            "CCO-SIDE-2-CCO-SIDE-1",
            "CCO-PERI-BAC-CCO-CYTOSOL",
            "CCO-PERI-BAC-CCO-IN",
            "CCO-CHLOR-STR-CCO-THY-LUM-CYA",
            "CCO-MIT-IM-SPC-CCO-MIT-LUM",
        ]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_p"]["compartment"], "PERIPLASM")
            self.assertEqual(r.reactions["RXN1_c_p"]["substrates"], {"cpd1_c": -1})
            self.assertEqual(r.reactions["RXN1_c_p"]["products"], {"cpd2_p": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_p"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_p"]["product_compartments"]

    def test_fix_compartments_transporters_p_p(self):
        locations = [
            "CCO-PERI-BAC-CCO-PERI-BAC",
        ]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
                "gibbs0": 0,
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd1_p"]["compartment"], "PERIPLASM")
            self.assertEqual(r.compounds["cpd2_p"]["compartment"], "PERIPLASM")
            self.assertEqual(r.reactions["RXN1_p"]["substrates"], {"cpd1_p": -1})
            self.assertEqual(r.reactions["RXN1_p"]["products"], {"cpd2_p": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_p"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_p"]["product_compartments"]

    def test_fix_compartments_transporters_p_c(self):
        locations = [
            "CCO-CYTOSOL-CCO-CHLOR-STR",
            "CCO-CYTOSOL-CCO-CHROM-STR",
            "CCO-CYTOSOL-CCO-PLASTID-STR",
            "CCO-CYTOSOL-CCO-VESICLE",
            "CCO-SIDE-1-CCO-SIDE-2",
        ]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd1_p"]["compartment"], "PERIPLASM")
            self.assertEqual(r.reactions["RXN1_p_c"]["substrates"], {"cpd1_p": -1})
            self.assertEqual(r.reactions["RXN1_p_c"]["products"], {"cpd2_c": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_p_c"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_p_c"]["product_compartments"]

    def test_fix_compartments_transporters_c_e(self):
        locations = [
            "CCO-EXTRACELLULAR-CCO-CYTOSOL",
            "CCO-EXTRACELLULAR-CCO-IN",
            "CCO-EXTRACELLULAR-CCO-UNKNOWN-SPACE",
            "CCO-OUT-CCO-CYTOSOL",
            "CCO-OUT-CCO-IN",
            "CCO-OUT-CCO-RGH-ER-LUM",
            "CCO-OUT",
        ]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_e"]["compartment"], "EXTRACELLULAR")
            self.assertEqual(r.reactions["RXN1_c_e"]["substrates"], {"cpd1_c": -1})
            self.assertEqual(r.reactions["RXN1_c_e"]["products"], {"cpd2_e": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_e"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_c_e"]["product_compartments"]

    def test_fix_compartments_transporters_e_e(self):
        locations = ["CCO-OUT-CCO-EXTRACELLULAR"]
        for location in locations:
            compounds = {
                "cpd1_c": {
                    "base_id": "cpd1",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
                "cpd2_c": {
                    "base_id": "cpd2",
                    "formula": {"C": 1},
                    "charge": 1,
                    "compartment": "CYTOSOL",
                },
            }
            compound_types = {}
            rxn = {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-OUT"},
                "locations": [location],
            }
            reactions = {"RXN1": rxn}
            r = Repairer(
                compounds=compounds,
                compound_types=compound_types,
                reactions=reactions,
                compartment_map=COMPARTMENT_MAP,
            )
            r.fix_reaction_compartments("RXN1")
            self.assertEqual(r.compounds["cpd1_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd2_c"]["compartment"], "CYTOSOL")
            self.assertEqual(r.compounds["cpd1_e"]["compartment"], "EXTRACELLULAR")
            self.assertEqual(r.reactions["RXN1_e"]["substrates"], {"cpd1_e": -1})
            self.assertEqual(r.reactions["RXN1_e"]["products"], {"cpd2_e": 1})
            with self.assertRaises(KeyError):
                r.reactions["RXN1"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_e"]["substrate_compartments"]
            with self.assertRaises(KeyError):
                r.reactions["RXN1_e"]["product_compartments"]

    def test_set_stoichiometry_basic_case(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "products": {"cpd2_c": 1},
            }
        }

        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertTrue(res)
        self.assertEqual(r.reactions["RXN1"]["stoichiometries"], {"cpd1_c": -1, "cpd2_c": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]["substrates"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]["products"]

    def test_set_stoichiometry_to_be_removed(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "products": {"cpd1_c": 1},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertFalse(res)

    def test_set_stoichiometry_empty_products(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -2},
                "products": {"cpd1_c": 1},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertFalse(res)

    def test_set_stoichiometry_empty_products2(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -2},
                "products": {},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertFalse(res)

    def test_set_stoichiometry_empty_substrates(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1},
                "products": {"cpd1_c": 2},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertFalse(res)

    def test_set_stoichiometry_empty_substrates2(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {},
                "products": {"cpd1_c": 2},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertFalse(res)

    def test_set_stoichiometry_remove_duplicates(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -2},
                "products": {"cpd1_c": 1, "cpd2_c": 1},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertTrue(res)
        self.assertEqual(r.reactions["RXN1"]["stoichiometries"], {"cpd1_c": -1, "cpd2_c": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]["substrates"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]["products"]

    def test_set_stoichiometry_remove_duplicates2(self):
        compounds = {}
        compound_types = {}
        reactions = {
            "RXN1": {
                "id": "RXN1",
                "base_id": None,
                "substrates": {"cpd1_c": -1, "cpd2_c": -1},
                "products": {"cpd1_c": 2},
            }
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        res = r.set_reaction_stoichiometry(r.reactions["RXN1"])
        self.assertTrue(res)
        self.assertEqual(r.reactions["RXN1"]["stoichiometries"], {"cpd2_c": -1, "cpd1_c": 1})
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]["substrates"]
        with self.assertRaises(KeyError):
            r.reactions["RXN1"]["products"]


class EnzymeComplexTests(unittest.TestCase):
    def test_check_for_monomers_single_layer(self):
        enzrxn_to_monomer = {}
        enzrxns = {
            "ENZRXN-CPLX-1": {"enzyme": "CPLX-1"},
        }
        monomers = {"MONOMER-1"}
        complexes = {
            "CPLX-1": {"MONOMER-1"},
        }
        enzrxn = "ENZRXN-CPLX-1"
        protein = enzrxns[enzrxn]["enzyme"]
        _check_for_monomer(
            enzrxn=enzrxn,
            protein=protein,
            monomers=monomers,
            complexes=complexes,
            enzrxn_to_monomer=enzrxn_to_monomer,
        )
        self.assertEqual(enzrxn_to_monomer, {"ENZRXN-CPLX-1": {"MONOMER-1"}})

    def test_check_for_monomers_single_layer_two_monomers(self):
        enzrxn_to_monomer = {}
        enzrxns = {
            "ENZRXN-CPLX-1": {"enzyme": "CPLX-1"},
        }
        monomers = {"MONOMER-1", "MONOMER-2"}
        complexes = {
            "CPLX-1": {"MONOMER-1", "MONOMER-2"},
        }
        enzrxn = "ENZRXN-CPLX-1"
        protein = enzrxns[enzrxn]["enzyme"]
        _check_for_monomer(
            enzrxn=enzrxn,
            protein=protein,
            monomers=monomers,
            complexes=complexes,
            enzrxn_to_monomer=enzrxn_to_monomer,
        )
        self.assertEqual(enzrxn_to_monomer, {"ENZRXN-CPLX-1": {"MONOMER-1", "MONOMER-2"}})

    def test_check_for_monomers_single_layer_two_monomers_one_missing(self):
        enzrxn_to_monomer = {}
        enzrxns = {
            "ENZRXN-CPLX-1": {"enzyme": "CPLX-1"},
        }
        monomers = {"MONOMER-1"}
        complexes = {
            "CPLX-1": {"MONOMER-1", "MONOMER-2"},
        }
        enzrxn = "ENZRXN-CPLX-1"
        protein = enzrxns[enzrxn]["enzyme"]
        _check_for_monomer(
            enzrxn=enzrxn,
            protein=protein,
            monomers=monomers,
            complexes=complexes,
            enzrxn_to_monomer=enzrxn_to_monomer,
        )
        self.assertEqual(enzrxn_to_monomer, {"ENZRXN-CPLX-1": {"MONOMER-1"}})

    def test_check_for_monomers_two_layers(self):
        enzrxns = {
            "ENZRXN-CPLX-1": {"enzyme": "CPLX-2"},
        }

        enzrxn_to_monomer = {}
        monomers = {"MONOMER-1", "MONOMER-2"}
        complexes = {
            "CPLX-1": {"MONOMER-2"},
            "CPLX-2": {"CPLX-1", "MONOMER-1"},
        }

        enzrxn = "ENZRXN-CPLX-1"
        protein = enzrxns[enzrxn]["enzyme"]

        _check_for_monomer(
            enzrxn=enzrxn,
            protein=protein,
            monomers=monomers,
            complexes=complexes,
            enzrxn_to_monomer=enzrxn_to_monomer,
        )
        self.assertEqual(enzrxn_to_monomer, {"ENZRXN-CPLX-1": {"MONOMER-1", "MONOMER-2"}})

    def test_get_enzrnx_to_monomer_mapping(self):
        enzrxns = {
            "ENZRXN-MONO-1": {"enzyme": "MONOMER-1"},
            "ENZRXN-CPLX-1": {"enzyme": "CPLX-2"},
        }
        monomers = {"MONOMER-1", "MONOMER-2"}
        complexes = {
            "CPLX-1": {"MONOMER-2"},
            "CPLX-2": {"CPLX-1", "MONOMER-1"},
        }
        self.assertEqual(
            _get_enzrnx_to_monomer_mapping(enzrxns=enzrxns, monomers=monomers, complexes=complexes),
            {
                "ENZRXN-MONO-1": {"MONOMER-1"},
                "ENZRXN-CPLX-1": {"MONOMER-1", "MONOMER-2"},
            },
        )

    def test_get_enzrnx_to_sequence_mapping(self):
        enzrxn_to_monomer = {
            "ENZRXN-MONO-1": {"MONOMER-1"},
            "ENZRXN-CPLX-1": {"MONOMER-2", "MONOMER-3", "MONOMER-MISSING"},
        }
        sequences = {
            "MONOMER-1": "ATGC",
            "MONOMER-2": "TGCA",
            "MONOMER-3": "GCAT",
        }

        self.assertEqual(
            _get_enzrnx_to_sequence_mapping(enzrxn_to_monomer=enzrxn_to_monomer, sequences=sequences),
            {
                "ENZRXN-MONO-1": {"MONOMER-1": "ATGC"},
                "ENZRXN-CPLX-1": {"MONOMER-3": "GCAT", "MONOMER-2": "TGCA"},
            },
        )

    def test_map_reactions_to_sequences(self):
        enzrxn_to_monomer = {
            "ENZRXN-MONO-1": {"MONOMER-1"},
            "ENZRXN-CPLX-1": {"MONOMER-2", "MONOMER-3"},
        }

        enzrxn_to_sequences = {
            "ENZRXN-MONO-1": {"MONOMER-1": "ATGC"},
            "ENZRXN-CPLX-1": {"MONOMER-2": "TGCA", "MONOMER-3": "GCAT"},
        }

        reactions = {
            "RXN-1": {"enzymes": {"ENZRXN-MONO-1"}},
            "RXN-2": {"enzymes": {"ENZRXN-CPLX-1"}},
            "RXN-MISSING-1": {"enzymes": {"ENZRXN-MISSING"}},
            "RXN-MISSING-2": {},
        }

        _map_reactions_to_sequences(
            reactions=reactions,
            enzrxn_to_monomer=enzrxn_to_monomer,
            enzrxn_to_seq=enzrxn_to_sequences,
        )

        self.assertEqual(
            reactions,
            {
                "RXN-1": {
                    "enzymes": {"ENZRXN-MONO-1"},
                    "sequences": {"MONOMER-1": "ATGC"},
                    "monomers": {"ENZRXN-MONO-1": {"MONOMER-1"}},
                },
                "RXN-2": {
                    "enzymes": {"ENZRXN-CPLX-1"},
                    "sequences": {"MONOMER-2": "TGCA", "MONOMER-3": "GCAT"},
                    "monomers": {"ENZRXN-CPLX-1": {"MONOMER-3", "MONOMER-2"}},
                },
                "RXN-MISSING-1": {
                    "enzymes": {"ENZRXN-MISSING"},
                    "sequences": {},
                    "monomers": {"ENZRXN-MISSING": set()},
                },
                "RXN-MISSING-2": {"sequences": {}, "monomers": {}},
            },
        )

    def test_map_reactions_to_kinetic_parameters(self):
        reactions = {
            "RXN-1": {"enzymes": {"ENZRXN-MONO-1"}},
            "RXN-2": {"enzymes": {"ENZRXN-CPLX-1"}},
            "RXN-MISSING-1": {"enzymes": {"ENZRXN-MISSING"}},
            "RXN-MISSING-2": {},
        }

        enzrxns = {
            "ENZRXN-MONO-1": {"enzyme": "MONOMER-1", "km": 1, "vmax": 2},
            "ENZRXN-CPLX-1": {"enzyme": "CPLX-2", "kcat": 1},
        }

        _map_reactions_to_kinetic_parameters(
            reactions=reactions,
            enzrxns=enzrxns,
        )

        self.assertEqual(
            reactions,
            {
                "RXN-1": {
                    "enzymes": {"ENZRXN-MONO-1"},
                    "enzrxns": {"ENZRXN-MONO-1": {"km": 1, "vmax": 2}},
                },
                "RXN-2": {
                    "enzymes": {"ENZRXN-CPLX-1"},
                    "enzrxns": {"ENZRXN-CPLX-1": {"kcat": 1}},
                },
                "RXN-MISSING-1": {"enzymes": {"ENZRXN-MISSING"}},
                "RXN-MISSING-2": {},
            },
        )


class CycIntegrationTests(unittest.TestCase):
    def test_cyc_parse(self):
        compounds, reactions, compartments = Cyc(
            pgdb_path=TESTCYC_PATH,
            compartment_map=COMPARTMENT_MAP,
            parse_sequences=True,
        ).parse()
        self.assertTrue(True)

    def test_cyc_parse_no_sequences(self):
        compounds, reactions, compartments = Cyc(
            pgdb_path=TESTCYC_WO_SEQ_PATH,
            compartment_map=COMPARTMENT_MAP,
            parse_sequences=True,
        ).parse()
        self.assertTrue(True)


class RepairerIntegrationTests(unittest.TestCase):
    def test_repair(self):
        compounds = {
            "cpd1_c": {
                "base_id": "cpd1",
                "charge": 1,
                "formula": {"C": 6},
                "compartment": "CYTOSOL",
            },
            "cpd2_c": {
                "base_id": "cpd2",
                "charge": 1,
                "formula": {"C": 6},
                "compartment": "CYTOSOL",
            },
            "cpd3_c": {
                "base_id": "cpd3",
                "charge": 2,
                "formula": {"C": 6},
                "compartment": "CYTOSOL",
            },
            "cpd4_c": {
                "base_id": "cpd4",
                "charge": 1,
                "formula": {"C": 3},
                "compartment": "CYTOSOL",
            },
        }
        compound_types = {
            "T1": ["cpd1_c"],
            "T2": ["cpd2_c"],
            "T3": ["cpd3_c"],
            "T4": ["cpd4_c"],
        }
        reactions = {
            "RXN-PASS": {
                "id": "RXN1",
                "base_id": "RXN1",
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": [],
                "reversible": False,
            },
            "RXN-fail-on-cpd-existence": {
                "id": "RXN2",
                "base_id": "RXN2",
                "substrates": {"cpdX_c": -1},
                "substrate_compartments": {"cpdX_c": "CCO-IN"},
                "products": {"cpd2_c": 1},
                "product_compartments": {"cpd2_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": [],
                "reversible": False,
            },
            "RXN-fail-on-charge-balance": {
                "id": "RXN3",
                "base_id": "RXN3",
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd3_c": 1},
                "product_compartments": {"cpd3_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": [],
                "reversible": False,
            },
            "RXN-fail-on-mass-balance": {
                "id": "RXN4",
                "base_id": "RXN4",
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd4_c": 1},
                "product_compartments": {"cpd4_c": "CCO-IN"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": [],
                "reversible": False,
            },
            "RXN-create-variants": {
                "id": "RXN5",
                "base_id": "RXN5",
                "substrates": {"T1": -1},
                "substrate_compartments": {"T1": "CCO-IN"},
                "products": {"T2": 1},
                "product_compartments": {"T2": "CCO-IN"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": [],
                "reversible": False,
            },
            "RXN-create-compartment-variants": {
                "id": "RXN6",
                "base_id": "RXN6",
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd1_c": 1},
                "product_compartments": {"cpd1_c": "CCO-OUT"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": ["CCO-EXTRACELLULAR-CCO-CYTOSOL"],
                "reversible": False,
            },
            "RXN-create-compartment-variants-fail-on-stoichiometry": {
                "id": "RXN7",
                "base_id": "RXN7",
                "substrates": {"cpd1_c": -1},
                "substrate_compartments": {"cpd1_c": "CCO-IN"},
                "products": {"cpd1_c": 1},
                "product_compartments": {"cpd1_c": "CCO-OUT"},
                "gibbs0": -10,
                "direction": "LEFT-TO-RIGHT",
                "locations": ["CCO-CYTOSOL-CCO-CYTOSOL"],
                "reversible": False,
            },
        }
        r = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=COMPARTMENT_MAP,
        )
        compounds, reactions, compartments = r.repair()
        self.assertEqual(set([i.id for i in reactions]), {"RXN1_c", "RXN6_c_e", "RXN5__var__0_c"})
