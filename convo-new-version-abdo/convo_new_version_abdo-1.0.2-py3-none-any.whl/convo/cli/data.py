import argparse
import logging
import os
import shutil
from pathlib import Path
from typing import List, Text, Dict

import convo.shared.core.domain
from convo import telemetry
from convo.cli import SubParsersAction
from convo.cli.arguments import data as arguments
import convo.cli.utils
import convo.nlu.convert
from convo.shared.constants import (
    CONVO_DEFAULT_DATA_PATH ,
    DEFAULT_CONFIGURATION_PATH,
    CONVO_DEFAULT_DOMAIN_PATH,
    MIGRATION_GUIDE_DOCUMENTS_URL,
)
import convo.shared.data
from convo.shared.core.constants import (
    USERS_INTENT_OUT_OF_SCOPE  ,
    ACTION_DEFAULT_FALLBACK_NAME,
)
from convo.shared.core.training_data.story_reader.yaml_story_reader import (
    YAMLStoryReviewer,
)
from convo.shared.core.training_data.story_writer.yaml_story_writer import (
    YAMLStoryAuthor,
)
from convo.shared.core.training_data.structures import StoryStage
from convo.shared.importers.convo import FileImporter
import convo.shared.nlu.training_data.loading
import convo.shared.nlu.training_data.util
import convo.shared.utils.cli
import convo.utils.common
from convo.utils.converter import TrainingDataSetModifier
from convo.validator import Validate
from convo.shared.core.domain import Domain, InvalidDomain
import convo.shared.utils.io
import convo.core.config
from convo.core.policies.form_policy import FormPolicy
from convo.core.policies.fallback import PolicyFallback
from convo.core.policies.two_stage_fallback import TwoStageFallbackPolicy
from convo.core.policies.mapping_policy import MappingPolicy

logger = logging.getLogger(__name__)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all data parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    data_set_parser = subparsers.add_parser(
        "data",
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Utils for the Convo training files.",
    )
    data_set_parser.set_defaults(func=lambda _: data_set_parser.print_help(None))

    data_set_subparsers = data_set_parser.add_subparsers()

    _append_data_conversion_parsers(data_set_subparsers, parents)
    _append_data_split_parsers(data_set_subparsers, parents)
    _append_data_validate_parsers(data_set_subparsers, parents)


def _append_data_conversion_parsers(
    data_subparsers, parents: List[argparse.ArgumentParser]
) -> None:
    transform_parser = data_subparsers.add_parser(
        "convert",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Converts Convo data between different formats.",
    )
    transform_parser.set_defaults(func=lambda _: transform_parser.print_help(None))

    transform_subparsers = transform_parser.add_subparsers()
    transform_nlu_parser = transform_subparsers.add_parser(
        "nlu",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Converts NLU data between formats.",
    )
    transform_nlu_parser.set_defaults(func=_nlu_data_conversion)

    arguments.set_convert_argument(transform_nlu_parser, data_type="Convo NLU")

    transform_nlg_parser = transform_subparsers.add_parser(
        "nlg",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Converts NLG data between formats.",
    )
    transform_nlg_parser.set_defaults(func=_nlg_data_conversion)

    arguments.set_convert_argument(transform_nlg_parser, data_type="Convo NLG")

    transform_core_parser = transform_subparsers.add_parser(
        "core",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Converts Core data between formats.",
    )
    transform_core_parser.set_defaults(func=_core_data_conversion)

    arguments.set_convert_argument(transform_core_parser, data_type="Convo Core")

    migrate_configuration_parser = transform_subparsers.add_parser(
        "config",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Migrate model configuration between Convo Open Source versions.",
    )
    migrate_configuration_parser.set_defaults(func=_migrate_model_configuration)
    _append_migrate_configuration_args(migrate_configuration_parser)


