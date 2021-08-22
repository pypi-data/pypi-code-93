import numpy as np
from .linear_elastic import solve_linear_elastic


class CrossSection:
    def __init__(self, E: float = None, A: float = None) -> None:
        self.E = E or 1
        self.A = A or 1


class Node:
    # number of nodes
    nno = 0
    ndof = 2

    def __init__(self, x: float, y: float) -> None:
        Node.nno += 1
        self.id = Node.nno
        self.x = x
        self.y = y
        self.dofs = [(Node.nno - 1) * 2, (Node.nno - 1) * 2 + 1]
        self.support = [False, False]
        self.load = [0, 0]

    @property
    def coordinates(self) -> np.array:
        return np.array([self.x, self.y])

    @property
    def supported_dofs(self):
        return [dof for dof, supp in zip(self.dofs, self.support) if supp]

    def distance(self, other) -> float:
        return np.linalg.norm(self.coordinates - other.coordinates)


class Element:
    # number of elements
    nel = 0
    ndof = 4

    def __init__(self, node1: Node, node2: Node, cross_section: CrossSection) -> None:
        Element.nel += 1
        self.id = Element.nel
        self.node1 = node1
        self.node2 = node2
        self.cross_section = cross_section

    @property
    def coordinates(self) -> np.array:
        return np.vstack((self.node1.coordinates, self.node2.coordinates))

    @property
    def length(self) -> float:
        return self.node1.distance(self.node2)

    @property
    def dofs(self):
        return self.node1.dofs + self.node2.dofs


class Truss:
    def __init__(self, nodes: list, elements: list) -> None:
        self.nodes = nodes
        self.elements = elements
        self.deformations = None
        self.element_forces = None

    @classmethod
    def from_dict(cls, inputdict: dict) -> "FE_truss":
        nodes = []
        elements = []
        for coordinates in inputdict["nodes"]:
            nodes.append(Node(*coordinates))

        cross_section = CrossSection(**inputdict["cross_section"])

        for topology in inputdict["elements"]:
            elements.append(
                Element(
                    nodes[topology[0]],
                    nodes[topology[1]],
                    cross_section,
                )
            )
        for node_id, support in inputdict["supports"].items():
            nodes[node_id].support = support

        for node_id, load in inputdict["loads"].items():
            nodes[node_id].load = load
        return cls(nodes, elements)

    @property
    def nno(self):
        return Node.nno

    @property
    def nel(self):
        return Element.nel

    @property
    def ndofs(self):
        return sum([node.ndof for node in self.nodes])

    def supported_dofs(self) -> list:
        supported_dofs = []
        for n in self.nodes:
            supported_dofs.extend(n.supported_dofs)
        return list(set(supported_dofs))

    def load_vector(model) -> np.array:
        f = np.zeros((model.ndofs, 1))
        for n in model.nodes:
            f[n.dofs[0]] += n.load[0]
            f[n.dofs[1]] += n.load[1]
        return f

    def solve_linear_elastic(self):
        self.deformations, self.element_forces = solve_linear_elastic(self)