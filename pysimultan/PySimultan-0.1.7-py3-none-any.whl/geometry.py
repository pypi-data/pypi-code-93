# from . geometry_import import import_geometry


class GeometricalElement(object):
    def __init__(self, *args, **kwargs):
        self.content = kwargs.get('content', None)

        for name, value in self.content.items():
            if isinstance(value, (list, tuple)):
               setattr(self, name, [obj(x) if isinstance(x, dict) else x for x in value])
            else:
               setattr(self, name, obj(value) if isinstance(name, dict) else value)


class Layer(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Parent = None
    pass


class Vertex(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Layer = None
    pass


class Edge(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Layer = None
        self.Vertex1ID = None
        self.Vertex2ID = None
    pass


class EdgeLoop(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Edges = []
    pass


class Polyline(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Layer = None
        self.Edges = []
    pass


class Faces(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Layer = None
        self.Holes = None
        self.Boundary = None
    pass


class Volumes(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Layer = None
        self.Faces = []
    pass


class Proxies(GeometricalElement):
    def __init__(self, *args, **kwargs):
        GeometricalElement.__init__(self, *args, **kwargs)
        self.Layer = None
        self.Vertex = None
        self.Faces = []

    pass


class Geometry:
    def __init__(self, *args, **kwargs):
        self.project_path = kwargs.get('project_path', None)
        if kwargs.get('project_path', None):
            self.project_path = kwargs.get('project_path', None)
            self.content = import_geometry(self.project_path)

        if kwargs.get('content', None):
            self.content = kwargs.get('content', None)

        self.layers = self.get_layers()
        self.vertices = self.get_vertices()
        self.edges = self.get_edges()
        self.edge_loops = self.get_edge_loops()
        self.polylines = self.get_polylines()
        self.faces = self.get_faces()
        self.volumes = self.get_volumes()
        # self.linked_models = self.get_linked_models()
        self.proxies = self.get_proxies()
        # self.geo_refs = self.get_geo_refs()

    def get_layers(self):
        layers = {}
        for layer_json in list(self.content[2]):
            # layer_json['Parent'] = None
            layer = Layer(content=layer_json)
            layers[layer.ID] = layer
        for layer in layers.values():
            if layer.ParentID:
                layer.Parent = layers[layer.ParentID]
        return layers

    def get_vertices(self):
        vertices = {}
        for vertex_json in list(self.content[3]):
            # vertex_json['Layer'] = None
            vertex = Vertex(content=vertex_json)
            if vertex.LayerID:
                vertex.Layer = self.layers[vertex.LayerID]
            vertices[vertex.ID] = vertex
        return vertices

    def get_edges(self):
        edges = {}
        for edge_json in list(self.content[4]):
            # edge_json['Layer'] = None
            # edge_json['Vertex1ID'] = None
            # edge_json['Vertex2ID'] = None
            edge = Edge(content=edge_json)

            if edge.Vertex1:
                edge.Vertex1ID = edge.Vertex1
                edge.Vertex1 = self.vertices[edge.Vertex1ID]

            if edge.Vertex2:
                edge.Vertex2ID = edge.Vertex2
                edge.Vertex2 = self.vertices[edge.Vertex2ID]

            edges[edge.ID] = edge

        return edges

    def get_edge_loops(self):
        edge_loops = {}
        for edge_loop_json in list(self.content[5]):
            edge_loop = EdgeLoop(content=edge_loop_json)
            if edge_loop.EdgeIDs:
                edge_loop.Edges = [self.edges[edgeID] for edgeID in edge_loop.EdgeIDs]

            edge_loops[edge_loop.ID] = edge_loop

        return edge_loops

    def get_polylines(self):
        polylines = {}
        for polyline_json in list(self.content[6]):
            polyline = Polyline(content=polyline_json)
            if polyline.EdgeIDs:
                polyline.Edges = [self.edges[edgeID] for edgeID in polyline.EdgeIDs]
            polylines[polyline.ID] = polyline

        return polylines

    def get_faces(self):
        faces = {}
        for face_json in list(self.content[7]):
            face = Faces(content=face_json)
            if face.BoundaryID:
                face.Boundary = self.edge_loops[face.BoundaryID]
            if face.HoleIDs:
                face.Holes = [self.edge_loops[holeID] for holeID in face.HoleIDs]
            faces[face.ID] = face

        return faces

    def get_volumes(self):
        volumes = {}
        for volume_json in list(self.content[8]):
            volume = Volumes(content=volume_json)
            if volume.FaceIDs:
                volume.Edges = [self.faces[faceID] for faceID in volume.FaceIDs]
            volumes[volume.ID] = volume
        return volumes

    def get_proxies(self):
        proxies = {}
        for proxy_json in list(self.content[8]):
            proxy = Volumes(content=proxy_json)
            if proxy.LayerID:
                proxy.Layer = self.layers[proxy.LayerID]
            proxies[proxy.ID] = proxy
        return proxies