def _append_migrate_configuration_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_CONFIGURATION_PATH,
        help="Path to the model configuration which should be migrated",
    )
    parser.add_argument(
        "-d", "--domain", default=CONVO_DEFAULT_DOMAIN_PATH, help="Path to the model domain"
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default=os.path.join(CONVO_DEFAULT_DATA_PATH , "rules.yml"),
        help="Path to the file which should contain any rules which are created as "
        "part of the migration. If the file doesn't exist, it will be created.",
    )


def _append_data_split_parsers(
    data_subparsers, parents: List[argparse.ArgumentParser]
) -> None:
    split_parser = data_subparsers.add_parser(
        "split",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Splits Convo data into training and test data.",
    )
    split_parser.set_defaults(func=lambda _: split_parser.print_help(None))

    separate_subparsers = split_parser.add_subparsers()
    separate_nlu_parser = separate_subparsers.add_parser(
        "nlu",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Performs a split of your NLU data into training and test data "
        "according to the specified percentages.",
    )
    separate_nlu_parser.set_defaults(func=split_nlu_data_set)

    arguments.set_split_argument(separate_nlu_parser)


def _append_data_validate_parsers(
    data_subparsers, parents: List[argparse.ArgumentParser]
) -> None:
    verify_parser = data_subparsers.add_parser(
        "validate",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Validates domain and data files to check for possible mistakes.",
    )
    _add_story_structure_args(verify_parser)
    verify_parser.set_defaults(func=verify_files)
    arguments.set_validator_argument(verify_parser)

    verify_subparsers = verify_parser.add_subparsers()
    stories_struct_parser = verify_subparsers.add_parser(
        "stories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="Checks for inconsistencies in the story files.",
    )
    _add_story_structure_args(stories_struct_parser)
    stories_struct_parser.set_defaults(func=verify_stories)
    arguments.set_validator_argument(stories_struct_parser)


def _add_story_structure_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--max-history",
        type=int,
        default=None,
        help="Number of turns taken into account for story structure validation.",
    )


def split_nlu_data_set(args: argparse.Namespace) -> None:
    """Load data from a file path and split the NLU data into test and train examples.

    Args:
        args: Commandline arguments
    """
    data_set_path_flow = convo.cli.utils.fetch_validated_path(args.nlu, "nlu", CONVO_DEFAULT_DATA_PATH)
    data_set_path_flow = convo.shared.data.get_nlu_directory(data_set_path_flow)

    nlu_data_set = convo.shared.nlu.training_data.loading.load_data_set(data_set_path_flow)
    extension_ = convo.shared.nlu.training_data.util.fetch_file_format_ext(data_set_path_flow)

    train_, data_test = nlu_data_set.training_test_split(args.training_fraction, args.random_seed)

    train_.persist(args.out, filename=f"training_data{extension_}")
    data_test.persist(args.out, filename=f"test_data{extension_}")

    telemetry.track_data_split(args.training_fraction, "nlu")


def verify_files(args: argparse.Namespace, stories_only: bool = False) -> None:
    """Validates either the story structure or the entire project.

    Args:
        args: Commandline arguments
        stories_only: If `True`, only the story structure is validated.
    """
    file_importer = FileImporter(
        domain_path=args.domain, training_data_paths=args.data
    )

    validate = convo.utils.common.running_in_loop(Validate.importers(file_importer))

    if stories_only:
        all_is_well = _validate_story_structure(validate, args)
    else:
        all_is_well = (
            _verify_domain(validate)
            and _verify_nlu(validate, args)
            and _validate_story_structure(validate, args)
        )

    telemetry.traverse_validate_files(all_is_well)
    if not all_is_well:
        convo.shared.utils.cli.printing_error_exit(
            "Project validation completed with errors."
        )


def verify_stories(args: argparse.Namespace) -> None:
    """Validates that training data file content conforms to training data spec.

    Args:
        args: Commandline arguments
    """
    verify_files(args, stories_only=True)


def _verify_domain(validator: Validate) -> bool:
    return validator.domain_validity_verification()


def _verify_nlu(validator: Validate, args: argparse.Namespace) -> bool:
    return validator.nlu_verification(not args.fail_on_warnings)


