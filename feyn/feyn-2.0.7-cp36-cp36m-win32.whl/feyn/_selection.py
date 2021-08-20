"""Functions to prune models and select better ones."""
from functools import partial
from typing import List, Callable, Optional, Tuple, Set
from math import exp

import numpy as np

import feyn
from feyn._config_evolution_params import _HalfLife_params
from feyn._typings import check_types, _raise

from collections import Counter


def _prune_models_v2(
    models: List[feyn.Model],
    keep_n: Optional[int] = None,
) -> List[feyn.Model]:

    if keep_n is None:
        keep_n = len(models)

    # Always keep the best
    res = models[0:1]

    hashes = set()
    qid_counter = Counter()

    for m in models[1:]:
        if len(res) == keep_n:
            break

        # Check for duplicate structure
        model_hash = hash(m._program)
        if model_hash in hashes:
            continue

        qid = m._program.qid
        qid_counter[qid] += 1

        # Calculate the half-life of the model and decide if it should die.
        models_density = 100
        max_age = 100
        n = 7
        tau = 0.693
        if m.age > max_age * exp(-qid_counter[qid] / (models_density / (n * tau))) + 1:
            continue

        hashes.add(model_hash)
        res.append(m)

    return res


@check_types()
def prune_models(
    models: List[feyn.Model],
    dropout: bool = True,
    decay: bool = True,
    keep_n: Optional[int] = None,
) -> List[feyn.Model]:
    """Prune a list of models to remove redunant and poorly performing ones.

    Arguments:
        models {List[feyn.Model]} -- The list of models to prune.

    Keyword Arguments:
        dropout {bool} -- Whether or not to implement dropout regularization based on where in the QLattice models were generated. (default: {True})
        decay {bool} -- Whether or not to implement decay of old models that have not lived up to their potential. (default: {True})
        keep_n {Optional[int]} -- At most this many models will be returned. If None, models are left to be pruned by other redundancies. (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if models is an empty list.

    Returns:
        List[feyn.Model] -- The list of pruned models.
    """
    if len(models) == 0:
        raise ValueError("Empty list of models passed as argument.")

    if hasattr(models[0], "_program"):
        return _prune_models_v2(models, keep_n)

    max_model_density = 50
    if keep_n is not None and keep_n < 0:
        raise ValueError("keep_n needs to be positive")

    res = []
    locs = {}
    hashes = set()

    if keep_n is None:
        keep_n = len(models)
    # Select best three unique models
    for i, m in enumerate(models):
        model_hash = hash(m)
        if model_hash in hashes:
            continue
        res.append(m)
        if len(res) >= 3:
            break

    # Select location for dropout that is not in the best models
    barren_x = -1
    if dropout:
        x_locs = _output_locs_set(models)
        best_locs = _output_locs_set(res)
        # If all we have are the best models, don't prune
        candidate_locs = x_locs.difference(best_locs)
        if candidate_locs:
            barren_x = np.random.choice(list(candidate_locs))

    for m in models[i + 1 :]:
        # Check for duplicate structure
        model_hash = hash(m)
        if model_hash in hashes:
            continue

        output_loc = m[-1]._latticeloc[0]

        # Remove models from crowded locations
        density = locs.get(output_loc, 0)
        if density >= max_model_density:
            continue

        if dropout and output_loc == barren_x:
            continue

        # The density count becomes more expensive as we progress through the models
        if decay and _model_should_decay(m, density, max_model_density):
            continue

        res.append(m)
        locs[output_loc] = density + 1
        hashes.add(model_hash)

        if len(res) == keep_n:
            break

    return res


def _best_diverse_models_v2(models: List[feyn.Model], per_qid: int = 5) -> List[feyn.Model]:

    todo = set(m._qid for m in models)

    res = {}
    for m in models:
        qid = m._qid
        if qid not in todo:
            continue

        res.setdefault(qid, []).append(m)
        if len(res.get(qid, [])) == per_qid:
            todo.remove(qid)

    return sum(res.values(), [])


@check_types()
def best_diverse_models(
    models: List[feyn.Model],
    n: int = 10,
    distance_func: Optional[Callable[[feyn.Model, feyn.Model], bool]] = None,
) -> List[feyn.Model]:
    """Separate the n best performing models from a collection, such that they are sufficiently diverse in the context of some distance function.

    Arguments:
        models {List[feyn.Model]} -- The list of models to find the best ones in.

    Keyword Arguments:
        n {int} -- The maximum number of best models to identify. (default: {10})
        distance_func {Optional[Callable[[feyn.Model, feyn.Model], bool]]} -- Function to calculate model distance with. If the return is False, the model in the first argument is not sufficiently distant and not considered. If no function is specified, this defaults to being sufficiently distant in the QLattice. (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if models is an empty list.

    Returns:
        List[feyn.Model] -- The best sufficiently diverse models under distance_func.
    """
    if len(models) == 0:
        raise ValueError("Empty list of models passed as argument.")

    if hasattr(models[0], "_program"):
        return _best_diverse_models_v2(models)

    lattice_shape = _infer_shape(models)

    dist_func = distance_func or partial(_dist_x, lattice_shape=lattice_shape)

    if not isinstance(dist_func(models[0], models[0]), bool):
        _raise("distance_func", Callable[[feyn.Model, feyn.Model], bool])

    res = []
    for m in models:
        if not all(dist_func(m, other) for other in res):
            continue
        res.append(m)
        if len(res) >= n:
            break
    return res


def _infer_shape(models: List[feyn.Model]):
    """Infer the shape of the QLattice based on the models that were sampled from it."""
    x = max(m[-1]._latticeloc[0] for m in models)
    y = max(m[-1]._latticeloc[1] for m in models)
    z = max(m[-1]._latticeloc[2] for m in models)
    return x, y, z


def _output_locs_set(models: List[feyn.Model]) -> Set[int]:
    """Set of output x locations of from models."""
    return set(m[-1]._latticeloc[0] for m in models)


def _model_should_decay(model: feyn.Model, loc_density: int, max_density: int) -> bool:
    """Calculate the half-life of the model and decide if it should die."""
    A0 = _HalfLife_params.get("A0", 200)
    n = _HalfLife_params.get("n", 20)
    tau = _HalfLife_params.get("tau", 0.693)
    return model.age > A0 * exp(-loc_density / (max_density / (n * tau))) + 1


def _dist_x(
    model: feyn.Model,
    model_: feyn.Model,
    lattice_shape: Tuple[int, int, int],
    min_dist=3,
) -> bool:
    """Find the x distance in lattice space between two input models."""
    mx = model[-1]._latticeloc[0]
    mx_ = model_[-1]._latticeloc[0]

    mod = lattice_shape[0]
    d = abs(mx_ - mx) % mod
    return min(d, mod - d) >= min_dist
