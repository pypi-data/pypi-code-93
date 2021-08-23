"""Parse and repair metacyc or biocyc PGDB databases."""

import itertools as it
import pathlib
import re
import warnings
from collections import defaultdict
from copy import deepcopy

from ..core.compound import Compound
from ..core.reaction import Reaction

COMPARTMENT_SUFFIXES = {
    # Common to all
    "CYTOSOL": "c",
    "EXTRACELLULAR": "e",
    "PERIPLASM": "p",
    "MITOCHONDRIA": "m",
    "PEROXISOME": "x",
    "ER": "r",
    "VACUOLE": "v",
    "NUCLEUS": "n",
    "GOLGI": "g",
    "THYLAKOID": "u",
    "LYSOSOME": "l",
    "CHLOROPLAST": "h",
    "FLAGELLUM": "f",
    "EYESPOT": "s",
    "INTERMEMBRANE": "im",
    "CARBOXYSOME": "cx",
    "THYLAKOID-MEMBRANE": "um",
    "CYTOSOLIC-MEMBRANE": "cm",
    "INNER-MITOCHONDRIA": "i",
    "MITOCHONDRIA-INNER-MEMBRANE": "mm",
    "WILDTYPE": "w",
    "CYTOCHROME-COMPLEX": "y",
}

# Often lines starting with these identifiers
# are malformed
MALFORMED_LINE_STARTS = {"/", "COMMENT", "CITATIONS", "^CITATIONS", "SYNONYMS", "#"}


def map_compartment_to_model_compartments(compartment, compartment_map):
    """Map metacyc compartments to model compartments.

    Parameters
    ----------
    compartment : str
        The metacyc compartment

    Returns
    -------
    compartment : str
        Our choice of compartment for the given compartment
    """
    return compartment_map[compartment]


def add_moped_compartment_suffix(object_id, compartment):
    """Add a compartment suffix (e.g. _e for extracellular) to the id.

    Raises
    ------
    KeyError
        If compartment does not exist
    """
    return object_id + f"_{COMPARTMENT_SUFFIXES[compartment]}"


def _check_for_monomer(enzrxn, protein, monomers, complexes, enzrxn_to_monomer):
    """Check complex tree until you arrive at monomers."""
    try:
        for subcomplex in complexes[protein]:
            if subcomplex in monomers:
                enzrxn_to_monomer.setdefault(enzrxn, set()).add(subcomplex)
            else:
                _check_for_monomer(enzrxn, subcomplex, monomers, complexes, enzrxn_to_monomer)
    except KeyError:
        pass


def _get_enzrnx_to_monomer_mapping(enzrxns, monomers, complexes):
    """Get mapping of enzyme reactions to monomers."""
    enzrxn_to_monomer = {}
    for enzrxn, enzrxn_dict in enzrxns.items():
        protein = enzrxn_dict["enzyme"]
        if protein in monomers:
            enzrxn_to_monomer.setdefault(enzrxn, set()).add(protein)
        else:
            _check_for_monomer(enzrxn, protein, monomers, complexes, enzrxn_to_monomer)
    return enzrxn_to_monomer


def _get_enzrnx_to_sequence_mapping(enzrxn_to_monomer, sequences):
    """Get mapping of enzyme reactions to sequences."""
    enzrxn_to_sequence = {}
    for enzrxn, monomers in enzrxn_to_monomer.items():
        for monomer in monomers:
            try:
                sequence = sequences[monomer]
                enzrxn_to_sequence.setdefault(enzrxn, dict())[monomer] = sequence
            except KeyError:
                pass
    return enzrxn_to_sequence


def _map_reactions_to_sequences(reactions, enzrxn_to_monomer, enzrxn_to_seq):
    """Get mapping of enzyme reactions to sequences."""
    for reaction in reactions.values():
        reaction["sequences"] = {}
        reaction["monomers"] = {}
        try:
            for enzrxn in reaction["enzymes"]:
                try:
                    reaction["sequences"].update(enzrxn_to_seq[enzrxn])
                except KeyError:
                    pass
                try:
                    reaction["monomers"].setdefault(enzrxn, set()).update(enzrxn_to_monomer[enzrxn])
                except KeyError:
                    pass
        except KeyError:
            pass


def _map_reactions_to_kinetic_parameters(reactions, enzrxns):
    """Get mapping of enzyme reactions to kinetic parameters."""
    for reaction in reactions.values():
        try:
            for enzrxn in reaction["enzymes"]:
                try:
                    enzrxn_dict = enzrxns[enzrxn]
                except KeyError:
                    pass
                else:
                    for k, v in enzrxn_dict.items():
                        if k != "enzyme":
                            reaction.setdefault("enzrxns", {}).setdefault(enzrxn, {}).setdefault(k, v)
        except KeyError:
            pass


class Cyc:
    """Base class for all metacyc/biocyc related databases."""

    def __init__(
        self,
        pgdb_path,
        compartment_map,
        parse_sequences=True,
    ):
        """Parse a *cyc pgdb into a moped.Model.

        Parameters
        ----------
        pgdb_path : pathlib.Path
            Path to the pgdb
        parse_enzymes : bool
        parse_sequences : bool
        name : str, optional

        Returns
        -------
        moped.Model
        """
        self.path = pathlib.Path(pgdb_path)
        self.parse_sequences = parse_sequences
        self.compartment_map = compartment_map

    def parse(self):
        """Parse the database."""
        path = self.path
        compounds, compound_types = CompoundParser(path / "compounds.dat").parse()
        reactions = ReactionParser(path / "reactions.dat").parse()

        if self.parse_sequences:
            try:
                enzrxns = EnzymeParser(path / "enzrxns.dat").parse()
                monomers, complexes = ProteinParser(path / "proteins.dat").parse()
                sequences = SequenceParser(path / "protseq.fsa").parse()
            except FileNotFoundError:
                pass
            else:
                enzrxn_to_monomer = _get_enzrnx_to_monomer_mapping(enzrxns, monomers, complexes)
                enzrxn_to_seq = _get_enzrnx_to_sequence_mapping(enzrxn_to_monomer, sequences)
                enzrxn_to_monomer = _get_enzrnx_to_monomer_mapping(enzrxns, monomers, complexes)
                enzrxn_to_seq = _get_enzrnx_to_sequence_mapping(enzrxn_to_monomer, sequences)
                _map_reactions_to_sequences(reactions, enzrxn_to_monomer, enzrxn_to_seq)
                _map_reactions_to_kinetic_parameters(reactions, enzrxns)

        compounds, reactions, compartments = Repairer(
            compounds=compounds,
            compound_types=compound_types,
            reactions=reactions,
            compartment_map=self.compartment_map,
        ).repair()
        return compounds, reactions, compartments


