import pickle
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import geometry as shg

from lgblkb_tools import logger


class SpatialMan(object):
    def __init__(self, fields: gpd.GeoDataFrame):
        self.fields = fields
        self._assert_validity(fields)

    @staticmethod
    def _assert_validity(fields):
        if not isinstance(fields, gpd.GeoDataFrame):
            raise TypeError('Wrong type provided, expected gpd.GeoDataFrame',
                            dict(provided_type=str(type(fields))))
        if 'geometry' not in fields.columns:
            raise KeyError('Columns of fields should contain geometry column named "geometry".',
                           dict(existing_columns=list(fields.columns)))
        if fields.crs is None:
            raise ValueError('CRS for fields should be set.', dict(current_crs=str(fields.crs)))

    def geoseries_to_geodataframe(self, fields: gpd.GeoSeries, crs):
        self.fields = gpd.GeoDataFrame(fields, columns=['geometry'], crs=crs)
        return self

    @classmethod
    def get_random_fields(cls, bounding_geometry, crs, geoms_count, size_range=(0.01, 0.1)):
        from lgblkb_tools.geometry import FieldPoly
        geom_fm = cls.from_geoms([bounding_geometry], crs)
        area = geom_fm.area[0]
        radius = np.sqrt(area / np.pi)
        geom = geom_fm.get_geoms()[0]
        product_poly = FieldPoly(geom)
        points = product_poly.get_subparcel_centers(area / geoms_count)
        geoms = [shg.Point(*xy).buffer(
            np.random.randint(radius * size_range[0], radius * size_range[1])) for xy in points]
        fm = cls.from_geoms(geoms, crs)
        fm.fields = fm.fields.reset_index().rename(columns=dict(index='id'))
        return fm

    @classmethod
    def from_pickle(cls, pickle_path):
        fields = pickle.load(open(pickle_path, 'rb'))
        return cls(fields)

    @classmethod
    def from_geoms(cls, geoms, crs):
        return cls(gpd.GeoDataFrame(geoms, crs=crs, columns=['geometry']))

    @classmethod
    def from_combine(cls, multiple_fields):
        if not multiple_fields:
            logger.warning('fields are empty. Nothing to concatenate.')
            fields = gpd.GeoDataFrame(columns=['geometry'], crs='epsg:3857')
            return cls(fields)
        crs = multiple_fields[0].crs
        if crs is None:
            raise ValueError('Provided field crs is None.', dict(input_field=str(multiple_fields[0])))
        for i, field in enumerate(multiple_fields):
            if field.empty: continue
            cls._assert_validity(field)
            if field.crs != crs:
                raise ValueError('Provided fields have different CRS.',
                                 {'first crs': str(crs), f'{i}-th crs': str(field.crs)})
        concatenated = pd.concat(multiple_fields, ignore_index=True).drop_duplicates().reset_index(drop=True)
        if concatenated.empty:
            logger.warning('fields are empty. Nothing to concatenate.')
            fields = gpd.GeoDataFrame(columns=['geometry'], crs='epsg:3857')
            return cls(fields)
        else:
            fields = gpd.GeoDataFrame(concatenated, crs=crs)
            return cls(fields)

    @logger.trace()
    def buffer(self, distance, join_style=2, **kwargs):
        self.fields = self.fields.buffer(distance, join_style=join_style, **kwargs)
        return self

    def get_geoms(self, exploded=True):
        if exploded:
            return self.fields.explode().reset_index(drop=True).geometry
        else:
            return self.fields.geometry

    @logger.trace()
    def to_crs(self, crs):
        input_crs = self.fields.crs
        logger.debug("input_crs: %s", input_crs)
        self.fields.to_crs(crs, inplace=True)
        output_crs = self.fields.crs
        logger.debug("output_crs: %s", output_crs)
        return self

    def to_geojson(self, out_filepath, na="null", show_bbox=False, lazy=False, **kwargs):
        if lazy and Path(out_filepath).exists():
            return out_filepath
        json_str = self.fields.to_json(na=na, show_bbox=show_bbox, **kwargs)
        with open(out_filepath, 'w') as file:
            file.write(json_str)
        return out_filepath


    @property
    def area(self):
        crs = '+proj=eck4 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m no_defs'
        return self.fields.geometry.to_crs(crs).area
