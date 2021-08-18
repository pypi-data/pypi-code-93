import logging
import re
from collections import OrderedDict
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Text, Optional, Tuple, Dict, Union

from convo.shared.constants import LEGACY_DOCUMENTS_BASE_URL
from convo.shared.nlu.constants import TXT
from convo.shared.nlu.training_data.formats.readerwriter import (
    TrainingDataReviewer,
    TrainingDataAuthor,
)
import convo.shared.utils.io
from convo.shared.nlu.training_data.util import encode_str, decode_str
from convo.shared.nlu.training_data.training_data import TrainingDataSet

ENTITY_VALUE_OF_GROUP = "value"
TYPE_OF_GROUP_ENTITY = "entity"
GROUP_ENTITY_DICTIONARY = "entity_dict"
ENTITY_TEXT_OF_GROUP = "entity_text"


INTENTION = "intent"
SIMILAR = "synonym"
REGULAR_EXPRESSION = "regex"
LOOK_UP = "lookup"
SECTIONS_AVAILABLE = [INTENTION, SIMILAR, REGULAR_EXPRESSION, LOOK_UP]
MARK_DOWN_SECTION_MARKERS = [f"## {s}:" for s in SECTIONS_AVAILABLE]

item_regular_expression = re.compile(r"\s*[-*+]\s*((?:.+\s*)*)")
comment_regular_expression = re.compile(r"<!--[\s\S]*?--!*>", re.MULTILINE)
first_name_regex = re.compile(r"\s*([^-*+]+)")

log = logging.getLogger(__name__)


class MarkdownReviewer(TrainingDataReviewer):
    """Reads markdown training data and creates a TrainingDataSet object."""

    def __init__(self) -> None:
        super().__init__()
        self.current_title = None
        self.current_section = None
        self.training_examples = []
        self.entity_synonyms = {}
        self.regex_features = []
        self.lookup_tables = []

    def data_reads(self, s_val: Text, **kwargs: Any) -> "TrainingDataSet":
        """Read markdown string and create TrainingDataSet object"""
        s_val = self.stripping_comments(s_val)
        for sentence in s_val.splitlines():
            sentence = decode_str(sentence.strip())
            header_val = self.finding_section_header(sentence)
            if header_val:
                self.setting_current_section(header_val[0], header_val[1])
            else:
                self.parsing_item(sentence)
                self.loading_files(sentence)

        return TrainingDataSet(
            self.training_examples,
            self.entity_synonyms,
            self.regex_features,
            self.lookup_tables,
        )

    @staticmethod
    def stripping_comments(text: Text) -> Text:
        """ Removes comments defined by `comment_regex` from `text`. """
        return re.sub(comment_regular_expression, "", text)

    @staticmethod
    def finding_section_header(line: Text) -> Optional[Tuple[Text, Text]]:
        """Checks if the current line contains a section header
        and returns the section and the title."""
        exact_match = re.search(r"##\s*(.+?):(.+)", line)
        if exact_match is not None:
            return exact_match.group(1), exact_match.group(2)

        return None

    def loading_files(self, line: Text) -> None:
        """Checks line to see if filename was supplied.  If so, inserts the
        filename into the lookup table slot for processing from the regex
        featurizer."""
        if self.current_section == LOOK_UP:
            exact_match = re.match(first_name_regex, line)
            if exact_match:
                first_name = line.strip()
                self.lookup_tables.append(
                    {"name": self.current_title, "elements": str(first_name)}
                )

    def parsing_item(self, line: Text) -> None:
        """Parses an md list item line based on the current section type."""
        import convo.shared.nlu.training_data.lookup_tables_parser as lookup_tables_parser
        import convo.shared.nlu.training_data.synonyms_parser as synonyms_parser
        from convo.shared.nlu.training_data import entities_parser

        exact_match = re.match(item_regular_expression, line)
        if exact_match:
            object = exact_match.group(1)
            if self.current_section == INTENTION:
                item_parsed = entities_parser.parsing_training_example(
                    object, self.current_title
                )
                synonyms_parser.adding_synonyms_from_entities(
                    item_parsed.get(TXT), item_parsed.get("entities", []), self.entity_synonyms
                )
                self.training_examples.append(item_parsed)
            elif self.current_section == SIMILAR:
                synonyms_parser.adding_synonyms(
                    object, self.current_title, self.entity_synonyms
                )
            elif self.current_section == REGULAR_EXPRESSION:
                self.regex_features.append(
                    {"name": self.current_title, "pattern": object}
                )
            elif self.current_section == LOOK_UP:
                lookup_tables_parser.adding_items_to_lookup_tables(
                    self.current_title, object, self.lookup_tables
                )

    @staticmethod
    def get_validated_dictionary(json_str: Text) -> Dict[Text, Text]:
        """Converts the provided json_str to a valid dict containing the entity
        attributes.

        Users can specify entity roles, synonyms, groups for an entity in a dict, e.g.
        [LA]{"entity": "city", "role": "to", "value": "Los Angeles"}

        Args:
            json_str: the entity dict as string without "{}"

        Raises:
            ValidationError if validation of entity dict fails.
            JSONDecodeError if provided entity dict is not valid json.

        Returns:
            a proper python dict
        """
        import json
        import convo.shared.utils.validation as validation_utils
        import convo.shared.nlu.training_data.schemas.data_schema as schema

        # add {} as they are not part of the regex
        try:
            data_set = json.loads(f"{{{json_str}}}")
        except JSONDecodeError as e:
            convo.shared.utils.io.raising_warning(
                f"Incorrect training data format ('{{{json_str}}}'), make sure your "
                f"data is valid. For more information about the format visit "
                f"{LEGACY_DOCUMENTS_BASE_URL}/nlu/training-data-format/."
            )
            raise e

        validation_utils.validating_training_data(data_set, schema.entity_dictionary_schema())

        return data_set

    def setting_current_section(self, section: Text, title: Text) -> None:
        """Update parsing mode."""
        if section not in SECTIONS_AVAILABLE:
            raise ValueError(
                "Found markdown section '{}' which is not "
                "in the allowed sections '{}'."
                "".format(section, "', '".join(SECTIONS_AVAILABLE))
            )

        self.current_section = section
        self.current_title = title

    @staticmethod
    def markdown_nlu_file_check(filename: Union[Text, Path]) -> bool:
        matter = convo.shared.utils.io.read_file(filename)
        return any(marker in matter for marker in MARK_DOWN_SECTION_MARKERS)


