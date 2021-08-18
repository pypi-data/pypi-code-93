import argparse
import os
import sys
from typing import List, Optional, Text, Dict

from convo.cli import SubParsersAction
import convo.cli.arguments.train as train_arguments

import convo.cli.utils
from convo.shared.utils.cli import printing_error
from convo.shared.constants import (
    CONFIGURATION_MANDATORY_KEYS_CORE ,
    CONFIGURATION_MANDATORY_KEYS_NLU ,
    CONFIGURATION_MANDATORY_KEYS ,
    DEFAULT_CONFIGURATION_PATH,
    CONVO_DEFAULT_DOMAIN_PATH,
    CONVO_DEFAULT_DATA_PATH ,
)

import convo.utils.common


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all training parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    train_analyser = subparsers.add_parser(
        "train",
        help="Trains a Convo model using your NLU data and stories.",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    train_arguments.set_train_arguments(train_analyser)

    train_core_analyser = train_analyser.add_subparsers()
    train_core_parser = train_core_analyser.add_parser(
        "core",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Trains a Convo Core model using your stories.",
    )
    train_core_parser.set_defaults(func=supervise_core)

    train_nlu_analyser = train_core_analyser.add_parser(
        "nlu",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Trains a Convo NLU model using your NLU data.",
    )
    train_nlu_analyser.set_defaults(func=supervise_nlu)

    train_analyser.set_defaults(func=train)

    train_arguments.set_train_core_arguments(train_core_parser)
    train_arguments.set_train_nlu_arguments(train_nlu_analyser)


def train(args: argparse.Namespace) -> Optional[Text]:
    import convo

    domain_name = convo.cli.utils.fetch_validated_path(
        args.domain, "domain", CONVO_DEFAULT_DOMAIN_PATH, none_is_valid=True
    )

    configuration = _fetch_valid_configuration(args.config, CONFIGURATION_MANDATORY_KEYS)

    training_file = [
        convo.cli.utils.fetch_validated_path(
            f, "data", CONVO_DEFAULT_DATA_PATH , none_is_valid=True
        )
        for f in args.data
    ]

    return convo.train(
        domain=domain_name,
        config=configuration,
        training_files=training_file,
        output=args.out,
        force_training=args.force,
        fixed_model_name=args.fixed_model_name,
        persist_nlu_training_data=args.persist_nlu_data,
        core_additional_args=extract_core_additional_args(args),
        nlu_additional_args=extract_nlu_additional_args(args),
    )


def supervise_core(
    args: argparse.Namespace, train_path: Optional[Text] = None
) -> Optional[Text]:
    from convo.train import supervise_core

    result = train_path or args.out

    args.domain = convo.cli.utils.fetch_validated_path(
        args.domain, "domain", CONVO_DEFAULT_DOMAIN_PATH, none_is_valid=True
    )
    stories_files = convo.cli.utils.fetch_validated_path(
        args.stories, "stories", CONVO_DEFAULT_DATA_PATH , none_is_valid=True
    )
    add_on_arguments = extract_core_additional_args(args)

    # Policies might be a list for the compare training. Do normal training
    # if only list item was passed.
    if not isinstance(args.config, list) or len(args.config) == 1:
        if isinstance(args.config, list):
            args.config = args.config[0]

        configuration = _fetch_valid_configuration(args.config, CONFIGURATION_MANDATORY_KEYS_CORE)

        return supervise_core(
            domain=args.domain,
            config=configuration,
            stories=stories_files,
            output=result,
            train_path=train_path,
            fixed_model_name=args.fixed_model_name,
            add_on_arguments=add_on_arguments,
        )
    else:
        from convo.core.train import do_compare_training

        convo.utils.common.running_in_loop(
            do_compare_training(args, stories_files, add_on_arguments)
        )


def supervise_nlu(
    args: argparse.Namespace, train_path: Optional[Text] = None
) -> Optional[Text]:
    from convo.train import supervise_nlu

    result = train_path or args.out

    config = _fetch_valid_configuration(args.config, CONFIGURATION_MANDATORY_KEYS_NLU )
    nlu_data_set = convo.cli.utils.fetch_validated_path(
        args.nlu, "nlu", CONVO_DEFAULT_DATA_PATH , none_is_valid=True
    )

    if args.domain:
        args.domain = convo.cli.utils.fetch_validated_path(
            args.domain, "domain", CONVO_DEFAULT_DOMAIN_PATH, none_is_valid=True
        )

    return supervise_nlu(
        config=config,
        nlu_data=nlu_data_set,
        output=result,
        train_path=train_path,
        fixed_model_name=args.fixed_model_name,
        persist_nlu_training_data=args.persist_nlu_data,
        add_on_arguments=extract_nlu_additional_arguments(args),
        domain=args.domain,
    )


def extract_core_additional_args(args: argparse.Namespace) -> Dict:
    arguments = {}

    if "augmentation" in args:
        arguments["augmentation_factor"] = args.augmentation
    if "debug_plots" in args:
        arguments["debug_plots"] = args.debug_plots

    return arguments


def extract_nlu_additional_args(args: argparse.Namespace) -> Dict:
    arguments = {}

    if "num_threads" in args:
        arguments["num_threads"] = args.num_threads

    return arguments


def _fetch_valid_configuration(
    configuration: Optional[Text],
    mandatory_keys: List[Text],
    default_config: Text = DEFAULT_CONFIGURATION_PATH,
) -> Text:
    """Get a config from a config file and check if it is valid.

    Exit if the config isn't valid.

    Args:
        configuration: Path to the config file.
        mandatory_keys: The keys that have to be specified in the config file.
        default_config: default config to use if the file at `config` doesn't exist.

    Returns: The path to the config file if the config is valid.
    """
    configuration = convo.cli.utils.fetch_validated_path(configuration, "config", default_config)

    if not os.path.exists(configuration):
        printing_error(
            "The config file '{}' does not exist. Use '--config' to specify a "
            "valid config file."
            "".format(configuration)
        )
        sys.exit(1)

    lost_keys = convo.cli.utils.lost_configuration_keys(configuration, mandatory_keys)
    if lost_keys:
        printing_error(
            "The config file '{}' is missing mandatory parameters: "
            "'{}'. Add missing parameters to config file and try again."
            "".format(configuration, "', '".join(lost_keys))
        )
        sys.exit(1)

    return configuration  # pytype: disable=bad-return-type
