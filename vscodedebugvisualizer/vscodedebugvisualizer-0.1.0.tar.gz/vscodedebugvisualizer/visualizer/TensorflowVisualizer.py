from vscodedebugvisualizer.visualizer.NumpyVisualizer import NumpyVisualizer


class TensorflowVisualizer(NumpyVisualizer):
    def checkType(self, t):
        try:
            import tensorflow
        except ImportError:
            return False

        return isinstance(t, tensorflow.Tensor)

    def visualize(self, data):
        data = data.numpy()

        return super().visualize(data)
