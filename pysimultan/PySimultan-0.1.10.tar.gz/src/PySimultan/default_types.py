from collections import UserList
from functools import lru_cache
import pandas as pd
import numpy as np
from weakref import WeakSet
import colorlog

from ParameterStructure.Instances import InstancePlacementGeometry
from .config import continue_on_error

from copy import copy
logger = colorlog.getLogger('PySimultan')


class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class SimultanObject(object):

    _cls_instances = WeakSet()  # weak set with all created objects
    _create_all = False     # if true all properties are evaluated to create python objects when initialized
    _cls_instances_dict_cache = None

    @classproperty
    def _cls_instances_dict(cls):
        if cls._cls_instances_dict_cache is None:
            cls._cls_instances_dict_cache = dict(zip([x.id for x in cls._cls_instances], [x() for x in cls._cls_instances]))
        return cls._cls_instances_dict_cache

    @classproperty
    def cls_instances(cls):
        return list(cls._cls_instances)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        if "_cls_instances" not in cls.__dict__:
            cls._cls_instances = WeakSet()
        try:
            cls._cls_instances.add(instance)
            cls._cls_instances_dict_cache = None
        except Exception as e:
            logger.error(f'Error adding instance {instance} to _cls_instances: {e}')

        return instance

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        self._contained_components = kwargs.get('contained_components', None)
        self._contained_parameters = kwargs.get('contained_parameters', None)
        self._flat_sub_comp_list = kwargs.get('flat_sub_comp_list', None)
        self._referenced_components = kwargs.get('referenced_components', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        if self._create_all:
            _ = self.contained_components
            _ = self.contained_parameters
            _ = self.referenced_components

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except KeyError:
            wrapped = object.__getattribute__(self, '_wrapped_obj')
            if wrapped is not None:
                return object.__getattribute__(wrapped, attr)
            else:
                raise KeyError

    def __setattr__(self, attr, value):
        if hasattr(self, '_wrapped_obj'):

            if hasattr(self._wrapped_obj, attr) and (self._wrapped_obj is not None):
                object.__setattr__(self._wrapped_obj, attr, value)
            else:
                object.__setattr__(self, attr, value)
        else:
            object.__setattr__(self, attr, value)

        # if (attr in self.__dict__) or (attr in ['_wrapped_obj',
        #                                         '_contained_components',
        #                                         '_contained_parameters',
        #                                         '_flat_sub_comp_list',
        #                                         '_referenced_components',
        #                                         '_template_parser',
        #                                         '_data_model_id']):
        #
        #     object.__setattr__(self, attr, value)
        # else:
        #     object.__setattr__(self._wrapped_obj, attr, value)

    @property
    def id(self):
        if self._wrapped_obj is not None:
            return self._wrapped_obj.ID

    @property
    def name(self):
        if self._wrapped_obj is not None:
            return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def contained_components(self):
        if self._contained_components is None:
            if self._wrapped_obj is not None:
                self._contained_components = [self._template_parser.create_python_object(x) for x in self._wrapped_obj.ContainedComponentsAsList]
        return self._contained_components

    @property
    def contained_parameters(self):
        if self._contained_parameters is None:
            if self._wrapped_obj is not None:
                self._contained_parameters = {x.Name: x.get_ValueCurrent() for x in self._wrapped_obj.ContainedParameters.Items}
        return self._contained_parameters

    @property
    def flat_sub_comp_list(self):
        if self._flat_sub_comp_list is None:
            if self._wrapped_obj is not None:
                self._flat_sub_comp_list = [self._template_parser.create_python_object(x) for x in self._wrapped_obj.GetFlatSubCompList()]
        return self._flat_sub_comp_list

    @property
    def referenced_components(self):
        if self._referenced_components is None:
            if self._wrapped_obj is not None:
                self._referenced_components = [self._template_parser.create_python_object(x) for x in self._wrapped_obj.ReferencedComponents.Items]
        return self._referenced_components

    def __repr__(self):
        return f'{self.name}: ' + object.__repr__(self)

    def __del__(self):
        self.__class__._cls_instances_dict_cache = None


class List(UserList):

    _create_all = False     # if true all properties are evaluated to create python objects when initialized

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        if self._wrapped_obj is not None:
            self.data = self._wrapped_obj.ContainedComponentsAsList
        self._contained_components = kwargs.get('contained_components', None)
        self._contained_parameters = kwargs.get('contained_parameters', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        if self._create_all:
            _ = self.contained_components
            _ = self.contained_parameters

    def __getitem__(self, i):
        if isinstance(i, slice):
            if self._template_parser is None:
                return self.__class__(self.data[i])
            return [self._template_parser.create_python_object(x) for x in self.__class__(self.data[i])]
        else:
            if self._template_parser is None:
                return self.data[i]
            return self._template_parser.create_python_object(self.data[i])

    def __repr__(self):
        return f'{self.name}: ' + repr(list(self.data))

    @property
    def contained_components(self):
        if self._contained_components is None:
            if self._wrapped_obj is not None:
                self._contained_components = [self._template_parser.create_python_object(x) for x in self._wrapped_obj.ContainedComponentsAsList]
        return self._contained_components

    @property
    def contained_parameters(self):
        if self._contained_parameters is None:
            if self._wrapped_obj is not None:
                self._contained_parameters = {x.Name: x.get_ValueCurrent() for x in self._wrapped_obj.ContainedParameters.Items}
        return self._contained_parameters

    @property
    def name(self):
        if self._wrapped_obj is not None:
            if hasattr(self._wrapped_obj, 'Name'):
                return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value


class ValueField(pd.DataFrame):

    _metadata = pd.DataFrame._metadata + ['_wrapped_obj', '_template_parser', '_data_model_id']

    def __init__(self, *args, **kwargs):

        # self._wrapped_obj = kwargs.get('wrapped_obj')
        self._wrapped_obj = kwargs.pop('wrapped_obj', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        row_headers = [x.Name for x in self._wrapped_obj.ValueField.RowHeaders.Items]
        column_headers = [x.Name for x in self._wrapped_obj.ValueField.ColumnHeaders.Items]
        values = self._wrapped_obj.ValueField.Values

        super().__init__(dict(zip(column_headers, np.array(values).T)),  index=row_headers)

    @property
    def base_class_view(self):
        # use this to view the base class, needed for debugging in some IDEs.
        return pd.DataFrame(self)


class BuildInFace(SimultanObject):

    def __init__(self, *args, **kwargs):
        SimultanObject.__init__(self, *args, **kwargs)

        self._geo_instances = kwargs.get('geo_instances', None)
        self._boundaries = kwargs.get('boundaries', None)

    @property
    def geo_ids(self):
        if self.geo_instances is not None:
            return [x.Id for x in self.geo_instances]

    @property
    def area(self):
        idx = next((i for i, x in enumerate(self._wrapped_obj.ContainedParameters.Items) if x.Name == 'A'), None)
        param = self._wrapped_obj.ContainedParameters.Items[idx]
        return param.get_ValueCurrent()

    @property
    def geo_ids(self):
        geo_ids = []
        for item in self._wrapped_obj.GeometryInstances.Items:

            geom_placement = next(x for x in item.Placements.Items if isinstance(x, InstancePlacementGeometry))

            file_id = geom_placement.FileId
            geometry_id = geom_placement.GeometryId

            geo_ids.append({'FileId': file_id,
                           'GeometryId': geometry_id})
        return geo_ids

    @property
    def geo_instances(self):
        if self._geo_instances is None:
            self._geo_instances = self.get_geo_instances()
        return self._geo_instances

    @geo_instances.setter
    def geo_instances(self, value):
        self._geo_instances = value

    @property
    def boundaries(self):
        if self._boundaries is None:
            if self.geo_instances is not None:
                self._boundaries = [x.boundary for x in self.geo_instances]
        return self._boundaries

    @property
    def construction(self):
        obj = next((x.Reference for x in self._wrapped_obj.ReferencedComponents.Items if x.ReferenceFunction.SlotFull == 'Aufbau_0AG0'), None)
        return self._template_parser.create_python_object(obj)

    def get_geo_instances(self):
        geo_instances = []

        for item in self._wrapped_obj.GeometryInstances.Items:

            geom_placement = next(x for x in item.Placements.Items if isinstance(x, InstancePlacementGeometry))

            file_id = geom_placement.FileId
            geometry_id = geom_placement.GeometryId

            # geo_model = self._template_parser.data_models[self._data_model_id].get_typed_model_by_file_id(file_id)
            geo_model = self._template_parser.typed_geo_models[file_id]
            geo_instance = geo_model.get_face_by_id(geometry_id)

            # geo_instance = self._template_parser.data_models[self._data_model_id].typed_geo_models[file_id].get_face_by_id(geometry_id)

            geo_instances.append(geo_instance)

        return geo_instances


class BuildInVolume(SimultanObject):

    def __init__(self, *args, **kwargs):
        """
        Grundflächen und Rauminhalte nach DIN 277
        :param args:
        :param kwargs:
        """
        SimultanObject.__init__(self, *args, **kwargs)

        self._geo_instances = kwargs.get('geo_instances', None)
        self._surfaces = kwargs.get('surfaces', None)
        self._volumes = kwargs.get('volumes', None)

    @property
    def volumes(self):
        return self.geo_instances

    @property
    def geo_faces(self):
        """
        Faces of the Geometry-Model
        :return: list with faces
        """
        faces = []
        try:
            [faces.extend(x.faces) for x in self.geo_instances if x is not None]
        except AttributeError as e:
            raise e
        return faces

    @property
    def face_components(self):
        return None

    @property
    def geo_instances(self):
        if self._geo_instances is None:
            self._geo_instances = self.get_geo_instances()
        return self._geo_instances

    @geo_instances.setter
    def geo_instances(self, value):
        self._geo_instances = value

    @property
    @lru_cache(maxsize=None)
    def v_a(self):
        return next((x.ValueCurrent for x in self._wrapped_obj.ContainedParameters.Items if x.Name == 'Vᴀ'), None)

    @property
    @lru_cache(maxsize=None)
    def v_nri(self):
        """
        Netto-Rauminhalt NRI: Anteil des Brutto-Rauminhalts (BRI), der das Volumen über der Netto-Raumfläche (NRF) umfasst; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.ContainedParameters.Items if x.Name == 'Vɴʀɪ'), None)

    @property
    @lru_cache(maxsize=None)
    def v_bri(self):
        """
        Brutto-Rauminhalt BRI: gesamtes Volumen eines Bauwerks oder eines Geschosses, das sich in Netto-Rauminhalt (NRI) und
        Konstruktions-Rauminhalt (KRI) gliedert; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.ContainedParameters.Items if x.Name == 'Vᴃʀɪ'), None)

    @property
    @lru_cache(maxsize=None)
    def a_bgf(self):
        """
        Brutto-Grundfläche; gesamte Grundfläche eines Bauwerks oder eines Geschosses, die sich in Netto-Raumfläche (NRF)
        und Konstruktions-Grundfläche (KGF) gliedert; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.ContainedParameters.Items if x.Name == 'Aᴃɢꜰ'), None)

    @property
    @lru_cache(maxsize=None)
    def a_ngf(self):
        """
        Netto-Grundfläche; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.ContainedParameters.Items if x.Name == 'Aɴɢꜰ'), None)

    def get_geo_instances(self):

        geo_instances = []

        for item in self._wrapped_obj.GeometryInstances.Items:

            try:
                geom_placement = next(x for x in item.Placements.Items if isinstance(x, InstancePlacementGeometry))
            except Exception as e:
                logger.error(f'{self.__class__.__name__} {self.name} {self.id}: Could not find Geometry Placement for GeometryInstance {item}')
                if continue_on_error:
                    continue
                else:
                    raise e

            file_id = geom_placement.FileId
            geometry_id = geom_placement.GeometryId

            # geo_model = self._template_parser.data_models[self._data_model_id].get_typed_model_by_file_id(file_id)
            geo_model = self._template_parser.typed_geo_models[file_id]
            geo_instance = geo_model.get_zone_by_id(geometry_id)

            if geo_instance is None:
                logger.error(f'{self.__class__.__name__} {self.name} {self.id}: Geometry Instance with file id: {file_id}, geometry id: {geometry_id} not found')
                if not continue_on_error:
                    raise KeyError(f'{self.__class__.__name__} {self.name} {self.id}: Geometry Instance with file id: {file_id}, geometry id: {geometry_id} not found')

            else:
                geo_instances.append(geo_instance)

        return geo_instances


class BuildInZone(SimultanObject):

    def __init__(self, *args, **kwargs):
        """

        """
        SimultanObject.__init__(self, *args, **kwargs)

    @property
    @lru_cache(maxsize=None)
    def volumes(self):
        return [x for x in self.contained_components if x._wrapped_obj.FitsInSlots[0] == 'Geometrische_Volumina']

    @property
    @lru_cache(maxsize=None)
    def faces(self):
        return [x for x in self.contained_components if x._wrapped_obj.FitsInSlots[0] == 'Geometrische_Flächen']










