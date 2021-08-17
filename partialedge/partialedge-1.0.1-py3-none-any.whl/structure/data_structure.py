from pygeos.creation import linestrings
from pygeos.measurement import length
from pygeos.set_operations import intersection
from pygeos import line_interpolate_point
from pygeos import line_locate_point
from pygeos import shortest_line
from pygeos import get_point
from pygeos import get_coordinates

EPSILON = 0.03  # absolute value
STUB_REDUCTION_MAX = 0.5  # percent of stub length
FULL_LENGTH_STUB = 0.5
FULL_LENGTH_TUPLE = [FULL_LENGTH_STUB, FULL_LENGTH_STUB]


class Graph:

    def __init__(self, nodes, edges):
        self.nodes = sorted(nodes, key=lambda x: x.index)
        self.edges = edges

    def draw(self, subplot):
        for edge in self.edges:
            edge.draw(subplot)
        for node in self.nodes:
            node.draw(subplot)

    def get_ink_value(self):
        sum = 0
        for edge in self.edges:
            sum += edge.get_length()
        return sum


class Node:

    def __init__(self, index, color="black"):
        self.index = index
        self.coords = None
        self.color = color

    def draw(self, subplot):
        subplot.plot(self.coords[0], self.coords[1], color=self.color, marker="o")

    def draw_label(self, subplot, index):
        subplot.text(x=self.coords[0]+0.01, y=self.coords[1]+0.01, s=str(index))


class Edge:

    def __init__(self, nodes, color="black"):
        self.nodes = nodes
        self.color = color
        self.factor = FULL_LENGTH_TUPLE
        self.linestyle = "-"

    def get_segment(self):
        return linestrings([self.nodes[0].coords, self.nodes[1].coords])

    def get_length(self):
        return length(self.get_segment())

    def draw(self, subplot):
        stub1 = get_coordinates(self.get_stub_one())
        x = [point[0] for point in stub1]
        y = [point[1] for point in stub1]
        subplot.plot(x, y, linestyle=self.linestyle, color=self.color, antialiased=True)

        stub2 = get_coordinates(self.get_stub_two())
        x = [point[0] for point in stub2]
        y = [point[1] for point in stub2]
        subplot.plot(x, y, linestyle=self.linestyle, color=self.color, antialiased=True)

    def draw_label(self, subplot, index):
        point = line_interpolate_point(self.get_stub_one(), 0.5, normalized=True)
        x, y = get_coordinates(point)[0]
        subplot.text(x=x, y=y, s="{:.2f}".format(self.factor[0]))

        point = line_interpolate_point(self.get_stub_two(), 0.5, normalized=True)
        x, y = get_coordinates(point)[0]
        subplot.text(x=x, y=y, s="{:.2f}".format(self.factor[1]))

    def get_stub_one(self):
        segment = self.get_segment()

        e = EPSILON if self.factor != FULL_LENGTH_TUPLE else 0
        stub_length = self.get_length() * self.factor[0]
        reduced_stub_length = stub_length - min(e, stub_length * STUB_REDUCTION_MAX)
        endpoint = line_interpolate_point(segment, reduced_stub_length, normalized=False)
        stub_reduced = shortest_line(get_point(segment, 0), endpoint)
        return stub_reduced

    def get_stub_two(self):
        segment = self.get_segment()

        e = EPSILON if self.factor != FULL_LENGTH_TUPLE else 0
        stub_length = self.get_length() * self.factor[1]
        reduced_stub_length = stub_length - min(e, stub_length * STUB_REDUCTION_MAX)
        endpoint = line_interpolate_point(segment, -reduced_stub_length, normalized=False)
        stub_reduced = shortest_line(get_point(segment, 1), endpoint)
        return stub_reduced

    def intersect(self, other):
        segment = self.get_segment()
        intersection_point = intersection(segment, other.get_segment())
        factor = line_locate_point(segment, intersection_point, normalized=True)
        return factor


class IntersectionNode(Node):

    def __init__(self, index, edge, symmetric):
        super(IntersectionNode, self).__init__(index)
        self.edge = edge
        self.symmetric = symmetric

    def get_length(self):
        return self.edge.get_length()

    def intersect(self, other):
        c = self.edge.intersect(other.edge)
        if self.symmetric:
            symmetric_c = min(c, 1 - c)
            return [symmetric_c, symmetric_c]
        else:
            return [c, 1-c]

    def draw(self, subplot):
        subplot.plot(self.coords[0], self.coords[1], color=self.edge.color, marker="o")

    def __str__(self):
        return "({}, {})".format(self.edge.nodes[0].index, self.edge.nodes[1].index)


class ContentNode:

    def __init__(self, intersection_node, symmetric):
        self.intersection_node = intersection_node
        self.symmetric = symmetric
        self.intersections = dict()

    def get_stub_combinations(self):
        stubs = list(self.intersections.values())
        if self.symmetric:
            return [FULL_LENGTH_TUPLE] + stubs
        else:
            combinations = [FULL_LENGTH_TUPLE]
            stubs.sort()
            for i in range(len(stubs)):
                for j in range(i, len(stubs)):
                    combinations.append([stubs[i][0], stubs[j][1]])
            return combinations

    def __repr__(self):
        return str(self.intersection_node)