###############################################################################
# Universal functions
###############################################################################


def _remove_top_comments(file):
    """Remove the metainformation from a pgdb file."""
    for i, line in enumerate(file):
        if line.startswith("UNIQUE-ID"):
            break
    return file[i:], i


def _open_file_and_remove_comments(path):
    """Read the file and remove metainformation."""
    with open(path, encoding="ISO-8859-14") as f:
        file = f.readlines()
    return _remove_top_comments(file)


def _rename(content):
    """Remove garbage from compound and reaction ids.

    Parameters
    ----------
    content : str

    Returns
    -------
    content : str
    """
    return (
        content.replace("<i>", "")
        .replace("</i>", "")
        .replace("<SUP>", "")
        .replace("</SUP>", "")
        .replace("<sup>", "")
        .replace("</sup>", "")
        .replace("<sub>", "")
        .replace("</sub>", "")
        .replace("<SUB>", "")
        .replace("</SUB>", "")
        .replace("&", "")
        .replace(";", "")
        .replace("|", "")
    )


def _do_nothing(*args):
    """Chill. The archetype of a useful function."""
    pass


def _set_gibbs0(dictionary, id_, gibbs0):
    dictionary[id_]["gibbs0"] = float(gibbs0)


def _set_name(dictionary, id_, name):
    dictionary[id_]["name"] = _rename(name)


def _add_database_link(dictionary, id_, content):
    """Short description.

    Database links are of form DBLINKS - (REFMET "Tryptophan" NIL |midford| 3697479617 NIL NIL)
    so content will be (REFMET "Tryptophan" NIL |midford| 3697479617 NIL NIL)
    """
    database, database_id, *_ = content[1:-1].split(" ")
    dictionary[id_]["database_links"].setdefault(database, set()).add(database_id[1:-1])


def _add_type(dictionary, id_, type_):
    """Short description.

    Parameters
    ----------
    Compounds : dict
    id_ : str
    content :
    """
    dictionary[id_]["types"].append(type_)


###############################################################################
# Compound function
###############################################################################


def _set_atom_charges(compounds, id_, content):
    """Short description.

    Parameters
    ----------
    Compounds : dict
    id_ : str
    content : str(int int)
        Are of form "(8 -1)", we only need the second part
    """
    compounds[id_]["charge"] += float(content[1:-1].split()[-1])


def _set_chemical_formula(compounds, id_, content):
    """Short description.

    Parameters
    ----------
    Compounds : dict
    id_ : str
    content : str(int int)
        Are of form (C 11)
    """
    atom, count = content[1:-1].split(" ")
    compounds[id_]["formula"][atom] = int(count)


def _set_smiles(compounds, id_, content):
    """Short description.

    Parameters
    ----------
    Compounds : dict
    id_ : str
    content : str
    """
    compounds[id_]["smiles"] = content


