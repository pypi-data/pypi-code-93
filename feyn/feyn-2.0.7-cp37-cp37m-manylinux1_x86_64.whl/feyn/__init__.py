"""Feyn is the main Python module to build and execute models that utilizes a QLattice.

The QLattice stores and updates probabilistic information about the mathematical relationships (models) between observable quantities.

The workflow is typically:

# Connect to the QLattice
>>> ql = feyn.connect_qlattice()

# Extract models from the QLattice
>>> models = ql.sample_models(data.columsn, output="out")

# Fit the list of models to a local dataset
>>> models = feyn.fit_models(models, data)

# Pick the best Model from the fitted models
>>> best = models[0]

# Update the remote QLattice with this model to explore similar models.
>>> ql.update(best)

# Or use the model to make predictions
>>> predicted_y = model.predict(new_data)
"""
from ._version import _read_version, _read_git_sha
from ._model import Model
from ._svgrenderer import show_model, _render_svg
from ._sgdtrainer import fit_models, start_performance_log, stop_and_get_performance_log

from ._selection import prune_models, best_diverse_models
from ._validation import validate_data

from ._qlattice import connect_qlattice

from ._config_evolution_params import _HalfLife_params

from . import tools
from . import losses
from . import criteria
from . import filters
from . import metrics
from . import plots
from . import reference
from . import datasets

_current_renderer = _render_svg
_disable_type_checks = False

__all__ = ['connect_qlattice', 'fit_models', 'prune_models', 'best_diverse_models', 'show_model', 'Model', 'validate_data']

__version__ = _read_version()
__git_sha__ = _read_git_sha()
