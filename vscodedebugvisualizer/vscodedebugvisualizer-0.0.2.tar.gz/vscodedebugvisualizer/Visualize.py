from vscodedebugvisualizer.visualizer.ListVisualizer import ListVisualizer
from vscodedebugvisualizer.visualizer.NumpyVisualizer import NumpyVisualizer
from vscodedebugvisualizer.visualizer.PandasVisualizer import PandasVisualizer
from vscodedebugvisualizer.visualizer.PrimitiveVisualizer import PrimitiveVisualizer
from vscodedebugvisualizer.visualizer.PyTorchVisualizer import PyTorchVisualizer
from vscodedebugvisualizer.visualizer.TensorflowVisualizer import TensorflowVisualizer


class Visualize:
    visualizers = []

    def addVisualizer(self, vis):
        self.visualizers.append(vis)

    def visualize(self, data):
        for v in self.visualizers:
            print("Check type for %s found" % v)
            if v.checkType(data):
                print("Visualizer %s found" % v)
                return v.visualize(data)
        print("No Visualizer found for specified Type: %s" % type(data))
        return None


class Visualizer:
    def checkType(self, type):
        raise Exception("checkType() needs to be overwritten")

    def visualize(self, data):
        raise Exception("visualize() needs to be overwritten")


globalVisualizationFactory = Visualize()
globalVisualizationFactory.addVisualizer(PrimitiveVisualizer())
globalVisualizationFactory.addVisualizer(ListVisualizer())
globalVisualizationFactory.addVisualizer(NumpyVisualizer())
globalVisualizationFactory.addVisualizer(PyTorchVisualizer())
globalVisualizationFactory.addVisualizer(TensorflowVisualizer())
globalVisualizationFactory.addVisualizer(PandasVisualizer())


def visualize(d):
    return globalVisualizationFactory.visualize(d)
