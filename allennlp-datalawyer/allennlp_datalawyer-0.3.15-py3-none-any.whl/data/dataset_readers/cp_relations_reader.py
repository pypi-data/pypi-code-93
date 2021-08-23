import logging
import json

from typing import Dict, Iterator

from allennlp.common.file_utils import cached_path
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.fields import TextField, MetadataField, LabelField, IndexField
from allennlp.data.instance import Instance
from allennlp.data.token_indexers import TokenIndexer

logger = logging.getLogger(__name__)


@DatasetReader.register("cp_relations_reader")
class RelationsDatasetReader(DatasetReader):

    def __init__(self,
                 label_namespace: str = "labels",
                 token_indexers: Dict[str, TokenIndexer] = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self._token_indexers = token_indexers
        self.label_namespace = label_namespace

    def _read(self, file_path: str) -> Iterator[Instance]:
        file_path = cached_path(file_path)
        with open(file_path, mode='r', encoding='utf8') as f:
            for line in f.readlines():
                yield self.text_to_instance(json.loads(line))

    def text_to_instance(self, cp_data_item: Dict) -> Instance:
        fields = dict()

        tokens = cp_data_item['token']
        tokenized_context = self._token_indexers["tokens"]._allennlp_tokenizer.tokenize(' '.join(tokens))

        context_field = TextField(tokens=tokenized_context, token_indexers=self._token_indexers)
        fields["context"] = context_field

        head_position = [idx for idx, token in enumerate(tokenized_context) if token.text == '[unused1]'][0]
        tail_position = [idx for idx, token in enumerate(tokenized_context) if token.text == '[unused3]'][0]

        fields["head"] = IndexField(index=head_position, sequence_field=context_field)
        fields["tail"] = IndexField(index=tail_position, sequence_field=context_field)

        if 'relation' in cp_data_item and cp_data_item['relation'] is not None:
            fields["labels"] = LabelField(label=cp_data_item['relation'], label_namespace=self.label_namespace)

        # make the metadata
        fields["metadata"] = MetadataField(metadata={
            "data_item": cp_data_item,
            "context_tokens": tokenized_context
        })

        return Instance(fields)
