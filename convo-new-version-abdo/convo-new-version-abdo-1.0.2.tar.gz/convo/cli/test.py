import argparse
import logging
import os
from typing import List

from convo.cli import SubParsersAction
import convo.shared.data
from convo.shared.exceptions import YamlExceptions 
import convo.shared.utils.io
import convo.shared.utils.cli
from convo.cli.arguments import test as arguments
from convo.shared.constants import (
    CONFIGURATION_SCHEMA_FILE ,
    DEFAULT_E2E_TEST_PATH ,
    DEFAULT_CONFIGURATION_PATH,
    DEFAULT_MODEL_PATH ,
    CONVO_DEFAULT_DATA_PATH ,
    DEFAULT_RESULT_PATH ,
)
import convo.shared.utils.validation as validation_utils
import convo.cli.utils

log = logging.getLogger(__name__)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all test parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    test_parser = subparsers.add_parser(
        "test",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Tests Convo models using your test NLU data and stories.",
    )

    arguments.set_testing_arguments(test_parser)

    test_subparsers = test_parser.add_subparsers()
    test_core_parser = test_subparsers.add_parser(
        "core",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Tests Convo Core models using your test stories.",
    )
    arguments.set_testing_core_arguments(test_core_parser)

    nlu_parser_testing = test_subparsers.add_parser(
        "nlu",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Tests Convo NLU models using your test NLU data.",
    )
    arguments.set_testing_nlu_arguments(nlu_parser_testing)

    test_core_parser.set_defaults(func=execute_core_test)
    nlu_parser_testing.set_defaults(func=execute_nlu_test)
    test_parser.set_defaults(func=test, stories=DEFAULT_E2E_TEST_PATH)


def execute_core_test(args: argparse.Namespace) -> None:
    """Run core tests."""
    from convo.test import test_core_models_in_dir, test_core, testiing_core_model

    stroy = convo.cli.utils.fetch_validated_path(
        args.stories, "stories", CONVO_DEFAULT_DATA_PATH 
    )
    if args.e2e:
        stroy = convo.shared.data.get_test_dir (stroy)
    else:
        stroy = convo.shared.data.get_core_dir(stroy)

    result = args.out or DEFAULT_RESULT_PATH
    args.errors = not args.no_errors

    convo.shared.utils.io.create_dir(result)

    if isinstance(args.model, list) and len(args.model) == 1:
        args.model = args.model[0]

    if args.model is None:
        convo.shared.utils.cli.printing_error(
            "No model provided. Please make sure to specify the model to test with '--model'."
        )
        return

    if isinstance(args.model, str):
        model_path = convo.cli.utils.fetch_validated_path(
            args.model, "model", DEFAULT_MODEL_PATH 
        )

        if args.evaluate_model_directory:
            test_core_models_in_dir(args.model, stroy, result)
        else:
            test_core(
                model=model_path,
                stories=stroy,
                output=result,
                add_on_arguments=vars(args),
            )

    else:
        testiing_core_model(args.model, stroy, result)


def execute_nlu_test(args: argparse.Namespace) -> None:
    """Run NLU tests."""
    from convo.test import comparison_nlu_models, execute_nlu_cross_validate, test_nlu

    nlu_data_set = convo.cli.utils.fetch_validated_path(args.nlu, "nlu", CONVO_DEFAULT_DATA_PATH)
    nlu_data_set = convo.shared.data.get_nlu_directory(nlu_data_set)
    result = args.out or DEFAULT_RESULT_PATH
    args.errors = not args.no_errors

    convo.shared.utils.io.create_dir(result)

    if args.config is not None and len(args.config) == 1:
        args.config = os.path.abspath(args.config[0])
        if os.path.isdir(args.config):
            args.config = convo.shared.utils.io.listing_files(args.config)

    if isinstance(args.config, list):
        log.info(
            "Multiple configuration files specified, running nlu comparison mode."
        )

        configuration_files = []
        for file in args.config:
            try:
                validation_utils.validating_yaml_schema(
                    convo.shared.utils.io.read_file(file), CONFIGURATION_SCHEMA_FILE ,
                )
                configuration_files.append(file)
            except YamlExceptions:
                convo.shared.utils.io.raising_warning(
                    f"Ignoring file '{file}' as it is not a valid config file."
                )
                continue

        comparison_nlu_models(
            configs=configuration_files,
            nlu=nlu_data_set,
            output=result,
            runs=args.runs,
            exclusion_percentages=args.percentages,
        )
    elif args.cross_validation:
        log.info("Test model using cross validation.")
        config = convo.cli.utils.fetch_validated_path(
            args.config, "config", DEFAULT_CONFIGURATION_PATH
        )
        execute_nlu_cross_validate(config, nlu_data_set, result, vars(args))
    else:
        model_path_flow = convo.cli.utils.fetch_validated_path(
            args.model, "model", DEFAULT_MODEL_PATH 
        )

        test_nlu(model_path_flow, nlu_data_set, result, vars(args))


def test(args: argparse.Namespace):
    """Run end-to-end tests."""
    setattr(args, "e2e", True)
    execute_core_test(args)
    execute_nlu_test(args)
