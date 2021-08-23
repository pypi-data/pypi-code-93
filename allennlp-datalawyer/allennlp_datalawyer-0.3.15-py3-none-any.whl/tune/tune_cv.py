"""
The `train` subcommand can be used to train a model.
It requires a configuration file and a directory in
which to write the results.
"""

import argparse
import json
import logging
import os
import numpy as np

from typing import Dict
from functools import partial

import allennlp
from allennlp.common import util as common_util
from allennlp.common.params import Params
from allennlp.commands.subcommand import Subcommand
from allennlp.commands.train import TrainModel

import optuna
from optuna import Trial
from optuna.integration.allennlp import _fetch_pruner_config, _PRUNER_KEYS, _PRUNER_CLASS, _MONITOR, _TRIAL_ID, \
    _STORAGE_NAME, _STUDY_NAME, _PREFIX
from overrides import overrides

import _jsonnet

logger = logging.getLogger(__name__)


def tune_cv(args: argparse.Namespace) -> None:
    config_file = args.param_path
    hparam_path = args.hparam_path
    n_folds = args.n_folds
    optuna_param_path = args.optuna_param_path
    serialization_dir = args.serialization_dir
    include_package = args.include_package

    load_if_exists = args.skip_if_exists
    direction = args.direction
    n_trials = args.n_trials
    timeout = args.timeout
    study_name = args.study_name
    storage = args.storage
    metrics = args.metrics

    os.makedirs(serialization_dir, exist_ok=True)

    for package_name in include_package:
        allennlp.common.util.import_module_and_submodules(package_name)

    def _is_encodable(value: str) -> bool:
        # https://github.com/allenai/allennlp/blob/master/allennlp/common/params.py#L77-L85
        return (value == "") or (value.encode("utf-8", "ignore") != b"")

    def _environment_variables() -> Dict[str, str]:
        return {key: value for key, value in os.environ.items() if _is_encodable(value)}

    def load_params(trial: Trial, config_file: str) -> Params:
        pruner_params = _fetch_pruner_config(trial)
        pruner_params = {
            "{}_{}".format(_PREFIX, key): str(value) for key, value in pruner_params.items()
        }

        system_attrs = {
            _STUDY_NAME: trial.study.study_name,
            _TRIAL_ID: str(trial._trial_id),
            _STORAGE_NAME: trial.study._storage._backend.url,
            _MONITOR: metrics,
            _PRUNER_KEYS: ",".join(pruner_params.keys()),
        }

        if trial.study.pruner is not None:
            system_attrs[_PRUNER_CLASS] = type(trial.study.pruner).__name__

        system_attrs.update(pruner_params)

        for key, value in system_attrs.items():
            os.environ[key] = value

        dict_params = _environment_variables()
        dict_params.update({key: str(value) for key, value in trial.params.items()})
        dict_params.update(system_attrs)
        params = allennlp.common.params.Params(
            json.loads(_jsonnet.evaluate_file(config_file, ext_vars=dict_params))
        )
        common_util.prepare_environment(params)
        return params

    def define_params_per_fold(trial: Trial, n_folds: int) -> Dict[int, Params]:

        params_per_fold: Dict[int, Params] = dict()

        for fold in range(n_folds):
            os.environ['FOLD'] = str(fold)
            params_per_fold[fold] = load_params(trial, config_file)

        return params_per_fold

    def _objective_cv(trial: Trial,
                      hparam_path: str,
                      n_folds: int) -> np.float:

        for hparam in json.load(open(hparam_path)):
            attr_type = hparam["type"]
            suggest = getattr(trial, "suggest_{}".format(attr_type))
            suggest(**hparam["attributes"])

        optuna_serialization_dir = os.path.join(serialization_dir, "trial_{}".format(trial.number))
        params_per_fold = define_params_per_fold(trial, n_folds)
        scores = []
        for fold in range(n_folds):
            os.environ['FOLD'] = str(fold)
            _serialization_dir = os.path.join(optuna_serialization_dir, "fold_{}".format(fold))
            train_loop = TrainModel.from_params(
                params=params_per_fold[fold],
                serialization_dir=_serialization_dir,
                local_rank=0,
            )
            loop_metrics = train_loop.run()
            train_loop.finish(loop_metrics)
            scores.append(loop_metrics[metrics])
        return np.mean(scores).item()

    if optuna_param_path is not None and os.path.isfile(optuna_param_path):
        optuna_config = json.load(open(optuna_param_path))
    else:
        optuna_config = {}

    if "pruner" in optuna_config:
        pruner_class = getattr(optuna.pruners, optuna_config["pruner"]["type"])
        pruner = pruner_class(**optuna_config["pruner"].get("attributes", {}))
    else:
        pruner = None

    if "sampler" in optuna_config:
        sampler_class = getattr(optuna.samplers, optuna_config["sampler"]["type"])
        sampler = sampler_class(optuna_config["sampler"].get("attributes", {}))
    else:
        sampler = None

    study = optuna.create_study(
        study_name=study_name,
        direction=direction,
        storage=storage,
        pruner=pruner,
        sampler=sampler,
        load_if_exists=load_if_exists,
    )

    objective_cv = partial(
        _objective_cv,
        hparam_path=hparam_path,
        n_folds=n_folds
    )
    study.optimize(objective_cv, n_trials=n_trials, timeout=timeout)


@Subcommand.register("tune-cv")
class Tune(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction) -> argparse.ArgumentParser:
        description = """Train the specified model on the specified dataset."""
        subparser = parser.add_parser(self.name, description=description, help="Optimize hyperparameter of a model.")

        subparser.add_argument(
            "param_path",
            type=str,
            help="path to parameter file describing the model to be trained",
        )

        subparser.add_argument(
            "hparam_path",
            type=str,
            help="path to hyperparameter file",
            default="hyper_params.json",
        )

        subparser.add_argument(
            "--optuna-param-path",
            type=str,
            help="path to Optuna config",
        )

        subparser.add_argument(
            "--serialization-dir",
            required=True,
            type=str,
            help="directory in which to save the model and its logs",
        )

        # ---- Optuna -----

        subparser.add_argument(
            "--skip-if-exists",
            default=False,
            action="store_true",
            help="If specified, the creation of the study is skipped "
                 "without any error when the study name is duplicated.",
        )

        subparser.add_argument(
            "--direction",
            type=str,
            choices=("minimize", "maximize"),
            default="minimize",
            help="Set direction of optimization to a new study. Set 'minimize' "
                 "for minimization and 'maximize' for maximization.",
        )

        subparser.add_argument(
            "--n-trials",
            type=int,
            help="The number of trials. If this argument is not given, as many " "trials run as possible.",
            default=50,
        )

        subparser.add_argument(
            "--timeout",
            type=float,
            help="Stop study after the given number of second(s). If this argument"
                 " is not given, as many trials run as possible.",
        )

        subparser.add_argument(
            "--study-name", default=None, help="The name of the study to start optimization on."
        )

        subparser.add_argument(
            "--storage",
            type=str,
            help=(
                "The path to storage. "
                "allennlp-optuna supports a valid URL" "for sqlite3, mysql, postgresql, or redis."
            ),
            default="sqlite:///allennlp_optuna.db",
        )

        subparser.add_argument(
            "--metrics",
            type=str,
            help="The metrics you want to optimize.",
            default="best_validation_loss",
        )

        subparser.add_argument(
            "--n-folds",
            type=int,
            help="The number of folds in cross-validation. "
                 "Training config should have the datasets adapted to use the splits of this size.",
            default=10,
        )

        subparser.set_defaults(func=tune_cv)
        return subparser
