import copy
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Text, Dict, Any, List, Set, Optional

import convo.shared.constants
import convo.shared.utils.cli
import convo.shared.utils.common
import convo.shared.utils.io

log = logging.getLogger(__name__)

COMMENT_FOR_KEYS = {
    "pipeline": (
        f"# # No configuration for the NLU pipeline was provided. The following "
        f"default pipeline was used to train your model.\n"
        f"# # If you'd like to customize it, uncomment and adjust the pipeline.\n"
        f"# # See {convo.shared.constants.PIPELINE_DOCUMENTS_URL } for more information.\n"
    ),
    "policies": (
        f"# # No configuration for policies was provided. The following default "
        f"policies were used to train your model.\n"
        f"# # If you'd like to customize them, uncomment and adjust the policies.\n"
        f"# # See {convo.shared.constants.POLICIES_DOCUMENTS_URL } for more information.\n"
    ),
}


class TrainingClassification(Enum):
    NLU = 1
    CORE = 2
    TWO = 3


def get_config(
    config_file_path: Text, training_type: Optional[TrainingClassification] = TrainingClassification.TWO
) -> Dict[Text, Any]:
    """Determine configuration from a configuration file.

    Keys that are provided and have a value in the file are kept. Keys that are not
    provided are configured automatically.

    Args:
        config_file_path: The path to the configuration file.
        training_type: NLU, CORE or BOTH depending on what is trained.
    """
    if not config_file_path or not os.path.exists(config_file_path):
        log.debug("No configuration file was provided to the TrainingDataImporter.")
        return {}

    configuration = convo.shared.utils.io.read_configuration_file(config_file_path)

    missed_keys = get_missing_configuration_keys(configuration, training_type)
    keys_to_configuration = get_unspecified_auto_configurable_keys(configuration, training_type)

    if keys_to_configuration:
        configuration = auto_configuration(configuration, keys_to_configuration)
        dump_configuration(
            configuration, config_file_path, missed_keys, keys_to_configuration, training_type
        )

    return configuration


def get_unspecified_auto_configurable_keys(
    config: Dict[Text, Any], training_type: Optional[TrainingClassification] = TrainingClassification.TWO
) -> Set[Text]:
    if training_type == TrainingClassification.NLU:
        every_keys = convo.shared.constants.CONFIGURATION_AUTO_CONFIGURABLE_KEYS_NLU
    elif training_type == TrainingClassification.CORE:
        every_keys = convo.shared.constants.CONFIGURATION_AUTO_CONFIGURABLE_KEYS_CORE
    else:
        every_keys = convo.shared.constants.CONFIGURATION_AUTO_CONFIGURABLE_KEYS

    return {k for k in every_keys if not config.get(k)}


def get_missing_configuration_keys(
    config: Dict[Text, Any], training_type: Optional[TrainingClassification] = TrainingClassification.TWO
) -> Set[Text]:
    if training_type == TrainingClassification.NLU:
        every_keys = convo.shared.constants.CONFIGURATION_KEYS_NLU
    elif training_type == TrainingClassification.CORE:
        every_keys = convo.shared.constants.CONFIGURATION_KEYS_CORE
    else:
        every_keys = convo.shared.constants.CONFIGURATION_KEYS

    return {k for k in every_keys if k not in config.keys()}


def auto_configuration(
    configuration: Dict[Text, Any], keys_to_configure: Set[Text]
) -> Dict[Text, Any]:
    """Complete a config by adding automatic configuration for the specified keys.

    Args:
        configuration: The provided configuration.
        keys_to_configure: Keys to be configured automatically (e.g. `policies`).

    Returns:
        The resulting configuration including both the provided and the automatically
        configured keys.
    """
    import pkg_resources

    if keys_to_configure:
        log.debug(
            f"The provided configuration does not contain the key(s) "
            f"{convo.shared.utils.common.transforming_collection_to_sentence(keys_to_configure)}. "
            f"Values will be provided from the default configuration."
        )

    file_name = "default_config.yml"

    default_configuration_file = pkg_resources.resource_filename(__name__, file_name)
    default_configuration = convo.shared.utils.io.read_configuration_file(default_configuration_file)

    configuration = copy.deepcopy(configuration)
    for key in keys_to_configure:
        configuration[key] = default_configuration[key]

    return configuration


