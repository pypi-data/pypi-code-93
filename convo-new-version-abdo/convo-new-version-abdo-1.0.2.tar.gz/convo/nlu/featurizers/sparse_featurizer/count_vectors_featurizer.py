import logging
import os
import re
import scipy.sparse
from typing import Any, Dict, List, Optional, Text, Type, Tuple

import convo.shared.utils.io
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
import convo.utils.io as io_utils
from sklearn.feature_extraction.text import CountVectorizer
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.tokenizers.tokenizer import Tokenizer
from convo.nlu.components import Element
from convo.nlu.featurizers.featurizer import InfrequentFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.model import Metadataset
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import (
    NAMES_OF_TOKENS,
    MSG_ATTRS,
    DENSE_FEATURE_ATTRS,
    FEATURE_CLASS_AS,
)
from convo.shared.nlu.constants import (
    TXT,
    INTENTION,
    KEY_INTENT_RESPONSE,
    FEATURED_TYPE_SENTENCE,
    FEATURED_TYPE_SEQUENCE,
    ACT_NAME,
)

logger = logging.getLogger(__name__)


class CountVectorsFeaturizer(InfrequentFeaturizer):
    """Creates a sequence of token counts features based on sklearn's `CountVectorizer`.

    All tokens which consist only of digits (e.g. 123 and 99
    but not ab12d) will be represented by a single feature.

    Set `analyzer` to 'char_wb'
    to use the idea of Subword Semantic Hashing
    from https://arxiv.org/abs/1810.07150.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [Tokenizer]

    defaults = {
        # whether to use a shared vocab
        "use_shared_vocab": False,
        # the parameters are taken from
        # sklearn's CountVectorizer
        # whether to use word or character n-grams
        # 'char_wb' creates character n-grams inside word boundaries
        # n-grams at the edges of words are padded with space.
        "analyzer": "word",  # use 'char' or 'char_wb' for character
        # remove accents during the preprocessing step
        "strip_accents": None,  # {'ascii', 'unicode', None}
        # list of stop words
        "stop_words": None,  # string {'english'}, list, or None (default)
        # min document frequency of a word to add to vocabulary
        # float - the parameter represents a proportion of documents
        # integer - absolute counts
        "min_df": 1,  # float in range [0.0, 1.0] or int
        # max document frequency of a word to add to vocabulary
        # float - the parameter represents a proportion of documents
        # integer - absolute counts
        "max_df": 1.0,  # float in range [0.0, 1.0] or int
        # set range of ngrams to be extracted
        "min_ngram": 1,  # int
        "max_ngram": 1,  # int
        # limit vocabulary size
        "max_features": None,  # int or None
        # if convert all characters to lowercase
        "lowercase": True,  # bool
        # handling Out-Of-Vocabulary (OOV) words
        # will be converted to lowercase if lowercase is True
        "OOV_token": None,  # string or None
        "OOV_words": [],  # string or list of strings
        # indicates whether the featurizer should use the lemma of a word for
        # counting (if available) or not
        "use_lemma": True,
    }

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["sklearn"]

    def _load_count_vect_parameters(self) -> None:

        # Use shared vocabulary between text and all others attributes of Msg
        self.use_shared_vocab = self.component_config["use_shared_vocab"]

        # set analyzer
        self.analyzer = self.component_config["analyzer"]

        # remove accents during the preprocessing step
        self.strip_accents = self.component_config["strip_accents"]

        # list of stop words
        self.stop_words = self.component_config["stop_words"]

        # min number of word occurancies in the document to add to vocabulary
        self.min_df = self.component_config["min_df"]

        # max number (fraction if float) of word occurancies
        # in the document to add to vocabulary
        self.max_df = self.component_config["max_df"]

        # set ngram range
        self.min_ngram = self.component_config["min_ngram"]
        self.max_ngram = self.component_config["max_ngram"]

        # limit vocabulary size
        self.max_features = self.component_config["max_features"]

        # if convert all characters to lowercase
        self.lowercase = self.component_config["lowercase"]

        # use the lemma of the words or not
        self.use_lemma = self.component_config["use_lemma"]

    # noinspection PyPep8Naming
    def _load_OOV_parameters(self) -> None:
        self.OOV_token = self.component_config["OOV_token"]

        self.OOV_words = self.component_config["OOV_words"]
        if self.OOV_words and not self.OOV_token:
            logger.error(
                "The list OOV_words={} was given, but "
                "OOV_token was not. OOV words are ignored."
                "".format(self.OOV_words)
            )
            self.OOV_words = []

        if self.lowercase and self.OOV_token:
            # convert to lowercase
            self.OOV_token = self.OOV_token.lower()
            if self.OOV_words:
                self.OOV_words = [w.lower() for w in self.OOV_words]

    def _check_attribute_vocab(self, attribute: Text) -> bool:
        """Check if trained vocabulary exists in attribute's count vectorizer"""
        try:
            return hasattr(self.vectorizers[attribute], "vocabulary_")
        except (AttributeError, TypeError):
            return False

    def _fetch_attribute_vocab(self, attribute: Text) -> Optional[Dict[Text, int]]:
        """Get trained vocabulary from attribute's count vectorizer"""

        try:
            return self.vectorizers[attribute].vocabulary_
        except (AttributeError, TypeError):
            return None

    def _fetch_attribute_vocab_tokens(self, attribute: Text) -> Optional[List[Text]]:
        """Get all keys of vocabulary of an attribute"""

        attribute_vocab = self._fetch_attribute_vocab(attribute)
        try:
            return list(attribute_vocab.keys())
        except TypeError:
            return None

    def _examine_analyzer(self) -> None:
        if self.analyzer != "word":
            if self.OOV_token is not None:
                logger.warning(
                    "Analyzer is set to character, "
                    "provided OOV word token will be ignored."
                )
            if self.stop_words is not None:
                logger.warning(
                    "Analyzer is set to character, "
                    "provided stop words will be ignored."
                )
            if self.max_ngram == 1:
                logger.warning(
                    "Analyzer is set to character, "
                    "but max n-gram is set to 1. "
                    "It means that the vocabulary will "
                    "contain single letters only."
                )

    @staticmethod
    def _attr_for(analyzer: Text) -> List[Text]:
        """Create a list of attributes that should be featurized."""

        # convo_intents should be featurized only by word level count vectorizer
        return (
            MSG_ATTRS if analyzer == "word" else DENSE_FEATURE_ATTRS
        )

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        vectorizers: Optional[Dict[Text, "CountVectorizer"]] = None,
    ) -> None:
        """Construct a new count vectorizer using the sklearn framework."""

        super().__init__(component_config)

        # parameters for sklearn's CountVectorizer
        self._load_count_vect_parameters()

        # handling Out-Of-Vocabulary (OOV) words
        self._load_OOV_parameters()

        # warn that some of config parameters might be ignored
        self._examine_analyzer()

        # set which attributes to featurize
        self._attributes = self._attr_for(self.analyzer)

        # declare class instance for CountVectorizer
        self.vectorizers = vectorizers

    def _fetch_msg_tokens_by_attribute(
        self, message: "Msg", attribute: Text
    ) -> List[Text]:
        """Get text tokens of an attribute of a message"""
        if message.get(NAMES_OF_TOKENS[attribute]):
            return [
                t.lemma if self.use_lemma else t.text
                for t in message.get(NAMES_OF_TOKENS[attribute])
            ]
        else:
            return []

    def _tokens_processed(self, count_vectors_featurizer_tokens: List[Text], attribute: Text = TXT) -> List[Text]:
        """Apply processing and cleaning steps to text"""

        if attribute in [INTENTION, ACT_NAME, KEY_INTENT_RESPONSE]:
            # Don't do any processing for intent attribute. Treat them as whole labels
            return count_vectors_featurizer_tokens

        # replace all digits with NUMBER token
        count_vectors_featurizer_tokens = [re.sub(r"\b[0-9]+\b", "__NUMBER__", text) for text in count_vectors_featurizer_tokens]

        # convert to lowercase if necessary
        if self.lowercase:
            count_vectors_featurizer_tokens = [text.lower() for text in count_vectors_featurizer_tokens]

        return count_vectors_featurizer_tokens

    def _change_with_oov_token(
        self, count_vectors_featurizer_tokens: List[Text], attribute: Text
    ) -> List[Text]:
        """Replace OOV words with OOV token"""

        if self.OOV_token and self.analyzer == "word":
            vocabulary_exists = self._check_attribute_vocab(attribute)
            if vocabulary_exists and self.OOV_token in self._fetch_attribute_vocab(
                attribute
            ):
                # CountVectorizer is trained, process for prediction
                count_vectors_featurizer_tokens = [
                    t
                    if t in self._fetch_attribute_vocab_tokens(attribute)
                    else self.OOV_token
                    for t in count_vectors_featurizer_tokens
                ]
            elif self.OOV_words:
                # CountVectorizer is not trained, process for train
                count_vectors_featurizer_tokens = [self.OOV_token if t in self.OOV_words else t for t in count_vectors_featurizer_tokens]

        return count_vectors_featurizer_tokens

    def _fetch_processed_msg_tokens_by_attribute(
        self, message: Msg, attribute: Text = TXT
    ) -> List[Text]:
        """Get processed text of attribute of a message"""

        if message.get(attribute) is None:
            # return empty list since sklearn countvectorizer does not like None
            # object while training and predicting
            return []

        count_vectors_featurizer_tokens = self._fetch_msg_tokens_by_attribute(message, attribute)
        count_vectors_featurizer_tokens = self._tokens_processed(count_vectors_featurizer_tokens, attribute)
        count_vectors_featurizer_tokens = self._change_with_oov_token(count_vectors_featurizer_tokens, attribute)

        return count_vectors_featurizer_tokens

    # noinspection PyPep8Naming
    def _examine_OOV_present(self, all_tokens: List[List[Text]], attribute: Text) -> None:
        """Check if an OOV word is present"""
        if not self.OOV_token or self.OOV_words or not all_tokens:
            return

        for tokens in all_tokens:
            for text in tokens:
                if self.OOV_token in text or (
                    self.lowercase and self.OOV_token in text.lower()
                ):
                    return

        if any(text for tokens in all_tokens for text in tokens):
            training_data_set_type = "NLU" if attribute == TXT else "ResponseSelector"

            # if there is some text in tokens, warn if there is no oov token
            convo.shared.utils.io.raising_warning(
                f"The out of vocabulary token '{self.OOV_token}' was configured, but "
                f"could not be found in any one of the {training_data_set_type} "
                f"training examples. All unseen words will be ignored during prediction.",
                docs=COMPONENTS_DOCUMENTS_URL + "#countvectorsfeaturizer",
            )

    def _fetch_all_attributes_processed_tokens(
        self, training_data: TrainingDataSet
    ) -> Dict[Text, List[List[Text]]]:
        """Get processed text for all attributes of examples in training data"""

        processed_attr_tokens = {}
        for attribute in self._attributes:
            every_tokens = [
                self._fetch_processed_msg_tokens_by_attribute(example, attribute)
                for example in training_data.training_examples
            ]
            if attribute in DENSE_FEATURE_ATTRS:
                # check for oov tokens only in text based attributes
                self._examine_OOV_present(every_tokens, attribute)
            processed_attr_tokens[attribute] = every_tokens

        return processed_attr_tokens

    @staticmethod
    def _change_attribute_tokens_to_txt(
        attribute_tokens: Dict[Text, List[List[Text]]]
    ) -> Dict[Text, List[Text]]:
        attr_txts = {}

        for attribute in attribute_tokens.keys():
            tokens_list = attribute_tokens[attribute]
            attr_txts[attribute] = [" ".join(tokens) for tokens in tokens_list]

        return attr_txts

    def _train_with_shared_vocabulary(self, attribute_texts: Dict[Text, List[Text]]):
        """Construct the vectorizers and train them with a shared vocab"""

        self.vectorizers = self._generate_shared_vocab_vectorizers(
            {
                "strip_accents": self.strip_accents,
                "lowercase": self.lowercase,
                "stop_words": self.stop_words,
                "min_ngram": self.min_ngram,
                "max_ngram": self.max_ngram,
                "max_df": self.max_df,
                "min_df": self.min_df,
                "max_features": self.max_features,
                "analyzer": self.analyzer,
            }
        )

        combined_cleaned_txt = []
        for attribute in self._attributes:
            combined_cleaned_txt += attribute_texts[attribute]

        try:
            self.vectorizers[TXT].fit(combined_cleaned_txt)
        except ValueError:
            logger.warning(
                "Unable to train a shared CountVectorizer. "
                "Leaving an untrained CountVectorizer"
            )

    @staticmethod
    def _attr_txt_is_non_empty(attribute_texts: List[Text]) -> bool:
        return any(attribute_texts)

    def _train_with_independent_vocabulary(self, attribute_texts: Dict[Text, List[Text]]):
        """Construct the vectorizers and train them with an independent vocab"""

        self.vectorizers = self._generate_independent_vocab_vectorizers(
            {
                "strip_accents": self.strip_accents,
                "lowercase": self.lowercase,
                "stop_words": self.stop_words,
                "min_ngram": self.min_ngram,
                "max_ngram": self.max_ngram,
                "max_df": self.max_df,
                "min_df": self.min_df,
                "max_features": self.max_features,
                "analyzer": self.analyzer,
            }
        )

        for attribute in self._attributes:
            if self._attr_txt_is_non_empty(attribute_texts[attribute]):
                try:
                    self.vectorizers[attribute].fit(attribute_texts[attribute])
                except ValueError:
                    logger.warning(
                        f"Unable to train CountVectorizer for message "
                        f"attribute {attribute}. Leaving an untrained "
                        f"CountVectorizer for it."
                    )
            else:
                logger.debug(
                    f"No text provided for {attribute} attribute in any messages of "
                    f"training data. Skipping training a CountVectorizer for it."
                )

    def _generate_features(
        self, attribute: Text, all_tokens: List[List[Text]]
    ) -> Tuple[
        List[Optional[scipy.sparse.spmatrix]], List[Optional[scipy.sparse.spmatrix]]
    ]:
        if not self.vectorizers.get(attribute):
            return [None], [None]

        seq_features = []
        statement_features = []

        for i, tokens in enumerate(all_tokens):
            if not tokens:
                # nothing to featurize
                seq_features.append(None)
                statement_features.append(None)
                continue

            # vectorizer.transform returns a sparse matrix of size
            # [n_samples, n_features]
            # set input to list of tokens if sequence should be returned
            # otherwise join all tokens to a single string and pass that as a list
            if not tokens:
                # attribute is not set (e.g. response not present)
                seq_features.append(None)
                statement_features.append(None)
                continue

            sequence_vec = self.vectorizers[attribute].transform(tokens)
            sequence_vec.sort_indices()

            seq_features.append(sequence_vec.tocoo())

            if attribute in DENSE_FEATURE_ATTRS:
                tokens_txt = [" ".join(tokens)]
                statement_vec = self.vectorizers[attribute].transform(tokens_txt)
                statement_vec.sort_indices()

                statement_features.append(statement_vec.tocoo())
            else:
                statement_features.append(None)

        return seq_features, statement_features

    def _fetch_featurized_attribute(
        self, attribute: Text, all_tokens: List[List[Text]]
    ) -> Tuple[
        List[Optional[scipy.sparse.spmatrix]], List[Optional[scipy.sparse.spmatrix]]
    ]:
        """Return features of a particular attribute for complete data"""

        if self._check_attribute_vocab(attribute):
            # count vectorizer was trained
            return self._generate_features(attribute, all_tokens)
        else:
            return [], []

    def _put_attribute_features(
        self,
        attribute: Text,
        sequence_features: List[scipy.sparse.spmatrix],
        sentence_features: List[scipy.sparse.spmatrix],
        examples: List[Msg],
    ) -> None:
        """Set computed features of the attribute to corresponding message objects"""
        for i, message in enumerate(examples):
            # create bag for each example
            if sequence_features[i] is not None:
                final_seq_features = Features(
                    sequence_features[i],
                    FEATURED_TYPE_SEQUENCE,
                    attribute,
                    self.component_config[FEATURE_CLASS_AS],
                )
                message.adding_features(final_seq_features)

            if sentence_features[i] is not None:
                final_seq_features = Features(
                    sentence_features[i],
                    FEATURED_TYPE_SENTENCE,
                    attribute,
                    self.component_config[FEATURE_CLASS_AS],
                )
                message.adding_features(final_seq_features)

    def train(
        self,
        training_data: TrainingDataSet,
        cfg: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        """Train the featurizer.

        Take parameters from config and
        construct a new count vectorizer using the sklearn framework.
        """

        nlp_spacy = kwargs.get("spacy_nlp")
        if nlp_spacy is not None:
            # create spacy lemma_ for OOV_words
            self.OOV_words = [
                t.lemma_ if self.use_lemma else t.text
                for w in self.OOV_words
                for t in nlp_spacy(w)
            ]

        # process sentences and collect data for all attributes
        processed_attr_tokens = self._fetch_all_attributes_processed_tokens(
            training_data
        )

        # train for all attributes
        attribute_txt = self._change_attribute_tokens_to_txt(
            processed_attr_tokens
        )
        if self.use_shared_vocab:
            self._train_with_shared_vocabulary(attribute_txt)
        else:
            self._train_with_independent_vocabulary(attribute_txt)

        # transform for all attributes
        for attribute in self._attributes:
            seq_features, statement_features = self._fetch_featurized_attribute(
                attribute, processed_attr_tokens[attribute]
            )

            if seq_features and statement_features:
                self._put_attribute_features(
                    attribute,
                    seq_features,
                    statement_features,
                    training_data.training_examples,
                )

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Process incoming message and compute and set features"""

        if self.vectorizers is None:
            logger.error(
                "There is no trained CountVectorizer: "
                "component is either not trained or "
                "didn't receive enough training data"
            )
            return
        for attribute in self._attributes:
            msg_tokens = self._fetch_processed_msg_tokens_by_attribute(
                message, attribute
            )

            # features shape (1, seq, dim)
            seq_features, statement_features = self._generate_features(
                attribute, [msg_tokens]
            )

            self._put_attribute_features(
                attribute, seq_features, statement_features, [message]
            )

    def _gather_vectorizer_vocabularies(self) -> Dict[Text, Optional[Dict[Text, int]]]:
        """Get vocabulary for all attributes"""

        attr_vocabularies = {}
        for attribute in self._attributes:
            attr_vocabularies[attribute] = self._fetch_attribute_vocab(
                attribute
            )
        return attr_vocabularies

    @staticmethod
    def _is_any_trained_model(attribute_vocabularies) -> bool:
        """Check if any model got trained"""

        return any(value is not None for value in attribute_vocabularies.values())

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir.

        Returns the metadata necessary to load the model again.
        """

        filename = filename + ".pkl"

        if self.vectorizers:
            # vectorizer instance was not None, some models could have been trained
            attr_vocabularies = self._gather_vectorizer_vocabularies()
            if self._is_any_trained_model(attr_vocabularies):
                # Definitely need to persist some vocabularies
                featurizer_filename = os.path.join(model_dir, filename)

                if self.use_shared_vocab:
                    # Only persist vocabulary from one attribute. Can be loaded and
                    # distributed to all attributes.
                    vocabulary = attr_vocabularies[TXT]
                else:
                    vocabulary = attr_vocabularies

                io_utils.dictionary_pickle(featurizer_filename, vocabulary)

        return {"file": filename}

    @classmethod
    def _generate_shared_vocab_vectorizers(
        cls, parameters: Dict[Text, Any], vocabulary: Optional[Any] = None
    ) -> Dict[Text, CountVectorizer]:
        """Create vectorizers for all attributes with shared vocabulary"""

        vectorizer_shared = CountVectorizer(
            token_pattern=r"(?u)\b\w+\b" if parameters["analyzer"] == "word" else None,
            strip_accents=parameters["strip_accents"],
            lowercase=parameters["lowercase"],
            stop_words=parameters["stop_words"],
            ngram_range=(parameters["min_ngram"], parameters["max_ngram"]),
            max_df=parameters["max_df"],
            min_df=parameters["min_df"],
            max_features=parameters["max_features"],
            analyzer=parameters["analyzer"],
            vocabulary=vocabulary,
        )

        attr_vectorizers = {}

        for attribute in cls._attr_for(parameters["analyzer"]):
            attr_vectorizers[attribute] = vectorizer_shared

        return attr_vectorizers

    @classmethod
    def _generate_independent_vocab_vectorizers(
        cls, parameters: Dict[Text, Any], vocabulary: Optional[Any] = None
    ) -> Dict[Text, CountVectorizer]:
        """Create vectorizers for all attributes with independent vocabulary"""

        attribute_vectorizers = {}

        for attribute in cls._attr_for(parameters["analyzer"]):
            attr_vocabulary = vocabulary[attribute] if vocabulary else None

            attr_vectorizers = CountVectorizer(
                token_pattern=r"(?u)\b\w+\b"
                if parameters["analyzer"] == "word"
                else None,
                strip_accents=parameters["strip_accents"],
                lowercase=parameters["lowercase"],
                stop_words=parameters["stop_words"],
                ngram_range=(parameters["min_ngram"], parameters["max_ngram"]),
                max_df=parameters["max_df"],
                min_df=parameters["min_df"],
                max_features=parameters["max_features"],
                analyzer=parameters["analyzer"],
                vocabulary=attr_vocabulary,
            )
            attribute_vectorizers[attribute] = attr_vectorizers

        return attribute_vectorizers

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["CountVectorsFeaturizer"] = None,
        **kwargs: Any,
    ) -> "CountVectorsFeaturizer":

        filename = meta.get("file")
        featurizer_filename = os.path.join(model_dir, filename)

        if not os.path.exists(featurizer_filename):
            return cls(meta)

        vocab = io_utils.json_un_pickle(featurizer_filename)

        share_vocab = meta["use_shared_vocab"]

        if share_vocab:
            vectorizers = cls._generate_shared_vocab_vectorizers(
                meta, vocabulary=vocab
            )
        else:
            vectorizers = cls._generate_independent_vocab_vectorizers(
                meta, vocabulary=vocab
            )

        ftr = cls(meta, vectorizers)

        # make sure the vocabulary has been loaded correctly
        for attribute in vectorizers:
            ftr.vectorizers[attribute]._validate_vocabulary()

        return ftr
