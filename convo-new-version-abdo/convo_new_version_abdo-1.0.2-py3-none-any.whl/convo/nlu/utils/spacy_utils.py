import logging
import typing
from typing import Any, Dict, List, Optional, Text, Tuple

from convo.nlu.components import Element
from convo.nlu.config import ConvoNLUModelConfiguration, overriding_dfault_values
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.model import NotvalidModelError
from convo.nlu.constants import SPACY_DOCUMENTS, DENSE_FEATURE_ATTRS

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from spacy.language import Language
    from spacy.tokens.doc import Doc  # pytype: disable=import-error
    from convo.nlu.model import Metadataset


class SpacyNLP(Element):

    defaults = {
        # name of the language model to load - if it is not set
        # we will be looking for a language model that is named
        # after the language of the model, e.g. `en`
        "model": None,
        # when retrieving word vectors, this will decide if the casing
        # of the word is relevant. E.g. `hello` and `Hello` will
        # retrieve the same vector, if set to `False`. For some
        # applications and models it makes sense to differentiate
        # between these two words, therefore setting this to `True`.
        "case_sensitive": False,
    }

    def __init__(
        self, component_config: Dict[Text, Any] = None, nlp: "Language" = None
    ) -> None:

        self.nlp = nlp
        super().__init__(component_config)

    @staticmethod
    def load_model_data(spacy_model_name: Text) -> "Language":
        """Try loading the model, catching the OSError if missing."""
        import spacy

        try:
            return spacy.load(spacy_model_name, disable=["parser"])
        except OSError:
            raise NotvalidModelError(
                "Model '{}' is not a linked spaCy model.  "
                "Please download and/or link a spaCy model, "
                "e.g. by running:\npython -m spacy download "
                "en_core_web_md\npython -m spacy link "
                "en_core_web_md en".format(spacy_model_name)
            )

    @classmethod
    def req_package(cls) -> List[Text]:
        return ["spacy"]

    @classmethod
    def create(
        cls, component_configuration: Dict[Text, Any], config: ConvoNLUModelConfiguration
    ) -> "SpacyNLP":

        component_configuration = overriding_dfault_values(cls.defaults, component_configuration)

        model_spacy_name = component_configuration.get("model")

        # if no model is specified, we fall back to the language string
        if not model_spacy_name:
            model_spacy_name = config.lang
            component_configuration["model"] = config.lang

        log.info(f"Trying to load spacy model with name '{model_spacy_name}'")

        natural_language_processing = cls.load_model_data(model_spacy_name)

        cls.ensure_proper_lang_model(natural_language_processing)
        return cls(component_configuration, natural_language_processing)

    @classmethod
    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: "Metadataset"
    ) -> Optional[Text]:

        # Fallback, use the language name, e.g. "en",
        # as the model name if no explicit name is defined
        model_spacy_name = component_meta.get("model", model_metadata.lang)

        return cls.name + "-" + model_spacy_name

    def give_context(self) -> Dict[Text, Any]:
        return {"spacy_nlp": self.nlp}

    def txt_for_documents(self, text: Text) -> "Doc":

        return self.nlp(self.pre_procedure_txt(text))

    def pre_procedure_txt(self, text: Optional[Text]) -> Text:

        if text is None:
            # converted to empty string so that it can still be passed to spacy.
            # Another option could be to neglect tokenization of the attribute of
            # this example, but since we are processing in batch mode, it would
            # get complex to collect all processed and neglected examples.
            text = ""
        if self.component_config.get("case_sensitive"):
            return text
        else:
            return text.lower()

    def fetch_txt(self, example: Dict[Text, Any], attribute: Text) -> Text:

        return self.pre_procedure_txt(example.get(attribute))

    @staticmethod
    def mix_content_lst(
        indexed_training_samples: List[Tuple[int, Text]],
        doc_lists: List[Tuple[int, "Doc"]],
    ) -> List[Tuple[int, "Doc"]]:
        """Merge lists with processed Docs back into their original order."""

        dictionary = dict(indexed_training_samples)
        dictionary.update(dict(doc_lists))
        return sorted(dictionary.items())

    @staticmethod
    def train_fltr_sample_by_content(
        indexed_training_samples: List[Tuple[int, Text]]
    ) -> Tuple[List[Tuple[int, Text]], List[Tuple[int, Text]]]:
        """Separates empty training samples from content bearing ones."""

        document_to_pipe = list(
            filter(
                lambda training_sample: training_sample[1] != "",
                indexed_training_samples,
            )
        )
        empty_documents = list(
            filter(
                lambda training_sample: training_sample[1] == "",
                indexed_training_samples,
            )
        )
        return document_to_pipe, empty_documents

    def procedure_content_bear_sample(
        self, samples_to_pipe: List[Tuple[int, Text]]
    ) -> List[Tuple[int, "Doc"]]:
        """Sends content bearing training samples to spaCy's pipe."""

        documents = [
            (to_pipe_sample[0], doc)
            for to_pipe_sample, doc in zip(
                samples_to_pipe,
                [
                    doc
                    for doc in self.nlp.pipe(
                        [txt for _, txt in samples_to_pipe], batch_size=50
                    )
                ],
            )
        ]
        return documents

    def procedure_non_content_bear_sample(
        self, empty_samples: List[Tuple[int, Text]]
    ) -> List[Tuple[int, "Doc"]]:
        """Creates empty Doc-objects from zero-lengthed training samples strings."""

        from spacy.tokens import Doc

        n_documents = [
            (empty_sample[0], doc)
            for empty_sample, doc in zip(
                empty_samples, [Doc(self.nlp.vocab) for doc in empty_samples]
            )
        ]
        return n_documents

    def documents_for_train_data(
        self, training_data: TrainingDataSet
    ) -> Dict[Text, List[Any]]:
        attribute_documents = {}
        for attribute in DENSE_FEATURE_ATTRS:
            txt = [
                self.fetch_txt(e, attribute) for e in training_data.training_examples
            ]
            # Index and freeze indices of the training samples for preserving the order
            # after processing the data.
            index_train_sample = [(idx, text) for idx, text in enumerate(txt)]

            example_to_pipe, void_samples = self.train_fltr_sample_by_content(
                index_train_sample
            )

            content_bearing_documents = self.procedure_content_bear_sample(example_to_pipe)

            non_content_bearing_documents = self.procedure_non_content_bear_sample(
                void_samples
            )

            attribute_doc_lists = self.mix_content_lst(
                index_train_sample,
                content_bearing_documents + non_content_bearing_documents,
            )

            # Since we only need the training samples strings,
            # we create a list to get them out of the tuple.
            attribute_documents[attribute] = [doc for _, doc in attribute_doc_lists]
        return attribute_documents

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        attribute_documents = self.documents_for_train_data(training_data)

        for attribute in DENSE_FEATURE_ATTRS:

            for idx, example in enumerate(training_data.training_examples):
                example_attribute_doc = attribute_documents[attribute][idx]
                if len(example_attribute_doc):
                    # If length is 0, that means the initial text feature
                    # was None and was replaced by ''
                    # in preprocess method
                    example.put(SPACY_DOCUMENTS[attribute], example_attribute_doc)

    def process(self, message: Msg, **kwargs: Any) -> None:
        for attribute in DENSE_FEATURE_ATTRS:
            if message.get(attribute):
                message.put(
                    SPACY_DOCUMENTS[attribute], self.txt_for_documents(message.get(attribute))
                )

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: "Metadataset" = None,
        cached_component: Optional["SpacyNLP"] = None,
        **kwargs: Any,
    ) -> "SpacyNLP":

        if cached_component:
            return cached_component

        name_model = meta.get("model")

        natural_language_processing = cls.load_model_data(name_model)
        cls.ensure_proper_lang_model(natural_language_processing)
        return cls(meta, natural_language_processing)

    @staticmethod
    def ensure_proper_lang_model(nlp: Optional["Language"]) -> None:
        """Checks if the spacy language model is properly loaded.

        Raises an exception if the model is invalid."""

        if nlp is None:
            raise Exception(
                "Failed to load spacy language model. "
                "Loading the model returned 'None'."
            )
        if nlp.path is None:
            # Spacy sets the path to `None` if
            # it did not load the model from disk.
            # In this case `nlp` is an unusable stub.
            raise Exception(
                "Failed to load spacy language model for "
                "lang '{}'. Make sure you have downloaded the "
                "correct model (https://spacy.io/docs/usage/)."
                "".format(nlp.lang)
            )
