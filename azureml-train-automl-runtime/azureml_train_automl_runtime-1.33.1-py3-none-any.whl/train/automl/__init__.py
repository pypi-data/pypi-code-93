# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality representing core automated ML and runtime components in Azure Machine Learning.

The *azureml-train-automl-runtime* package contains functionality for automatically finding the best machine learning
model and its parameters, given training and test data. 

The runtime package contains functionality to run training in pipelines as well as create advanced training logic
with ensembles. The runtime package has dependencies on other packages such as *pandas*, *numpy*, or *scikit-learn*.

The related *azureml-train-automl-client* package can be used for interactively submitting automate ML experiments,
and is is a lighterweight package with fewer dependencies.

For more information about automated ML in Azure, see [What is automated machine
learning?](https://docs.microsoft.com/azure/machine-learning/concept-automated-ml)
"""
import sys
from azureml.automl.core.package_utilities import get_sdk_dependencies
from azureml.automl.core._logging import log_server
from azureml.automl.core.shared import logging_utilities

import warnings
with warnings.catch_warnings():
    # Suppress the warnings at the import phase.
    warnings.simplefilter("ignore")
    from azureml.train.automl.automlconfig import AutoMLConfig

try:
    __all__ = [
        'AutoMLConfig',
        'get_sdk_dependencies']
except ImportError:
    __all__ = [
        'AutoMLConfig',
        'get_sdk_dependencies']

# TODO copy this file as part of setup in runtime package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)    # type: ignore

try:
    from ._version import ver as VERSION, selfver as SELFVERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    SELFVERSION = VERSION
    __version__ = VERSION

# Mark this package as being allowed to log certain built-in types
module = sys.modules[__name__]
logging_utilities.mark_package_exceptions_as_loggable(module)
log_server.install_handler('azureml.train.automl')