def _validate_story_structure(validator: Validate, args: argparse.Namespace) -> bool:
    # Check if a valid setting for `max_history` was given
    if isinstance(args.max_history, int) and args.max_history < 1:
        raise argparse.ArgumentTypeError(
            f"The value of `--max-history {args.max_history}` is not a positive integer."
        )

    return validator.story_structure_varification(
        not args.fail_on_warnings, max_history=args.max_history
    )


def _nlu_data_conversion(args: argparse.Namespace) -> None:
    from convo.nlu.training_data.converters.nlu_markdown_to_yaml_converter import (
        NLUMarkdown_To_YamlConverter,
    )

    if args.format in ["json", "md"]:
        convo.nlu.convert.training_data_conversion(
            args.data, args.out, args.format, args.language
        )
        telemetry.traverse_data_convert(args.format, "nlu")
    elif args.format == "yaml":
        convo.utils.common.running_in_loop(
            _conversion_to_yaml(args, NLUMarkdown_To_YamlConverter())
        )
        telemetry.traverse_data_convert(args.format, "nlu")
    else:
        convo.shared.utils.cli.printing_error_exit(
            "Could not recognize output format. Supported output formats: 'json', "
            "'md', 'yaml'. Specify the desired output format with '--format'."
        )


def _core_data_conversion(args: argparse.Namespace) -> None:
    from convo.core.training.converters.story_markdown_to_yaml_converter import (
        StoryMarkdownToYamlConverter,
    )

    if args.format == "yaml":
        convo.utils.common.running_in_loop(
            _conversion_to_yaml(args, StoryMarkdownToYamlConverter())
        )
        telemetry.traverse_data_convert(args.format, "core")
    else:
        convo.shared.utils.cli.printing_error_exit(
            "Could not recognize output format. Supported output formats: "
            "'yaml'. Specify the desired output format with '--format'."
        )


def _nlg_data_conversion(args: argparse.Namespace) -> None:
    from convo.nlu.training_data.converters.nlg_markdown_to_yaml_converter import (
        NLGMarkdown_To_YamlConverter,
    )

    if args.format == "yaml":
        convo.utils.common.running_in_loop(
            _conversion_to_yaml(args, NLGMarkdown_To_YamlConverter())
        )
        telemetry.traverse_data_convert(args.format, "nlg")
    else:
        convo.shared.utils.cli.printing_error_exit(
            "Could not recognize output format. Supported output formats: "
            "'yaml'. Specify the desired output format with '--format'."
        )


async def _conversion_to_yaml(
    args: argparse.Namespace, converter: TrainingDataSetModifier
) -> None:

    output = Path(args.out)
    if not os.path.exists(output):
        convo.shared.utils.cli.printing_error_exit(
            f"The output path '{output}' doesn't exist. Please make sure to specify "
            f"an existing dir and try again."
        )

    training_data_set = Path(args.data)
    if not os.path.exists(training_data_set):
        convo.shared.utils.cli.printing_error_exit(
            f"The training data path {training_data_set} doesn't exist "
            f"and will be skipped."
        )

    number_of_files_converted = 0

    if os.path.isfile(training_data_set):
        if await _convert_file_to_yaml(training_data_set, output, converter):
            number_of_files_converted += 1
    elif os.path.isdir(training_data_set):
        for root, _, files in os.walk(training_data_set, followlinks=True):
            for f in sorted(files):
                source_path = Path(os.path.join(root, f))
                if await _convert_file_to_yaml(source_path, output, converter):
                    number_of_files_converted += 1

    if number_of_files_converted:
        convo.shared.utils.cli.printing_information(
            f"Converted {number_of_files_converted} file(s), saved in '{output}'."
        )
    else:
        convo.shared.utils.cli.printing_warning(
            f"Didn't convert any files under '{training_data_set}' path. "
            "Did you specify the correct file/directory?"
        )


