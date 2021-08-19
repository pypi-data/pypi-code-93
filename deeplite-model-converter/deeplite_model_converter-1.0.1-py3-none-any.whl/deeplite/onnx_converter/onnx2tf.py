import os
import onnx
from onnx_tf.backend import prepare

from deeplite.converter.converter import ModelConverter 
from deeplite.converter.formatter import getLogger
from deeplite.converter.formatter import ModelFormat
logger = getLogger()

class ONNX2TF(ModelConverter):
    def __init__(self, model):
        super().__init__(model)
        self.source_format = ModelFormat.ONNX
        self.target_format = ModelFormat.TF

    def load_model(self, path):
        return onnx.load(path) 
        
    def convert(self):
        try:
            tf_rep = prepare(self.model)  # creating TensorflowRep object
            tf_rep.tf_module.is_export = True
            signatures = tf_rep.tf_module.__call__.get_concrete_function(**tf_rep.signatures)
            tf_rep.tf_module.is_export = False
            logger.info("Model has been converted to TF signatures format")
            rval = 0
        except Exception as e:
            logger.error("Model could not be converted in TF signatures format")
            logger.warning(
                "Model could not be converted in TF signatures format, it contains an unsupported operation '{}'".format(e))
            signatures = None
            rval = 1
        
        return signatures, rval

    def save(self, model, path='output.tf'):
        return NotImplementedError