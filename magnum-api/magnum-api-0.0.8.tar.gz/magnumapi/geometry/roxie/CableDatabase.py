import json
from typing import List

import pandas as pd

from magnumapi.geometry.roxie.CableDefinition import CableDefinition
from magnumapi.geometry.roxie.ConductorDefinition import ConductorDefinition
from magnumapi.geometry.roxie.Definition import Definition
from magnumapi.geometry.roxie.FilamentDefinition import FilamentDefinition
from magnumapi.geometry.roxie.InsulationDefinition import InsulationDefinition
from magnumapi.geometry.roxie.QuenchDefinition import QuenchDefinition
from magnumapi.geometry.roxie.RemFitDefinition import RemFitDefinition
from magnumapi.geometry.roxie.StrandDefinition import StrandDefinition
from magnumapi.geometry.roxie.TransientDefinition import TransientDefinition
import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI
from magnumapi.tool_adapters.DirectoryManager import DirectoryManager


class CableDatabase:
    keyword_to_class = {'INSUL': InsulationDefinition,
                        'REMFIT': RemFitDefinition,
                        'FILAMENT': FilamentDefinition,
                        'STRAND': StrandDefinition,
                        'TRANSIENT': TransientDefinition,
                        'QUENCH': QuenchDefinition,
                        'CABLE': CableDefinition,
                        'CONDUCTOR': ConductorDefinition}

    def __init__(self,
                 insul_defs: List[InsulationDefinition],
                 remfit_defs: List[RemFitDefinition],
                 filament_defs: List[FilamentDefinition],
                 strand_defs: List[StrandDefinition],
                 transient_defs: List[TransientDefinition],
                 quench_defs: List[QuenchDefinition],
                 cable_defs: List[CableDefinition],
                 conductor_defs: List[ConductorDefinition]):

        self.insul_defs = insul_defs
        self.remfit_defs = remfit_defs
        self.filament_defs = filament_defs
        self.strand_defs = strand_defs
        self.transient_defs = transient_defs
        self.quench_defs = quench_defs
        self.cable_defs = cable_defs
        self.conductor_defs = conductor_defs

    @classmethod
    def initialize_definitions(cls, cadata_file_path: str, keyword: str) -> List[Definition]:
        ClassDefinition = cls.keyword_to_class[keyword.upper()]
        try:
            df = RoxieAPI.read_bottom_header_table(cadata_file_path, keyword=keyword)
            df = df.drop(columns=['No'])
            df = df.rename(columns=ClassDefinition.get_roxie_to_magnum_dct())
            df_dicts = df.to_dict('records')
            defs = []
            for df_dict in df_dicts:
                defs.append(ClassDefinition(**df_dict))

            return defs
        except IndexError:
            return [ClassDefinition(name='', comment='')]

    def get_insul_definition(self, condname) -> InsulationDefinition:
        insul_name = self.get_conductor_definition(condname).insulation

        return _find_matching_definition(self.insul_defs, insul_name, 'insulation')

    def get_remfit_definition(self, condname) -> RemFitDefinition:
        remfit_name = self.get_filament_definition(condname).fit_perp

        return _find_matching_definition(self.remfit_defs, remfit_name, 'rem_fit')

    def get_filament_definition(self, condname) -> FilamentDefinition:
        filament_name = self.get_conductor_definition(condname).filament

        return _find_matching_definition(self.filament_defs, filament_name, 'filament')

    def get_strand_definition(self, condname) -> StrandDefinition:
        strand_name = self.get_conductor_definition(condname).strand

        return _find_matching_definition(self.strand_defs, strand_name, 'strand')

    def get_transient_definition(self, condname) -> TransientDefinition:
        trans_name = self.get_conductor_definition(condname).transient

        if trans_name == 'NONE':
            return TransientDefinition(name='', comment='')

        return _find_matching_definition(self.transient_defs, trans_name, 'transient')

    def get_quench_definition(self, condname) -> QuenchDefinition:
        quench_name = self.get_conductor_definition(condname).quench_mat

        if quench_name == 'NONE':
            return QuenchDefinition(name='', comment='')

        return _find_matching_definition(self.quench_defs, quench_name, 'quench')

    def get_cable_definition(self, condname) -> CableDefinition:
        geometry_name = self.get_conductor_definition(condname).cable_geom

        return _find_matching_definition(self.cable_defs, geometry_name, 'cable')

    def get_conductor_definition(self, condname) -> ConductorDefinition:
        return _find_matching_definition(self.conductor_defs, condname, 'conductor')

    @classmethod
    def read_json(cls, json_file_path: str) -> "CableDatabase":
        with open(json_file_path) as json_file:
            data = json.load(json_file)

        # Optional definitions
        if 'remfit' in data:
            remfit_defs = [RemFitDefinition(**remfit_def) for remfit_def in data['remfit']]
        else:
            remfit_defs = [RemFitDefinition(name='', comment='')]

        if 'transient' in data:
            transient_defs = [TransientDefinition(**transient_def) for transient_def in data['transient']]
        else:
            transient_defs = [TransientDefinition(name='', comment='')]

        if 'quench' in data:
            quench_defs = [QuenchDefinition(**quench_def) for quench_def in data['quench']]
        else:
            quench_defs = [QuenchDefinition(name='', comment='')]

        # Mandatory definitions
        insul_defs = [InsulationDefinition(**insulation_def) for insulation_def in data['insulation']]
        filament_defs = [FilamentDefinition(**filament_def) for filament_def in data['filament']]
        strand_defs = [StrandDefinition(**strand_def) for strand_def in data['strand']]
        cable_defs = [CableDefinition(**cable_def) for cable_def in data['cable']]
        conductor_defs = [ConductorDefinition(**conductor_def) for conductor_def in data['conductor']]

        return CableDatabase(insul_defs=insul_defs,
                             remfit_defs=remfit_defs,
                             filament_defs=filament_defs,
                             strand_defs=strand_defs,
                             transient_defs=transient_defs,
                             quench_defs=quench_defs,
                             cable_defs=cable_defs,
                             conductor_defs=conductor_defs)

    def write_json(self, json_output_path: str) -> None:

        json_cadata = {"insulation": self._get_insulation_definitions_as_list_of_dict(),
                       "remfit": self._get_remfit_definitions_as_list_of_dict(),
                       "filament": self._get_filament_definitions_as_list_of_dict(),
                       "strand": self._get_strand_definitions_as_list_of_dict(),
                       "transient": self._get_transient_definitions_as_list_of_dict(),
                       "quench": self._get_quench_definitions_as_list_of_dict(),
                       "cable": self._get_cable_definitions_as_list_of_dict(),
                       "conductor": self._get_conductor_definitions_as_list_of_dict()}

        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(json_cadata, f, ensure_ascii=False, indent=4)

    def _get_conductor_definitions_as_list_of_dict(self):
        return [ConductorDefinition.reorder_dct(conductor_def.__dict__) for conductor_def in self.conductor_defs]

    def _get_cable_definitions_as_list_of_dict(self):
        return [CableDefinition.reorder_dct(cable_def.__dict__) for cable_def in self.cable_defs]

    def _get_quench_definitions_as_list_of_dict(self):
        return [QuenchDefinition.reorder_dct(quench_def.__dict__) for quench_def in self.quench_defs]

    def _get_transient_definitions_as_list_of_dict(self):
        return [TransientDefinition.reorder_dct(transient_def.__dict__) for transient_def in self.transient_defs]

    def _get_strand_definitions_as_list_of_dict(self):
        return [StrandDefinition.reorder_dct(strand_def.__dict__) for strand_def in self.strand_defs]

    def _get_filament_definitions_as_list_of_dict(self):
        return [FilamentDefinition.reorder_dct(filament_def.__dict__) for filament_def in self.filament_defs]

    def _get_remfit_definitions_as_list_of_dict(self):
        return [RemFitDefinition.reorder_dct(remfit_def.__dict__) for remfit_def in self.remfit_defs]

    def _get_insulation_definitions_as_list_of_dict(self):
        return [InsulationDefinition.reorder_dct(insul_def.__dict__) for insul_def in self.insul_defs]

    @classmethod
    def read_cadata(cls, cadata_file_path):
        DirectoryManager.check_if_file_exists(cadata_file_path)

        return CableDatabase(insul_defs=cls.initialize_definitions(cadata_file_path, keyword='INSUL'),
                             remfit_defs=cls.initialize_definitions(cadata_file_path, keyword='REMFIT'),
                             filament_defs=cls.initialize_definitions(cadata_file_path, keyword='FILAMENT'),
                             strand_defs=cls.initialize_definitions(cadata_file_path, keyword='STRAND'),
                             transient_defs=cls.initialize_definitions(cadata_file_path, keyword='TRANSIENT'),
                             quench_defs=cls.initialize_definitions(cadata_file_path, keyword='QUENCH'),
                             cable_defs=cls.initialize_definitions(cadata_file_path, keyword='CABLE'),
                             conductor_defs=cls.initialize_definitions(cadata_file_path, keyword='CONDUCTOR'))

    def write_cadata(self, cadata_output_path: str) -> None:
        output = ['VERSION 11',
                  self._convert_definitions_df_to_bottom_header_str(self.get_insul_df(), 'INSUL'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_remfit_df(), 'REMFIT'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_filament_df(), 'FILAMENT'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_strand_df(), 'STRAND'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_transient_df(), 'TRANSIENT'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_quench_df(), 'QUENCH'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_cable_df(), 'CABLE'),
                  self._convert_definitions_df_to_bottom_header_str(self.get_conductor_df(), 'CONDUCTOR')
                  ]

        # Write to a text file
        with open(cadata_output_path, 'w') as file_write:
            for output_el in output:
                file_write.write(output_el + '\n\n')

    @classmethod
    def _convert_definitions_df_to_bottom_header_str(cls, df: pd.DataFrame, keyword: str) -> str:
        # Get the definition class
        ClassDefinition = cls.keyword_to_class[keyword.upper()]
        # Convert to a dataframe
        df = df.rename(columns=ClassDefinition.get_magnum_to_roxie_dct())
        # Take only those columns that are needed for ROXIE
        df = df[ClassDefinition.get_roxie_to_magnum_dct().keys()]
        # Add apostrophes around comment column
        df['Comment'] = '\'' + df['Comment'] + '\''
        # Add No column (1-based)
        columns = df.columns
        df['No'] = df.index + 1
        df = df[['No'] + list(columns)]
        df = df.astype({'No': 'int32'})
        # Convert a dataframe to a bottom header table
        return RoxieAPI.convert_bottom_header_table_to_str(df, keyword=keyword)

    def get_insul_df(self):
        insulation_definitions = self._get_insulation_definitions_as_list_of_dict()
        return pd.DataFrame(insulation_definitions)

    def get_remfit_df(self):
        remfit_definitions = self._get_remfit_definitions_as_list_of_dict()
        return pd.DataFrame(remfit_definitions)

    def get_filament_df(self):
        filament_definitions = self._get_filament_definitions_as_list_of_dict()
        return pd.DataFrame(filament_definitions)

    def get_strand_df(self):
        strand_definitions = self._get_strand_definitions_as_list_of_dict()
        return pd.DataFrame(strand_definitions)

    def get_transient_df(self):
        transient_definitions = self._get_transient_definitions_as_list_of_dict()
        return pd.DataFrame(transient_definitions)

    def get_quench_df(self):
        quench_definitions = self._get_quench_definitions_as_list_of_dict()
        return pd.DataFrame(quench_definitions)

    def get_cable_df(self):
        cable_definitions = self._get_cable_definitions_as_list_of_dict()
        return pd.DataFrame(cable_definitions)

    def get_conductor_df(self):
        conductor_definitions = self._get_conductor_definitions_as_list_of_dict()
        return pd.DataFrame(conductor_definitions)


def _find_matching_definition(defs, name_def, desc_def):
    matches = list(filter(lambda x: x.name == name_def, defs))

    if matches:
        return matches[0]
    else:
        raise KeyError('%s name %s not present in %s definitions.' % (desc_def.capitalize(), name_def, desc_def))
