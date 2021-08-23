import os
from inspect import getmodule
from argparse import ArgumentParser

import json
import yaml
import logging


class Grain(ArgumentParser):
    """A class derived from class ArgumentParser which can
    be used for creating python objects from arguments.

    These arguments can be obtained from:

    1. Command Line Inputs
    2. Metadata JSON Files

    Grain can also be used to load arguments for models
    and log model inputs

    Parameters
    ----------
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment
    *args : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        a non keyworded arguments' list.
    **kwargs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        a keyworded arguments' list.

    Attributes
    ----------
    add_argument : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        adds arguments to Grain object.
    _band_ids_sep : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        splits band ids.
    _input_shape_sep : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        splits input shape.
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment

    Examples
    --------
    1. Parsing dummy CLI arguments through a default Grain instance

    >>> grain_exp = Grain()
    >>> args = grain_exp.parse_args([
    ... '--sensor', 'dummy', '--band_ids', 'gray', '--input_shape',
    ... '1,16,16,2', '--resolution', '0.5'
    ... ])
    >>> args.input_shape
    [1, 16, 16, 2]

    2. Parsing dummy CLI arguments through a Grain instance linked to a polyaxon experiment

    >>> from polyaxon.tracking import Run
    >>> experiment = Run()
    >>> grain_exp = Grain(polyaxon_exp=experiment)
    >>> args = grain_exp.parse_args(['--sensor', 'dummy',
    ...                              '--band_ids', 'gray',
    ...                              '--input_shape', '1,16,16,2',
    ...                              '--resolution', '1'])
    >>> args.input_shape
    [1, 16, 16, 2]

    3. Parsing dummy metadata JSON through a Grain instance

    >>> grain_exp = Grain()
    >>> args = grain_exp.parse_args_from_json('/tmp/metadata.json')
    >>> args.sensor
    'sentinel2'

    4. Load a dummy model through Grain instance

    >>> class DummyNet(nn.Module):
    ... def __init__(self, foo):
    ...     super(DummyNet, self).__init__()
    ...     self.layer = foo
    ...
    ... def forward(self, x):
    ...     return x
    >>>
    >>> grain_exp = Grain()
    >>> model = grain_exp.load_model(DummyNet, foo='bar')
    >>> model.layer
    'bar'

    """

    def __init__(self, polyaxon_exp=None, *args, **kwargs):
        super(Grain, self).__init__(*args, **kwargs)
        self.polyaxon_exp = polyaxon_exp

        self.add_argument('--sensor',
                          type=str,
                          required=True,
                          help='Sensor in use (sentinel-2, landsat, planet)')

        self.add_argument('--band_ids',
                          type=self._band_ids_sep,
                          required=True,
                          help='Sensor band ids used in experiment')

        self.add_argument('--input_shape',
                          type=self._input_shape_sep,
                          required=True,
                          help='patch size for training process')

        self.add_argument('--resolution',
                          type=float,
                          required=True,
                          help='resolution of training process tensor')

    def parse_args(self, args=None, namespace=None):
        """Parse arguments passed as CLI Inputs

        Parameters
        ----------
        args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_, optional
            list of arguments to be parsed, by default None
        namespace : `argparse.Namespace <https://docs.python.org/3/library/argparse.html#argparse.Namespace>`_, optional
            namespace to validate arguments from, by default None

        Returns
        -------
        `object <https://docs.python.org/3/reference/datamodel.html#objects-values-and-types>`_
            object of parsed arguments
        """
        logging.debug("Enter parse_args routine")
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = ('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))

        if self.polyaxon_exp:
            self.polyaxon_exp.log_inputs(**vars(args))

        logging.debug("Exit parse_args routine")
        return args

    def parse_args_from_json(self, json_file):
        """Parse arguments passed in json_file

        Parameters
        ----------
        json_file  : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            string represent metadata JSON file path

        Returns
        -------
        `object <https://docs.python.org/3/reference/datamodel.html#objects-values-and-types>`_
            object of parsed arguments
        """
        with open(json_file, 'r') as fin:
            logging.debug("Enter parse_args_from_json routine")
            metadata = json.load(fin)
            self.set_defaults(**metadata)

            args = self.parse_args([
                '--sensor', metadata['sensor'], '--band_ids',
                metadata['band_ids'], '--input_shape', metadata['input_shape'],
                '--resolution',
                str(metadata['resolution'])
            ])

            logging.debug("Exit parse_args_from_json routine")
            return args
    
    def parse_args_from_yaml(self, yaml_file):
        """Parse arguments passed in json_file

        Parameters
        ----------
        json_file  : metadata JSON file

        Returns
        -------
        type
            list of parsed arguments
        """
        with open(yaml_file, 'r') as fin:
            logging.debug("Enter parse_args_from_json routine")
            metadata = yaml.safe_load(fin)
            self.set_defaults(**metadata)

            args = self.parse_args([
                '--sensor', metadata['sensor'], '--band_ids',
                metadata['band_ids'], '--input_shape', metadata['input_shape'],
                '--resolution',
                str(metadata['resolution'])
            ])

            logging.debug("Exit parse_args_from_json routine")
            return args

    def load_model(self, model_cls, **kwargs):
        """Log and instantiate a model with keyword arguments

        Parameters
        ----------
        model_cls : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            A pytorch model class to instantiate.
        **kwargs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            all model positional arguments

        Returns
        -------
        `object <https://docs.python.org/3/reference/datamodel.html#objects-values-and-types>`_
            pytorch model object created from keyword arguments.

        """
        logging.debug("Enter load_model routine")
        if self.polyaxon_exp:
            self._log_model(model_cls, **kwargs)
        logging.debug("Exit load_model routine")
        return model_cls(**kwargs)

    def _log_model(self, model_cls, **kwargs):
        """Log model inputs

        Parameters
        ----------
        model_cls : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            A pytorch model class.
        **kwargs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            all model positional arguments

        """
        logging.debug("Enter _log_model routine")
        model_module = getmodule(model_cls).__name__
        model_path = os.path.relpath(getmodule(model_cls).__file__)
        model_name = model_cls.__name__

        self.polyaxon_exp.log_inputs(model_path=model_path,
                                     model_name=model_name,
                                     model_module=model_module,
                                     model_args=kwargs)
        logging.debug("Exit _log_model routine")

    @staticmethod
    def _band_ids_sep(band_ids):
        """splits band ids.

        Parameters
        ----------
        band_ids : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_ / `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            band ids to select.

        Returns
        -------
        `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            list of band ids.

        """
        logging.debug("Inside _band_ids_sep routine")
        if isinstance(band_ids, list):
            return band_ids
        return band_ids.split(',')

    @staticmethod
    def _input_shape_sep(input_shape):
        """splits input shape.

        Parameters
        ----------
        input_shape : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_ / `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            shape of input patch.

        Returns
        -------
        `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            list of input patch dimensions.

        """
        logging.debug("Inside _input_shape_sep routine")
        if isinstance(input_shape, list):
            return input_shape
        return list(map(int, input_shape.split(',')))