class CompoundParser:
    """Class to parse compounds."""

    def __init__(self, path):
        """Parser compound information."""
        file, start_idx = _open_file_and_remove_comments(path)
        self.file = file
        self.start_idx = start_idx

        self.actions = {
            "TYPES": _add_type,
            "COMMON-NAME": _set_name,
            "ABBREV-NAME": _do_nothing,
            "ACCESSION-1": _do_nothing,
            "ANTICODON": _do_nothing,
            "ATOM-CHARGES": _set_atom_charges,
            "ATOM-ISOTOPES": _do_nothing,
            "CATALYZES": _do_nothing,
            "CFG-ICON-COLOR": _do_nothing,
            "CHEMICAL-FORMULA": _set_chemical_formula,
            "CITATIONS": _do_nothing,
            "CODING-SEGMENTS": _do_nothing,
            "CODONS": _do_nothing,
            "COFACTORS-OF": _do_nothing,
            "COMMENT": _do_nothing,
            "COMPONENT-COEFFICIENTS": _do_nothing,
            "COMPONENT-OF": _do_nothing,
            "COMPONENTS": _do_nothing,
            "CONSENSUS-SEQUENCE": _do_nothing,
            "COPY-NUMBER": _do_nothing,
            "CREDITS": _do_nothing,
            "DATA-SOURCE": _do_nothing,
            "DBLINKS": _add_database_link,
            "DNA-FOOTPRINT-SIZE": _do_nothing,
            "DOCUMENTATION": _do_nothing,
            "ENZYME-NOT-USED-IN": _do_nothing,
            "EXPRESSION-MECHANISM": _do_nothing,
            "FAST-EQUILIBRATING-INSTANCES?": _do_nothing,
            "FEATURES": _do_nothing,
            "FUNCTIONAL-ASSIGNMENT-COMMENT": _do_nothing,
            "FUNCTIONAL-ASSIGNMENT-STATUS": _do_nothing,
            "GENE": _do_nothing,
            "GIBBS-0": _set_gibbs0,
            "GO-TERMS": _do_nothing,
            "GROUP-COORDS-2D": _do_nothing,
            "GROUP-INTERNALS": _do_nothing,
            "HAS-NO-STRUCTURE?": _do_nothing,
            "HIDE-SLOT?": _do_nothing,
            "IN-MIXTURE": _do_nothing,
            "INCHI": _do_nothing,
            "INCHI-KEY": _do_nothing,
            "INSTANCE-NAME-TEMPLATE": _do_nothing,
            "INTERNALS-OF-GROUP": _do_nothing,
            "ISOZYME-SEQUENCE-SIMILARITY": _do_nothing,
            "LEFT-END-POSITION": _do_nothing,
            "LOCATIONS": _do_nothing,
            "MEMBER-SORT-FN": _do_nothing,
            "MODIFIED-FORM": _do_nothing,
            "MOLECULAR-WEIGHT": _do_nothing,
            "MOLECULAR-WEIGHT-EXP": _do_nothing,
            "MOLECULAR-WEIGHT-KD": _do_nothing,
            "MOLECULAR-WEIGHT-SEQ": _do_nothing,
            "MONOISOTOPIC-MW": _do_nothing,
            "N+1-NAME": _do_nothing,
            "N-1-NAME": _do_nothing,
            "N-NAME": _do_nothing,
            "NEIDHARDT-SPOT-NUMBER": _do_nothing,
            "NON-STANDARD-INCHI": _do_nothing,
            "PATHOLOGIC-NAME-MATCHER-EVIDENCE": _do_nothing,
            "PATHOLOGIC-PWY-EVIDENCE": _do_nothing,
            "PI": _do_nothing,
            "PKA1": _do_nothing,
            "PKA2": _do_nothing,
            "PKA3": _do_nothing,
            "RADICAL-ATOMS": _do_nothing,
            "REGULATED-BY": _do_nothing,
            "REGULATES": _do_nothing,
            "RIGHT-END-POSITION": _do_nothing,
            "SMILES": _set_smiles,
            "SPECIES": _do_nothing,
            "SPLICE-FORM-INTRONS": _do_nothing,
            "STRUCTURE-GROUPS": _do_nothing,
            "STRUCTURE-LINKS": _do_nothing,
            "SUPERATOMS": _do_nothing,
            "SYMMETRY": _do_nothing,
            "SYNONYMS": _do_nothing,
            "SYSTEMATIC-NAME": _do_nothing,
            "TAUTOMERS": _do_nothing,
            "UNMODIFIED-FORM": _do_nothing,
            "LOGP": _do_nothing,
            "POLAR-SURFACE-AREA": _do_nothing,
        }

    @staticmethod
    def gather_compound_types(compounds):
        """Return (type: list(cpds)) dictionary.

        Only uses the highest-level type
        """
        types = defaultdict(list)
        for id_, cpd in compounds.items():
            if bool(cpd["types"]):
                # Only use highest level
                types[cpd["types"][-1] + "_c"].append(id_)
        return dict(types)

    def parse(self):
        """Parse."""
        id_ = ""
        compounds = {}
        for line in self.file:
            if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
                continue
            else:
                identifier, content = line.rstrip().split(" - ", maxsplit=1)
                if identifier == "UNIQUE-ID":
                    base_id = content
                    id_ = content + "_c"
                    compounds[id_] = {
                        "id": id_,
                        "base_id": base_id,
                        "name": None,
                        "charge": 0,
                        "compartment": "CYTOSOL",
                        "gibbs0": None,
                        "types": [],
                        "formula": {},
                        "smiles": None,
                        "database_links": {},
                    }
                else:
                    try:
                        self.actions[identifier](compounds, id_, content)
                    except KeyError:
                        warnings.warn(f"Unknown identifier {identifier} for compound {id_}")
        compound_types = self.gather_compound_types(compounds)
        return compounds, compound_types


###############################################################################
# Reaction functions
###############################################################################
def _set_ec_number(reactions, id_, ec_number):
    reactions[id_]["ec"] = ec_number


def _add_reaction_pathway(reactions, id_, pathway):
    reactions[id_]["pathways"].add(pathway)


def _add_reaction_enzyme(reactions, id_, enzyme):
    reactions[id_]["enzymes"].add(enzyme)


def _set_reaction_direction(reactions, id_, direction):
    reactions[id_]["direction"] = direction
    if direction == "REVERSIBLE":
        reactions[id_]["reversible"] = True
    else:
        reactions[id_]["reversible"] = False


def _add_reaction_location(reactions, id_, location):
    location = location.replace("CCI-", "CCO-")
    if location.startswith("CCO-"):
        reactions[id_]["locations"].append(location)


def _set_substrate(reactions, id_, substrate):
    substrate = _rename(substrate) + "_c"
    reactions[id_]["substrates"][substrate] = -1
    reactions[id_]["substrate_compartments"][substrate] = "CCO-IN"


def _set_product(reactions, id_, product):
    product = _rename(product) + "_c"
    reactions[id_]["products"][product] = 1
    reactions[id_]["product_compartments"][product] = "CCO-IN"


def _set_substrate_coefficient(reactions, id_, coefficient, substrate):
    try:
        reactions[id_]["substrates"][_rename(substrate) + "_c"] = -float(coefficient)
    except ValueError:
        pass


def _set_product_coefficient(reactions, id_, coefficient, product):
    try:
        reactions[id_]["products"][_rename(product) + "_c"] = float(coefficient)
    except ValueError:
        pass


def _set_substrate_compartment(reactions, id_, compartment, substrate):
    if compartment == "CCO-OUT":
        reactions[id_]["substrate_compartments"][_rename(substrate) + "_c"] = compartment
    elif compartment == "CCO-MIDDLE":
        reactions[id_]["substrate_compartments"][_rename(substrate) + "_c"] = "CCO-OUT"


def _set_product_compartment(reactions, id_, compartment, product):
    if compartment == "CCO-OUT":
        reactions[id_]["product_compartments"][_rename(product) + "_c"] = compartment
    elif compartment == "CCO-MIDDLE":
        reactions[id_]["product_compartments"][_rename(product) + "_c"] = "CCO-OUT"


