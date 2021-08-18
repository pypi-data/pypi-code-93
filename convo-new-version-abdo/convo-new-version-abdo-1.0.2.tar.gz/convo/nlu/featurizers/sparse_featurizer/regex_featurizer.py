import logging
import os
import re
from typing import Any, Dict, List, Optional, Text, Type, Tuple

import numpy as np
import scipy.sparse

import convo.shared.utils.io
import convo.utils.io
import convo.nlu.utils.pattern_utils as pattern_utils
from convo.nlu import utils
from convo.nlu.components import Element
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.constants import NAMES_OF_TOKENS, FEATURE_CLASS_AS
from convo.shared.nlu.constants import (
    TXT,
    RETURN_RESPONSE,
    FEATURED_TYPE_SENTENCE,
    FEATURED_TYPE_SEQUENCE,
    ACT_TEXT,
)
from convo.nlu.featurizers.featurizer import InfrequentFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.model import Metadataset
from convo.nlu.tokenizers.tokenizer import Tokenizer
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)


class RegexFeaturizer(InfrequentFeaturizer):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [Tokenizer]

    defaults = {
        # text will be processed with case sensitive as default
        "case_sensitive": True,
        # use lookup tables to generate features
        "use_lookup_tables": True,
        # use regexes to generate features
        "use_regexes": True,
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        known_patterns: Optional[List[Dict[Text, Text]]] = None,
    ) -> None:

        super().__init__(component_config)

        self.known_patterns = known_patterns if known_patterns else []
        self.case_sensitive = self.component_config["case_sensitive"]

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        self.known_patterns = pattern_utils.patterns_extract(
            training_data,
            use_lookup_tables=self.component_config["use_lookup_tables"],
            use_regexes=self.component_config["use_regexes"],
        )

        for example in training_data.training_examples:
            for attribute in [TXT, RETURN_RESPONSE, ACT_TEXT]:
                self._txt_features_with_regex(example, attribute)

    def process(self, message: Msg, **kwargs: Any) -> None:
        self._txt_features_with_regex(message, TXT)

    def _txt_features_with_regex(self, message: Msg, attribute: Text) -> None:
        if self.known_patterns:
            seq_features, set_features = self._features_for_design(
                message, attribute
            )

            if seq_features is not None:
                final_sequence = Features(
                    seq_features,
                    FEATURED_TYPE_SEQUENCE,
                    attribute,
                    self.component_config[FEATURE_CLASS_AS],
                )
                message.adding_features(final_sequence)

            if set_features is not None:
                final_sentence = Features(
                    set_features,
                    FEATURED_TYPE_SENTENCE,
                    attribute,
                    self.component_config[FEATURE_CLASS_AS],
                )
                message.adding_features(final_sentence)

    def _features_for_design(
        self, message: Msg, attribute: Text
    ) -> Tuple[Optional[scipy.sparse.coo_matrix], Optional[scipy.sparse.coo_matrix]]:
        """Checks which known design match the message.
        Given a sentence, returns a vector of {1,0} values indicating which
        regexes did match. Furthermore, if the
        message is tokenized, the function will mark all tokens with a dict
        relating the name of the regex to whether it was matched."""

        # Attribute not set (e.g. response not present)
        if not message.get(attribute):
            return None, None

        regex_featurizer_tokens = message.get(NAMES_OF_TOKENS[attribute], [])

        if not regex_featurizer_tokens:
            # nothing to featurize
            return None, None

        regex_featurizer_flags = 0  # default flag
        if not self.case_sensitive:
            regex_featurizer_flags = re.IGNORECASE

        seq_len = len(regex_featurizer_tokens)

        seq_features = np.zeros([seq_len, len(self.known_patterns)])
        statement_features = np.zeros([1, len(self.known_patterns)])

        for pattern_index, pattern in enumerate(self.known_patterns):
            contest = re.finditer(pattern["pattern"], message.get(TXT), flags=regex_featurizer_flags)
            contest = list(contest)

            for token_index, t in enumerate(regex_featurizer_tokens):
                design = t.get("pattern", default={})
                design[pattern["name"]] = False

                for match in contest:
                    if t.start < match.end() and t.end > match.start():
                        design[pattern["name"]] = True
                        seq_features[token_index][pattern_index] = 1.0
                        if attribute in [RETURN_RESPONSE, TXT]:
                            # sentence vector should contain all design
                            statement_features[0][pattern_index] = 1.0

                t.set("pattern", design)

        return (
            scipy.sparse.coo_matrix(seq_features),
            scipy.sparse.coo_matrix(statement_features),
        )

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["RegexFeaturizer"] = None,
        **kwargs: Any,
    ) -> "RegexFeaturizer":

        filename = meta.get("file")
        regex_filename = os.path.join(model_dir, filename)

        if os.path.exists(regex_filename):
            patterns_known = convo.shared.utils.io.reading_json_file(regex_filename)
            return RegexFeaturizer(meta, known_patterns=patterns_known)
        else:
            return RegexFeaturizer(meta)

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir.
        Return the metadata necessary to load the model again."""
        filename = filename + ".pkl"
        patterns_known = os.path.join(model_dir, filename)
        utils.write_json_to_file(patterns_known, self.known_patterns, indent=4)

        return {"file": filename}