class MarkdownAuthor(TrainingDataAuthor):
    def data_dumps(self, training_data: "TrainingDataSet") -> Text:
        """Transforms a TrainingDataSet object into a markdown string."""

        md = ""
        md += self.generating_training_examples_md(training_data)
        md += self.generating_synonyms_md(training_data)
        md += self.generating_regex_features_md(training_data)
        md += self.generating_lookup_tables_md(training_data)

        return md

    def generating_training_examples_md(self, training_data: "TrainingDataSet") -> Text:
        """Generates markdown training examples."""

        import convo.shared.nlu.training_data.util as convo_nlu_training_data_utils

        trainings_exps = OrderedDict()

        # Sort by intent while keeping basic intent order
        for example in [e.as_dictionary_nlu() for e in training_data.training_examples]:
            convo_nlu_training_data_utils.remove_untrainable_entities(example)
            intention = example[INTENTION]
            trainings_exps.setdefault(intention, [])
            trainings_exps[intention].append(example)

        # Don't prepend newline for first line
        prefix_new_line = False
        sentences = []

        for intention, examples in trainings_exps.items():
            section_header_val = self.generating_section_header_md(
                INTENTION, intention, prepend_newline=prefix_new_line
            )
            sentences.append(section_header_val)
            prefix_new_line = True

            sentences += [
                self.generate_list_item(self.generate_msg(example))
                for example in examples
            ]

        return "".join(sentences)

    def generating_synonyms_md(self, training_data: "TrainingDataSet") -> Text:
        """Generates markdown for entity synomyms."""

        synonyms_entity = sorted(
            training_data.entity_synonyms.items(), key=lambda x: x[1]
        )
        md = ""
        for i, synonym in enumerate(synonyms_entity):
            if i == 0 or synonyms_entity[i - 1][1] != synonym[1]:
                md += self.generating_section_header_md(SIMILAR, synonym[1])

            md += self.generate_list_item(synonym[0])

        return md

    def generating_regex_features_md(self, training_data: "TrainingDataSet") -> Text:
        """Generates markdown for regex features."""

        md = ""
        # regex features are already sorted
        regular_expression_features = training_data.regex_features
        for i, regex_feature in enumerate(regular_expression_features):
            if i == 0 or regular_expression_features[i - 1]["name"] != regex_feature["name"]:
                md += self.generating_section_header_md(REGULAR_EXPRESSION, regex_feature["name"])

            md += self.generate_list_item(regex_feature["pattern"])

        return md

    def generating_lookup_tables_md(self, training_data: "TrainingDataSet") -> Text:
        """Generates markdown for regex features."""

        md = ""
        # regex features are already sorted
        look_up_tables = training_data.lookup_tables
        for lookup_table in look_up_tables:
            md += self.generating_section_header_md(LOOK_UP, lookup_table["name"])
            components = lookup_table["elements"]
            if isinstance(components, list):
                for e in components:
                    md += self.generate_list_item(e)
            else:
                md += self.generating_first_name_md(components)
        return md

    @staticmethod
    def generating_section_header_md(
        section_type: Text, title_value: Text, prepend_newline: bool = True
    ) -> Text:
        """Generates markdown section header."""

        affix = "\n" if prepend_newline else ""
        title_value = encode_str(title_value)

        return f"{affix}## {section_type}:{title_value}\n"

    @staticmethod
    def generating_first_name_md(text: Text) -> Text:
        """Generates markdown for a lookup table file path."""

        return f"  {encode_str(text)}\n"
