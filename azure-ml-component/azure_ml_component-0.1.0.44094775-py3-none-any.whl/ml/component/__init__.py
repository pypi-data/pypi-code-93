# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains core functionality for Azure Machine Learning components.

Azure Machine Learning components allow you to create reusable machine learning workflows that can be used as a
template for your machine learning scenarios. This package contains the core functionality for working with
Azure ML components.

A machine learning components can also be constructed by a collection of :class:`azure.ml.component.Component` object
that can sequenced and parallelized, or be created with explicit dependencies.

You can create and work with components in a Jupyter Notebook or any other IDE with the Azure ML SDK installed.
"""

from .component import Component
from .pipeline import Pipeline
# from .endpoint import PipelineEndpoint
from .run import Run
from .run_settings import RunSettings
from .environment import Environment

__all__ = [
    'Component',
    'Pipeline',
    'Run',
    'RunSettings',
    'Environment'
]
