import importlib
import tensorflow as tf
from tensorflow import keras
from model_metadata import ModelMetadata

#preuzeto sa
#https://github.com/keras-team/keras/issues/10886


class Model(keras.models.Model):
    """ Subclass of keras' Model. It's extended so it saves and loads additional objects into HDF5 files
    Each object that is to be saved/loaded should implement two methods
    `get_config` - Method that returns a dictionary with the objects' configurations. Keys should only strings and
        values can be ints, floats, strings or lists of those types
    `from_config` - Method that receives a dict similar to the one returned by `get_config` and returns an instantiated
        object. This should be annotated with @classmethod
    The `ModelExtension` class is an abstract class that can be extended for this task, although that is not checked
    :param bf_metadata: Dictionary of name -> model bf_metadata. This dictionary can be later accessed through the
        `bf_metadata` attribute of this class. e.g.
        ```
        model = ExtendedModel(inputs, outputs, bf_metadata={'foo': model_extension})
        print(model.bf_metadata['foo'])  # prints the model_extension object
        ```
        This parameter can only be referenced by keyword. It'll never be positional
    The rest of the initialization parameters are the same as Model
    """
    def __init__(self, *args, **kwargs):
        bf_metadata = kwargs.get('bf_metadata')
        if bf_metadata is not None:
            del kwargs['bf_metadata']
        super().__init__(*args, **kwargs)
        self.bf_metadata = bf_metadata or dict()

    def get_config(self):
        config = super().get_config()
        if hasattr(self, 'bf_metadata') and self.bf_metadata is not None:
            config['bf_metadata'] = self.bf_metadata.get_config()
        return config

    @classmethod
    def from_config(cls, config, custom_objects=None):
        model = keras.models.Model.from_config(config, custom_objects)
        if 'bf_metadata' in config and config['bf_metadata'] is not None:
            model.bf_metadata = ModelMetadata.from_config(config['bf_metadata'])
        return model
    
    @staticmethod
    def load_model(filepath, custom_objects=None, compile=True):
        keras_custom_objects = {}
        if custom_objects is not None:
            keras_custom_objects.update(custom_objects)
        keras_custom_objects['Model'] = Model
        model = keras.models.load_model(filepath, keras_custom_objects, compile)

        if isinstance(model, Model) == False:
            from types import MethodType

            get_config_old = model.get_config

            def get_config_tmp(self):
                config = get_config_old()
                if hasattr(self, 'bf_metadata') and self.bf_metadata is not None:
                    config['bf_metadata'] = self.bf_metadata.get_config()
                return config

            model.get_config = MethodType(get_config_tmp, model)

        return model