class ReactionParser:
    """Reaction Parser."""

    def __init__(self, path):
        """Parse reactions and pathways."""
        file, start_idx = _open_file_and_remove_comments(path)
        self.file = file
        self.start_idx = start_idx

        self.actions = {
            "TYPES": _add_type,
            "COMMON-NAME": _set_name,
            "ATOM-MAPPINGS": _do_nothing,
            "CANNOT-BALANCE?": _do_nothing,
            "CITATIONS": _do_nothing,
            "COMMENT": _do_nothing,
            "CREDITS": _do_nothing,
            "DATA-SOURCE": _do_nothing,
            "DBLINKS": _add_database_link,
            "DOCUMENTATION": _do_nothing,
            "EC-NUMBER": _set_ec_number,
            "ENZYMATIC-REACTION": _add_reaction_enzyme,
            "ENZYMES-NOT-USED": _do_nothing,
            "EQUILIBRIUM-CONSTANT": _do_nothing,
            "GIBBS-0": _set_gibbs0,
            "HIDE-SLOT?": _do_nothing,
            "IN-PATHWAY": _add_reaction_pathway,
            "INSTANCE-NAME-TEMPLATE": _do_nothing,
            "LEFT": _set_substrate,
            "MEMBER-SORT-FN": _do_nothing,
            "ORPHAN?": _do_nothing,
            "PATHOLOGIC-NAME-MATCHER-EVIDENCE": _do_nothing,
            "PATHOLOGIC-PWY-EVIDENCE": _do_nothing,
            "PHYSIOLOGICALLY-RELEVANT?": _do_nothing,
            "PREDECESSORS": _do_nothing,
            "PRIMARIES": _do_nothing,
            "REACTION-BALANCE-STATUS": _do_nothing,
            "REACTION-DIRECTION": _set_reaction_direction,
            "REACTION-LIST": _do_nothing,
            "REGULATED-BY": _do_nothing,
            "REQUIREMENTS": _do_nothing,
            "RIGHT": _set_product,
            "RXN-LOCATIONS": _add_reaction_location,
            "SIGNAL": _do_nothing,
            "SPECIES": _do_nothing,
            "SPONTANEOUS?": _do_nothing,
            "STD-REDUCTION-POTENTIAL": _do_nothing,
            "SYNONYMS": _do_nothing,
            "SYSTEMATIC-NAME": _do_nothing,
            "TAXONOMIC-RANGE": _do_nothing,
        }

        self.sub_actions = {
            "^COMPARTMENT": {
                "LEFT": _set_substrate_compartment,
                "RIGHT": _set_product_compartment,
            },
            "^OFFICIAL?": {
                "EC-NUMBER": _do_nothing,
            },
            "^COEFFICIENT": {
                "LEFT": _set_substrate_coefficient,
                "RIGHT": _set_product_coefficient,
            },
        }

    def parse(self):
        """Parse."""
        id_ = ""
        reactions = {}
        for line in self.file:
            if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
                continue
            else:
                identifier, content = line.rstrip().split(" - ", maxsplit=1)
                if identifier == "UNIQUE-ID":
                    id_ = content
                    reactions[id_] = {
                        "id": id_,
                        "base_id": id_,
                        "name": None,
                        "ec": None,
                        "substrates": {},
                        "substrate_compartments": {},
                        "products": {},
                        "product_compartments": {},
                        "types": [],
                        "gibbs0": None,
                        "locations": [],
                        "pathways": set(),
                        "enzymes": set(),
                        "direction": "LEFT-TO-RIGHT",
                        "reversible": False,
                        "transmembrane": False,
                        "database_links": {},
                    }
                elif not identifier.startswith("^"):
                    try:
                        self.actions[identifier](reactions, id_, content)
                        last_identifier = identifier
                        last_content = content
                    except KeyError:
                        warnings.warn(f"Unknown identifier {identifier} for reaction {id_}")
                else:
                    self.sub_actions[identifier][last_identifier](reactions, id_, content, last_content)
        return reactions


###############################################################################
# Enzyme functions
###############################################################################


def _set_enzyme(enzrxns, id_, enzyme):
    enzrxns[id_]["enzyme"] = enzyme


def _add_kcat(enzrxns, id_, substrate, kcat):
    enzrxns[id_].setdefault("kcat", {}).setdefault(substrate, kcat)


def _add_km(enzrxns, id_, substrate, km):
    enzrxns[id_].setdefault("km", {}).setdefault(substrate, km)


def _add_vmax(enzrxns, id_, substrate, vmax):
    enzrxns[id_].setdefault("vmax", {}).setdefault(substrate, vmax)


class EnzymeParser:
    """Enzyme Parser."""

    def __init__(self, path):
        file, start_idx = _open_file_and_remove_comments(path)
        self.file = file
        self.start_idx = start_idx
        self.actions = {
            "UNIQUE-ID": _do_nothing,
            "TYPES": _do_nothing,
            "COMMON-NAME": _do_nothing,
            "ALTERNATIVE-COFACTORS": _do_nothing,
            "ALTERNATIVE-SUBSTRATES": _do_nothing,
            "BASIS-FOR-ASSIGNMENT": _do_nothing,
            "CITATIONS": _do_nothing,
            "COFACTOR-BINDING-COMMENT": _do_nothing,
            "COFACTORS": _do_nothing,
            "COMMENT": _do_nothing,
            "CREDITS": _do_nothing,
            "DATA-SOURCE": _do_nothing,
            "DBLINKS": _do_nothing,
            "DOCUMENTATION": _do_nothing,
            "ENZRXN-IN-PATHWAY": _do_nothing,
            "ENZYME": _set_enzyme,
            "HIDE-SLOT?": _do_nothing,
            "INSTANCE-NAME-TEMPLATE": _do_nothing,
            "KCAT": _do_nothing,
            "KM": _do_nothing,
            "MEMBER-SORT-FN": _do_nothing,
            "PATHOLOGIC-NAME-MATCHER-EVIDENCE": _do_nothing,
            "PATHOLOGIC-PWY-EVIDENCE": _do_nothing,
            "PH-OPT": _do_nothing,
            "PHYSIOLOGICALLY-RELEVANT?": _do_nothing,
            "REACTION": _do_nothing,
            "REACTION-DIRECTION": _do_nothing,
            "REGULATED-BY": _do_nothing,
            "REQUIRED-PROTEIN-COMPLEX": _do_nothing,
            "SPECIFIC-ACTIVITY": _do_nothing,
            "SYNONYMS": _do_nothing,
            "TEMPERATURE-OPT": _do_nothing,
            "VMAX": _do_nothing,
            "ENZRXN-EC-NUMBER": _do_nothing,
        }
        self.sub_actions = {
            "^SUBSTRATE": {"KM": _add_km, "VMAX": _add_vmax, "KCAT": _add_kcat},
            "^CITATIONS": {
                "KM": _do_nothing,
                "VMAX": _do_nothing,
                "KCAT": _do_nothing,
            },
        }

    def parse(self):
        """Parse."""
        id_ = ""
        enzrxns = {}
        for line in self.file:
            if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
                continue
            else:
                identifier, content = line.rstrip().split(" - ", maxsplit=1)
                if identifier == "UNIQUE-ID":
                    id_ = content
                    enzrxns[id_] = {}
                elif not identifier.startswith("^"):
                    try:
                        self.actions[identifier](enzrxns, id_, content)
                        last_identifier = identifier
                        last_content = content
                    except KeyError:
                        warnings.warn(f"Unknown identifier {identifier} for enzyme {id_}")
                else:
                    self.sub_actions[identifier][last_identifier](enzrxns, id_, content, last_content)
        return enzrxns


