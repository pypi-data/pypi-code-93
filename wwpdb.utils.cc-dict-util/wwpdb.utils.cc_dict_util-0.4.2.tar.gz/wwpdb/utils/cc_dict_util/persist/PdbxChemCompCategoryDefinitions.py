##
# File: PdbxChemCompCategoryDefintions.py
# Date: 21-Feb-2012  John Westbrook
#
# Updates:
#
##
"""
A definitions of data categories used in the chemical component dictionary.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


class PdbxChemCompCategoryDefinitions(object):
    _categoryInfo = [
        ("chem_comp", "key-value"),
        ("chem_comp_atom", "table"),
        ("chem_comp_bond", "table"),
        ("chem_comp_identifier", "table"),
        ("chem_comp_descriptor", "table"),
        ("pdbx_chem_comp_audit", "table"),
        ("pdbx_chem_comp_import", "table"),
        ("pdbx_chem_comp_atom_edit", "table"),
        ("pdbx_chem_comp_bond_edit", "table"),
    ]
    _cDict = {
        "chem_comp": [
            ("_chem_comp.id", "%s", "str", ""),
            ("_chem_comp.name", "%s", "str", ""),
            ("_chem_comp.type", "%s", "str", ""),
            ("_chem_comp.pdbx_type", "%s", "str", ""),
            ("_chem_comp.formula", "%s", "str", ""),
            ("_chem_comp.mon_nstd_parent_comp_id", "%s", "str", ""),
            ("_chem_comp.pdbx_synonyms", "%s", "str", ""),
            ("_chem_comp.pdbx_formal_charge", "%s", "str", ""),
            ("_chem_comp.pdbx_initial_date", "%s", "str", ""),
            ("_chem_comp.pdbx_modified_date", "%s", "str", ""),
            ("_chem_comp.pdbx_ambiguous_flag", "%s", "str", ""),
            ("_chem_comp.pdbx_release_status", "%s", "str", ""),
            ("_chem_comp.pdbx_replaced_by", "%s", "str", ""),
            ("_chem_comp.pdbx_replaces", "%s", "str", ""),
            ("_chem_comp.formula_weight", "%s", "str", ""),
            ("_chem_comp.one_letter_code", "%s", "str", ""),
            ("_chem_comp.three_letter_code", "%s", "str", ""),
            ("_chem_comp.pdbx_model_coordinates_details", "%s", "str", ""),
            ("_chem_comp.pdbx_model_coordinates_missing_flag", "%s", "str", ""),
            ("_chem_comp.pdbx_ideal_coordinates_details", "%s", "str", ""),
            ("_chem_comp.pdbx_ideal_coordinates_missing_flag", "%s", "str", ""),
            ("_chem_comp.pdbx_model_coordinates_db_code", "%s", "str", ""),
            ("_chem_comp.pdbx_subcomponent_list", "%s", "str", ""),
            ("_chem_comp.pdbx_processing_site", "%s", "str", ""),
        ],
        "chem_comp_atom": [
            ("_chem_comp_atom.comp_id", "%s", "str", ""),
            ("_chem_comp_atom.atom_id", "%s", "str", ""),
            ("_chem_comp_atom.alt_atom_id", "%s", "str", ""),
            ("_chem_comp_atom.type_symbol", "%s", "str", ""),
            ("_chem_comp_atom.charge", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_align", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_aromatic_flag", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_leaving_atom_flag", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_stereo_config", "%s", "str", ""),
            ("_chem_comp_atom.model_Cartn_x", "%s", "str", ""),
            ("_chem_comp_atom.model_Cartn_y", "%s", "str", ""),
            ("_chem_comp_atom.model_Cartn_z", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_model_Cartn_x_ideal", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_model_Cartn_y_ideal", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_model_Cartn_z_ideal", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_component_atom_id", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_component_comp_id", "%s", "str", ""),
            ("_chem_comp_atom.pdbx_ordinal", "%s", "str", ""),
        ],
        "chem_comp_bond": [
            ("_chem_comp_bond.comp_id", "%s", "str", ""),
            ("_chem_comp_bond.atom_id_1", "%s", "str", ""),
            ("_chem_comp_bond.atom_id_2", "%s", "str", ""),
            ("_chem_comp_bond.value_order", "%s", "str", ""),
            ("_chem_comp_bond.pdbx_aromatic_flag", "%s", "str", ""),
            ("_chem_comp_bond.pdbx_stereo_config", "%s", "str", ""),
            ("_chem_comp_bond.pdbx_ordinal", "%s", "str", ""),
        ],
        "chem_comp_descriptor": [
            ("_pdbx_chem_comp_descriptor.comp_id", "%s", "str", ""),
            ("_pdbx_chem_comp_descriptor.type", "%s", "str", ""),
            ("_pdbx_chem_comp_descriptor.program", "%s", "str", ""),
            ("_pdbx_chem_comp_descriptor.program_version", "%s", "str", ""),
            ("_pdbx_chem_comp_descriptor.descriptor", "%s", "str", ""),
        ],
        "chem_comp_identifier": [
            ("_pdbx_chem_comp_identifier.comp_id", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.type", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.program", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.program_version", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.identifier", "%s", "str", ""),
        ],
        "pdbx_chem_comp_import": [
            ("_pdbx_chem_comp_identifier.comp_id", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.comp_alias_id", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.model_path", "%s", "str", ""),
        ],
        "pdbx_chem_comp_audit": [
            ("_pdbx_chem_comp_identifier.comp_id", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.action_type", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.date", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.processing_site", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.annotator", "%s", "str", ""),
            ("_pdbx_chem_comp_identifier.details", "%s", "str", ""),
        ],
        "pdbx_chem_comp_atom_edit": [
            ("_pdbx_chem_comp_atom_edit.ordinal", "%d", "int", ""),
            ("_pdbx_chem_comp_atom_edit.comp_id", "%s", "str", ""),
            ("_pdbx_chem_comp_atom_edit.atom_id", "%s", "str", ""),
            ("_pdbx_chem_comp_atom_edit.edit_op", "%s", "str", ""),
            ("_pdbx_chem_comp_atom_edit.edit_atom_id", "%s", "str", ""),
            ("_pdbx_chem_comp_atom_edit.edit_atom_value", "%s", "str", ""),
        ],
        "pdbx_chem_comp_bond_edit": [
            ("_pdbx_chem_comp_bond_edit.ordinal", "%d", "int", ""),
            ("_pdbx_chem_comp_bond_edit.comp_id_1", "%s", "str", ""),
            ("_pdbx_chem_comp_bond_edit.atom_id_1", "%s", "str", ""),
            ("_pdbx_chem_comp_bond_edit.comp_id_2", "%s", "str", ""),
            ("_pdbx_chem_comp_bond_edit.atom_id_2", "%s", "str", ""),
            ("_pdbx_chem_comp_bond_edit.edit_op", "%s", "str", ""),
            ("_pdbx_chem_comp_bond_edit.edit_bond_value", "%s", "str", ""),
        ],
    }