def dump_configuration(
    config: Dict[Text, Any],
    config_file_path: Text,
    missing_keys: Set[Text],
    autoconfigured_keys: Set[Text],
    training_type: Optional[TrainingClassification] = TrainingClassification.TWO,
) -> None:
    """Dump the automatically configured keys into the config file.

    The configuration provided in the file is kept as it is (preserving the order of
    keys and comments).
    For keys that were automatically configured, an explanatory comment is added and the
    automatically chosen configuration is added commented-out.
    If there are already blocks with comments from a previous auto configuration run,
    they are replaced with the new auto configuration.

    Args:
        config: The configuration including the automatically configured keys.
        config_file_path: The file into which the configuration should be dumped.
        missing_keys: Keys that need to be added to the config file.
        autoconfigured_keys: Keys for which a commented out auto configuration section
                              needs to be added to the config file.
        training_type: NLU, CORE or BOTH depending on which is trained.
    """

    configuration_as_expected = expected_configuration_file_check(
        config_file_path, missing_keys, autoconfigured_keys, training_type
    )
    if not configuration_as_expected:
        convo.shared.utils.cli.printing_error(
            f"The configuration file at '{config_file_path}' has been removed or "
            f"modified while the automatic configuration was running. The current "
            f"configuration will therefore not be dumped to the file. If you want to "
            f"your model to use the configuration provided in '{config_file_path}', "
            f"you need to re-run training."
        )
        return

    add_missing_configuration_keys_to_file(config_file_path, missing_keys)

    autoconfiguration_lines = get_commented_out_autoconfiguration_lines(config, autoconfigured_keys)

    current_configuration_content = convo.shared.utils.io.read_file(config_file_path)
    current_configuration_files = current_configuration_content.splitlines(keepends=True)

    update_lines = get_lines_including_auto_configuration(
        current_configuration_files, autoconfiguration_lines
    )

    convo.shared.utils.io.writing_text_file("".join(update_lines), config_file_path)

    autoconfigured_keys = convo.shared.utils.common.transforming_collection_to_sentence(
        autoconfigured_keys
    )
    convo.shared.utils.cli.printing_information(
        f"The configuration for {autoconfigured_keys} was chosen automatically. It "
        f"was written into the config file at '{config_file_path}'."
    )


def expected_configuration_file_check(
    config_file_path: Text,
    missing_keys: Set[Text],
    auto_configured_keys: Set[Text],
    training_type: Optional[TrainingClassification] = TrainingClassification.TWO,
) -> bool:
    try:
        matter = convo.shared.utils.io.read_configuration_file(config_file_path)
    except ValueError:
        matter = ""

    return (
            bool(matter)
            and missing_keys == get_missing_configuration_keys(matter, training_type)
            and auto_configured_keys
            == get_unspecified_auto_configurable_keys(matter, training_type)
    )


def add_missing_configuration_keys_to_file(
    config_file_path: Text, missing_keys: Set[Text]
) -> None:
    if not missing_keys:
        return
    with open(
        config_file_path, "a", encoding=convo.shared.utils.io.ENCODING_DEFAULT
    ) as f:
        for key in missing_keys:
            f.write(f"{key}:\n")


def get_lines_including_auto_configuration(
    lines: List[Text], autoconfig_lines: Dict[Text, List[Text]]
) -> List[Text]:
    autoconfigured_keys = autoconfig_lines.keys()

    lines_with_autoconfiguration = []
    remove_comment_till_next_uncommented_line = False
    for statement in lines:
        inserting_section = None

        # remove old auto configuration
        if remove_comment_till_next_uncommented_line:
            if statement.startswith("#"):
                continue
            remove_comment_till_next_uncommented_line = False

        # add an explanatory comment to auto configured sections
        for key in autoconfigured_keys:
            if statement.startswith(f"{key}:"):  # start of next auto-section
                statement = statement + COMMENT_FOR_KEYS[key]
                inserting_section = key
                remove_comment_till_next_uncommented_line = True

        lines_with_autoconfiguration.append(statement)

        if not inserting_section:
            continue

        # add the auto configuration (commented out)
        lines_with_autoconfiguration += autoconfig_lines[inserting_section]

    return lines_with_autoconfiguration


def get_commented_out_autoconfiguration_lines(
    config: Dict[Text, Any], auto_configured_keys: Set[Text]
) -> Dict[Text, List[Text]]:
    import ruamel.yaml as yaml
    import ruamel.yaml.compat

    yaml_analyser = yaml.YAML()
    yaml_analyser.indent(mapping=2, sequence=4, offset=2)

    autoconfiguration_lines = {}

    for key in auto_configured_keys:
        data_stream = yaml.compat.StringIO()
        yaml_analyser.dump(config.get(key), data_stream)
        dump = data_stream.getvalue()

        statement = dump.split("\n")
        if not statement[-1]:
            statement = statement[:-1]  # yaml dump adds an empty line at the end
        statement = [f"# {line}\n" for line in statement]

        autoconfiguration_lines[key] = statement

    return autoconfiguration_lines
