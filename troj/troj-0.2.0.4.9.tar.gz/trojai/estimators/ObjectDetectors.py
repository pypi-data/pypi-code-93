import torch
import torch.nn as nn


class PytorchObjectDetector(nn.Module):
    def __init__(self, model):
        """

        :param model: Pytorch Object Detection model
        """
        super(PytorchObjectDetector, self).__init__()
        self.model = model

    def compute_loss(self, samples, labels, grad=False, reduce=True):
        """
        :param: samples: Samples to make predictions on as list of tensors.
        :param: labels: labels as list of dictionaries
        :param: grad: If true, the gradient is computed.
        :param: reduce: If true, the losses are reduced via summation and a single scalar is returned, otherwise a dictionary is returned.
        """
        self.model.train()
        if grad == False:
            with torch.no_grad():
                losses = self.model(samples, labels)
        else:
            losses = self.model(samples, labels)
        if reduce:
            losses = sum(loss for loss in losses.values())
        return losses

    def predict(self, sample):
        self.model.eval()
        preds = self.model(sample)
        return preds
