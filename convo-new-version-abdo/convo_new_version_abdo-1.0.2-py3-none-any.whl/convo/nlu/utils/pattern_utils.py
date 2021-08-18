import re
from typing import Dict, List, Text, Union

import convo.shared.utils.io
from convo.shared.nlu.training_data.training_data import TrainingDataSet


def _convert_lookup_tables_to_regular_expression(
    training_data: TrainingDataSet, use_only_entities: bool = False
) -> List[Dict[Text, Text]]:
    """Convert the lookup tables from the training data to regex patterns.
    Args:
        training_data: The training data.
        use_only_entities: If True only regex features with a name equal to a entity
          are considered.

    Returns:
        A list of regex patterns.
    """
    pattern = []
    for table in training_data.lookup_tables:
        if use_only_entities and table["name"] not in training_data.entities:
            continue
        pattern_regex = create_lookup_regular_expression(table)
        regular_expression_lookup = {"name": table["name"], "pattern": pattern_regex}
        pattern.append(regular_expression_lookup)
    return pattern


def create_lookup_regular_expression(lookup_table: Dict[Text, Union[Text, List[Text]]]) -> Text:
    """Creates a regex pattern from the given lookup table.

    The lookup table is either a file or a list of entries.

    Args:
        lookup_table: The lookup table.

    Returns:
        The regex pattern.
    """
    element_lookup = lookup_table["elements"]

    # if it's a list, it should be the elements directly
    if isinstance(element_lookup, list):
        regex_to_element = element_lookup
    # otherwise it's a file path.
    else:
        regex_to_element = file_read_lookup_table(element_lookup)

    # sanitize the regex, escape special characters
    sanitize_elements = [re.escape(e) for e in regex_to_element]

    # regex matching elements with word boundaries on either side
    return "(\\b" + "\\b|\\b".join(sanitize_elements) + "\\b)"


def file_read_lookup_table(lookup_table_file: Text) -> List[Text]:
    """Read the lookup table file.

    Args:
        lookup_table_file: the file path to the lookup table

    Returns:
        Elements listed in the lookup table file.
    """
    try:
        g = open(lookup_table_file, "r", encoding=convo.shared.utils.io.ENCODING_DEFAULT)
    except OSError:
        raise ValueError(
            f"Could not load lookup table {lookup_table_file}. "
            f"Please make sure you've provided the correct path."
        )

    regex_to_element = []
    with g:
        for line in g:
            new_element = line.strip()
            if new_element:
                regex_to_element.append(new_element)
    return regex_to_element


def _regular_expression_collect_features(
    training_data: TrainingDataSet, use_only_entities: bool = False
) -> List[Dict[Text, Text]]:
    """Get regex features from training data.

    Args:
        training_data: The training data
        use_only_entities: If True only regex features with a name equal to a entity
          are considered.

    Returns:
        Regex features.
    """
    if not use_only_entities:
        return training_data.regex_features

    return [
        regex
        for regex in training_data.regex_features
        if regex["name"] in training_data.entities
    ]


def patterns_extract(
    training_data: TrainingDataSet,
    use_lookup_tables: bool = True,
    use_regexes: bool = True,
    use_only_entities: bool = False,
) -> List[Dict[Text, Text]]:
    """Extract a list of patterns from the training data.

    The patterns are constructed using the regex features and lookup tables defined
    in the training data.

    Args:
        training_data: The training data.
        use_only_entities: If True only lookup tables and regex features with a name
          equal to a entity are considered.
        use_regexes: Boolean indicating whether to use regex features or not.
        use_lookup_tables: Boolean indicating whether to use lookup tables or not.

    Returns:
        The list of regex patterns.
    """
    if not training_data.lookup_tables and not training_data.regex_features:
        return []

    pattern = []

    if use_regexes:
        pattern.extend(_regular_expression_collect_features(training_data, use_only_entities))
    if use_lookup_tables:
        pattern.extend(
            _convert_lookup_tables_to_regular_expression(training_data, use_only_entities)
        )

    return pattern
