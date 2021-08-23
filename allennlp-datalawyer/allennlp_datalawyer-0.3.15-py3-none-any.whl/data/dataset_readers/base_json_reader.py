import logging
import json

from typing import Dict, List, Iterator

from allennlp.common.file_utils import cached_path
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.token_indexers import TokenIndexer
from allennlp.data.tokenizers import Tokenizer

from allennlp_datalawyer.data.dataset_readers.relations import SingleToken, Sentence, Entity, Relation, clean_text

logger = logging.getLogger(__name__)


class BaseJsonReader(DatasetReader):

    def __init__(self,
                 token_indexers: Dict[str, TokenIndexer] = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self._token_indexers = token_indexers

    @property
    def tokenizer(self) -> Tokenizer:
        return self._token_indexers["tokens"]._allennlp_tokenizer

    def _load_sentences(self, file_path: str) -> Iterator[Sentence]:
        file_path = cached_path(file_path)
        json_sentences = json.load(open(file_path, mode='r', encoding='utf-8'))
        for json_sentence in json_sentences:
            if json_sentence:
                yield self._parse_sentence(json_sentence)

    def _parse_sentence(self, sentence_json):
        sentence_id = sentence_json['orig_id']
        tokens_json = sentence_json['tokens']
        if 'relations' in sentence_json:
            relations_json = sentence_json['relations']
        entities_json = sentence_json['entities']

        # parse tokens
        sentence_tokens, sentence_encoding = self._parse_tokens(tokens_json, sentence_id)

        # parse entity mentions
        entities = self._parse_entities(entities_json, sentence_tokens, sentence_id)

        # parse relations
        if 'relations' in sentence_json:
            relations = self._parse_relations(relations_json, entities, sentence_id)
        else:
            relations = []

        return Sentence(sentence_id=sentence_id, tokens=sentence_tokens, entities=entities,
                        relations=relations, encoding=sentence_encoding)

    def _parse_tokens(self, tokens_json: List[str], sentence_id):
        sentence_tokens = []

        sentence_encoding = [self.tokenizer.tokenizer.convert_tokens_to_ids('[CLS]')]

        # parse tokens
        for token_idx, token_phrase in enumerate(tokens_json):
            token_encoding = self.tokenizer.tokenizer.encode(token_phrase, add_special_tokens=False)
            span_start, span_end = (len(sentence_encoding), len(sentence_encoding) + len(token_encoding))

            token = SingleToken(tid=token_idx, sentence_id=sentence_id, index=token_idx,
                                span_start=span_start, span_end=span_end, phrase=token_phrase)

            sentence_tokens.append(token)
            sentence_encoding += token_encoding

        sentence_encoding += [self.tokenizer.tokenizer.convert_tokens_to_ids('[SEP]')]

        return sentence_tokens, sentence_encoding

    @staticmethod
    def _parse_entities(entities_json: List[dict], sentence_tokens: List[SingleToken], sentence_id: str) -> \
            List[Entity]:
        entities = []

        for entity_idx, entity_json in enumerate(entities_json):
            entity_type = entity_json['type']
            start, end = entity_json['start'], entity_json['end']

            # create entity mention
            tokens = sentence_tokens[start:end]
            phrase = entity_json['text']
            if type(phrase) == str:
                phrase = clean_text(phrase)
                assert "".join([token.phrase for token in tokens]).replace(" ", "") == phrase.replace(" ", "")
            elif type(phrase) == list:
                assert "".join([token.phrase for token in tokens]).replace(" ", "") == "".join(
                    [token for token in phrase]).replace(" ", "")
            if 'id' in entity_json:
                custom_id = entity_json['id']
            else:
                custom_id = 'sent_id:' + str(sentence_id) + '/category:' + entity_type + '/span:' + str(
                    start) + '-' + str(
                    end)
            entity = Entity(eid=entity_idx, sentence_id=sentence_id,
                            entity_type=entity_type, tokens=tokens, phrase=phrase,
                            start_token_idx=start, end_token_idx=end,
                            custom_id=custom_id)
            entities.append(entity)

        return entities

    @staticmethod
    def _parse_relations(relations_json: List[dict], entities: List[Entity], sentence_id: str) -> List[Relation]:
        relations = []

        for relation_idx, relation_json in enumerate(relations_json):
            relation_type = relation_json['type'] if 'type' in relation_json else None

            head_idx = relation_json['head']
            tail_idx = relation_json['tail']

            # create relation
            head = entities[head_idx]
            tail = entities[tail_idx]

            reverse = int(tail.tokens[0].index) < int(head.tokens[0].index)

            relation = Relation(rid=relation_idx, sentence_id=sentence_id, relation_type=relation_type,
                                head_entity=head, tail_entity=tail, reverse=reverse)
            relations.append(relation)

        return relations
