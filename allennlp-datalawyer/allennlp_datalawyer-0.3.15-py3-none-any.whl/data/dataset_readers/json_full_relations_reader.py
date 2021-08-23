import logging

from itertools import combinations
from typing import Dict, List, Iterator

from allennlp.data import Token
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.fields import TextField, SpanField, MetadataField, LabelField, ListField
from allennlp.data.instance import Instance
from allennlp.data.token_indexers import TokenIndexer

from allennlp_datalawyer.data.dataset_readers.base_json_reader import BaseJsonReader
from allennlp_datalawyer.data.dataset_readers.json_relations_reader import get_relation_for_entities_pair
from allennlp_datalawyer.data.dataset_readers.relations import Entity, Relation, NO_RELATION_LABEL

logger = logging.getLogger(__name__)


@DatasetReader.register("full_relations_reader")
class FullRelationsDatasetReader(BaseJsonReader):

    def __init__(self,
                 add_negative_samples: bool = True,
                 label_namespace: str = "labels",
                 token_indexers: Dict[str, TokenIndexer] = None,
                 **kwargs) -> None:
        super().__init__(token_indexers, **kwargs)
        self.add_negative_samples = add_negative_samples
        self.label_namespace = label_namespace

    def _read(self, file_path: str) -> Iterator[Instance]:

        for sentence in self._load_sentences(file_path=file_path):
            context = [token.phrase for token in sentence.tokens]
            tokenized_context = self.tokenizer.tokenize(' '.join(context))

            if self.add_negative_samples:

                negative_tuples = [(entity_1, entity_2) for entity_1, entity_2 in combinations(sentence.entities, 2)
                                   if
                                   get_relation_for_entities_pair(entity_1, entity_2, sentence.relations) is None]

                for idx, (entity_1, entity_2) in enumerate(negative_tuples):
                    sentence.relations.append(
                        Relation(rid=idx + len(sentence.relations),
                                 sentence_id=sentence.sentence_id,
                                 relation_type=NO_RELATION_LABEL,
                                 head_entity=entity_1, tail_entity=entity_2))

            if len(sentence.entities) > 1:
                yield self.text_to_instance(context=context, entities=sentence.entities, relations=sentence.relations,
                                            tokenized_context=tokenized_context)

    def text_to_instance(self,
                         context: List[str],
                         entities: List[Entity],
                         relations: List[Relation],
                         tokenized_context: List[Token]) -> Instance:
        fields = dict()

        if tokenized_context is None:
            tokenized_context = self.tokenizer.tokenize(' '.join(context))

        context_field = TextField(tokens=tokenized_context, token_indexers=self._token_indexers)
        fields["context"] = context_field
        entities_spans = []

        for entity in entities:
            entities_spans.append(SpanField(span_start=entity.span_start,
                                            span_end=entity.span_end,
                                            sequence_field=context_field))

        fields["entities_spans"] = ListField(entities_spans)

        head_entities = []
        tail_entities = []
        labels = []

        for relation in relations:
            head_entities.append(SpanField(span_start=relation.head_entity.span_start,
                                           span_end=relation.head_entity.span_end,
                                           sequence_field=context_field))
            tail_entities.append(SpanField(span_start=relation.tail_entity.span_start,
                                           span_end=relation.tail_entity.span_end,
                                           sequence_field=context_field))
            if relation.relation_type is not None:
                labels.append(LabelField(label=relation.relation_type, label_namespace=self.label_namespace))

        if len(relations) > 0:
            fields["heads"] = ListField(head_entities) if len(head_entities) > 0 else None
            fields["tails"] = ListField(tail_entities) if len(tail_entities) > 0 else None

        if len(labels) > 0:
            fields["labels"] = ListField(labels)

        # make the metadata
        fields["metadata"] = MetadataField(metadata={
            "entities": entities,
            "relations": relations,
            "context": context,
            "context_tokens": tokenized_context
        })

        return Instance(fields)