###############################################################################
# Protein functions
###############################################################################


def _add_component(complexes, complex_id, component):
    complexes[complex_id].add(component)


class ProteinParser:
    """Protein parser."""

    def __init__(self, path):
        file, start_idx = _open_file_and_remove_comments(path)
        self.file = file
        self.start_idx = start_idx
        self.actions = {
            # "UNIQUE-ID": _do_nothing,
            "TYPES": _do_nothing,
            "COMMON-NAME": _do_nothing,
            "ABBREV-NAME": _do_nothing,
            "ACCESSION-1": _do_nothing,
            "AROMATIC-RINGS": _do_nothing,
            "ATOM-CHARGES": _do_nothing,
            "ATOM-ISOTOPES": _do_nothing,
            "CATALYZES": _do_nothing,
            "CHEMICAL-FORMULA": _do_nothing,
            "CITATIONS": _do_nothing,
            "CODING-SEGMENTS": _do_nothing,
            "COFACTORS-OF": _do_nothing,
            "COMMENT": _do_nothing,
            "COMPONENT-COEFFICIENTS": _do_nothing,
            "COMPONENT-OF": _do_nothing,
            "COMPONENTS": _add_component,
            "CONSENSUS-SEQUENCE": _do_nothing,
            "COPY-NUMBER": _do_nothing,
            "CREDITS": _do_nothing,
            "DATA-SOURCE": _do_nothing,
            "DBLINKS": _do_nothing,
            "DNA-FOOTPRINT-SIZE": _do_nothing,
            "DOCUMENTATION": _do_nothing,
            "ENZYME-NOT-USED-IN": _do_nothing,
            "EXPRESSION-MECHANISM": _do_nothing,
            "FAST-EQUILIBRATING-INSTANCES?": _do_nothing,
            "FEATURES": _do_nothing,
            "FUNCTIONAL-ASSIGNMENT-COMMENT": _do_nothing,
            "FUNCTIONAL-ASSIGNMENT-STATUS": _do_nothing,
            "GENE": _do_nothing,
            "GIBBS-0": _do_nothing,
            "GO-TERMS": _do_nothing,
            "GROUP-COORDS-2D": _do_nothing,
            "HAS-NO-STRUCTURE?": _do_nothing,
            "HIDE-SLOT?": _do_nothing,
            "IN-MIXTURE": _do_nothing,
            "INCHI": _do_nothing,
            "INCHI-KEY": _do_nothing,
            "INSTANCE-NAME-TEMPLATE": _do_nothing,
            "INTERNALS-OF-GROUP": _do_nothing,
            "ISOZYME-SEQUENCE-SIMILARITY": _do_nothing,
            "LOCATIONS": _do_nothing,
            "MEMBER-SORT-FN": _do_nothing,
            "MODIFIED-FORM": _do_nothing,
            "MOLECULAR-WEIGHT": _do_nothing,
            "MOLECULAR-WEIGHT-EXP": _do_nothing,
            "MOLECULAR-WEIGHT-KD": _do_nothing,
            "MOLECULAR-WEIGHT-SEQ": _do_nothing,
            "MONOISOTOPIC-MW": _do_nothing,
            "N+1-NAME": _do_nothing,
            "N-1-NAME": _do_nothing,
            "N-NAME": _do_nothing,
            "NEIDHARDT-SPOT-NUMBER": _do_nothing,
            "NON-STANDARD-INCHI": _do_nothing,
            "PATHOLOGIC-NAME-MATCHER-EVIDENCE": _do_nothing,
            "PATHOLOGIC-PWY-EVIDENCE": _do_nothing,
            "PI": _do_nothing,
            "PKA1": _do_nothing,
            "PKA2": _do_nothing,
            "PKA3": _do_nothing,
            "PROMOTER-BOX-NAME-1": _do_nothing,
            "PROMOTER-BOX-NAME-2": _do_nothing,
            "RADICAL-ATOMS": _do_nothing,
            "RECOGNIZED-PROMOTERS": _do_nothing,
            "REGULATED-BY": _do_nothing,
            "REGULATES": _do_nothing,
            "SMILES": _do_nothing,
            "SPECIES": _do_nothing,
            "SPLICE-FORM-INTRONS": _do_nothing,
            "STRUCTURE-BONDS": _do_nothing,
            "STRUCTURE-GROUPS": _do_nothing,
            "STRUCTURE-LINKS": _do_nothing,
            "SUPERATOMS": _do_nothing,
            "SYMMETRY": _do_nothing,
            "SYNONYMS": _do_nothing,
            "SYSTEMATIC-NAME": _do_nothing,
            "TAUTOMERS": _do_nothing,
            "UNMODIFIED-FORM": _do_nothing,
        }

    def parse(self):
        """Parse."""
        id_ = ""
        proteins = {}
        for i, line in enumerate(self.file, self.start_idx):
            if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
                continue
            else:
                try:
                    identifier, content = line.rstrip().split(" - ", maxsplit=1)
                    if identifier == "UNIQUE-ID":
                        id_ = content
                        proteins[id_] = set()
                    elif not identifier.startswith("^"):
                        try:
                            self.actions[identifier](proteins, id_, content)
                        except KeyError:
                            warnings.warn(f"Unknown identifier {identifier} for protein {id_}")
                except ValueError:
                    warnings.warn(f"Malformed line {i} in proteins.dat")
        monomers = set()
        complexes = dict()
        for k, v in proteins.items():
            if bool(v):
                complexes[k] = v
            else:
                monomers.add(k)

        return monomers, complexes


###############################################################################
# Sequence functions
###############################################################################