async def _convert_file_to_yaml(
    source_file: Path, target_dir: Path, converter: TrainingDataSetModifier
) -> bool:
    """Converts a single training data file to `YAML` format.

    Args:
        source_file: Training data file to be converted.
        target_dir: Target dir for the converted file.
        converter: Converter to be used.

    Returns:
        `True` if file was converted, `False` otherwise.
    """
    if not convo.shared.data.filetype_validity(source_file):
        return False

    if converter.filter(source_file):
        await converter.converting_and_writing(source_file, target_dir)
        return True

    convo.shared.utils.cli.printing_warning(f"Skipped file: '{source_file}'.")

    return False


def _migrate_model_configuration(args: argparse.Namespace) -> None:
    """Migrates old "rule-like" policies to the new `RulePolicy`.

    Updates the config, domain, and generates the required rules.

    Args:
        args: The commandline args with the required convo_paths.
    """
    config_file = Path(args.config)
    model_config = _get_config(config_file)

    domain_files = Path(args.domain)
    domain_name = _domain(domain_files)

    rule_output_file = _fetch_rules_path(args.out)

    (
        model_config,
        domain_name,
        new_rules,
    ) = convo.core.config.migrate_mapping_policy_to_rules(model_config, domain_name)

    model_config, fallback_rule = convo.core.config.migrate_fall_back_policies(
        model_config
    )

    if new_rules:
        _stand_by(domain_files)
        domain_name.persist_trash(domain_files)

    if fallback_rule:
        new_rules.append(fallback_rule)

    if new_rules:
        _stand_by(config_file)
        convo.shared.utils.io.writing_yaml(model_config, config_file)
        _dump_protocol(rule_output_file, new_rules)

    telemetry.traverse_data_convert("yaml", "config")

    _print_success_msg(new_rules, rule_output_file)


def _get_config(path: Path) -> Dict:
    config = {}
    try:
        config = convo.shared.utils.io.read_configuration_file(path)
    except Exception:
        convo.shared.utils.cli.printing_error_exit(
            f"'{path}' is not a path to a valid model configuration. "
            f"Please provide a valid path."
        )

    policy_names = [p.get("name") for p in config.get("policies", [])]

    _assert_configuration_needs_migration(policy_names)
    _given_nlu_pipeline_assertion(config, policy_names)
    _assertion_two_step_fallback_protocol_is_migratable(config)
    _assertion_just_one_fallback_protocol_present(policy_names)

    if FormPolicy.__name__ in policy_names:
        _warning_manual_forms_migration()

    return config


def _assert_configuration_needs_migration(policies: List[Text]) -> None:
    migratable_policies = {
        MappingPolicy.__name__,
        PolicyFallback.__name__,
        TwoStageFallbackPolicy.__name__,
    }

    if not migratable_policies.intersection((set(policies))):
        convo.shared.utils.cli.printing_error_exit(
            f"No policies were found which need migration. This command can migrate "
            f"'{MappingPolicy.__name__}', '{PolicyFallback.__name__}' and "
            f"'{TwoStageFallbackPolicy.__name__}'."
        )


def _warning_manual_forms_migration() -> None:
    convo.shared.utils.cli.printing_warning(
        f"Your model configuration contains the '{FormPolicy.__name__}'. "
        f"Note that this command does not migrate the '{FormPolicy.__name__}' and "
        f"you have to migrate the '{FormPolicy.__name__}' manually. "
        f"Please see the migration guide for further details: "
        f"{MIGRATION_GUIDE_DOCUMENTS_URL}"
    )


def _given_nlu_pipeline_assertion(config: Dict, policy_names: List[Text]) -> None:
    if not config.get("pipeline") and any(
        policy in policy_names
        for policy in [PolicyFallback.__name__, TwoStageFallbackPolicy.__name__]
    ):
        convo.shared.utils.cli.printing_error_exit(
            "The model configuration has to include an NLU pipeline. This is required "
            "in order to migrate the fallback policies."
        )


