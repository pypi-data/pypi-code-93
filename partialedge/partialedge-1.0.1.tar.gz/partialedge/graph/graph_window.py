import os
from matplotlib import pyplot as plt


class PyplotWindow:

    def __init__(self):
        self.fig = plt.figure(figsize=(6, 6), dpi=300)

    def show(self):
        plt.show()

    def export_as_png(self, dir, file_name):
        os.makedirs(dir, exist_ok=True)
        path = os.path.join(dir, file_name)
        self.fig.savefig(path, dpi=300)

    def close(self):
        plt.close(self.fig)


class GraphWindow(PyplotWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()
        self.graph = self.fig.add_subplot(111)
        self.graph.axis((-1, 1, -1, 1))

    def draw_graph(self, graph):
        graph.draw(self.graph)
        self.graph.axis("equal")


class GraphDuoWindow(PyplotWindow):

    def __init__(self):
        super(GraphDuoWindow, self).__init__()

        self.origin = self.fig.add_subplot(211)
        self.origin.axis((-1, 1, -1, 1))
        self.result = self.fig.add_subplot(212)
        self.result.axis((-1, 1, -1, 1))

    def draw_origin(self, graph):
        graph.draw(self.origin)

    def draw_result(self, graph):
        graph.draw(self.result)


class GraphQuadWindow(PyplotWindow):

    def __init__(self):
        super(GraphQuadWindow, self).__init__()

        self.origin = self.fig.add_subplot(221)
        self.intersection = self.fig.add_subplot(222)
        self.result = self.fig.add_subplot(223)
        self.intersection_resolved = self.fig.add_subplot(224)

    def draw_origin(self, graph):
        graph.draw(self.origin)

    def draw_intersection(self, graph):
        graph.draw(self.intersection)

    def draw_result(self, graph):
        graph.draw(self.result)

    def draw_intersection_resolved(self, graph):
        graph.draw(self.intersection_resolved)
