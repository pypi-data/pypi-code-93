import logging
from collections import OrderedDict
from pathlib import Path
from typing import Text, Any, List, Dict, Tuple, Union, Iterator, Optional

import convo.shared.data
from convo.shared.exceptions import YamlExceptions 
from convo.shared.utils import validation
from ruamel.yaml import StringIO

from convo.shared.constants import (
    TRAINING_DATA_DOCUMENTS_URL,
    TRAINING_DATA_LATEST_FORMAT_VERSION ,
)
from convo.shared.nlu.training_data.formats.readerwriter import (
    TrainingDataReviewer,
    TrainingDataAuthor,
)
import convo.shared.utils.io

from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)

NLU_KEY = "nlu"
RESPONSES_KEY = "responses"
INTENT_KEY = "intent"
KEY_INTENT_EXPS = "examples"
KEY_INTENT_TEXT_STR= "text"
SYNONYM_KEY= "synonym"
KEY_SYNONYM_EXPS= "examples"
REGEX_KEY= "regex"
KEY_REGEX_EXPS= "examples"
LOOKUP_KEY= "lookup"
KEY_LOOKUP_EXPS= "examples"
KEY_META_DATA = "metadata"

MULTI_LINE_TRAINING_EXP_LEADING_SYMBOL= "-"

NLU_SCHEMA_FILE_NAME = "shared/nlu/training_data/schemas/nlu.yml"

STRIPPING_SYMBOLS= "\n\r "


