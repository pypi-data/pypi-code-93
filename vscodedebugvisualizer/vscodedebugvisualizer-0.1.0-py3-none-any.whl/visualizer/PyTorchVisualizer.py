from vscodedebugvisualizer.visualizer.NumpyVisualizer import NumpyVisualizer


class PyTorchVisualizer(NumpyVisualizer):
    def checkType(self, t):
        try:
            import torch
        except ImportError:
            return False

        return isinstance(t, torch.Tensor)

    def visualize(self, data):
        data = data.cpu().detach()

        return super().visualize(data)