class SequenceParser:
    """SequenceParser."""

    def __init__(self, path):
        with open(path, encoding="ISO-8859-14") as f:
            self.file = f.readlines()

    def parse(self):
        """Parse."""
        RE_PAT = re.compile(r"^>gnl\|.*?\|")
        sequences = {}
        for id_, sequence in zip(self.file[::2], self.file[1::2]):
            id_ = re.sub(RE_PAT, "", id_).split(" ", maxsplit=1)[0]
            sequences[id_] = sequence.strip()
        return sequences


###############################################################################
# Repairer
###############################################################################


class Repairer:
    """Modifies the pgdb databases in such a way that they can be used for metabolic modelling purposes."""

    def __init__(self, compounds, compound_types, reactions, compartment_map):
        self.compartment_map = compartment_map
        self.compounds = compounds
        self.compound_types = compound_types
        self.compound_type_set = set(compound_types)
        self.reactions = reactions
        self.manual_additions = {
            "Acceptor_c": {
                "base_id": "Acceptor",
                "id": "Acceptor_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Donor-H2_c": {
                "base_id": "Donor-H2",
                "id": "Donor-H2_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1, "H": 2},
            },
            "Oxidized-ferredoxins_c": {
                "base_id": "Oxidized-ferredoxins",
                "id": "Oxidized-ferredoxins_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "Reduced-ferredoxins_c": {
                "base_id": "Reduced-ferredoxins",
                "id": "Reduced-ferredoxins_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Red-NADPH-Hemoprotein-Reductases_c": {
                "base_id": "Red-NADPH-Hemoprotein-Reductases",
                "id": "Red-NADPH-Hemoprotein-Reductases_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1, "H": 2},
            },
            "Ox-NADPH-Hemoprotein-Reductases_c": {
                "base_id": "Ox-NADPH-Hemoprotein-Reductases",
                "id": "Ox-NADPH-Hemoprotein-Reductases_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Cytochromes-C-Oxidized_c": {
                "base_id": "Cytochromes-C-Oxidized",
                "id": "Cytochromes-C-Oxidized_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "Cytochromes-C-Reduced_c": {
                "base_id": "Cytochromes-C-Reduced",
                "id": "Cytochromes-C-Reduced_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Oxidized-Plastocyanins_c": {
                "base_id": "Oxidized-Plastocyanins",
                "id": "Oxidized-Plastocyanins_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "Plastocyanin-Reduced_c": {
                "base_id": "Plastocyanin-Reduced",
                "id": "Plastocyanin-Reduced_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "ETF-Oxidized_c": {
                "base_id": "ETF-Oxidized",
                "id": "ETF-Oxidized_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "ETF-Reduced_c": {
                "base_id": "ETF-Reduced",
                "id": "ETF-Reduced_c",
                "compartment": "CYTOSOL",
                "charge": 2,
                "formula": {"Unknown": 1, "H": 3},
            },
            "Ox-Glutaredoxins_c": {
                "base_id": "Ox-Glutaredoxins",
                "id": "Ox-Glutaredoxins_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "Red-Glutaredoxins_c": {
                "base_id": "Red-Glutaredoxins",
                "id": "Red-Glutaredoxins_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Ox-Thioredoxin_c": {
                "base_id": "Ox-Thioredoxin",
                "id": "Ox-Thioredoxin_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Red-Thioredoxin_c": {
                "base_id": "Red-Thioredoxin",
                "id": "Red-Thioredoxin_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1, "H": 2},
            },
            "Ox-FMN-Flavoproteins_c": {
                "base_id": "Ox-FMN-Flavoproteins",
                "id": "Ox-FMN-Flavoproteins_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "Red-FMNH2-Flavoproteins_c": {
                "base_id": "Red-FMNH2-Flavoproteins",
                "id": "Red-FMNH2-Flavoproteins_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1, "H": 2},
            },
            "Ox-FAD-Flavoproteins_c": {
                "base_id": "Ox-FAD-Flavoproteins",
                "id": "Ox-FAD-Flavoproteins_c",
                "compartment": "CYTOSOL",
                "charge": 1,
                "formula": {"Unknown": 1},
            },
            "Red-FADH2-Flavoproteins_c": {
                "base_id": "Red-FADH2-Flavoproteins",
                "id": "Red-FADH2-Flavoproteins_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1, "H": 2},
            },
            "Light_c": {
                "base_id": "Light",
                "id": "Light_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 0},
            },
            "Oxidized-flavodoxins_c": {
                "base_id": "Oxidized-flavodoxins",
                "id": "Oxidized-flavodoxins_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1},
            },
            "Reduced-flavodoxins_c": {
                "base_id": "Reduced-flavodoxins",
                "id": "Reduced-flavodoxins_c",
                "compartment": "CYTOSOL",
                "charge": 0,
                "formula": {"Unknown": 1, "H": 2},
            },
        }

    @staticmethod
    def reverse_stoichiometry(reaction):
        """Reverse the stoichiometry of a reaction.

        This also reverses the compartments and the gibbs0.
        """
        substrates = reaction["substrates"].copy()
        products = reaction["products"].copy()
        reaction["substrates"] = {k: -v for k, v in products.items()}
        reaction["products"] = {k: -v for k, v in substrates.items()}
        if reaction["gibbs0"] is not None:
            reaction["gibbs0"] = -reaction["gibbs0"]
        reaction["substrate_compartments"], reaction["product_compartments"] = (
            reaction["product_compartments"],
            reaction["substrate_compartments"],
        )

    def unify_reaction_direction(self, reaction):
        """Set every reaction to be LEFT-TO-RIGHT and add bounds accordingly."""
        if reaction["reversible"]:
            del reaction["direction"]
            reaction["bounds"] = (-1000, 1000)
        else:
            direction = reaction["direction"]
            if direction in (
                "LEFT-TO-RIGHT",
                "PHYSIOL-LEFT-TO-RIGHT",
                "IRREVERSIBLE-LEFT-TO-RIGHT",
            ):
                del reaction["direction"]
                reaction["bounds"] = (0, 1000)
            elif direction in (
                "RIGHT-TO-LEFT",
                "PHYSIOL-RIGHT-TO-LEFT",
                "IRREVERSIBLE-RIGHT-TO-LEFT",
            ):
                del reaction["direction"]
                self.reverse_stoichiometry(reaction)
                reaction["bounds"] = (0, 1000)
            else:
                warnings.warn(
                    f"Weird reaction direction '{direction}' for reaction {reaction['id']}, setting to LEFT-TO-RIGHT"
                )
                del reaction["direction"]
                reaction["bounds"] = (0, 1000)

    def check_compound_existence(self, rxn):
        """Check if all compounds of a reaction exist."""
        for compound in it.chain(rxn["substrates"], rxn["products"]):
            if compound not in self.compounds:
                return False
        return True

    def check_mass_balance(self, rxn):
        """Check if the reaction is mass-balanced."""
        lhs, rhs = rxn["substrates"], rxn["products"]

        lhs_atoms = defaultdict(lambda: 0)
        rhs_atoms = defaultdict(lambda: 0)

        for cpd, stoich in lhs.items():
            formula = self.compounds[cpd]["formula"]
            # Check if compound has a formula in the first place
            if not bool(formula):
                return False
            for atom, count in formula.items():
                lhs_atoms[atom] -= count * stoich

        for cpd, stoich in rhs.items():
            # Check if compound has a formula in the first place
            formula = self.compounds[cpd]["formula"]
            if not bool(formula):
                return False
            for atom, count in formula.items():
                rhs_atoms[atom] += count * stoich

        for k in set((*lhs_atoms, *rhs_atoms)):
            diff = lhs_atoms[k] - rhs_atoms[k]
            if diff != 0:
                return False
        return True

    def check_charge_balance(self, rxn):
        """Check if the reaction is charge-balanced."""
        lhs_charge, rhs_charge = 0, 0
        for cpd, stoich in rxn["substrates"].items():
            try:
                lhs_charge -= stoich * self.compounds[cpd]["charge"]
            except TypeError:
                return False
        for cpd, stoich in rxn["products"].items():
            try:
                rhs_charge += stoich * self.compounds[cpd]["charge"]
            except TypeError:
                return False
        if lhs_charge - rhs_charge == 0:
            return True
        return False

    def create_reaction_variants(
        self,
        rxn_id,
        rxn,
    ):
        """Create all mass and charge balanced reaction variants of reactions containing compound classes."""
        count = 0
        substrate_variants = {
            cpd: self.compound_types[cpd] for cpd in rxn["substrates"] if cpd in self.compound_type_set
        }
        product_variants = {
            cpd: self.compound_types[cpd] for cpd in rxn["products"] if cpd in self.compound_type_set
        }
        if len(substrate_variants) + len(product_variants) > 0:
            variants = {**substrate_variants, **product_variants}
            # Remove base reaction
            rxn = self.reactions.pop(rxn_id)
            for new_cpds, old_cpds in zip(
                it.product(*variants.values()),
                it.repeat(variants.keys()),
            ):
                # Copy reaction
                local_rxn = deepcopy(rxn)
                new_cpds = dict(zip(old_cpds, new_cpds))
                for old_sub in substrate_variants:
                    new_sub = new_cpds[old_sub]
                    local_rxn["substrates"][new_sub] = local_rxn["substrates"].pop(old_sub)
                    local_rxn["substrate_compartments"][new_sub] = local_rxn["substrate_compartments"].pop(
                        old_sub
                    )
                for old_prod in product_variants:
                    new_prod = new_cpds[old_prod]
                    local_rxn["products"][new_prod] = local_rxn["products"].pop(old_prod)
                    local_rxn["product_compartments"][new_prod] = local_rxn["product_compartments"].pop(
                        old_prod
                    )
                # Filter garbage reactions
                if not self.check_compound_existence(local_rxn):
                    continue
                if not self.check_mass_balance(local_rxn):
                    continue
                if not self.check_charge_balance(local_rxn):
                    continue
                local_rxn["id"] = f"{local_rxn['id']}__var__{count}"
                self.reactions[local_rxn["id"]] = local_rxn
                count += 1
            return True
        return False

    def split_location_string(self, location_string):
        """Split concatented rxn-location strings.

        Example input:

        CCO-EXTRACELLULAR-CCO-CYTOSOL
        CCO-PM-BAC-NEG
        In some cases only one is given, even if a transporter is
        described. In that case, the in-compartment is always the cytosol
        """
        split = re.split(r"(\-?CCO\-)", location_string)
        try:
            out_, in_ = split[2::2]
        except ValueError:
            out_ = split[2]
            in_ = "CYTOSOL"
        out_ = map_compartment_to_model_compartments(compartment=out_, compartment_map=self.compartment_map)
        in_ = map_compartment_to_model_compartments(compartment=in_, compartment_map=self.compartment_map)
        return dict(zip(("CCO-OUT", "CCO-IN"), (out_, in_)))

    def add_compartment_compound_variant(self, cpd_id, compartment):
        """Add a copy of the compound and change the suffix."""
        base_id = self.compounds[cpd_id]["base_id"]
        new_id = add_moped_compartment_suffix(
            object_id=base_id,
            compartment=compartment,
        )
        new_cpd = deepcopy(self.compounds[cpd_id])
        new_cpd["id"] = new_id
        new_cpd["compartment"] = compartment
        self.compounds[new_id] = new_cpd
        return new_id

    def _create_compartment_reaction(self, local_rxn, compartment):
        for substrate, side in local_rxn["substrate_compartments"].items():
            new_cpd = self.add_compartment_compound_variant(substrate, compartment)
            local_rxn["substrates"][new_cpd] = local_rxn["substrates"].pop(substrate)
        del local_rxn["substrate_compartments"]
        for product, side in local_rxn["product_compartments"].items():
            new_cpd = self.add_compartment_compound_variant(product, compartment)
            local_rxn["products"][new_cpd] = local_rxn["products"].pop(product)
        del local_rxn["product_compartments"]
        # Add suffix to reaction name
        suffix = add_moped_compartment_suffix(object_id="", compartment=compartment)
        local_rxn["id"] += suffix
        local_rxn["compartment"] = compartment
        self.reactions[local_rxn["id"]] = local_rxn

    def _create_transmembrane_reaction(self, local_rxn, sides):
        for substrate, side in local_rxn["substrate_compartments"].items():
            new_cpd = self.add_compartment_compound_variant(substrate, sides[side])
            local_rxn["substrates"][new_cpd] = local_rxn["substrates"].pop(substrate)
        del local_rxn["substrate_compartments"]
        for product, side in local_rxn["product_compartments"].items():
            new_cpd = self.add_compartment_compound_variant(product, sides[side])
            local_rxn["products"][new_cpd] = local_rxn["products"].pop(product)
        del local_rxn["product_compartments"]
        # Add suffix to reaction name
        in_suffix = add_moped_compartment_suffix(
            object_id="",
            compartment=sides["CCO-IN"],
        )
        out_suffix = add_moped_compartment_suffix(
            object_id="",
            compartment=sides["CCO-OUT"],
        )
        # Add suffix to reaction name
        local_rxn["id"] += in_suffix
        local_rxn["id"] += out_suffix
        local_rxn["compartment"] = (sides["CCO-IN"], sides["CCO-OUT"])
        local_rxn["transmembrane"] = True
        self.reactions[local_rxn["id"]] = local_rxn

    def fix_reaction_compartments(self, rxn_id):
        """Fix issues with consistency of pgdbs when it comes to compartments.

        This maps the location information according to the compartment_map that
        was supplied. By default only CYTOSOL, PERIPLASM and EXTRACELLULAR are used.

        If no location is given, CCO-CYTOSOL is assumed for CCO-IN and CCO-EXTRACELLULAR
        for CCO-OUT. Accordingly transport reactions with no location are assumed to be
        CCO-EXTRACELLULAR-CCO-CYTOSOL.

        Notes
        -----
        CCO-EXTRACELLULAR-CCO-CYTOSOL means CCO-OUT means EXTRACELLULAR and CCO-IN means
        CYTOSOL, so the format is CCO-OUT-CCO-IN. No idea why.
        """
        # Remove base reaction
        rxn = self.reactions.pop(rxn_id)
        if all(
            i == "CCO-IN"
            for i in it.chain(
                rxn["substrate_compartments"].values(),
                rxn["product_compartments"].values(),
            )
        ):
            if not bool(rxn["locations"]):
                rxn["locations"] = ["CCO-CYTOSOL"]
            for location in rxn["locations"]:
                if "-CCO-" in location:
                    sides = self.split_location_string(location)
                else:
                    sides = {
                        "CCO-IN": map_compartment_to_model_compartments(
                            compartment=location[4:],
                            compartment_map=self.compartment_map,
                        )
                    }
                local_rxn = deepcopy(rxn)
                del local_rxn["locations"]
                self._create_compartment_reaction(local_rxn, sides["CCO-IN"])
        elif all(
            i == "CCO-OUT"
            for i in it.chain(
                rxn["substrate_compartments"].values(),
                rxn["product_compartments"].values(),
            )
        ):
            if not bool(rxn["locations"]):
                rxn["locations"] = ["CCO-EXTRACELLULAR"]
            for location in rxn["locations"]:
                if "-CCO-" in location:
                    sides = self.split_location_string(location)
                else:
                    sides = {
                        "CCO-OUT": map_compartment_to_model_compartments(
                            compartment=location[4:],
                            compartment_map=self.compartment_map,
                        )
                    }
                local_rxn = deepcopy(rxn)
                del local_rxn["locations"]
                self._create_compartment_reaction(local_rxn, sides["CCO-OUT"])
        else:
            if not bool(rxn["locations"]):
                rxn["locations"] = ["CCO-EXTRACELLULAR-CCO-CYTOSOL"]
            for location in rxn["locations"]:
                local_rxn = deepcopy(rxn)
                del local_rxn["locations"]
                sides = self.split_location_string(location)
                if sides["CCO-IN"] == sides["CCO-OUT"]:
                    self._create_compartment_reaction(local_rxn, sides["CCO-OUT"])
                else:
                    self._create_transmembrane_reaction(local_rxn, sides)

    @staticmethod
    def set_reaction_stoichiometry(reaction):
        """Set the stoichiometry from the information given by the substrates and products."""
        substrates = reaction["substrates"]
        products = reaction["products"]

        # Check for duplicates
        for compound in set(substrates).intersection(set(products)):
            diff = products[compound] - abs(substrates[compound])
            if diff == 0:
                del substrates[compound]
                del products[compound]
            elif diff < 0:
                substrates[compound] = diff
                del products[compound]
            else:
                del substrates[compound]
                products[compound] = diff

        # Create stoichiometry
        stoichiometries = {**substrates, **products}
        if len(stoichiometries) <= 1:
            return False
        reaction["stoichiometries"] = stoichiometries
        del reaction["substrates"]
        del reaction["products"]
        return True

    def repair(self, verbose=False):
        """Repair the database.

        Steps:
        - Unify reaction direction
        - Create reaction variants for compound classes
        - Remove everything that is not charge-balanced or mass-balanced
        - Fix compartmentalized reactions
        """
        # Manually add important compounds to the model
        self.compounds.update(self.manual_additions)

        # First loop to create reaction variants and filter garbage
        for rxn_id, rxn in tuple(self.reactions.items()):
            self.unify_reaction_direction(rxn)
            if self.create_reaction_variants(rxn_id, rxn):
                continue
            else:
                if not self.check_compound_existence(rxn):
                    del self.reactions[rxn_id]
                    continue
                if not self.check_mass_balance(rxn):
                    del self.reactions[rxn_id]
                    continue
                if not self.check_charge_balance(rxn):
                    del self.reactions[rxn_id]
                    continue

        # New loop, as reaction variants have been created
        for rxn_id in tuple(self.reactions.keys()):
            self.fix_reaction_compartments(rxn_id)

        # New loop, as compartment variants have been created
        for rxn_id, rxn in tuple(self.reactions.items()):
            if not self.set_reaction_stoichiometry(rxn):
                del self.reactions[rxn_id]

        # Return proper objects
        compounds = [Compound(**v) for v in self.compounds.values()]
        reactions = [Reaction(**v) for v in self.reactions.values()]
        used_compartments = {i.compartment for i in compounds}
        compartments = {i: COMPARTMENT_SUFFIXES[i] for i in used_compartments}
        return compounds, reactions, compartments
