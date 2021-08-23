"""The main model class, with which users are supposed to interface."""

import copy
import pathlib
import re
import warnings
from collections import defaultdict

import cobra
import numpy as np
import pandas as pd

from .. import topological
from ..databases import Cyc
from ..utils import get_temporary_directory
from .compound import Compound
from .constants import BIOMASS_TEMPLATES
from .reaction import Reaction

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import modelbase.ode as ode
    from modelbase.ode import ratelaws as rl

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
    "PM-FUNGI": "PERIPLASM",
    "RGH-ER-MEM": "PERIPLASM",
    "THY-LUM-CYA": "CYTOSOL",
    "VAC-LUM": "CYTOSOL",
    "VAC-MEM": "PERIPLASM",
    "VESICLE": "PERIPLASM",
    "OUT": "PERIPLASM",
    "THY-MEM-CYA": "PERIPLASM",
}


class Model:
    """The main model class."""

    def __init__(
        self,
        compounds=None,
        reactions=None,
        compartments=None,
        objective=None,
        name=None,
    ):
        """Initialize a model object.

        Parameters
        ----------
        compounds: iterable, optional
            Iterable of moped.Compound objects
        reactions: iterable, optional
            Iterable of moped.Reaction objects
        compartments: dict, optional
            compartment_id: suffix mapping
        objective: dict(str: float), optional
            Mapping of reaction ids to objective coefficient
        name: str, optional
        """
        self.name = name if name is not None else "Model"
        self.compartments = {}
        self.compounds = {}
        self.base_compounds = {}
        self._compound_types = {}
        self.reactions = {}
        self._reaction_types = {}
        self.base_reactions = {}
        self.variant_reactions = {}
        self._duplicate_reactions = set()
        self.pathways = {}
        self.objective = {}
        self._monomers = {}
        if compartments is not None:
            self.add_compartments(compartments=compartments)
        if compounds is not None:
            self.add_compounds(compounds=compounds)
        if reactions is not None:
            self.add_reactions(reactions=reactions)
        if objective is not None:
            self.set_objective(objective=objective)
        self.cofactor_pairs = {}
        self.minimal_seed = set()

    def __repr__(self):
        """Return model representation."""
        s = f"Model: {self.name}\n"
        s += f"    compounds: {len(self.compounds)}\n"
        s += f"    reactions: {len(self.reactions)}\n"
        return s

    def __str__(self):
        """Return model string representation."""
        s = f"Model: {self.name}\n"
        s += f"    compounds: {len(self.compounds)}\n"
        s += f"    reactions: {len(self.reactions)}\n"
        return s

    def __enter__(self):
        """Return and save a copy for context manager."""
        self._copy = self.copy()
        return self.copy()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Restore any changes made to the model."""
        self.__dict__ = self._copy.__dict__

    def copy(self):
        """Create a deepcopy of the reaction.

        While this is more costly than shallow copies, it takes away
        the hassle of always keeping track if a shallow copy is what
        you want at the moment. So it's mostly for me not getting
        confused ;)

        Returns
        -------
        self: moped.Model
        """
        return copy.deepcopy(self)

    def add_compartment(self, compartment_id, compartment_suffix):
        """Add a compartment to the model.

        compartment_id: str
            Name of the compartment, e.g. cytosol
        compartment_suffix: str
            Suffix of the compartment, e.g. c. Should not include the underscore.

        Examples
        --------
        model.add_compartment(compartment_id='cytosol', compartment_suffix='c')
        """
        self.compartments[compartment_id] = compartment_suffix

    def add_compartments(self, compartments):
        """Add multiple compartments to the model.

        compartments: dict(str: str)
            compartment_id: compartment_suffix

        Examples
        --------
        model.add_compartments(compartments={'cytosol': 'c'})
        """
        for compartment_id, compartment_suffix in compartments.items():
            self.add_compartment(compartment_id=compartment_id, compartment_suffix=compartment_suffix)

    ##########################################################################
    # Utils
    ##########################################################################

    def _add_compartment_suffix(self, object_id, compartment_id):
        """Add a compartment suffix (e.g. _e for extracellular) to the id.

        Raises
        ------
        KeyError
            If compartment does not exist
        """
        suffix = self.compartments[compartment_id]
        if suffix != "":
            return object_id + f"_{suffix}"
        return object_id

    def _strip_compartment_suffix(self, object_id, compartment_pattern):
        """Split the compartment string from an object_id.

        Parameters
        ----------
        object_id : str

        Returns
        -------
        object_id : str
            Object id without the compartment suffix, e.g. _e
        """
        return re.sub(compartment_pattern, "", object_id)

    ##########################################################################
    # Creation routines
    ##########################################################################

    def _fix_periplasm_proton_gradient(self):
        """Set reactions that do not match proton gradient criteria to irreversible.

        The criteria are the following:
        - All reactions of the following types are always kept
            TR-13 (Transport Energized by Phosphoanhydride-Bond Hydrolysis)
            TR-15 (Transport Energized by Decarboxylation)
            Membrane-Protein-Modification-Reactions
            Electron-Transfer-Reactions
        - If a reaction otherwise transports protons inside of the periplasm it is
         usually of the type
            TR-12 (Transport Energized by the Membrane Electrochemical Gradient)
        Keeping those reactions leads to thermodynamically infeasible loops, therefore
        they are reverted to a way that they only transport protons to the cytosol
        and are irreversible.
        """
        if "PERIPLASM" in self.get_model_compartment_ids():
            periplasm_recs = [
                self.reactions[i] for i in self.get_transport_reactions(compartment_id="PERIPLASM")
            ]
            proton_translocators = {i.id for i in periplasm_recs if "PROTON_p" in i.stoichiometries}
            try:
                tr13 = self.get_reactions_of_type(reaction_type="TR-13")
            except KeyError:
                tr13 = set()
            try:
                tr15 = self.get_reactions_of_type(reaction_type="TR-15")
            except KeyError:
                tr15 = set()
            try:
                mpmr = self.get_reactions_of_type(reaction_type="Membrane-Protein-Modification-Reactions")
            except KeyError:
                mpmr = set()
            try:
                etr = self.get_reactions_of_type(reaction_type="Electron-Transfer-Reactions")
            except KeyError:
                etr = set()
            to_fix = proton_translocators.difference(tr13 | tr15 | etr | mpmr)
            for reaction_id in to_fix:
                reaction = self.reactions[reaction_id]
                if reaction.stoichiometries["PROTON_p"] > 0:
                    reaction.reverse_stoichiometry()
                reaction.make_irreversible()

    def _move_electron_transport_cofactors_to_cytosol(self):
        """Move all periplasmatic electron transport cofactors into cytosol.

        This is done to keep the connectivity of the network.
        """
        cofactor_dict = {
            "Reduced-ferredoxins_p": "Reduced-ferredoxins_c",
            "Oxidized-ferredoxins_p": "Oxidized-ferredoxins_c",
            "Cytochromes-C-Reduced_p": "Cytochromes-C-Reduced_c",
            "Cytochromes-C-Oxidized_p": "Cytochromes-C-Oxidized_c",
            "NADPH_p": "NADPH_c",
            "NADP_p": "NADP_c",
            "NAD_p": "NAD_c",
            "ATP_p": "ATP_c",
            "ADP_p": "ADP_c",
        }

        try:
            etr_reactions = self.get_reactions_of_type(reaction_type="Electron-Transfer-Reactions")
        except KeyError:
            pass
        else:
            for reaction_id in tuple(etr_reactions):
                reaction = self.reactions[reaction_id].copy()
                if "PERIPLASM" in reaction.compartment:
                    changed_cpds = False
                    for compound_id in tuple(reaction.stoichiometries):
                        if compound_id in cofactor_dict:
                            reaction.stoichiometries[
                                cofactor_dict[compound_id]
                            ] = reaction.stoichiometries.pop(compound_id)
                            changed_cpds = True
                    if changed_cpds:
                        self.remove_reaction(reaction_id=reaction_id, remove_empty_references=False)
                        reaction.id = reaction.base_id
                        new_compartments = {self.compounds[i].compartment for i in reaction.stoichiometries}
                        new_compartments = tuple(sorted(new_compartments))
                        if len(new_compartments) == 1:
                            compartment = new_compartments[0]
                            reaction.compartment = compartment
                            reaction.transmembrane = False
                            reaction.id += self._add_compartment_suffix(
                                object_id="", compartment_id=compartment
                            )
                        else:
                            reaction.compartment = new_compartments
                            reaction.transmembrane = True
                            for compartment_id in reaction.compartment:
                                reaction.id += self._add_compartment_suffix(
                                    object_id="", compartment_id=compartment_id
                                )
                        self.add_reaction(reaction=reaction)

    def _repair_photosynthesis_reactions(self):
        """Switch the photosynthesis reactions proton compartments.

        The way the photosynthesis reactions are currenlty annotated and parsed,
        they will transport protons out of the periplasm, while they are
        actually doing the opposite.
        """
        try:
            for reaction_id in self.pathways["PWY-101"]:
                reaction = self.reactions[reaction_id]
                if reaction.transmembrane:
                    st = reaction.stoichiometries
                    in_compartment, out_compartment = reaction.compartment
                    in_proton_name = self._add_compartment_suffix(
                        object_id="PROTON", compartment_id=in_compartment
                    )
                    out_proton_name = self._add_compartment_suffix(
                        object_id="PROTON", compartment_id=out_compartment
                    )
                    try:
                        in_protons = st.pop(in_proton_name)
                        in_error = False
                    except KeyError:
                        in_error = True
                    try:
                        out_protons = st.pop(out_proton_name)
                        out_error = False
                    except KeyError:
                        out_error = True
                    if not in_error:
                        st[out_proton_name] = in_protons
                    if not out_error:
                        st[in_proton_name] = out_protons
        except KeyError:
            pass

    def read_from_pgdb(
        self,
        pgdb_path,
        parse_sequences=True,
        move_electron_transport_cofactors_to_cytosol=True,
        repair_photosynthesis_reactions=True,
        fix_periplasm_proton_gradient=True,
        compartment_map=None,
        remove_unused_compounds=True,
    ):
        """Parse the model from a given pdgb, e.g. MetaCyc.

        Parameters
        ----------
        pgdb_path: str or pathlib.Path
            This is expected to lead to the data directory of the pgdb
            so e.g. metacyc/23.0/data
        parse_sequences: bool
            Whether to parse the protein sequences of the model.
            If they are not needed, set this to false to make the parsing
            faster.
        apply_fba-fixes: dict(str: bool)
            Whether to apply certain common fixes after parsing
        compartment_map: dict(str: str)

        """
        if compartment_map is None:
            compartment_map = COMPARTMENT_MAP
        pgdb_path = pathlib.Path(pgdb_path)
        compounds, reactions, compartments = Cyc(
            pgdb_path=pgdb_path,
            parse_sequences=parse_sequences,
            compartment_map=compartment_map,
        ).parse()
        self.compartments = compartments
        self.add_compounds(compounds=compounds)
        self.add_reactions(reactions=reactions)

        for strong_cofactor_base_id, weak_cofactor_base_id in {
            "ATP": "ADP",
            "GTP": "GDP",
            "NADH": "NAD",
            "NADPH": "NADP",
            "10-FORMYL-THF": "THF",
            "METHYLENE-THF": "THF",
            "5-METHYL-THF": "THF",
            "ACETYL-COA": "CO-A",
            "Donor-H2": "Acceptor",
            "Reduced-ferredoxins": "Oxidized-ferredoxins",
            "Red-NADPH-Hemoprotein-Reductases": "Ox-NADPH-Hemoprotein-Reductases",
            "Cytochromes-C-Reduced": "Cytochromes-C-Oxidized",
            "Plastocyanin-Reduced": "Oxidized-Plastocyanins",
            "ETF-Reduced": "ETF-Oxidized",
            "Red-Thioredoxin": "Ox-Thioredoxin",
            "CPD-12829": "PLASTOQUINONE-9",
        }.items():
            self.add_cofactor_pair(
                strong_cofactor_base_id=strong_cofactor_base_id,
                weak_cofactor_base_id=weak_cofactor_base_id,
            )

        self.add_minimal_seed(
            compound_ids={
                "WATER_c",
                "PROTON_c",
                "OXYGEN-MOLECULE_c",
                "CARBON-DIOXIDE_c",
                "Pi_c",
                "MN+2_c",
                "ZN+2_c",
                "CU+2_c",
                "CA+2_c",
                "SULFATE_c",
                "AMMONIA_c",
            }
        )
        if move_electron_transport_cofactors_to_cytosol:
            self._move_electron_transport_cofactors_to_cytosol()

        if repair_photosynthesis_reactions:
            self._repair_photosynthesis_reactions()

        if fix_periplasm_proton_gradient:
            self._fix_periplasm_proton_gradient()

        if remove_unused_compounds:
            self.remove_unused_compounds()

    def read_from_cobra(self, cobra_model):
        """Import a cobra model into this model.

        Parameters
        ----------
        cobra_model: cobra.Model
            Mapping of model compartments to moped compartments
        """
        compartment_map = cobra_model.compartments
        self.compartments.update({v: k for k, v in compartment_map.items()})
        compartment_suffixes = re.compile("|".join(set([f"(_{i}$)" for i in compartment_map.keys()])))

        objective = {}
        for metabolite in cobra_model.metabolites:
            base_id = self._strip_compartment_suffix(
                object_id=metabolite.id, compartment_pattern=compartment_suffixes
            )
            compartment = compartment_map[metabolite.compartment]
            self.add_compound(
                Compound(
                    base_id=base_id,
                    id=metabolite.id,
                    name=metabolite.name,
                    compartment=compartment,
                    formula=metabolite.elements,
                    charge=metabolite.charge,
                    gibbs0=None,
                    types=None,
                )
            )
        for reaction in cobra_model.reactions:
            obj_coef = reaction.objective_coefficient
            if obj_coef != 0:
                objective[reaction.id] = obj_coef

            self.add_reaction(
                Reaction(
                    base_id=self._strip_compartment_suffix(
                        object_id=reaction.id, compartment_pattern=compartment_suffixes
                    ),
                    id=reaction.id,
                    stoichiometries={k.id: v for k, v in reaction.metabolites.items()},
                    bounds=reaction.bounds,
                    reversible=reaction.reversibility,
                    gibbs0=None,
                    ec=None,
                    pathways=None,
                    name=reaction.name,
                )
            )
        self.set_objective(objective=objective)

    def read_from_sbml(self, sbml_file):
        """Import an sbml model into this model.

        Parameters
        ----------
        sbml_file: str or pathlib.Path
        """
        cobra_model = cobra.io.read_sbml_model(filename=sbml_file)
        self.read_from_cobra(cobra_model=cobra_model)

    def read_from_bigg(self, bigg_sbml_file):
        """Import a bigg sbml model into this model.

        Parameters
        ----------
        bigg_sbml_file: str or pathlib.Path
        """
        self.read_from_sbml(sbml_file=bigg_sbml_file)

        for strong_cofactor_base_id, weak_cofactor_base_id in {
            "atp": "adp",
            "gtp": "gdp",
            "nadh": "nad",
            "nadph": "nadp",
            "10fthf": "thf",
            "methf": "thf",
            "fdxrd": "fdxox",
            "trdrd": "trdox",
            "etfrd": "etfox",
            "accoa": "coa",
            "pcrd": "pcox",
        }.items():
            self.add_cofactor_pair(
                strong_cofactor_base_id=strong_cofactor_base_id,
                weak_cofactor_base_id=weak_cofactor_base_id,
            )

    ##########################################################################
    # Universal functions
    ##########################################################################

    def create_submodel(self, reaction_ids, name=None):
        """Create a subset of the model, containing the given reactions and their compounds.

        Parameters
        ----------
        reaction_ids: Iterable(str)
            Iterable of reaction_ids
        name: str, optional
            Name of the submodel

        Returns
        -------
        submodel: moped.Model
        """
        reactions = [self.reactions[i] for i in sorted(reaction_ids)]
        compounds = set()
        for rec in reactions:
            for cpd in rec.stoichiometries:
                cpd = self.compounds[cpd].copy()
                cpd.in_reaction = set()
                compounds.add(cpd)
        if name is None:
            name = self.name + " submodel"

        submodel = Model(
            compounds=compounds,
            reactions=reactions,
            name=name,
            compartments=self.compartments,
        )

        # submodel.cofactor_pairs = self.cofactor_pairs.copy()
        # This is wrong, submodel must not necessarily have the same cofactor pairs

        # Collect base cofactor pairs
        base_cofactor_pairs = {}
        for strong, weak in self.cofactor_pairs.items():
            strong_base_cpd = self.compounds[strong].base_id
            weak_base_cpd = self.compounds[weak].base_id
            base_cofactor_pairs[strong_base_cpd] = weak_base_cpd

        # Add cofactor pairs to submodel, that actually exist in there
        for strong, weak in base_cofactor_pairs.items():
            submodel.add_cofactor_pair(
                strong_cofactor_base_id=strong,
                weak_cofactor_base_id=weak,
            )
        return submodel

    def add_cofactor_pair(self, strong_cofactor_base_id, weak_cofactor_base_id):
        """Add a cofactor pair.

        This automatically adds all compartment variants of the given base ides.

        E.g. ATP as a strong cofactor and ADP as its weak pair.

        Parameters
        ----------
        strong_cofactor_base_id: str
        weak_cofactor_base_id: str
        """
        try:
            for strong_cpd_id in self.base_compounds[strong_cofactor_base_id]:
                for weak_cpd_id in self.base_compounds[weak_cofactor_base_id]:
                    if self.compounds[strong_cpd_id].compartment == self.compounds[weak_cpd_id].compartment:
                        self.cofactor_pairs[strong_cpd_id] = weak_cpd_id
        except KeyError:
            pass

    def get_weak_cofactors(self):
        """Get ids of weak cofactors.

        Returns
        -------
        cofactors: list(str)
            List of cofactor ids
        """
        return list(set([i for i in self.cofactor_pairs.values()]))

    def get_weak_cofactor_duplications(self):
        """Get ids of weak cofactors including the __cof__ tag.

        This function is useful for structural analyses, in which these
        tagged cofactors are used.

        Returns
        -------
        cofactors: list(str)
            List of cofactor ids
        """
        return list(set([i + "__cof__" for i in self.cofactor_pairs.values()]))

    def get_strong_cofactors(self):
        """Get ids of strong cofactors.

        Returns
        -------
        cofactors: list(str)
            List of cofactor ids
        """
        return list(set([i for i in self.cofactor_pairs.keys()]))

    def get_strong_cofactor_duplications(self):
        """Get ids of strong cofactors including the __cof__ tag.

        This function is useful for structural analyses, in which these
        tagged cofactors are used.

        Returns
        -------
        cofactors: list(str)
            List of cofactor ids
        """
        return list(set([i + "__cof__" for i in self.cofactor_pairs.keys()]))

    def update_from_reference(self, reference_model, verbose=False):
        """Update a model from a reference Model.

        Parameters
        ----------
        reference_model: moped.Model
        verbose: bool, optional

        Returns
        -------
        unmapped_reactions: list(str)
            List of reactions that could not be found in the reference database
        unmapped_compounds: list(str)
            List of compounds that could not be found in the reference database
        """
        mapped_compounds = set(self.compounds).intersection(reference_model.compounds)
        unmapped_compounds = set(self.compounds).difference(reference_model.compounds)

        old_base_reactions = set(self.base_reactions)
        old_variant_reactions = set(self.variant_reactions)

        new_base_reactions = set(reference_model.base_reactions)
        new_variant_reactions = set(reference_model.variant_reactions)

        unmapped_base_reactions = [
            j for i in old_base_reactions.difference(new_base_reactions) for j in self.base_reactions[i]
        ]
        unmapped_variant_reactions = [
            j
            for i in old_variant_reactions.difference(new_variant_reactions)
            for j in self.variant_reactions[i]
        ]
        unmapped_reactions = unmapped_base_reactions + unmapped_variant_reactions

        # Update all existing compounds
        for compound_id in mapped_compounds:
            self.add_compound_from_reference(reference_model=reference_model, compound_id=compound_id)

        # Update all existing base reactions
        for base_reaction_id in old_base_reactions.intersection(
            new_base_reactions
        ) | old_variant_reactions.intersection(new_variant_reactions):
            self.add_reaction_from_reference(
                reference_model=reference_model,
                reaction_id=base_reaction_id,
                update_compounds=True,
            )

        # Updating compounds can change the balance status
        # of the local reactions, thus those that cannot be mapped
        # need to be checked again
        for reaction_id in unmapped_reactions:
            if not self.check_mass_balance(reaction_id=reaction_id):
                self.remove_reaction(reaction_id=reaction_id)
                continue
            if not self.check_charge_balance(reaction_id=reaction_id):
                self.remove_reaction(reaction_id=reaction_id)
        if verbose:
            print(
                f"Could not map {len(unmapped_base_reactions) + len(unmapped_variant_reactions)} reactions "
                + f"and {len(unmapped_compounds)} compounds"
            )
            return unmapped_reactions, unmapped_compounds

    ##########################################################################
    # Compound functions
    ##########################################################################

    def add_compound(self, compound):
        """Add a compound to the model. Overwrites existing compounds.

        Parameters
        ----------
        compound: moped.Compound
            The compound object

        Raises
        ------
        TypeError
            If compound is not of type moped.Compound
        """
        if isinstance(compound, Compound):
            if not bool(compound.id):
                compound.id = self._add_compartment_suffix(
                    object_id=compound.base_id, compartment_id=compound.compartment
                )
            self.compounds[compound.id] = compound.copy()
            self.base_compounds.setdefault(compound.base_id, set()).add(compound.id)
            for compound_type in compound.types:
                self._compound_types.setdefault(compound_type, set()).add(compound.id)
        else:
            raise TypeError("Compound has to be of type moped.model.Compound")

    def add_compounds(self, compounds):
        """Add multiple compounds to the model. Overwrites existing compounds.

        Parameters
        ----------
        compounds: iterable(moped.Compound)
            The compound objects

        Raises
        ------
        TypeError
            If compound is not of type moped.Compound
        """
        for compound in compounds:
            self.add_compound(compound=compound)

    def add_compound_from_reference(self, reference_model, compound_id):
        """Overwrite local data from reference database or adds new one if it does not exist already.

        Parameters
        ----------
        reference_model: moped.Model
        compound_id: str
        """
        new_cpd = reference_model.compounds[compound_id].copy()
        try:
            old_cpd = self.compounds.pop(compound_id)
            new_cpd.in_reaction = old_cpd.in_reaction
        except KeyError:
            new_cpd.in_reaction = set()
        self.compounds[compound_id] = new_cpd

    def _create_compartment_variant(self, old_compound, compartment_id):
        """Create a variant of the compound in another compartment.

        This empties the in_reaction set, as the compound is only known
        to be part of the reactions in the previous compartment and
        we cannot know whether those reactions are also available
        in the new compartment.

        Parameters
        ----------
        old_compound: moped.Compound
        compartment_id: str


        Returns
        -------
        new_compound: Compound
        """
        new_compound = old_compound.copy()
        new_compound.id = self._add_compartment_suffix(
            object_id=old_compound.base_id, compartment_id=compartment_id
        )
        new_compound.compartment = compartment_id
        new_compound.in_reaction = set()
        self.add_compound(compound=new_compound)
        return new_compound

    def add_compartment_compound_variant(self, compound_id, compartment_id):
        """Add a copy of the compound in the respective compartment.

        Clears the in_reaction attribute. The compartments are named
        according to the metacyc database

        Parameters
        ----------
        compound_id: str
        compartment_id: str

        Raises
        ------
        TypeError
            If compound_id is not a string
        KeyError
            If compound is not in the model
        KeyError
            If the compartment does not exist

        Returns
        -------
        compartment_compound: moped.Compound
        """
        try:
            old_compound = self.compounds[compound_id]
        except KeyError:
            try:
                compound_variants = self.base_compounds[compound_id]
                old_compound = self.compounds[next(iter(compound_variants))]
            except KeyError:
                raise KeyError(f"Compound {compound_id} has to be in the model to create an external variant")
        new_compound_id = self._add_compartment_suffix(
            object_id=old_compound.base_id, compartment_id=compartment_id
        )
        try:
            new_compound = self.compounds[new_compound_id]
        except KeyError:
            new_compound = self._create_compartment_variant(
                old_compound=old_compound, compartment_id=compartment_id
            )
        return new_compound

    def set_compound_property(self, compound_id, property_dict):
        """Set one or multiple properties of a compound.

        Parameters
        ----------
        compound_id: str
        property_dict: dict

        Raises
        ------
        KeyError
            If Compound does not have an attribute specified in property_dict
        """
        for k, v in property_dict.items():
            try:
                setattr(self.compounds[compound_id], k, v)
            except AttributeError:
                raise KeyError(f"Compound does not have key '{k}', can only be one of {Compound.__slots__}")

    def remove_compound(self, compound_id):
        """Remove a compound from the model.

        Parameters
        ----------
        compound_id: str
        """
        compound = self.compounds.pop(compound_id)

        # Also remove from base compounds
        self.base_compounds[compound.base_id].remove(compound.id)
        if not bool(self.base_compounds[compound.base_id]):
            del self.base_compounds[compound.base_id]

        # Also remove from compound types
        for compound_type in compound.types:
            self._compound_types[compound_type].remove(compound.id)
            if not bool(self._compound_types[compound_type]):
                del self._compound_types[compound_type]

        compound_id = compound.id
        if compound_id in self.cofactor_pairs:
            del self.cofactor_pairs[compound_id]
        elif compound_id in self.get_weak_cofactors():
            weak_cofactors = self.get_weak_cofactors()
            strong_cofactors = self.get_strong_cofactors()
            weak_to_strong = dict(zip(weak_cofactors, strong_cofactors))
            del self.cofactor_pairs[weak_to_strong[compound_id]]

    def remove_compounds(self, compound_ids):
        """Remove multiple compounds from the model.

        Parameters
        ----------
        compound_ids: iterable(str)
        """
        for compound_id in compound_ids:
            self.remove_compound(compound_id=compound_id)

    def remove_unused_compounds(self):
        """Remove compounds from the model that are in no reaction."""
        all_compounds = set(self.compounds)
        used_compounds = set()
        for reaction in self.reactions.values():
            used_compounds.update(set(reaction.stoichiometries))
        unused = all_compounds.difference(used_compounds)
        self.remove_compounds(compound_ids=unused)

    def get_compound_base_id(self, compound_id):
        """Get the database links of a given compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        database_links: dict
        """
        return self.compounds[compound_id].base_id

    def get_compound_compartment_variants(self, compound_base_id):
        """Get compound ids for all respective compartments the compound is in.

        The compound_base_id for ATP_c for example would be ATP.

        Parameters
        ----------
        compound_base_id : str

        Returns
        -------
        compound_ids : set
        """
        return self.base_compounds[compound_base_id]

    def get_compound_compartment(self, compound_id):
        """Get compartment of a given compound compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        compartment: str
        """
        return self.compounds[compound_id].compartment

    def get_compound_formula(self, compound_id):
        """Get the charge of a given compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        formula: dict(str, int)
        """
        return self.compounds[compound_id].formula

    def get_compound_charge(self, compound_id):
        """Get the charge of a given compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        charge: num
        """
        return self.compounds[compound_id].charge

    def get_compound_gibbs0(self, compound_id):
        """Get the gibbs energy (free enthalpy) of the given compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        gibbs0: num
        """
        return self.compounds[compound_id].gibbs0

    def get_reactions_of_compound(self, compound_id):
        """Get all reactions of a compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        in_reaction: set(str)
            Set of reaction ids of which the compound is part
        """
        return self.compounds[compound_id].in_reaction

    def get_compound_database_links(self, compound_id):
        """Get the database links of a given compound.

        Parameters
        ----------
        compound_id: str

        Returns
        -------
        database_links: dict
        """
        return self.compounds[compound_id].database_links

    def get_base_compound_ids(self):
        """Get base IDs of all compounds.

        Returns
        -------
        base_compound_ids: set(str)
        """
        return set(i.base_id for i in self.compounds.values())

    def get_compound_type_ids(self):
        """Get all available compound types.

        Returns
        -------
        compound_types: set(str)
        """
        return set(self._compound_types)

    def get_model_compartment_ids(self):
        """Get all ids for compartments used in the model.

        Returns
        -------
        compartment_ids : set(str)
        """
        return set(self.compartments)

    def get_compounds_of_compartment(self, compartment_id):
        """Get all compounds from the respective compartment.

        To look up the available compartments, see model.get_model_compartment_ids

        Parameters
        ----------
        compartment_id: str

        Returns
        -------
        compounds_of_compartment: list(str)

        See Also
        --------
        model.get_model_compartment_ids
            To get all available compartments
        """
        if compartment_id not in self.get_model_compartment_ids():
            raise KeyError(
                f"Unknown compartment {compartment_id}, did you mean any of {self.get_model_compartment_ids()}?"
            )
        return [k for k, v in self.compounds.items() if v.compartment == compartment_id]

    def get_compounds_of_type(self, compound_type):
        """Get all compound ids of a given compound_type.

        Parameters
        ----------
        compound_type : str

        Returns
        -------
        compound_type : set
        """
        return self._compound_types[compound_type]

    ##########################################################################
    # Reaction functions
    ##########################################################################

    def add_reaction(self, reaction):
        """Add a reaction to the model.

        Also adds this reaction to each compounds in-reaction attribute,
        pathways and monomers

        Parameters
        ----------
        reaction: moped.Reaction

        Raises
        ------
        KeyError
            If any of the reaction compounds is not in the model
        TypeError
            If reaction is not of type moped.Reaction
        """
        if not isinstance(reaction, Reaction):
            raise TypeError("Reaction has to be of type moped.model.Reaction")
        reaction_id = reaction.id
        if "__var__" in reaction.id:
            self.variant_reactions.setdefault(reaction.base_id, set()).add(reaction_id)
        else:
            self.base_reactions.setdefault(reaction.base_id, set()).add(reaction_id)
        self.reactions[reaction_id] = reaction.copy()
        for compound in reaction.stoichiometries:
            self.compounds[compound].in_reaction.add(reaction_id)
        for type_ in reaction.types:
            self._reaction_types.setdefault(type_, set()).add(reaction.id)
        for pathway in reaction.pathways:
            self.add_reaction_to_pathway(pathway_id=pathway, reaction_id=reaction_id)
        for monomer in reaction.sequences:
            self._monomers.setdefault(monomer, set()).add(reaction.id)

    def add_reactions(self, reactions):
        """Add multiple reactions to the model.

        Parameters
        ----------
        reactions: iterable(moped.Reaction)

        Raises
        ------
        KeyError
            If any of the reaction compounds is not in the model
        TypeError
            If reaction is not of type moped.Reaction
        """
        for reaction in reactions:
            self.add_reaction(reaction=reaction)

    def add_reaction_from_reference(self, reference_model, reaction_id, update_compounds=True):
        """Add a reaction from a reference model.

        Always adds reversibiliy and cofactor duplicates as well. In this case all
        existing reaction variants are kept if they are not overwritten.
        Adds all variants of a reaction if the base_id of a variant reaction is given.
        In this case all other existing reaction variants are removed.

        Parameters
        ----------
        reference_model: moped.model
        reaction_id: str
        update_compounds: bool, optional
            Whether to update all compounds that take place in the reaction as well

        Raises
        ------
        KeyError
            If reaction_id cannot be found in the reference
        """
        try:
            reaction = self.reactions[reaction_id]
            base_id = reaction.base_id
        except KeyError:
            base_id = reaction_id
        if base_id in reference_model.variant_reactions:
            try:
                for reaction_id in tuple(self.variant_reactions[base_id]):
                    self.remove_reaction(reaction_id)
            except KeyError:
                pass
            new_reactions = [
                reference_model.reactions[reaction_id]
                for reaction_id in reference_model.variant_reactions[base_id]
            ]
            if update_compounds:
                new_compound_ids = {j for i in new_reactions for j in i.stoichiometries}
                for compound_id in new_compound_ids:
                    self.add_compound_from_reference(reference_model=reference_model, compound_id=compound_id)
            for reaction in new_reactions:
                self.add_reaction(reaction=reaction)
                if reaction.id in reference_model._duplicate_reactions:
                    self._duplicate_reactions.add(reaction.id)
        elif base_id in reference_model.base_reactions:
            try:
                for reaction_id in tuple(self.base_reactions[base_id]):
                    self.remove_reaction(reaction_id=reaction_id)
            except KeyError:
                pass
            new_reactions = [
                reference_model.reactions[reaction_id]
                for reaction_id in reference_model.base_reactions[base_id]
            ]
            if update_compounds:
                new_compound_ids = {j for i in new_reactions for j in i.stoichiometries}
                for compound_id in new_compound_ids:
                    self.add_compound_from_reference(reference_model=reference_model, compound_id=compound_id)
            for reaction in new_reactions:
                self.add_reaction(reaction=reaction)
                if reaction.id in reference_model._duplicate_reactions:
                    self._duplicate_reactions.add(reaction.id)
        elif base_id in reference_model.reactions:
            self.add_reaction_from_reference(
                reference_model=reference_model,
                reaction_id=reference_model.reactions[reaction_id].base_id,
            )
        else:
            raise KeyError(f"Could not find {reaction_id} in the reference_model")

    def add_reactions_from_reference(self, reference_model, reaction_ids, update_compounds=True):
        """Add reactions from a reference model, overwriting existing reactions.

        Parameters
        ----------
        reference_model : moped.Model
        reaction_ids : Iterable(str)
        update_compounds : bool
            Whether to update all compounds that take place in the reaction as well
        """
        for reaction_id in reaction_ids:
            self.add_reaction_from_reference(
                reference_model=reference_model,
                reaction_id=reaction_id,
                update_compounds=update_compounds,
            )

    def set_reaction_property(self, reaction_id, property_dict):
        """Set one or multiple properties of a reaction.

        Parameters
        ----------
        reaction_id: str
        property_dict
            Dictionary containing attribute: value pairs

        Raises
        ------
        KeyError
            If Reaction does not have one of the keys of property_dict
        """
        for k, v in property_dict.items():
            try:
                setattr(self.reactions[reaction_id], k, v)
            except AttributeError:
                raise KeyError(f"Reaction does not have key '{k}', can only be one of {Reaction.__slots__}")

    def remove_reaction(self, reaction_id, remove_empty_references=True):
        """Remove a reaction from the model.

        This also removes the reaction from reaction_variants, pathways
        and its compounds in_reaction attribute if applicable.
        If the compound in_reaction attribute is empty it also removes the compound

        Parameters
        ----------
        reaction_id: str
        remove_empty_references: bool, optional
            Whether e.g. reference to type of reaction should be removed
            if the reaction was the last one of it

        Raises
        ------
        KeyError
            If reaction is not in the model
        """
        reaction = self.reactions[reaction_id]
        if "__var__" in reaction_id:
            self.variant_reactions[reaction.base_id].remove(reaction_id)
            if remove_empty_references:
                if not bool(self.variant_reactions[reaction.base_id]):
                    del self.variant_reactions[reaction.base_id]
        else:
            self.base_reactions[reaction.base_id].remove(reaction_id)
            if remove_empty_references:
                if not bool(self.base_reactions[reaction.base_id]):
                    del self.base_reactions[reaction.base_id]
        for pathway in tuple(reaction.pathways):
            self.remove_reaction_from_pathway(pathway_id=pathway, reaction_id=reaction_id)
        for compound in reaction.stoichiometries:
            self.compounds[compound].in_reaction.remove(reaction_id)
            if remove_empty_references:
                if not bool(self.compounds[compound].in_reaction):
                    del self.compounds[compound]

        for type_ in reaction.types:
            self._reaction_types[type_].remove(reaction_id)
            if remove_empty_references:
                if not bool(self._reaction_types[type_]):
                    del self._reaction_types[type_]
        del self.reactions[reaction_id]

    def remove_reactions(self, reaction_ids):
        """Remove multiple reactions from the model.

        Parameters
        ----------
        reaction_ids: iterable(str)

        Raises
        ------
        KeyError
            If reaction is not in the model
        """
        for reaction_id in reaction_ids:
            self.remove_reaction(reaction_id=reaction_id)

    def get_reaction_base_id(self, reaction_id):
        """Get the base id of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        base_id: str
        """
        return self.reactions[reaction_id].base_id

    def get_reaction_compartment_variants(self, reaction_base_id):
        """Get the ids of the reaction in all compartments it takes place in.

        Parameters
        ----------
        reaction_base_id : str

        Returns
        -------
        reaction_ids : set
        """
        return self.base_reactions[reaction_base_id]

    def get_reaction_compartment(self, reaction_id):
        """Get the compartment of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        compartment: str
        """
        return self.reactions[reaction_id].compartment

    def get_reaction_gibbs0(self, reaction_id):
        """Get the database links of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        database_links: dict
        """
        return self.reactions[reaction_id].gibbs0

    def get_reaction_bounds(self, reaction_id):
        """Get the bounds of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        bounds: tuple(num, num)
        """
        return self.reactions[reaction_id].bounds

    def get_reaction_reversibility(self, reaction_id):
        """Get whether a reaction is reversible.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        reversible: bool
        """
        return self.reactions[reaction_id].reversible

    def get_reaction_pathways(self, reaction_id):
        """Get the pathways of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        pathways: set(str)
        """
        return self.reactions[reaction_id].pathways

    def get_reaction_sequences(self, reaction_id):
        """Get the protein sequences of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        sequences: dict(str: str)
        """
        return self.reactions[reaction_id].sequences

    def get_reaction_types(self, reaction_id):
        """Get the types of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        types: list(str)
        """
        return self.reactions[reaction_id].types

    def get_reaction_database_links(self, reaction_id):
        """Get the database links of a given reaction.

        Parameters
        ----------
        reaction_id: str

        Returns
        -------
        database_links: dict
        """
        return self.reactions[reaction_id].database_links

    def get_base_reaction_ids(self):
        """Get base IDs of all reactions.

        Returns
        -------
        base_compound_ids: set
        """
        return set(self.base_reactions)

    def get_reaction_type_ids(self):
        """Get all available reaction types.

        Returns
        -------
        reaction_types: set
        """
        return set(self._reaction_types)

    def get_reactions_of_type(self, reaction_type):
        """Get all reaction ids of a given type.

        Parameters
        ----------
        reaction_type : str

        Returns
        -------
        reaction_ids : str
        """
        return self._reaction_types[reaction_type]

    def get_reaction_variants(self, base_reaction_id):
        """Get all reaction variants.

        Parameters
        ----------
        base_reaction_id: str
            So e.g. rxn1, if the variants are rxn1__var__0 etc
        """
        return self.variant_reactions[base_reaction_id]

    def get_reversible_reactions(self):
        """Get all reactions marked as reversible.

        Returns
        -------
        reactions: list(str)
            List of reaction ids
        """
        return [k for k, v in self.reactions.items() if v.reversible]

    def get_irreversible_reactions(self):
        """Get all reactions marked as irreversible.

        Returns
        -------
        reactions: list(str)
            List of reaction ids
        """
        return [k for k, v in self.reactions.items() if not v.reversible]

    def get_transmembrane_reactions(self):
        """Get reaction ids for reactions with compounds in two compartments.

        Returns
        -------
        transmembrane_reactions : list(str)
        """
        return [k for k, v in self.reactions.items() if v.transmembrane]

    def get_reactions_of_compartment(self, compartment_id, include_transporters=True):
        """Reaction reaction ids for reactions that occur in a given compartment.

        Parameters
        ----------
        compartment_id: str
        include_transporters: bool
            Whether to include transmembrane reactions that transport anything in/out
            of the compartment

        Returns
        -------
        compartment_reactions : set(str)
        """
        reaction_ids = {
            reaction_id
            for compound_id in self.get_compounds_of_compartment(compartment_id=compartment_id)
            for reaction_id in self.compounds[compound_id].in_reaction
        }
        if include_transporters:
            return reaction_ids
        return reaction_ids.difference(self.get_transmembrane_reactions())

    def get_transport_reactions(self, compartment_id):
        """Get reactions that transport something in/out of a given compartment.

        Parameters
        ----------
        into_compartment : str

        Returns
        -------
        transport_reactions : set(str)
        """
        compartment_reactions = self.get_reactions_of_compartment(
            compartment_id=compartment_id, include_transporters=True
        )
        transmembrane_reactions = self.get_transmembrane_reactions()
        return set(transmembrane_reactions).intersection(compartment_reactions)

    ##########################################################################
    # Pathway functions
    ##########################################################################

    def add_pathway(self, pathway_id, pathway_reactions):
        """Add a pathway to the model.

        This also adds the pathway to all reaction objects

        Parameters
        ----------
        pathway_id: str
        pathway_reactions: list(str)
        """
        for reaction_id in pathway_reactions:
            self.reactions[reaction_id].pathways.add(pathway_id)
        self.pathways.setdefault(pathway_id, set()).update(pathway_reactions)

    def add_reaction_to_pathway(self, pathway_id, reaction_id):
        """Add a reaction to a pathway.

        This also adds the pathway to the reaction object

        Parameters
        ----------
        pathway_id: str
        reaction_id: str
        """
        self.reactions[reaction_id].pathways.add(pathway_id)
        self.pathways.setdefault(pathway_id, set()).add(reaction_id)

    def remove_pathway(self, pathway_id):
        """Remove a pathway from the model.

        This also removes the pathway from all the reactions

        Parameters
        ----------
        pathway_id: str
        """
        reactions = self.pathways.pop(pathway_id)
        for reaction in reactions:
            self.reactions[reaction].pathways.remove(pathway_id)

    def remove_reaction_from_pathway(self, pathway_id, reaction_id):
        """Remove a reaction from a pathway.

        This also removes the pathway from the reaction object

        Parameters
        ----------
        pathway_id: str
        reaction_id: str
        """
        self.pathways[pathway_id].remove(reaction_id)
        self.reactions[reaction_id].pathways.remove(pathway_id)
        # Remove pathway completely if it is empty
        if self.pathways[pathway_id] == set():
            self.remove_pathway(pathway_id=pathway_id)

    def get_reactions_of_pathway(self, pathway_id):
        """Get all reactions that are part of a pathway.

        Parameters
        ----------
        pathway_id: str
            Name of the pathway

        Returns
        -------
        pathways: set(str)
            Set of all reaction ids
        """
        return self.pathways[pathway_id]

    def get_pathway_ids(self):
        """Get all pathway ids.

        Returns
        -------
        pathway_ids: tuple(str)
        """
        return tuple(self.pathways.keys())

    ##########################################################################
    # Medium, biomass and objective functions
    ##########################################################################

    def add_transport_reaction(self, compound_id, compartment_id, bounds=(-1000, 1000)):
        """Add a transport reaction into another compartment.

        Parameters
        ----------
        compound_id: str
        compartment_id: str
            The compartment into which the compound is transported
        bounds: tuple(int, int)
        """
        into_cpd = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=compartment_id
        )
        into_suffix = self._add_compartment_suffix(object_id="", compartment_id=compartment_id)
        if bounds[0] < 0 and bounds[1] > 0:
            reversible = True
        else:
            reversible = False
        self.add_reaction(
            Reaction(
                id=f"TR_{compound_id}{into_suffix}",
                base_id=f"TR_{compound_id}",
                stoichiometries={compound_id: -1, into_cpd.id: 1},
                bounds=bounds,
                reversible=reversible,
                transmembrane=True,
            )
        )

    def add_influx(self, compound_id, extracellular_compartment_id):
        """Add an influx of a compound to the model.

        Parameters
        ----------
        compound_id: str
        extracellular_compartment_id: str
        """
        # Add influx
        ex_met = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=extracellular_compartment_id
        )
        self.add_reaction(
            Reaction(
                id=f"EX_{ex_met.base_id}_e",
                base_id=f"EX_{ex_met.base_id}",
                stoichiometries={ex_met.id: -1},
                bounds=(-1000, 0),
            )
        )

    def remove_influx(self, compound_id):
        """Remove the influx of a given compound.

        Parameters
        ----------
        compound_id : str
        """
        try:
            compound = self.compounds[compound_id]
            base_compound_id = compound.base_id
        except KeyError:
            if compound_id not in self.base_compounds:
                raise KeyError(f"Compound {compound_id} neither found in compounds nor base compounds")
            base_compound_id = compound_id
        self.remove_reaction(reaction_id=f"EX_{base_compound_id}_e")

    def add_efflux(self, compound_id, extracellular_compartment_id):
        """Add an efflux of a compound to the model.

        Parameters
        ----------
        compound_id: str
        extracellular_compartment_id: str
        """
        # Add efflux
        ex_met = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=extracellular_compartment_id
        )
        self.add_reaction(
            Reaction(
                id=f"EX_{ex_met.base_id}_e",
                base_id=f"EX_{ex_met.base_id}",
                stoichiometries={ex_met.id: -1},
                bounds=(0, 1000),
                reversible=False,
            )
        )

    def remove_efflux(self, compound_id):
        """Remove the efflux of a given compound.

        Parameters
        ----------
        compound_id : str
        """
        try:
            compound = self.compounds[compound_id]
            base_compound_id = compound.base_id
        except KeyError:
            if compound_id not in self.base_compounds:
                raise KeyError(f"Compound {compound_id} neither found in compounds nor base compounds")
            base_compound_id = compound_id
        self.remove_reaction(reaction_id=f"EX_{base_compound_id}_e")

    def add_medium_component(self, compound_id, extracellular_compartment_id):
        """Add a compound as a medium component.

        Parameters
        ----------
        compound_id: str
        extracellular_compartment_id: str
        """
        # Add medium influx/efflux
        ex_met = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=extracellular_compartment_id
        )
        self.add_reaction(
            Reaction(
                id=f"EX_{ex_met.base_id}_e",
                base_id=f"EX_{ex_met.base_id}",
                stoichiometries={ex_met.id: -1},
                bounds=(-1000, 1000),
                reversible=True,
            )
        )

    def remove_medium_component(self, compound_id):
        """Remove influx and outflux of a given compound.

        Parameters
        ----------
        compound_id : str
        """
        try:
            compound = self.compounds[compound_id]
            base_compound_id = compound.base_id
        except KeyError:
            if compound_id not in self.base_compounds:
                raise KeyError(f"Compound {compound_id} neither found in compounds nor base compounds")
            base_compound_id = compound_id
        self.remove_reaction(reaction_id=f"EX_{base_compound_id}_e")

    def get_biomass_template(self, organism="ecoli"):
        """Return an organism specific biomass composition.

        Parameters
        ----------
        organism: str

        Returns
        -------
        biomass_template: dict(str: float)
            Biomass composition of the organism
        """
        try:
            return BIOMASS_TEMPLATES[organism]
        except KeyError:
            raise KeyError(
                f"Could not find template for organism {organism}. "
                + f"Currenly supported organisms are {tuple(BIOMASS_TEMPLATES)}"
            )

    def set_objective(self, objective):
        """Set the objective function(s).

        Parameters
        ----------
        objective: dict(str: float)
            Dictionary containing reaction_id:coefficient pairings
        """
        for reaction_id in objective:
            if reaction_id not in self.reactions:
                raise KeyError(f"Objective reaction {reaction_id} is not in the model")
        self.objective = dict(objective)

    ##########################################################################
    # Quality control interface
    ##########################################################################

    def check_charge_balance(self, reaction_id, verbose=False):
        """Check the charge balance of a reaction.

        Parameter
        ---------
        reaction_id: str
        verbose: bool

        Returns
        -------
        balanced: bool
            Whether the reaction is balanced or not
        """
        substrate_charge = 0
        product_charge = 0
        for k, v in self.reactions[reaction_id].stoichiometries.items():
            if v < 0:
                substrate_charge -= self.compounds[k].charge * v
            else:
                product_charge += self.compounds[k].charge * v
        if verbose:
            print(f"Substrate charge: {substrate_charge}")
            print(f"Product charge: {product_charge}")
        if substrate_charge - product_charge == 0:
            return True
        return False

    def check_mass_balance(self, reaction_id, verbose=False):
        """Check the mass balance of a reaction.

        Parameter
        ---------
        reaction_id: str
        verbose: bool

        Returns
        -------
        balanced: bool
            Whether the reaction is balanced or not
        """
        lhs_atoms = defaultdict(int)
        rhs_atoms = defaultdict(int)
        for k, v in self.reactions[reaction_id].stoichiometries.items():
            formula = self.compounds[k].formula
            if not bool(formula):
                return False
            if v < 0:
                for atom, stoich in formula.items():
                    lhs_atoms[atom] -= stoich * v
            else:
                for atom, stoich in formula.items():
                    rhs_atoms[atom] += stoich * v
        if verbose:
            print(dict(lhs_atoms))
            print(dict(rhs_atoms))
        for k in set((*lhs_atoms, *rhs_atoms)):
            diff = lhs_atoms[k] - rhs_atoms[k]
            if diff != 0:
                return False
        return True

    ###########################################################################
    # Stoichiometric functions
    ###########################################################################

    def get_stoichiometric_matrix(self):
        """Return the stoichiometric matrix.

        Returns
        -------
        N: numpy.array
        """
        cpd_mapper = dict(zip(self.compounds, range(len(self.compounds))))
        N = np.zeros((len(self.compounds), len(self.reactions)))
        for i, rxn in enumerate(self.reactions.values()):
            for cpd, val in rxn.stoichiometries.items():
                N[cpd_mapper[cpd], i] = val
        return N

    def get_stoichiometric_df(self):
        """Return the stoichiometric matrix as an annotated pandas dataframe.

        Returns
        -------
        N: pandas.DataFrame
        """
        return pd.DataFrame(
            self.get_stoichiometric_matrix(),
            index=self.compounds,
            columns=self.reactions,
        )

    ##########################################################################
    # Structural functions
    ##########################################################################

    def add_minimal_seed(self, compound_ids):
        """Add compounds that make up a minimal seed for the given organism.

        Parameters
        ----------
        compound_ids : Iterable(str)
        """
        for compound in compound_ids:
            self.minimal_seed.add(compound)

    def get_minimal_seed(self, carbon_source_id):
        """Get a minimal seed for most organisms.

        Parameters
        ----------
        carbon_source_id: str
            compound_id of the carbon source

        Returns
        -------
        minimal_medium: list(str)
        """
        if not bool(self.minimal_seed):
            raise ValueError(
                "No minimal seed defined for this database. You can define one with Model.add_minimal_seed"
            )
        else:
            seed = self.minimal_seed.copy()
            seed.add(carbon_source_id)
            return seed

    def reversibility_duplication(self):
        """Add additional reverse reactions for all reactions that are reversible.

        Useful for structural analyses as scope and gapfilling

        Adds the __rev__ tag to those reactions.
        """
        for reaction_id in self.get_reversible_reactions():
            rev_reaction = self.reactions[reaction_id].copy()
            rev_reaction.id += "__rev__"
            rev_reaction.reverse_stoichiometry()
            rev_reaction.reversible = False
            self.add_reaction(reaction=rev_reaction)
            self._duplicate_reactions.add(rev_reaction.id)

    def remove_reversibility_duplication(self):
        """Remove the additional reverse reactions introduced.

        by model.reversibility_duplication
        """
        for reaction_id in tuple(self._duplicate_reactions):
            if "__rev__" in reaction_id:
                self.remove_reaction(reaction_id=reaction_id)
                self._duplicate_reactions.remove(reaction_id)
        self._duplicate_reactions = set()

    def cofactor_duplication(self):
        """Add additional reactions for reactions carrying cofactor pairs.

        Adds a __cof__ tag for every reaction that contains one of the cofactor pairs in model.cofactor_pairs.

        Useful for structural analyses as scope and gapfilling
        """
        # Add all cofacor metabolites, if they are in the model
        for k, v in self.cofactor_pairs.items():
            if k in self.compounds:
                cof_cpd = self.compounds[k].copy()
                cof_cpd.id = cof_cpd.id + "__cof__"
                self.add_compound(compound=cof_cpd)

                pair_cpd = self.compounds[v].copy()
                pair_cpd.id = pair_cpd.id + "__cof__"
                self.add_compound(compound=pair_cpd)

        for reaction in tuple(self.reactions.values()):
            reaction_cofactors = []
            for cof, pair in self.cofactor_pairs.items():
                if cof in reaction.stoichiometries:
                    if pair in reaction.stoichiometries:
                        if reaction.stoichiometries[cof] == -reaction.stoichiometries[pair]:
                            reaction_cofactors.append((cof, pair))
            if len(reaction_cofactors) > 0:
                cofactor_reaction = self.reactions[reaction.id].copy()
                cofactor_reaction.id += "__cof__"
                for (cof, pair) in reaction_cofactors:
                    cofactor_reaction.replace_compound(old_compound=cof, new_compound=cof + "__cof__")
                    cofactor_reaction.replace_compound(old_compound=pair, new_compound=pair + "__cof__")
                self.add_reaction(reaction=cofactor_reaction)
                self._duplicate_reactions.add(cofactor_reaction.id)

    def remove_cofactor_duplication(self):
        """Remove the additional reverse reactions introduced by model.cofactor_duplication."""
        for reaction_id in tuple(self._duplicate_reactions):
            if "__cof__" in reaction_id:
                self.remove_reaction(reaction_id)
                self._duplicate_reactions.remove(reaction_id)
        # for i in tuple(self.compounds):
        #     if "__cof__" in i:
        #         del self.compounds[i]

    def breadth_first_search(
        self,
        start_compound_id,
        end_compound_id,
        max_iterations=50,
        ignored_reaction_ids=None,
        ignored_compound_ids=None,
    ):
        """Breadth-first search to find shortest path connecting two metabolites.

        Parameters
        ----------
        start_compound_id: str
        end_compound_id: str
        max_iterations: int
        ignored_reaction_ids: iterable(str)
        ignored_compound_ids: iterable(str)

        Returns
        -------
        metabolites: list(str)
        reactions: list(str)
        """
        return topological.metabolite_tree_search(
            model=self,
            start_compound_id=start_compound_id,
            end_compound_id=end_compound_id,
            max_iterations=max_iterations,
            ignored_reaction_ids=ignored_reaction_ids,
            ignored_compound_ids=ignored_compound_ids,
            search_type="breadth-first",
        )

    def depth_first_search(
        self,
        start_compound_id,
        end_compound_id,
        max_iterations=50,
        ignored_reaction_ids=None,
        ignored_compound_ids=None,
    ):
        """Depth-first search to find shortest path connecting two metabolites.

        Parameters
        ----------
        start_compound_id: str
        end_compound_id: str
        max_iterations: int
        ignored_reaction_ids: iterable(str)
        ignored_compound_ids: iterable(str)

        Returns
        -------
        metabolites: list(str)
        reactions: list(str)"""
        return topological.metabolite_tree_search(
            model=self,
            start_compound_id=start_compound_id,
            end_compound_id=end_compound_id,
            max_iterations=max_iterations,
            ignored_reaction_ids=ignored_reaction_ids,
            ignored_compound_ids=ignored_compound_ids,
            search_type="depth-first",
        )

    def scope(self, seed, include_weak_cofactors=False, return_lumped_results=True):
        """Run the scope algorithm for a single seed.

        Parameters
        ----------
        seed: iterable
        include_weak_cofactors: bool
            Whether to include the weak cofactor duplications in the seed
        return_lumped_results: bool
            Whether to return the results as two sets or two lists of multiple sets
            for each iteration

        Returns
        -------
        scope_reactions: set
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False
        scope_compounds: set
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False


        See Also
        --------
        model.multiple_scopes
        """
        return topological.scope(
            model=self,
            seed=seed,
            include_weak_cofactors=include_weak_cofactors,
            return_lumped_results=return_lumped_results,
        )

    def multiple_scopes(
        self,
        seeds,
        include_weak_cofactors=False,
        return_lumped_results=True,
        multiprocessing=False,
    ):
        """Run the scope algorithm for multiple seeds.

        Parameters
        ----------
        seeds: iterable(iterable)
        include_weak_cofactors: bool
            Whether to include the weak cofactor duplications in the seed
        return_lumped_results: bool
            Whether to return the results as two sets or two lists of multiple sets
            for each iteration

        Returns
        -------
        scope_reactions: set
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False
        scope_compounds: set
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False


        See Also
        --------
        model.scope
        """
        return topological.multiple_scopes(
            model=self,
            seeds=seeds,
            include_weak_cofactors=include_weak_cofactors,
            return_lumped_results=return_lumped_results,
            multiprocessing=multiprocessing,
        )

    def get_gapfilling_reactions(
        self,
        reference_model,
        seed,
        targets,
        include_weak_cofactors=False,
        verbose=False,
    ):
        """Run the gapfilling algorithm.

        To find reactions out of a reference model
        necessary to produce all given targets from a given seed

        Parameters
        ----------
        reference_model: moped.Model
        seed: iterable(str)
            Seed compound ids
        targets: iterable(str)
            Target compound ids
        include_weak_cofactors: bool
            Whether to inlcude th weak cofactors into the seed

        Returns
        -------
        gapfilled_reactions: list(str)
            List of reaction ids which are necessary to produce all targets
        """
        return topological.gapfilling(
            model=self,
            reference_model=reference_model,
            seed=seed,
            targets=targets,
            include_weak_cofactors=include_weak_cofactors,
            verbose=verbose,
        )

    def gapfilling(
        self,
        reference_model,
        seed,
        targets,
        include_weak_cofactors=False,
        verbose=False,
    ):
        """Run the gapfilling algorithm and add the results to the model.

        To find reactions out of a reference model
        necessary to produce all given targets from a given seed

        Parameters
        ----------
        reference_model: moped.Model
        seed: iterable(str)
            Seed compound ids
        targets: iterable(str)
            Target compound ids
        include_weak_cofactors: bool
            Whether to inlcude th weak cofactors into the seed

        Returns
        -------
        gapfilled_reactions: list(str)
            List of reaction ids which are necessary to produce all targets
        """
        gapfilling_reactions = self.get_gapfilling_reactions(
            reference_model=reference_model,
            seed=seed,
            targets=targets,
            include_weak_cofactors=include_weak_cofactors,
            verbose=verbose,
        )
        if verbose:
            print(f"Adding reactions {gapfilling_reactions}")
        self.add_reactions_from_reference(
            reference_model=reference_model,
            reaction_ids=gapfilling_reactions,
            update_compounds=True,
        )

    ##########################################################################
    # Export functions
    ##########################################################################

    def to_cobra(self):
        """Export the model into a cobra model to do FBA topological.

        Returns
        -------
        cobra_model: cobra.Model
        """
        model = cobra.Model(self.name)
        model.compartments = {v: k for k, v in self.compartments.items()}
        model.add_metabolites(
            [
                cobra.Metabolite(
                    id=cpd.id,
                    formula=cpd.formula_to_string(),
                    charge=cpd.charge,
                    compartment=self.compartments[cpd.compartment],
                )
                for cpd in self.compounds.values()
            ]
        )

        for rxn in self.reactions.values():
            c_rxn = cobra.Reaction(id=rxn.id)
            model.add_reaction(c_rxn)
            c_rxn.bounds = rxn.bounds if rxn.bounds else (0, 1000)
            c_rxn.add_metabolites(rxn.stoichiometries)

        if self.objective is not None:
            model.objective = {model.reactions.get_by_id(k): v for k, v in self.objective.items()}
        return model

    ##########################################################################
    # Cobra interface
    ##########################################################################

    def get_influx_reactions(self, cobra_solution, sort_result=False):
        """Get influxes from a cobra simulation.

        Parameters
        ----------
        cobra_solution
        sort_result : bool
            Whether to sort the results ascendingly

        Returns
        -------
        influx_reactions: pandas.DataFrame
        """
        exchange_reactions = {i for i in self.reactions if i.startswith("EX_")}
        exchange_fluxes = cobra_solution.to_frame().loc[exchange_reactions, "fluxes"]
        result = exchange_fluxes[exchange_fluxes > 0]
        if sort_result:
            return result.sort_values(ascending=False)
        return result

    def get_efflux_reactions(self, cobra_solution, sort_result=False):
        """Get effluxes from a cobra simulation.

        Parameters
        ----------
        cobra_solution
        sort_result : bool
            Whether to sort the results ascendingly

        Returns
        -------
        influx_reactions: pandas.DataFrame
        """
        exchange_reactions = {i for i in self.reactions if i.startswith("EX_")}
        exchange_fluxes = cobra_solution.to_frame().loc[exchange_reactions, "fluxes"]
        result = exchange_fluxes[exchange_fluxes < 0]
        if sort_result:
            return result.sort_values(ascending=True)
        return result

    def get_producing_reactions(self, cobra_solution, compound_id, cutoff=0):
        """Get reactions that produce the compound in the cobra simulation.

        Parameters
        ----------
        cobra_model: cobra.Model
        compound_id: str
        cutoff: num

        Returns
        -------
        reactions: dict(str: float)
            Dictionary mapping the reation_id to the respective simulation flux
        """
        producing = {}
        for reaction_id in self.compounds[compound_id].in_reaction:
            flux = cobra_solution[reaction_id] * self.reactions[reaction_id].stoichiometries[compound_id]
            if flux > cutoff:
                producing[reaction_id] = flux
        return producing

    def get_consuming_reactions(self, cobra_solution, compound_id, cutoff=0):
        """Get reactions that consume the compound in the cobra simulation.

        Parameters
        ----------
        cobra_model: cobra.Model
        compound_id: str
        cutoff: num

        Returns
        -------
        reactions: dict(str: float)
            Dictionary mapping the reation_id to the respective simulation flux
        """
        consuming = {}
        for reaction_id in self.compounds[compound_id].in_reaction:
            flux = -cobra_solution[reaction_id] * self.reactions[reaction_id].stoichiometries[compound_id]
            if flux > cutoff:
                consuming[reaction_id] = flux
        return consuming

    ##########################################################################
    # modelbase interface
    ##########################################################################

    @staticmethod
    def _add_modelbase_influx_reaction(mod, rxn_id, metabolite, ratelaw="constant", suffix=None):
        if ratelaw == "constant":
            k_in = f"k_in_{rxn_id}"
            mod.add_parameters({k_in: 1})
            if suffix is not None:
                rxn_id += f"_{suffix}"
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id, ratelaw=rl.Constant(product=metabolite[0], k=k_in)
            )
        else:
            raise NotImplementedError

    @staticmethod
    def _add_modelbase_efflux_reaction(mod, rxn_id, metabolite, ratelaw="mass-action", suffix=None):
        if ratelaw == "mass-action":
            k_out = f"k_out_{rxn_id}"
            mod.add_parameters({k_out: 1})
            if suffix is not None:
                rxn_id += f"_{suffix}"
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.MassAction(substrates=metabolite, products=[], k_fwd=k_out),
            )
        else:
            raise NotImplementedError

    def _add_modelbase_medium_reaction(
        self,
        mod,
        rxn_id,
        metabolite,
        influx_ratelaw="constant",
        efflux_ratelaw="mass-action",
    ):
        self._add_modelbase_influx_reaction(
            mod=mod,
            rxn_id=rxn_id,
            metabolite=metabolite,
            ratelaw=influx_ratelaw,
            suffix="in",
        )
        self._add_modelbase_efflux_reaction(
            mod=mod,
            rxn_id=rxn_id,
            metabolite=metabolite,
            ratelaw=efflux_ratelaw,
            suffix="out",
        )

    @staticmethod
    def _add_modelbase_irreversible_reaction(mod, rxn_id, substrates, products, ratelaw="mass-action"):
        if ratelaw == "mass-action":
            k_fwd = f"k_{rxn_id}"
            mod.add_parameters({k_fwd: 1})
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.MassAction(substrates=substrates, products=products, k_fwd=k_fwd),
            )
        else:
            raise NotImplementedError

    @staticmethod
    def _add_modelbase_reversible_reaction(mod, rxn_id, substrates, products, ratelaw="mass-action"):
        if ratelaw == "mass-action":
            k_fwd = f"kf_{rxn_id}"
            k_bwd = f"kr_{rxn_id}"
            mod.add_parameters({k_fwd: 1, k_bwd: 1})
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.ReversibleMassAction(
                    substrates=substrates, products=products, k_fwd=k_fwd, k_bwd=k_bwd
                ),
            )
        else:
            raise NotImplementedError

    @staticmethod
    def _stoich_dict_to_list(stoich_dict, reaction):
        stoich_list = []
        for cpd, stoich in stoich_dict.items():
            if not stoich == int(stoich):
                warnings.warn(f"Check stoichiometries for reaction {reaction}, possible integer rounddown.")
            stoich_list.extend([cpd] * max(int(abs(stoich)), 1))
        return stoich_list

    def to_kinetic_model(
        self,
        reaction_ratelaw="mass-action",
        influx_ratelaw="constant",
        efflux_ratelaw="mass-action",
    ):
        """Convert the model into a kinetic modelbase model.

        Parameters
        ----------
        reaction_ratelaw: str
        influx_ratelaw: str
        efflux_ratelaw: str

        Returns
        -------
        modelbase.ode.Model
        """
        mod = ode.Model()
        mod.add_compounds(sorted(self.compounds))

        for reaction in sorted(self.reactions.values()):
            rxn_id = reaction.id
            substrates, products = reaction._split_stoichiometries()
            substrates = self._stoich_dict_to_list(substrates, reaction=rxn_id)
            products = self._stoich_dict_to_list(products, reaction=rxn_id)

            if len(reaction.stoichiometries) == 1:
                if reaction.reversible:
                    self._add_modelbase_medium_reaction(
                        mod=mod,
                        rxn_id=rxn_id,
                        metabolite=substrates,
                        influx_ratelaw=influx_ratelaw,
                        efflux_ratelaw=efflux_ratelaw,
                    )
                else:
                    if reaction.bounds[0] < 0:
                        self._add_modelbase_influx_reaction(
                            mod=mod,
                            rxn_id=rxn_id,
                            metabolite=substrates,
                            ratelaw=influx_ratelaw,
                        )
                    else:
                        self._add_modelbase_efflux_reaction(
                            mod=mod,
                            rxn_id=rxn_id,
                            metabolite=substrates,
                            ratelaw=efflux_ratelaw,
                        )
            else:
                if reaction.reversible:
                    self._add_modelbase_reversible_reaction(
                        mod=mod,
                        rxn_id=rxn_id,
                        substrates=substrates,
                        products=products,
                        ratelaw=reaction_ratelaw,
                    )
                else:
                    self._add_modelbase_irreversible_reaction(
                        mod=mod,
                        rxn_id=rxn_id,
                        substrates=substrates,
                        products=products,
                        ratelaw=reaction_ratelaw,
                    )
        return mod

    def to_kinetic_model_source_code(
        self,
        reaction_ratelaw="mass-action",
        influx_ratelaw="constant",
        efflux_ratelaw="mass-action",
    ):
        """Convert the model into modelbase model soure code.

        Parameters
        ----------
        reaction_ratelaw: str
        influx_ratelaw: str
        efflux_ratelaw: str

        Returns
        -------
        model_source: str
        """
        mod = self.to_kinetic_model(
            reaction_ratelaw=reaction_ratelaw,
            influx_ratelaw=influx_ratelaw,
            efflux_ratelaw=efflux_ratelaw,
        )
        return mod.generate_model_source_code()

    ##########################################################################
    # SBML interface
    ##########################################################################

    def to_sbml(self, filename="model.sbml"):
        """Export the model to sbml.

        Parameters
        ----------
        filename : str
        """
        cobra_model = self.to_cobra()
        for metabolite in cobra_model.metabolites:
            metabolite.charge = int(metabolite.charge)
        cobra.io.write_sbml_model(cobra_model=cobra_model, filename=filename)

    ##########################################################################
    # Blast interface
    ##########################################################################

    def get_monomer_sequences(self, reaction_ids):
        """Get all monomer sequences from the given reaction_ids.

        Parameters
        ----------
        reaction_ids: iterable(str)

        Returns
        -------
        sequences: set
            Sequences
        """
        sequences = set()
        for reaction_id in reaction_ids:
            reaction = self.reactions[reaction_id]
            for name, sequence in reaction.sequences.items():
                sequences.add(f">gnl|META|{name}\n{sequence}")
        return sequences

    def get_all_monomer_sequences(self):
        """Get all monomer sequences for all Model reactions.

        Returns
        -------
        sequences: set
            Sequences
        """
        sequences = set()
        for reaction in self.reactions.values():
            for name, sequence in reaction.sequences.items():
                sequences.add(f">gnl|META|{name}\n{sequence}")
        return sequences

    def blast_sequences(self, sequences, genome_file):
        """Blast all given sequences against a given nucleotide genome.

        Parameters
        ----------
        genome_file: str or pathlib.Path
            A nucleotide fasta file containing the genome of the organism

        Returns
        -------
        blast_monomers: pandas.DataFrame
            Results of the blast algorithm
        """
        genome_file = pathlib.Path(genome_file)
        if not genome_file.is_file():
            raise FileNotFoundError(f"genome_file '{genome_file}' does not exist.")
        return topological.blast(sequences=sequences, genome_file=genome_file)

    def blast_reactions(self, reaction_ids, genome_file):
        """Blast all given reactions against a given nucleotide genome.

        Parameters
        ----------
        genome_file: str or pathlib.Path
            A nucleotide fasta file containing the genome of the organism

        Returns
        -------
        blast_monomers: pandas.DataFrame
            Results of the blast algorithm
        """
        sequences = self.get_monomer_sequences(reaction_ids=reaction_ids)
        return self.blast_sequences(sequences=sequences, genome_file=genome_file)

    def blast_all_reactions(self, genome_file):
        """Blast all reactions of the model against a given nucleotide genome.

        Parameters
        ----------
        genome_file: str or pathlib.Path
            A nucleotide fasta file containing the genome of the organism

        Returns
        -------
        blast_monomers: pandas.DataFrame
            Results of the blast algorithm
        """
        sequences = self.get_all_monomer_sequences()
        return self.blast_sequences(sequences=sequences, genome_file=genome_file)

    def _get_reactions_from_blast_results(self, filtered_blast_monomers, require_all_complex_monomers):
        """Get all model reactions from the filtered_blast_monomers.

        Parameters
        ----------
        filtered_blast_monomers: set
            Ids of the filtered blast monomers
        require_all_complex_monomers: bool
            Whether to require, that all monomers of an enzyme reaction
            have to be found in order for that reaction to be encluded
            in the new model

        Returns
        -------
        blast_reactions: set
            All the reaction_ids of the reactions that were found.
        """
        if require_all_complex_monomers:
            blast_reactions = set()
            for reaction in self.reactions.values():
                for monomers in reaction.monomers.values():
                    if monomers.issubset(filtered_blast_monomers):
                        blast_reactions.add(reaction.id)
            return blast_reactions
        else:
            blast_reactions = set()
            for monomer in filtered_blast_monomers:
                for reaction in self._monomers[monomer]:
                    blast_reactions.add(reaction)
            return blast_reactions

    def create_submodel_from_blast_monomers(
        self,
        blast_monomers,
        name=None,
        max_evalue=1e-6,
        min_coverage=85,
        min_pident=85,
        require_all_complex_monomers=True,
        prefix_remove=r"gnl\|.*?\|",
        suffix_remove=None,
    ):
        """Create a submodel from given blast results.

        This reads in blast monomers as obtained by blast_sequences
        or blast_reactions and filters them according to the
        given quality criteria.

        Parameters
        ----------
        blast_monomers: pandas.DataFrame
            See blast_sequences
        name: str
        max_evalue: float
            Upper boundary for accepted Expect value
        min_coverage: float
            Lower boundary for accepted Query Coverage Per Subject
        min_pident: float
            Lower boundary for accepted Percentage of identical matches
        prefix_remove: raw_string
            Regular expression for a prefix to be removed ('^' is added automatically)
        suffix_remove: raw_string
            Regular expression for a suffix to be removed ('$' is added automatically)

        For a deeper explanation of the quality criteria
        (evalue, converage and pident) please consult the NCBI blast manual.

        Returns
        -------
        submodel: moped.Model
        """
        blast_monomers = topological.filter_blast_results(
            blast_monomers=blast_monomers,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
        )
        blast_reactions = self._get_reactions_from_blast_results(
            filtered_blast_monomers=blast_monomers,
            require_all_complex_monomers=require_all_complex_monomers,
        )
        return self.create_submodel(reaction_ids=blast_reactions, name=name)

    def create_submodel_from_sequences(
        self,
        sequences,
        genome_file,
        name=None,
        max_evalue=1e-6,
        min_coverage=85,
        min_pident=85,
        require_all_complex_monomers=True,
        prefix_remove=r"gnl\|.*?\|",
        suffix_remove=None,
        cache_blast_results=False,
    ):
        """Create a submodel from given protein monomer sequences and a nucleotide genome.

        This blasts all given protein monomer sequences against
        the nucleotide database and then checks which reactions
        can be found in that genome. The subset that can be found
        will be returned as a new model.

        Parameters
        ----------
        sequences: iterable(str)
        genome_file: str or pathlib.Path
            A nucleotide fasta file containing the genome of the organism
        max_evalue: float
            Upper boundary for accepted Expect value
        min_coverage: float
            Lower boundary for accepted Query Coverage Per Subject
        min_pident: float
            Lower boundary for accepted Percentage of identical matches
        prefix_remove: raw_string
            Regular expression for a prefix to be removed ('^' is added automatically)
        suffix_remove: raw_string
            Regular expression for a suffix to be removed ('$' is added automatically)

        For a deeper explanation of the quality criteria
        (evalue, converage and pident) please consult the NCBI blast manual.

        Returns
        -------
        submodel: moped.Model
        """
        if cache_blast_results:
            if name is None:
                raise ValueError("Name has to be given in order to cache results")
            blast_file = get_temporary_directory(subdirectory="blast") / f"blast_monomers_{name}.csv"
            if blast_file.is_file():
                blast_monomers = pd.read_csv(blast_file, index_col=0)
            else:
                blast_monomers = self.blast_sequences(sequences=sequences, genome_file=genome_file)
                blast_monomers.to_csv(blast_file)
        else:
            blast_monomers = self.blast_sequences(sequences=sequences, genome_file=genome_file)
        return self.create_submodel_from_blast_monomers(
            blast_monomers=blast_monomers,
            name=name,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            require_all_complex_monomers=require_all_complex_monomers,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
        )

    def create_submodel_from_genome(
        self,
        genome_file,
        name=None,
        max_evalue=1e-6,
        min_coverage=85,
        min_pident=85,
        require_all_complex_monomers=True,
        prefix_remove=r"gnl\|.*?\|",
        suffix_remove=None,
        cache_blast_results=False,
    ):
        """Create a submodel from a given nucleotide genome.

        This blasts all protein monomers of the model against
        the nucleotide database and then checks which reactions
        can be found in that genome. The subset that can be found
        will be returned as a new model.

        Parameters
        ----------
        genome_file: str or pathlib.Path
            A nucleotide fasta file containing the genome of the organism
        max_evalue: float
            Upper boundary for accepted Expect value
        min_coverage: float
            Lower boundary for accepted Query Coverage Per Subject
        min_pident: float
            Lower boundary for accepted Percentage of identical matches
        prefix_remove: raw_string
            Regular expression for a prefix to be removed ('^' is added automatically)
        suffix_remove: raw_string
            Regular expression for a suffix to be removed ('$' is added automatically)

        For a deeper explanation of the quality criteria
        (evalue, converage and pident) please consult the NCBI blast manual.

        Returns
        -------
        submodel: moped.Model
        """
        sequences = self.get_all_monomer_sequences()
        return self.create_submodel_from_sequences(
            sequences=sequences,
            genome_file=genome_file,
            name=name,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            require_all_complex_monomers=require_all_complex_monomers,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
            cache_blast_results=cache_blast_results,
        )