class ConvoYAMLReviewer(TrainingDataReviewer):
    """Reads YAML training data and creates a TrainingDataSet object."""

    def __init__(self) -> None:
        super().__init__()
        self.training_examples: List[Msg] = []
        self.entity_synonyms: Dict[Text, Text] = {}
        self.regex_features: List[Dict[Text, Text]] = []
        self.lookup_tables: List[Dict[Text, Any]] = []
        self.responses: Dict[Text, List[Dict[Text, Any]]] = {}

    def validating(self, string: Text) -> None:
        """Check if the string adheres to the NLU yaml data schema.

        If the string is not in the right format, an exception will be raised."""
        try:
            validation.validating_yaml_schema(string, NLU_SCHEMA_FILE_NAME)
        except YamlExceptions  as e:
            e.filename = self.filename
            raise e

    def data_reads(self, string: Text, **kwargs: Any) -> "TrainingDataSet":
        """Reads TrainingDataSet in YAML format from a string.

        Args:
            string: String with YAML training data.
            **kwargs: Keyword arguments.

        Returns:
            New `TrainingDataSet` object with parsed training data.
        """
        self.validating(string)

        content_of_yaml = convo.shared.utils.io.reading_yaml(string)

        if not validation.validating_training_data_format_version(
            content_of_yaml, self.filename
        ):
            return TrainingDataSet()

        for key, value in content_of_yaml.items():  # pytype: disable=attribute-error
            if key == NLU_KEY:
                self.parse_nlu(value)
            elif key == RESPONSES_KEY:
                self.responses = value

        return TrainingDataSet(
            self.training_examples,
            self.entity_synonyms,
            self.regex_features,
            self.lookup_tables,
            self.responses,
        )

    def parse_nlu(self, nlu_data: Optional[List[Dict[Text, Any]]]) -> None:

        if not nlu_data:
            return

        for nlu_item in nlu_data:
            if not isinstance(nlu_item, dict):
                convo.shared.utils.io.raising_warning(
                    f"Unexpected block found in '{self.filename}':\n"
                    f"{nlu_item}\n"
                    f"Items under the '{NLU_KEY}' key must be YAML dictionaries. "
                    f"This block will be skipped.",
                    docs=TRAINING_DATA_DOCUMENTS_URL,
                )
                continue

            if INTENT_KEY in nlu_item.keys():
                self.parse_intent(nlu_item)
            elif SYNONYM_KEY in nlu_item.keys():
                self.parsing_synonym(nlu_item)
            elif REGEX_KEY in nlu_item.keys():
                self.parsing_regex(nlu_item)
            elif LOOKUP_KEY in nlu_item.keys():
                self.parsing_lookup(nlu_item)
            else:
                convo.shared.utils.io.raising_warning(
                    f"Issue found while processing '{self.filename}': "
                    f"Could not find supported key in the section:\n"
                    f"{nlu_item}\n"
                    f"Supported keys are: '{INTENT_KEY}', '{SYNONYM_KEY}', "
                    f"'{REGEX_KEY}', '{LOOKUP_KEY}'. "
                    f"This section will be skipped.",
                    docs=TRAINING_DATA_DOCUMENTS_URL,
                )

    def parse_intent(self, intent_data: Dict[Text, Any]) -> None:
        import convo.shared.nlu.training_data.entities_parser as entities_parser
        import convo.shared.nlu.training_data.synonyms_parser as synonyms_parser

        intention = intent_data.get(INTENT_KEY, "")
        if not intention:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"The intent has an empty name. "
                f"convo_intents should have a name defined under the {INTENT_KEY} key. "
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        exps = intent_data.get(KEY_INTENT_EXPS, "")
        intent_meta_data = intent_data.get(KEY_META_DATA)
        for example, entities, metadata in self.parsing_traing_examples(
            exps, intention
        ):
            plain_text_str = entities_parser.replacing_entities(example)

            synonyms_parser.adding_synonyms_from_entities(
                plain_text_str, entities, self.entity_synonyms
            )

            self.training_examples.append(
                Msg.building(plain_text_str, intention, entities, intent_meta_data, metadata)
            )

    def parsing_traing_examples(
        self, examples: Union[Text, List[Dict[Text, Any]]], intent: Text
    ) -> List[Tuple[Text, List[Dict[Text, Any]], Optional[Any]]]:
        import convo.shared.nlu.training_data.entities_parser as entities_parser

        if isinstance(examples, list):
            tuples_example = [
                (
                    # pytype: disable=attribute-error
                    example.get(KEY_INTENT_TEXT, "").strip(STRIPPING_SYMBOLS),
                    example.get(KEY_META_DATA),
                )
                for example in examples
                if example
            ]
        # pytype: enable=attribute-error
        elif isinstance(examples, str):
            tuples_example = [
                (example, None)
                for example in self.parsing_multiine_example(intent, examples)
            ]
        else:
            convo.shared.utils.io.raising_warning(
                f"Unexpected block found in '{self.filename}' "
                f"while processing intent '{intent}':\n"
                f"{examples}\n"
                f"This block will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return []

        if not tuples_example:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"Intent '{intent}' has no examples.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )

        output = []
        for example, metadata in tuples_example:
            entities = entities_parser.search_entities_in_training_example(example)
            output.append((example, entities, metadata))

        return output

    def parsing_synonym(self, nlu_item: Dict[Text, Any]) -> None:
        import convo.shared.nlu.training_data.synonyms_parser as synonyms_parser

        name_of_synonym = nlu_item[SYNONYM_KEY]
        if not name_of_synonym:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"The synonym has an empty name. "
                f"Synonyms should have a name defined under the {SYNONYM_KEY} key. "
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        eg = nlu_item.get(KEY_SYNONYM_EXPS, "")

        if not eg:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"{SYNONYM_KEY}: {name_of_synonym} doesn't have any examples. "
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        if not isinstance(eg, str):
            convo.shared.utils.io.raising_warning(
                f"Unexpected block found in '{self.filename}':\n"
                f"{eg}\n"
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        for example in self.parsing_multiine_example(name_of_synonym, eg):
            synonyms_parser.adding_synonyms(example, name_of_synonym, self.entity_synonyms)

    def parsing_regex(self, nlu_item: Dict[Text, Any]) -> None:
        regular_expression_name = nlu_item[REGEX_KEY]
        if not regular_expression_name:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"The regex has an empty name."
                f"Regex should have a name defined under the '{REGEX_KEY}' key. "
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        eg = nlu_item.get(KEY_REGEX_EXPS, "")
        if not eg:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"'{REGEX_KEY}: {regular_expression_name}' doesn't have any examples. "
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        if not isinstance(eg, str):
            convo.shared.utils.io.raising_warning(
                f"Unexpected block found in '{self.filename}':\n"
                f"{eg}\n"
                f"This block will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        for example in self.parsing_multiine_example(regular_expression_name, eg):
            self.regex_features.append({"name": regular_expression_name, "pattern": example})

    def parsing_lookup(self, nlu_item: Dict[Text, Any]):
        import convo.shared.nlu.training_data.lookup_tables_parser as lookup_tables_parser

        look_up_item_name = nlu_item[LOOKUP_KEY]
        if not look_up_item_name:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"The lookup item has an empty name. "
                f"Lookup items should have a name defined under the '{LOOKUP_KEY}' "
                f"key. It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        eg = nlu_item.get(KEY_LOOKUP_EXPS, "")
        if not eg:
            convo.shared.utils.io.raising_warning(
                f"Issue found while processing '{self.filename}': "
                f"'{LOOKUP_KEY}: {look_up_item_name}' doesn't have any examples. "
                f"It will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        if not isinstance(eg, str):
            convo.shared.utils.io.raising_warning(
                f"Unexpected block found in '{self.filename}':\n"
                f"{eg}\n"
                f"This block will be skipped.",
                docs=TRAINING_DATA_DOCUMENTS_URL,
            )
            return

        for example in self.parsing_multiine_example(look_up_item_name, eg):
            lookup_tables_parser.adding_items_to_lookup_tables(
                look_up_item_name, example, self.lookup_tables
            )

    def parsing_multiine_example(self, item: Text, examples: Text) -> Iterator[Text]:
        for example in examples.splitlines():
            if not example.startswith(MULTI_LINE_TRAINING_EXP_LEADING_SYMBOL):
                convo.shared.utils.io.raising_warning(
                    f"Issue found while processing '{self.filename}': "
                    f"The item '{item}' contains an example that doesn't start with a "
                    f"'{MULTI_LINE_TRAINING_EXP_LEADING_SYMBOL}' symbol: "
                    f"{example}\n"
                    f"This training example will be skipped.",
                    docs=TRAINING_DATA_DOCUMENTS_URL,
                )
                continue
            yield example[1:].strip(STRIPPING_SYMBOLS)

    @staticmethod
    def yaml_nlu_file_check(filename: Text) -> bool:
        """Checks if the specified file possibly contains NLU training data in YAML.

        Args:
            filename: name of the file to check.

        Returns:
            `True` if the `filename` is possibly a valid YAML NLU file,
            `False` otherwise.

        Raises:
            YamlExceptions : if the file seems to be a YAML file (extension) but
                can not be read / parsed.
        """
        if not convo.shared.data.is_yaml_file (filename):
            return False

        matter = convo.shared.utils.io.reading_yaml_file(filename)

        return any(key in matter for key in {NLU_KEY, RESPONSES_KEY})


class ConvoYAMLAuthor(TrainingDataAuthor):
    """Writes training data into a file in a YAML format."""

    def data_dumps(self, training_data: "TrainingDataSet") -> Text:
        """Turns TrainingDataSet into a string."""
        data_stream = StringIO()
        self.dump(data_stream, training_data)
        return data_stream.getvalue()

    def dump(
        self, target: Union[Text, Path, StringIO], training_data: "TrainingDataSet"
    ) -> None:
        """Writes training data into a file in a YAML format.

        Args:
            target: Name of the target object to write the YAML to.
            training_data: TrainingDataSet object.
        """
        res = self.training_data_to_dictionary(training_data)

        if res:
            convo.shared.utils.io.writing_yaml(res, target, True)

    @classmethod
    def training_data_to_dictionary(
        cls, training_data: "TrainingDataSet"
    ) -> Optional[OrderedDict]:
        """Represents NLU training data to a dict/list structure ready to be
        serialized as YAML.

        Args:
            training_data: `TrainingDataSet` to convert.

        Returns:
            `OrderedDict` containing all training data.
        """
        from convo.shared.utils.validation import KEY_TRAINING_DATA_FORMAT_VER
        from ruamel.yaml.scalarstring import DoubleQuotedScalarString

        nlu_objects = []
        nlu_objects.extend(cls.processing_intents(training_data))
        nlu_objects.extend(cls.processing_synonyms(training_data))
        nlu_objects.extend(cls.processing_regexes(training_data))
        nlu_objects.extend(cls.processing_look_up_tables(training_data))

        if not any([nlu_objects, training_data.responses]):
            return None

        res = OrderedDict()
        res[KEY_TRAINING_DATA_FORMAT_VER] = DoubleQuotedScalarString(
            TRAINING_DATA_LATEST_FORMAT_VERSION 
        )

        if nlu_objects:
            res[NLU_KEY] = nlu_objects

        if training_data.responses:
            res[RESPONSES_KEY] = training_data.responses

        return res

    @classmethod
    def processing_intents(cls, training_data_set: "TrainingDataSet") -> List[OrderedDict]:
        training_data_set = cls.preparing_training_exps(training_data_set)
        return ConvoYAMLAuthor.processing_training_exp_by_key(
            training_data_set,
            INTENT_KEY,
            KEY_INTENT_EXPS,
            TrainingDataAuthor.generate_msg,
        )

    @classmethod
    def processing_synonyms(cls, training_data: "TrainingDataSet") -> List[OrderedDict]:
        synonyms_inverted = OrderedDict()
        for example, synonym in training_data.entity_synonyms.items():
            if not synonyms_inverted.get(synonym):
                synonyms_inverted[synonym] = []
            synonyms_inverted[synonym].append(example)

        return cls.processing_training_exp_by_key(
            synonyms_inverted, SYNONYM_KEY, KEY_SYNONYM_EXPS
        )

    @classmethod
    def processing_regexes(cls, training_data: "TrainingDataSet") -> List[OrderedDict]:
        regexes_inverted = OrderedDict()
        for regex in training_data.regex_features:
            if not regexes_inverted.get(regex["name"]):
                regexes_inverted[regex["name"]] = []
            regexes_inverted[regex["name"]].append(regex["pattern"])

        return cls.processing_training_exp_by_key(
            regexes_inverted, REGEX_KEY, KEY_REGEX_EXPS
        )

    @classmethod
    def processing_look_up_tables(cls, training_data: "TrainingDataSet") -> List[OrderedDict]:
        lookup_tables_prepared = OrderedDict()
        for lookup_table in training_data.lookup_tables:
            # this is a lookup table filename
            if isinstance(lookup_table["elements"], str):
                continue
            lookup_tables_prepared[lookup_table["name"]] = lookup_table["elements"]

        return cls.processing_training_exp_by_key(
            lookup_tables_prepared, LOOKUP_KEY, KEY_LOOKUP_EXPS
        )

    @staticmethod
    def processing_training_exp_by_key(
        training_examples: Dict,
        key_name: Text,
        key_examples: Text,
        example_extraction_predicate=lambda x: x,
    ) -> List[OrderedDict]:
        from ruamel.yaml.scalarstring import LiteralScalarString

        res = []
        for entity_key, examples in training_examples.items():
            examples_converted = [
                TrainingDataAuthor.generate_list_item(
                    example_extraction_predicate(example).strip(STRIPPING_SYMBOLS)
                )
                for example in examples
            ]

            item_next = OrderedDict()
            item_next[key_name] = entity_key
            item_next[key_examples] = LiteralScalarString("".join(examples_converted))
            res.append(item_next)

        return res
