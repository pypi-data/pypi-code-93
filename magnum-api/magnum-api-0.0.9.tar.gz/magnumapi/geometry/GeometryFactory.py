from enum import Enum, auto
from typing import List, Dict
import json

import pandas as pd

from magnumapi.geometry.CosThetaBlock import AbsoluteCosThetaBlock, RelativeCosThetaBlock
from magnumapi.geometry.CosThetaGeometry import RelativeCosThetaGeometry
from magnumapi.geometry.Geometry import Geometry
from magnumapi.geometry.RectangularBlock import RectangularBlock
from magnumapi.geometry.roxie.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.geometry.roxie.RectangularBlockDefinition import RectangularBlockDefinition
from magnumapi.geometry.roxie.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.geometry.roxie.CableDatabase import CableDatabase
import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI


class GeometryType(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()


class GeometryFactory:
    geometry_type_to_block = {1: AbsoluteCosThetaBlock,
                              2: RectangularBlock}

    geometry_type_to_block_definition = {1: AbsoluteCosThetaBlockDefinition,
                                         2: RectangularBlockDefinition}

    @classmethod
    def init_with_json(cls, json_file_path: str, cadata: CableDatabase):
        lst_dct = cls.read_json_file(json_file_path)
        return cls.init_with_dict(lst_dct, cadata)

    @staticmethod
    def read_json_file(json_file_path: str) -> List[dict]:
        with open(json_file_path) as f:
            lst_dct = json.load(f)
        return lst_dct

    @classmethod
    def init_with_dict(cls, lst_dct: List[Dict], cadata: CableDatabase):
        geom_type = cls.retrieve_geometry_type_dict(lst_dct)

        if geom_type == GeometryType.ABSOLUTE:
            return cls.init_absolute_with_dict(lst_dct, cadata)

        if geom_type == GeometryType.RELATIVE:
            return cls.init_relative_with_dict(lst_dct, cadata)

    @staticmethod
    def retrieve_geometry_type_dict(lst_dct: List[Dict]):
        if all(['alpha_r' in dct.keys() for dct in lst_dct]):
            return GeometryType.RELATIVE
        elif any(['alpha_r' in dct.keys() for dct in lst_dct]):
            raise AttributeError(
                'Error, inconsistent geometry definition. '
                'The geometry definition should consist of either all relative definitions or none.')
        else:
            return GeometryType.ABSOLUTE

    @staticmethod
    def init_absolute_with_dict(dct, cadata: CableDatabase):
        blocks = []
        for block_def in dct:
            BlockClass = GeometryFactory.geometry_type_to_block[block_def['type']]
            BlockDefinitionClass = GeometryFactory.geometry_type_to_block_definition[block_def['type']]
            block_abs = BlockDefinitionClass(**block_def)
            block = BlockClass(block_def=block_abs,
                               cable_def=cadata.get_cable_definition(block_abs.condname),
                               insul_def=cadata.get_insul_definition(block_abs.condname),
                               strand_def=cadata.get_strand_definition(block_abs.condname),
                               conductor_def=cadata.get_conductor_definition(block_abs.condname))

            blocks.append(block)

        return Geometry(blocks=blocks)

    @staticmethod
    def init_relative_with_dict(lst_dct, cadata: CableDatabase):
        blocks = []
        for dct in lst_dct:
            block_def = RelativeCosThetaBlockDefinition(**dct)
            block = RelativeCosThetaBlock(block_def=block_def,
                                          cable_def=cadata.get_cable_definition(block_def.condname),
                                          insul_def=cadata.get_insul_definition(block_def.condname),
                                          strand_def=cadata.get_strand_definition(block_def.condname),
                                          conductor_def=cadata.get_conductor_definition(block_def.condname))
            blocks.append(block)

        return RelativeCosThetaGeometry(blocks=blocks)

    @classmethod
    def init_with_data(cls, data_file_path: str, cadata: CableDatabase):
        block_df = RoxieAPI.read_bottom_header_table(data_file_path, keyword='BLOCK')
        return cls.init_with_df(block_df, cadata)

    @classmethod
    def init_with_csv(cls, csv_file_path: str, cadata: CableDatabase):
        block_df = pd.read_csv(csv_file_path, index_col=0)
        return cls.init_with_df(block_df, cadata)

    @classmethod
    def init_with_df(cls, block_df: pd.DataFrame, cadata: CableDatabase):
        geom_type = cls.retrieve_geometry_type_df(block_df)
        if geom_type == GeometryType.ABSOLUTE:
            return cls.init_absolute_with_df(block_df, cadata)

        if geom_type == GeometryType.RELATIVE:
            return cls.init_relative_with_df(block_df, cadata)

    @staticmethod
    def retrieve_geometry_type_df(block_df: pd.DataFrame) -> "GeometryType":
        if ('alpha_r' in block_df.columns) and ('phi_r' in block_df.columns):
            return GeometryType.RELATIVE
        elif ('alpha_r' in block_df.columns) or ('phi_r' in block_df.columns):
            raise AttributeError('Error, inconsistent geometry definition')
        else:
            return GeometryType.ABSOLUTE

    @staticmethod
    def init_absolute_with_df(block_df: pd.DataFrame, cadata: CableDatabase):
        blocks = []
        for _, row in block_df.iterrows():
            BlockClass = GeometryFactory.geometry_type_to_block[row['type']]
            BlockDefinitionClass = GeometryFactory.geometry_type_to_block_definition[row['type']]
            if row['type'] == 2:
                row = row.rename(BlockClass.roxie_to_magnum_dct)

            block_def = BlockDefinitionClass(**row.to_dict())
            block = BlockClass(block_def=block_def,
                               cable_def=cadata.get_cable_definition(block_def.condname),
                               insul_def=cadata.get_insul_definition(block_def.condname),
                               strand_def=cadata.get_strand_definition(block_def.condname),
                               conductor_def=cadata.get_conductor_definition(block_def.condname))

            blocks.append(block)

        return Geometry(blocks)

    @staticmethod
    def init_relative_with_df(block_df: pd.DataFrame, cadata: CableDatabase):
        blocks = []
        for row_dict in block_df.to_dict('records'):
            block_rel = RelativeCosThetaBlockDefinition(**row_dict)

            block = RelativeCosThetaBlock(block_def=block_rel,
                                          cable_def=cadata.get_cable_definition(block_rel.condname),
                                          insul_def=cadata.get_insul_definition(block_rel.condname),
                                          strand_def=cadata.get_strand_definition(block_rel.condname),
                                          conductor_def=cadata.get_conductor_definition(block_rel.condname))

            blocks.append(block)

        return RelativeCosThetaGeometry(blocks=blocks)
