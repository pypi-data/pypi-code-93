import os
import torch, torch.nn as nn
from deeplite.profiler import Device

from deeplite.converter.converter import ModelConverter
from deeplite.converter.formatter import getLogger
from deeplite.converter.formatter import ModelFormat
logger = getLogger()

class PyTorch2JIT(ModelConverter):
    def __init__(self, model):
        super().__init__(model)
        self.source_format = ModelFormat.PYTORCH
        self.target_format = ModelFormat.JIT

    def load_model(self, path=None):
        pass

    def convert(self, dataloader, device, batch_size=1):
        inputs_tuple = dataloader.forward_pass.create_random_model_inputs(batch_size)
        inputs_tuple = dataloader.forward_pass._tensor_sampler.to_device(
                inputs_tuple, device, standardize=False)
        try:
            traced_script_module = torch.jit.trace(self.model, inputs_tuple)
            rval = 0
            return traced_script_module, rval
        except Exception as e:
            logger.error("Model could not be converted to pytorch jit format")
            logger.warning("Model could not be converted to pytorch jit format '{}'".format(e))
            rval = 1
            return None, rval

    def save(self, model, path='output_jit.pt'):
        try:
            model.save(path)
            logger.info(
                "Model has been exported to pytorch jit format: {0}".format(os.path.abspath(path)))
            rval = 0
        except Exception as e:
            logger.error("Model could not be exported to pytorch jit format")
            logger.warning("Model could not be exported to pytorch jit format '{}'".format(e))
            rval = 1

        return rval