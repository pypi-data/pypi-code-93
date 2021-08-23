from typing import Dict, List, Iterable
import logging

from overrides import overrides

from allennlp.common.checks import ConfigurationError
from allennlp.data.dataset_readers.dataset_reader import DatasetReader, PathOrStr
from allennlp.data.dataset_readers.dataset_utils import to_bioul
from allennlp.data.fields import TextField, SequenceLabelField, Field, MetadataField
from allennlp.data.instance import Instance
from allennlp.data.token_indexers import TokenIndexer
from allennlp.data.tokenizers import Token

from allennlp_datalawyer.data.dataset_readers.base_json_reader import BaseJsonReader

logger = logging.getLogger(__name__)


@DatasetReader.register("entities_reader")
class EntitiesDatasetReader(BaseJsonReader):

    def __init__(
            self,
            token_indexers: Dict[str, TokenIndexer] = None,
            coding_scheme: str = "IOB1",
            label_namespace: str = "labels",
            **kwargs,
    ) -> None:
        super().__init__(
            token_indexers, manual_distributed_sharding=True, manual_multiprocess_sharding=True, **kwargs
        )

        if coding_scheme not in ("IOB1", "BIOUL"):
            raise ConfigurationError("unknown coding_scheme: {}".format(coding_scheme))

        self.coding_scheme = coding_scheme
        self.label_namespace = label_namespace
        self._original_coding_scheme = "IOB1"

    @overrides
    def _read(self, file_path: PathOrStr) -> Iterable[Instance]:
        for sentence in self._load_sentences(file_path=file_path):

            entities_labels = dict()
            for entity in sentence.entities:
                for position in range(entity.tokens[0].index, entity.tokens[-1].index + 1):
                    prefix = 'B' if position == entity.tokens[0].index else 'I'
                    entities_labels[position] = prefix + '-' + entity.entity_type

            ner_tags = []
            for idx, token in enumerate(sentence.tokens):
                ner_tag = entities_labels[idx] if idx in entities_labels else 'O'
                ner_tags.append(ner_tag)

            tokens = [Token(token.phrase) for token in sentence.tokens]
            yield self.text_to_instance(tokens, ner_tags)

    def text_to_instance(  # type: ignore
            self,
            tokens: List[Token],
            ner_tags: List[str] = None,
    ) -> Instance:
        """
        We take `pre-tokenized` input here, because we don't have a tokenizer in this class.
        """

        sequence = TextField(tokens)
        instance_fields: Dict[str, Field] = {"tokens": sequence}
        instance_fields["metadata"] = MetadataField({"words": [x.text for x in tokens]})

        # Recode the labels if necessary.
        if self.coding_scheme == "BIOUL":
            coded_ner = (
                to_bioul(ner_tags, encoding=self._original_coding_scheme)
                if ner_tags is not None
                else None
            )
        else:
            # the default IOB1
            coded_ner = ner_tags

        if coded_ner is not None:
            instance_fields["tags"] = SequenceLabelField(coded_ner, sequence, self.label_namespace)

        return Instance(instance_fields)

    @overrides
    def apply_token_indexers(self, instance: Instance) -> None:
        instance.fields["tokens"]._token_indexers = self._token_indexers  # type: ignore
