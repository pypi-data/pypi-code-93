from weakref import WeakSet
import numpy as np
import colorlog
# from copy import deepcopy
# from functools import lru_cache
from tqdm import tqdm
from .utils import classproperty
from .geo_default_types import geometry_types


logger = colorlog.getLogger('PySimultan')


class GeometryModel(object):

    _cls_instances = WeakSet()      # weak set with all created objects
    _create_all = False             # if true all properties are evaluated to create python objects when initialized

    @classproperty
    def _cls_instances_dict(cls):
        return dict(zip([x.id for x in cls._cls_instances], [x() for x in cls._cls_instances]))

    @classproperty
    def cls_instances(cls):
        return list(cls._cls_instances)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        if "_cls_instances" not in cls.__dict__:
            cls._cls_instances = WeakSet()
        try:
            cls._cls_instances.add(instance)
        except Exception as e:
            logger.error(f'Error adding instance {instance} to _cls_instances: {e}')

        return instance

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)

        self._vertices = kwargs.get('vertices', None)
        self._edges = kwargs.get('edges', None)
        self._edge_loops = kwargs.get('edge_loops', None)
        self._faces = kwargs.get('faces', None)
        self._volumes = kwargs.get('volumes', None)
        self._layers = kwargs.get('layers', None)

        self._geo_types = kwargs.get('geo_types', None)

        self.GeoBaseClass, self.LayerCls, self.VertexCls, self.EdgeCls, self.EdgeLoopCls, self.FaceCls, self.VolumeCls = create_geo_classes(self._geo_types)
        self.load_all()

    @property
    def id(self):
        return self._wrapped_obj.Id

    @property
    def name(self):
        if self._wrapped_obj is not None:
            return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def layers(self):
        if self._layers is None:
            self._layers = self.get_layers()
        return self._layers

    @property
    def vertices(self):
        if self._vertices is None:
            self._vertices = self.get_vertices()
        return self._vertices

    @property
    def edges(self):
        if self._edges is None:
            self._edges = self.get_edges()
        return self._edges

    @property
    def edge_loops(self):
        if self._edge_loops is None:
            self._edge_loops = self.get_edge_loops()
        return self._edge_loops

    @property
    def faces(self):
        if self._faces is None:
            self._faces = self.get_faces()
        return self._faces

    @property
    def volumes(self):
        if self._volumes is None:
            self._volumes = self.get_volumes()
        return self._volumes

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

    def get_vertices(self):
        return [self.VertexCls(wrapped_obj=x) for x in tqdm(self._wrapped_obj.Geometry.Vertices.Items)]

    def get_edges(self):
        return [self.EdgeCls(wrapped_obj=x) for x in tqdm(self._wrapped_obj.Geometry.Edges.Items)]

    def get_edge_loops(self):
        return [self.EdgeLoopCls(wrapped_obj=x) for x in tqdm(self._wrapped_obj.Geometry.EdgeLoops.Items)]

    def get_faces(self):
        return [self.FaceCls(wrapped_obj=x) for x in tqdm(self._wrapped_obj.Geometry.Faces.Items)]

    def get_volumes(self):
        return [self.VolumeCls(wrapped_obj=x) for x in tqdm(self._wrapped_obj.Geometry.Volumes.Items)]

    def get_layers(self):
        return [self.LayerCls(wrapped_obj=x) for x in tqdm(self._wrapped_obj.Geometry.Layers.Items)]

    def get_face_by_id(self, id):

        face = self.FaceCls.get_obj_by_id(id)
        if face is None:
            _ = self.faces
        face = self.FaceCls.get_obj_by_id(id)
        return face

    def get_zone_by_id(self, id):

        zone = self.VolumeCls.get_obj_by_id(id)
        if zone is None:
            _ = self.volumes
        zone = self.VolumeCls.get_obj_by_id(id)
        return zone

    def load_all(self):

        logger.info(f'Geometry model: {self.name}: loading vertices')
        _ = self.vertices
        logger.info(f'Geometry model: {self.name}: loading edges')
        _ = self.edges
        logger.info(f'Geometry model: {self.name}: loading edge loops')
        _ = self.edge_loops
        logger.info(f'Geometry model: {self.name}: loading faces')
        _ = self.faces
        logger.info(f'Geometry model: {self.name}: loading volumes')
        _ = self.volumes

        logger.info(f'\n\nGeometry model import info:\n----------------------------------------------')
        logger.info(f'Geometry model: {self.name}')
        logger.info(f'Number vertices: {self.vertices.__len__()}')
        logger.info(f'Number edges: {self.edges.__len__()}')
        logger.info(f'Number edge_loops: {self.edge_loops.__len__()}')
        logger.info(f'Number faces: {self.faces.__len__()}')
        logger.info(f'Number volumes: {self.volumes.__len__()}\n\n')


def create_geo_classes(geo_types):
    """
    Create new classes from geometric base classes

    :return:
    """

    logger.debug('creating base geo classes')

    class GeoBaseClass(geo_types['base']):
        pass

    class GeometricLayer(geo_types['layer']):
        pass

    class GeometricVertex(geo_types['vertex']):
        pass

    class GeometricEdge(geo_types['edge']):
        def get_vertices(self):
            return [GeometricVertex.get_obj_by_id(x.Id) for x in self._wrapped_obj.Vertices.Items]

    class GeometricEdgeLoop(geo_types['edge_loop']):
        def get_edges(self):
            return [GeometricEdge.get_obj_by_id(x.Edge.Id) for x in self._wrapped_obj.Edges.Items]

    class GeometricFace(geo_types['face']):

        @property
        def boundary(self):
            return GeometricEdgeLoop.get_obj_by_id(self._wrapped_obj.Boundary.Id)

        @property
        def holes(self):
            return [GeometricEdgeLoop.get_obj_by_id(x.Id) for x in self._wrapped_obj.Holes.Items]

        @property
        def points(self):
            return self.boundary.points

    class GeometricVolume(geo_types['volume']):

        def __init__(self, *args, **kwargs):
            geometry_types.volume.__init__(self, *args, **kwargs)
            # self._faces = kwargs.get('faces', None)

        @property
        def faces(self):
            if self._faces is None:
                self._faces = [GeometricFace.get_obj_by_id(x.Face.Id) for x in self._wrapped_obj.Faces.Items]
            return self._faces

        @faces.setter
        def faces(self, value):
            self._faces = value

    return GeoBaseClass, GeometricLayer, GeometricVertex, GeometricEdge, GeometricEdgeLoop, GeometricFace, GeometricVolume