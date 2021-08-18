import logging
import os
from pathlib import Path
import random
from collections import Counter, OrderedDict
import copy
from os.path import relpath
from typing import Any, Dict, List, Optional, Set, Text, Tuple, Callable

import convo.shared.data
from convo.shared.utils.common import lazy_property
import convo.shared.utils.io
from convo.shared.nlu.constants import (
    RETURN_RESPONSE,
    KEY_INTENT_RESPONSE,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ENTITY_TAG_ABSENT,
    INTENTION,
    ENTITIES_NAME,
    TXT,
    ACT_NAME,
    ACT_TEXT,
)
from convo.shared.nlu.training_data.message import Msg
from convo.shared.nlu.training_data import util


OUTPUT_PATH_FOR_DEFAULT_TRAINING_DATA = "training_data.yml"

log = logging.getLogger(__name__)


class TrainingDataSet:
    """Holds loaded intent and entity training data."""

    # Validation will ensure and warn if these lower limits are not met
    MINIMUM_EXAMPLES_PER_INTENT = 2
    MINIMUM_EXAMPLES_PER_ENTITY= 2

    def __init__(
        self,
        training_examples: Optional[List[Msg]] = None,
        entity_synonyms: Optional[Dict[Text, Text]] = None,
        regex_features: Optional[List[Dict[Text, Text]]] = None,
        lookup_tables: Optional[List[Dict[Text, Any]]] = None,
        responses: Optional[Dict[Text, List[Dict[Text, Any]]]] = None,
    ) -> None:

        if training_examples:
            self.training_examples = self.sanitize_exp(training_examples)
        else:
            self.training_examples = []
        self.entity_synonyms = entity_synonyms or {}
        self.regex_features = regex_features or []
        self.sorting_regex_features()
        self.lookup_tables = lookup_tables or []
        self.responses = responses or {}

        self.filling_response_phrases()

    def merge(self, *others: "TrainingDataSet") -> "TrainingDataSet":
        """Return merged instance of this data with others training data."""

        training_exp = copy.deepcopy(self.training_examples)
        entity_name_synonyms = self.entity_synonyms.copy()
        regular_expression_features = copy.deepcopy(self.regex_features)
        look_up_tables = copy.deepcopy(self.lookup_tables)
        resp = copy.deepcopy(self.responses)
        other_alternative = [others for others in others if others]

        for o in other_alternative:
            training_exp.extend(copy.deepcopy(o.training_examples))
            regular_expression_features.extend(copy.deepcopy(o.regex_features))
            look_up_tables.extend(copy.deepcopy(o.lookup_tables))

            for text, syn in o.entity_synonyms.items():
                util.duplicate_synonym_check(
                    entity_name_synonyms, text, syn, "merge training data"
                )

            entity_name_synonyms.update(o.entity_synonyms)
            resp.update(o.responses)

        return TrainingDataSet(
            training_exp, entity_name_synonyms, regular_expression_features, look_up_tables, resp
        )

    def filtering_training_exps(
        self, condition: Callable[[Msg], bool]
    ) -> "TrainingDataSet":
        """Filter training examples.

        Args:
            condition: A function that will be applied to filter training examples.

        Returns:
            TrainingDataSet: A TrainingDataSet with filtered training examples.
        """

        return TrainingDataSet(
            list(filter(condition, self.training_examples)),
            self.entity_synonyms,
            self.regex_features,
            self.lookup_tables,
            self.responses,
        )

    def __hash__(self) -> int:
        stringify = self.nlu_json() + self.nlg_markdown()
        hash_text= convo.shared.utils.io.fetch_text_hashcode(stringify)

        return int(hash_text, 16)


    @staticmethod
    def sanitize_exp(examples: List[Msg]) -> List[Msg]:
        """Makes sure the training data is clean.

        Remove trailing whitespaces from intent and response annotations and drop
        duplicate examples.
        """

        for ex in examples:
            if ex.get(INTENTION):
                ex.put(INTENTION, ex.get(INTENTION).strip())

            if ex.get(RETURN_RESPONSE):
                ex.put(RETURN_RESPONSE, ex.get(RETURN_RESPONSE).strip())

        return list(OrderedDict.fromkeys(examples))

    @lazy_property
    def nlu_exp(self) -> List[Msg]:
        return [ex for ex in self.training_examples if not ex.is_core_msg()]

    @lazy_property
    def intent_exp(self) -> List[Msg]:
        return [ex for ex in self.nlu_exp if ex.get(INTENTION)]

    @lazy_property
    def resp_examples(self) -> List[Msg]:
        return [ex for ex in self.nlu_exp if ex.get(KEY_INTENT_RESPONSE)]

    @lazy_property
    def entity_exp(self) -> List[Msg]:
        return [ex for ex in self.nlu_exp if ex.get(ENTITIES_NAME)]

    @lazy_property
    def convo_intents(self) -> Set[Text]:
        """Returns the set of convo_intents in the training data."""
        return {ex.get(INTENTION) for ex in self.training_examples} - {None}

    @lazy_property
    def retrieval_intents(self) -> Set[Text]:
        """Returns the total number of response types in the training data"""
        return {
            ex.get(INTENTION)
            for ex in self.training_examples
            if ex.get(KEY_INTENT_RESPONSE)
        }

    @lazy_property
    def no_of_examples_per_intent(self) -> Dict[Text, int]:
        """Calculates the number of examples per intent."""
        convo_intents = [ex.get(INTENTION) for ex in self.training_examples]
        return dict(Counter(convo_intents))

    @lazy_property
    def no_of_examples_per_response(self) -> Dict[Text, int]:
        """Calculates the number of examples per response."""
        resp = [
            ex.get(KEY_INTENT_RESPONSE)
            for ex in self.training_examples
            if ex.get(KEY_INTENT_RESPONSE)
        ]
        return dict(Counter(resp))

    @lazy_property
    def entities(self) -> Set[Text]:
        """Returns the set of entity types in the training data."""
        entity_types = [e.get(ATTRIBUTE_TYPE_ENTITY) for e in self.entities_sorted()]
        return set(entity_types)

    @lazy_property
    def roles_of_entity(self) -> Set[Text]:
        """Returns the set of entity roles in the training data."""
        types_of_entity = [
            e.get(ATTRIBUTE_ROLE_ENTITY)
            for e in self.entities_sorted()
            if ATTRIBUTE_ROLE_ENTITY in e
        ]
        return set(types_of_entity) - {ENTITY_TAG_ABSENT}

    @lazy_property
    def groups_of_entity(self) -> Set[Text]:
        """Returns the set of entity groups in the training data."""
        types_of_entity = [
            e.get(ATTRIBUTE_GROUP_ENTITY)
            for e in self.entities_sorted()
            if ATTRIBUTE_GROUP_ENTITY in e
        ]
        return set(types_of_entity) - {ENTITY_TAG_ABSENT}

    def used_entity_roles_groups(self) -> bool:
        used_entity_groups = (
                self.groups_of_entity is not None and len(self.groups_of_entity) > 0
        )
        used_entity_roles = self.roles_of_entity is not None and len(self.roles_of_entity) > 0

        return used_entity_groups or used_entity_roles

    @lazy_property
    def no_of_examples_per_entity(self) -> Dict[Text, int]:
        """Calculates the number of examples per entity."""

        entities = []

        def appending_entity(entity: Dict[Text, Any], attribute: Text) -> None:
            if attribute in entity:
                val = entity.get(attribute)
                if val is not None and val != ENTITY_TAG_ABSENT:
                    entities.append(f"{attribute} '{val}'")

        for entity in self.entities_sorted():
            appending_entity(entity, ATTRIBUTE_TYPE_ENTITY)
            appending_entity(entity, ATTRIBUTE_ROLE_ENTITY)
            appending_entity(entity, ATTRIBUTE_GROUP_ENTITY)

        return dict(Counter(entities))

    def sorting_regex_features(self) -> None:
        """Sorts regex features lexicographically by name+pattern"""
        self.regex_features = sorted(
            self.regex_features, key=lambda e: "{}+{}".format(e["name"], e["pattern"])
        )

    def filling_response_phrases(self) -> None:
        """Set response phrase for all examples by looking up NLG stories"""
        for example in self.training_examples:
            # if intent_response_key is None, that means the corresponding intent is not a
            # retrieval intent and hence no response text needs to be fetched.
            # If intent_response_key is set, fetch the corresponding response text
            if example.get(KEY_INTENT_RESPONSE) is None:
                continue

            # look for corresponding bot utterance
            key_story_lookup = util.intents_response_key_to_template_key(
                example.get_complete_intent()
            )
            asst_utterances = self.responses.get(key_story_lookup, [])
            if asst_utterances:

                # Use the first response text as training label if needed downstream
                for assistant_utterance in asst_utterances:
                    if assistant_utterance.get(TXT):
                        example.put(RETURN_RESPONSE, assistant_utterance[TXT])

                # If no text attribute was found use the key for training
                if not example.get(RETURN_RESPONSE):
                    example.put(RETURN_RESPONSE, key_story_lookup)

    def nlu_json(self, **kwargs: Any) -> Text:
        """Represent this set of training examples as json."""
        from convo.shared.nlu.training_data.formats import (  # pytype: disable=pyi-error
            ConvoAuthor,
        )

        return ConvoAuthor().data_dumps(self, **kwargs)

    def nlg_markdown(self) -> Text:
        """Generates the markdown representation of the response phrases (NLG) of
        TrainingDataSet."""

        from convo.shared.nlu.training_data.formats import (  # pytype: disable=pyi-error
            NLGMarkdownAuthor,
        )

        return NLGMarkdownAuthor().data_dumps(self)

    def nlg_yaml(self) -> Text:
        """Generates yaml representation of the response phrases (NLG) of TrainingDataSet.

        Returns:
            responses in yaml format as a string
        """
        from convo.shared.nlu.training_data.formats.convo_yaml import (  # pytype: disable=pyi-error
            ConvoYAMLAuthor,
        )

        # only dump responses. at some point it might make sense to remove the
        # differentiation between dumping NLU and dumping responses. but we
        # can't do that until after we remove markdown support.
        return ConvoYAMLAuthor().data_dumps(TrainingDataSet(responses=self.responses))

    def nlu_markdown(self) -> Text:
        """Generates the markdown representation of the NLU part of TrainingDataSet."""
        from convo.shared.nlu.training_data.formats import (  # pytype: disable=pyi-error
            MarkdownAuthor,
        )

        return MarkdownAuthor().data_dumps(self)

    def nlu_yaml(self) -> Text:
        from convo.shared.nlu.training_data.formats.convo_yaml import (  # pytype: disable=pyi-error
            ConvoYAMLAuthor,
        )

        # avoid dumping NLG data (responses). this is a workaround until we
        # can remove the distinction between nlu & nlg when converting to a string
        # (so until after we remove markdown support)
        no_resps_training_data = copy.copy(self)
        no_resps_training_data.responses = {}

        return ConvoYAMLAuthor().data_dumps(no_resps_training_data)

    def persisting_nlu(self, filename: Text = OUTPUT_PATH_FOR_DEFAULT_TRAINING_DATA) -> None:
        if convo.shared.data.is_json_file (filename):
            convo.shared.utils.io.writing_text_file(self.nlu_json(indent=2), filename)
        elif convo.shared.data.is_mark_down_file (filename):
            convo.shared.utils.io.writing_text_file(self.nlu_markdown(), filename)
        elif convo.shared.data.is_yaml_file (filename):
            convo.shared.utils.io.writing_text_file(self.nlu_yaml(), filename)
        else:
            raise ValueError(
                "Unsupported file format detected. Supported file formats are 'json', 'yml' "
                "and 'md'."
            )

    def persisting_nlg(self, filename: Text) -> None:
        if convo.shared.data.is_yaml_file (filename):
            convo.shared.utils.io.writing_text_file(self.nlg_yaml(), filename)
        elif convo.shared.data.is_mark_down_file (filename):
            nlg_serialized_data = self.nlg_markdown()
            if nlg_serialized_data:
                convo.shared.utils.io.writing_text_file(nlg_serialized_data, filename)
        else:
            raise ValueError(
                "Unsupported file format detected. Supported file formats are 'md' "
                "and 'yml'."
            )

    @staticmethod
    def fetch_nlg_persisting_file_name(nlu_filename: Text) -> Text:

        ext = Path(nlu_filename).suffix
        if convo.shared.data.is_json_file (nlu_filename):
            # backwards compatibility: previously NLG was always dumped as md. now
            # we are going to dump in the same format as the NLU data. unfortunately
            # there is a special case: NLU is in json format, in this case we use
            # md as we do not have a NLG json format
            ext = convo.shared.data.mark_down_file_extension ()
        # Add nlg_ as prefix and change ext to .md
        file_name = (
            Path(nlu_filename)
            .with_name("nlg_" + Path(nlu_filename).name)
            .with_suffix(ext)
        )
        return str(file_name)

    def persist(
        self, dir_name: Text, filename: Text = OUTPUT_PATH_FOR_DEFAULT_TRAINING_DATA
    ) -> Dict[Text, Any]:
        """Persists this training data to disk and returns necessary
        information to load it again."""

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        nlu_dataset_file = os.path.join(dir_name, filename)
        self.persisting_nlu(nlu_dataset_file)
        self.persisting_nlg(self.fetch_nlg_persisting_file_name(nlu_dataset_file))

        return {"training_data": relpath(nlu_dataset_file, dir_name)}

    def entities_sorted(self) -> List[Any]:
        """Extract all entities from examples and sorts them by entity type."""

        entity_exp = [
            entity for ex in self.entity_exp for entity in ex.get("entities")
        ]
        return sorted(entity_exp, key=lambda e: e["entity"])

    def sorted_intent_exp(self) -> List[Msg]:
        """Sorts the intent examples by the name of the intent and then response"""

        return sorted(
            self.intent_exp,
            key=lambda e: (e.get(INTENTION), e.get(KEY_INTENT_RESPONSE)),
        )

    def validating(self) -> None:
        """Ensures that the loaded training data is valid.

        Checks that the data has a minimum of certain training examples."""

        log.debug("Validating training data...")
        if "" in self.convo_intents:
            convo.shared.utils.io.raising_warning(
                "Found empty intent, please check your "
                "training data. This may result in wrong "
                "intent predictions."
            )

        if "" in self.responses:
            convo.shared.utils.io.raising_warning(
                "Found empty response, please check your "
                "training data. This may result in wrong "
                "response predictions."
            )

        # emit warnings for convo_intents with only a few training samples
        for intent, count in self.no_of_examples_per_intent.items():
            if count < self.MINIMUM_EXAMPLES_PER_INTENT:
                convo.shared.utils.io.raising_warning(
                    f"Intent '{intent}' has only {count} training examples! "
                    f"Minimum is {self.MINIMUM_EXAMPLES_PER_INTENT}, training may fail."
                )

        # emit warnings for entities with only a few training samples
        for entity, count in self.no_of_examples_per_entity.items():
            if count < self.MINIMUM_EXAMPLES_PER_ENTITY :
                convo.shared.utils.io.raising_warning(
                    f"Entity {entity} has only {count} training examples! "
                    f"The minimum is {self.MINIMUM_EXAMPLES_PER_ENTITY }, because of "
                    f"this the training may fail."
                )

        # emit warnings for response convo_intents without a response template
        for example in self.training_examples:
            if example.get(KEY_INTENT_RESPONSE) and not example.get(RETURN_RESPONSE):
                convo.shared.utils.io.raising_warning(
                    f"Your training data contains an example "
                    f"'{example.get(TXT)[:20]}...' "
                    f"for the {example.get_complete_intent()} intent. "
                    f"You either need to add a response phrase or correct the "
                    f"intent for this example in your training data. "
                    f"If you intend to use Response Selector in the pipeline, the "
                    f"training may fail."
                )

    def training_test_split(
        self, train_frac: float = 0.8, random_seed: Optional[int] = None
    ) -> Tuple["TrainingDataSet", "TrainingDataSet"]:
        """Split into a training and test dataset,
        preserving the fraction of examples per intent."""

        # collect all nlu data
        check, instruct = self.separate_nlu_exps(train_frac, random_seed)

        # collect all nlg stories
        test_resps = self.needed_resps_for_examples(check)
        train_resps = self.needed_resps_for_examples(instruct)

        data_set_train = TrainingDataSet(
            instruct,
            entity_synonyms=self.entity_synonyms,
            regex_features=self.regex_features,
            lookup_tables=self.lookup_tables,
            responses=train_resps,
        )

        data_set_test = TrainingDataSet(
            check,
            entity_synonyms=self.entity_synonyms,
            regex_features=self.regex_features,
            lookup_tables=self.lookup_tables,
            responses=test_resps,
        )

        return data_set_train, data_set_test

    def needed_resps_for_examples(
        self, examples: List[Msg]
    ) -> Dict[Text, List[Dict[Text, Any]]]:
        """Get all resps used in any of the examples.

        Args:
            examples: messages to select resps by.

        Returns:
            All resps that appear at least once in the list of examples.
        """

        resps = {}
        for ex in examples:
            if ex.get(KEY_INTENT_RESPONSE) and ex.get(RETURN_RESPONSE):
                key = util.intents_response_key_to_template_key(ex.get_complete_intent())
                resps[key] = self.responses[key]
        return resps

    def separate_nlu_exps(
        self, train_frac: float, random_seed: Optional[int] = None
    ) -> Tuple[list, list]:
        """Split the training data into a train and test set.

        Args:
            train_frac: percentage of exps to add to the training set.
            random_seed: random seed

        Returns:
            Test and training exps.
        """
        train, test = [], []
        training_exps = set(self.training_examples)

        def split(_examples: List[Msg], _count: int) -> None:
            if random_seed is not None:
                random.Random(random_seed).shuffle(_examples)
            else:
                random.shuffle(_examples)

            n_instruct = int(_count * train_frac)
            train.extend(_examples[:n_instruct])
            test.extend(_examples[n_instruct:])

        # to make sure we have at least one example per response and intent in the
        # training/test data, we first go over the response exps and then go over
        # intent exps

        for response, count in self.no_of_examples_per_response.items():
            exps = [
                e
                for e in training_exps
                if e.get(KEY_INTENT_RESPONSE) and e.get(KEY_INTENT_RESPONSE) == response
            ]
            split(exps, count)
            training_exps = training_exps - set(exps)

        for intent, count in self.no_of_examples_per_intent.items():
            exps = [
                e
                for e in training_exps
                if INTENTION in e.data and e.data[INTENTION] == intent
            ]
            split(exps, count)
            training_exps = training_exps - set(exps)

        return test, train

    def print_statistics(self) -> None:
        no_of_examples_for_each_intent = []
        for name_of_intent, example_count in self.no_of_examples_per_intent.items():
            no_of_examples_for_each_intent.append(
                f"intent: {name_of_intent}, training examples: {example_count}   "
            )
        new_line = "\n"

        log.info("Training data stats:")
        log.info(
            f"Number of intent examples: {len(self.intent_exp)} "
            f"({len(self.convo_intents)} distinct convo_intents)"
            "\n"
        )
        # log the number of training examples per intent

        log.debug(f"{new_line.join(no_of_examples_for_each_intent)}")

        if self.convo_intents:
            log.info(f"  Found convo_intents: {list_to_string(self.convo_intents)}")
        log.info(
            f"Number of response examples: {len(self.resp_examples)} "
            f"({len(self.responses)} distinct responses)"
        )
        log.info(
            f"Number of entity examples: {len(self.entity_exp)} "
            f"({len(self.entities)} distinct entities)"
        )
        if self.entities:
            log.info(f"  Found entity types: {list_to_string(self.entities)}")
        if self.roles_of_entity:
            log.info(f"  Found entity roles: {list_to_string(self.roles_of_entity)}")
        if self.groups_of_entity:
            log.info(f"  Found entity groups: {list_to_string(self.groups_of_entity)}")

    def empty_check(self) -> bool:
        """Checks if any training data was loaded."""

        lists_check = [
            self.training_examples,
            self.entity_synonyms,
            self.regex_features,
            self.lookup_tables,
        ]
        return not any([len(lst) > 0 for lst in lists_check])

    def nlu_model_train_check(self) -> bool:
        """Checks if any NLU training data was loaded."""

        lists_to_check = [
            self.nlu_exp,
            self.entity_synonyms,
            self.regex_features,
            self.lookup_tables,
        ]
        return not any([len(lst) > 0 for lst in lists_to_check])


def list_to_string(lst: List[Text], delim: Text = ", ", quote: Text = "'") -> Text:
    return delim.join([quote + e + quote for e in lst])
