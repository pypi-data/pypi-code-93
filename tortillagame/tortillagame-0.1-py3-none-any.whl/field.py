from tortilla.common.hex_neighbors import axial_neighbor
from tortilla.hexagon import Hexagon


class Field:
    def __init__(self, rows, cols, entities=None):
        self._rows = rows
        self._cols = cols
        self._hexagons = []
        self._init_hexagons()
        if entities:
            self._init_entities(entities)
        self._directed_hexagon = self._hexagons[0][0]
        self._selected_hexagon = None
        self._reachable_hexagons = None

    def _init_hexagons(self):
        graph = dict()

        # init_graph_vertices
        for row in range(self._rows):
            for col in range(self._cols - row % 2):
                q, r = col - row // 2, row
                graph[(q, r)] = []

        # init_graph_neighbors
        for q, r in graph:
            for direction in range(6):
                neighbor = axial_neighbor((q, r), direction)
                if neighbor in graph:
                    graph[(q, r)].append(neighbor)
                else:
                    graph[(q, r)].append(None)

        # init_hexagons
        for row in range(self._rows):
            self._hexagons.append([])
            for col in range(self._cols - row % 2):
                self._hexagons[row].append(Hexagon(row, col))

        # init_neighbors
        for q, r in graph:
            neighbors = graph[(q, r)]
            hexagonal_neighbors = []
            for neighbor in neighbors:
                if neighbor:
                    neighbor_row, neighbor_col = neighbor[1], neighbor[0] + neighbor[1] // 2
                    hexagonal_neighbors.append(self._hexagons[neighbor_row][neighbor_col])
                else:
                    hexagonal_neighbors.append(None)
            row, col = r, q + r // 2
            self._hexagons[row][col].neighbors = hexagonal_neighbors

    def _init_entities(self, entities):
        for entity, coordinates in entities:
            x, y = coordinates
            self._hexagons[x][y].entity = entity
        #self._hexagons[1][0].entity = entities['ships'][0]
        #self._hexagons[3][2].entity = entities['ships'][1]
        #self._hexagons[6][3].entity = entities['ships'][2]
        #self._hexagons[6][5].entity = entities['ships'][3]
        #self._hexagons[7][3].entity = entities['obstacles'][0]

    @property
    def rows(self): return self._rows

    @property
    def cols(self): return self._cols

    @property
    def hexagons(self): return self._hexagons

    @property
    def directed_hexagon(self): return self._directed_hexagon

    @directed_hexagon.setter
    def directed_hexagon(self, value: (int, int) or None):
        self._directed_hexagon = value

    @property
    def selected_hexagon(self):
        return self._selected_hexagon

    @selected_hexagon.setter
    def selected_hexagon(self, value: (int, int) or None):
        self._selected_hexagon = value

    @property
    def reachable_hexagons(self):
        return self._reachable_hexagons

    @reachable_hexagons.setter
    def reachable_hexagons(self, value):
        self._reachable_hexagons = value

    @property
    def highlighted_hexagons(self):
        value = {
            'directed_hexagon': self._directed_hexagon,
            'selected_hexagon': self._selected_hexagon,
            'reachable_hexagons': self._reachable_hexagons
        }
        return value