def _assertion_two_step_fallback_protocol_is_migratable(config: Dict) -> None:
    two_stage_fallback_config = next(
        (
            policy_config
            for policy_config in config.get("policies", [])
            if policy_config.get("name") == TwoStageFallbackPolicy.__name__
        ),
        None,
    )
    if not two_stage_fallback_config:
        return

    if (
        two_stage_fallback_config.get(
            "deny_suggestion_name_of_intent", USERS_INTENT_OUT_OF_SCOPE  
        )
        != USERS_INTENT_OUT_OF_SCOPE  
    ):
        convo.shared.utils.cli.printing_error_exit(
            f"The TwoStageFallback in Convo Open Source 2.0 has to use the intent "
            f"'{USERS_INTENT_OUT_OF_SCOPE  }' to recognize when users deny suggestions. "
            f"Please change the parameter 'deny_suggestion_name_of_intent' to "
            f"'{USERS_INTENT_OUT_OF_SCOPE  }' before migrating the model configuration. "
        )

    if (
        two_stage_fallback_config.get(
            "fallback_nlu_action_name", ACTION_DEFAULT_FALLBACK_NAME
        )
        != ACTION_DEFAULT_FALLBACK_NAME
    ):
        convo.shared.utils.cli.printing_error_exit(
            f"The Two-Stage Fallback in Convo Open Source 2.0 has to use the action "
            f"'{ACTION_DEFAULT_FALLBACK_NAME}' for cases when the user denies the "
            f"suggestion multiple times. "
            f"Please change the parameter 'fallback_nlu_action_name' to "
            f"'{ACTION_DEFAULT_FALLBACK_NAME}' before migrating the model "
            f"configuration. "
        )


def _assertion_just_one_fallback_protocol_present(policies: List[Text]) -> None:
    if (
        PolicyFallback.__name__ in policies
        and TwoStageFallbackPolicy.__name__ in policies
    ):
        convo.shared.utils.cli.printing_error_exit(
            "Your policy configuration contains two configured policies for handling "
            "fallbacks. Please decide on one."
        )


def _domain(path: Path) -> Domain:
    try:
        return Domain.from_path(path)
    except InvalidDomain:
        convo.shared.utils.cli.printing_error_exit(
            f"'{path}' is not a path to a valid domain file. "
            f"Please provide a valid domain."
        )


def _fetch_rules_path(path: Text) -> Path:
    rules_file = Path(path)

    if rules_file.is_dir():
        convo.shared.utils.cli.printing_error_exit(
            f"'{rules_file}' needs to be the path to a file."
        )

    if not rules_file.is_file():
        convo.shared.utils.cli.printing_information(
            f"Output file '{rules_file}' did not exist and will be created."
        )
        convo.shared.utils.io.create_dir_from_file(rules_file)

    return rules_file


def _dump_protocol(path: Path, new_rules: List[StoryStage]) -> None:
    existing_rules = []
    if path.exists():
        rules_reader = YAMLStoryReviewer()
        existing_rules = rules_reader.readFromFile(path)
        _stand_by(path)

    if existing_rules:
        convo.shared.utils.cli.printing_information(
            f"Found existing rules in the output file '{path}'. The new rules will "
            f"be appended to the existing rules."
        )

    protocol_writer = YAMLStoryAuthor()
    protocol_writer.dump(path, existing_rules + new_rules)


def _stand_by(path: Path) -> None:
    backup_files = path.parent / f"{path.name}.bak"
    shutil.copy(path, backup_files)


def _print_success_msg(new_rules: List[StoryStage], output_file: Path) -> None:
    if len(new_rules) > 1:
        postfix = "rule"
        data_verb = "was"
    else:
        postfix = "rules"
        data_verb = "were"

    convo.shared.utils.cli.printing_success(
        f"Finished migrating your policy configuration 🎉.\n"
        f"The migration generated {len(new_rules)} {postfix} which {data_verb} added to "
        f"'{output_file}'."
    )
