import os
import tensorflow as tf
from tensorflow.python.framework.ops import prepend_name_scope
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

from deeplite.converter.converter import ModelConverter 
from deeplite.converter.formatter import getLogger
from deeplite.converter.formatter import ModelFormat
logger = getLogger()

class TF2TFLite(ModelConverter):
    def __init__(self, model):
        super().__init__(model)
        self.source_format = ModelFormat.TF
        self.target_format = ModelFormat.TFLITE

    def load_model(self, path=None):
        pass
        
    def convert(self):
        try: 
            converter = tf.lite.TFLiteConverter.from_concrete_functions([self.model])
            converter.optimizations = [tf.compat.v1.lite.Optimize.DEFAULT]
            converter.experimental_new_converter = True
            converter.target_spec.supported_ops = [tf.compat.v1.lite.OpsSet.TFLITE_BUILTINS,
                                                tf.compat.v1.lite.OpsSet.SELECT_TF_OPS]
            tflite_model = converter.convert()
            logger.info("Model has been converted to TFLite format")
            rval = 0
        except Exception as e:
            logger.error("Model could not be converted in TFLite format")
            logger.warning(
                "Model could not be converted in TFLite format, it contains an unsupported operation '{}'".format(e))
            tflite_model = None
            rval = 1
        return tflite_model, rval

    def save(self, model, path='output.tflite'):
        try: 
            with open(path, 'wb') as f:
                f.write(model) 
            rval = 0
            logger.info(
                    "Model has been exported to TFLite format: {0}".format(os.path.abspath(path)))
        except Exception as e:
            logger.error("Model could not be exported to TFLite format")
            logger.warning("Model could not be exported to TFLiteformat '{}'".format(e))
            rval = 1

        return rval