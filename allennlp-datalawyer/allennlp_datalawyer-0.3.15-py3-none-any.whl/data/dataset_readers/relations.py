from typing import List

NO_RELATION_LABEL = 'NO_RELATION'
BOM = chr(ord('\ufeff'))


def clean_characters(string: str) -> str:
    return string.replace(BOM, '')


def clean_text(string: str) -> str:
    return clean_characters(string).replace('\n', '')


def get_id(_id: int, sentence_id: str):
    return "{}-{}".format(_id, sentence_id)


class SingleToken:
    def __init__(self, tid: int, index: int, sentence_id: str, span_start: int, span_end: int, phrase: str):
        self._tid = get_id(tid, sentence_id)  # ID within the corresponding dataset
        self._index = index  # original token index in document

        self._span_start = span_start  # start of token span in document (inclusive)
        self._span_end = span_end  # end of token span in document (exclusive)
        self._phrase = phrase

    @property
    def index(self):
        return self._index

    @property
    def span_start(self):
        return self._span_start

    @property
    def span_end(self):
        return self._span_end

    @property
    def span(self):
        return self._span_start, self._span_end

    @property
    def phrase(self):
        return self._phrase

    def __eq__(self, other):
        if isinstance(other, SingleToken):
            return self._tid == other._tid
        return False

    def __hash__(self):
        return hash(self._tid)

    def __str__(self):
        return self._phrase

    def __repr__(self):
        return self._phrase


class TokenSpan:
    def __init__(self, tokens: List[SingleToken]):
        self._tokens = tokens

    @property
    def span_start(self):
        return self._tokens[0].span_start

    @property
    def span_end(self):
        return self._tokens[-1].span_end

    @property
    def span(self):
        return self.span_start, self.span_end

    def __getitem__(self, s):
        if isinstance(s, slice):
            return TokenSpan(self._tokens[s.start:s.stop:s.step])
        else:
            return self._tokens[s]

    def __iter__(self):
        return iter(self._tokens)

    def __len__(self):
        return len(self._tokens)


class Entity:
    def __init__(self,
                 eid: int,
                 sentence_id: str,
                 entity_type: str,
                 tokens: List[SingleToken],
                 phrase: str,
                 start_token_idx: int,
                 end_token_idx: int,
                 custom_id: str = None):
        self._eid: str = get_id(eid, sentence_id)  # ID within the corresponding dataset

        self._entity_type: str = entity_type

        self._tokens: List[SingleToken] = tokens
        self._phrase: str = phrase
        self._start_token_idx = start_token_idx
        self._end_token_idx = end_token_idx
        self._custom_id: str = custom_id

    def to_json(self) -> dict:
        return {
            'id': self.custom_id,
            'type': self.entity_type,
            'tokens': [token.phrase for token in self._tokens],
            'text': self.phrase
        }

    def as_tuple(self):
        return self.span_start, self.span_end, self._entity_type

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def tokens(self):
        return TokenSpan(self._tokens)

    @property
    def span_start(self):
        return self._tokens[0].span_start

    @property
    def span_end(self):
        return self._tokens[-1].span_end

    @property
    def span(self):
        return self.span_start, self.span_end

    @property
    def phrase(self):
        return self._phrase

    @property
    def start_token_idx(self):
        return self._start_token_idx

    @property
    def end_token_idx(self):
        return self._end_token_idx

    @property
    def custom_id(self):
        return self._custom_id

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self._eid == other._eid
        return False

    def __hash__(self):
        return hash(self._eid)

    def __str__(self):
        return self._phrase


class Relation:
    def __init__(self, rid: int, sentence_id: str, relation_type: str, head_entity: Entity,
                 tail_entity: Entity, reverse: bool = False):
        self._rid = get_id(rid, sentence_id)  # ID within the corresponding dataset
        self._sentence_id = sentence_id
        self._relation_type = relation_type

        self._head_entity = head_entity
        self._tail_entity = tail_entity

        self._reverse = reverse

        self._first_entity = head_entity if not reverse else tail_entity
        self._second_entity = tail_entity if not reverse else head_entity

    def to_json(self):
        return {
            'sentence_id': self.sentence_id,
            'relation_type': self.relation_type,
            'head': self.head_entity.to_json(),
            'tail': self.tail_entity.to_json()
        }

    def as_tuple(self):
        head = self._head_entity
        tail = self._tail_entity
        head_start, head_end = (head.span_start, head.span_end)
        tail_start, tail_end = (tail.span_start, tail.span_end)

        t = ((head_start, head_end, head.entity_type),
             (tail_start, tail_end, tail.entity_type), self._relation_type)
        return t

    def matches_entities(self, entity_1: Entity, entity_2: Entity):
        head_matches_e1 = entity_1 == self._head_entity
        head_matches_e2 = entity_2 == self._head_entity
        tail_matches_e1 = entity_1 == self._tail_entity
        tail_matches_e2 = entity_2 == self._tail_entity
        return (head_matches_e1 and tail_matches_e2) or (tail_matches_e1 and head_matches_e2)

    @property
    def sentence_id(self) -> str:
        return self._sentence_id

    @property
    def relation_type(self) -> str:
        return self._relation_type

    def set_relation_type(self, relation_type: str):
        self._relation_type = relation_type

    @property
    def head_entity(self) -> Entity:
        return self._head_entity

    @property
    def tail_entity(self) -> Entity:
        return self._tail_entity

    @property
    def first_entity(self) -> Entity:
        return self._first_entity

    @property
    def second_entity(self) -> Entity:
        return self._second_entity

    @property
    def reverse(self):
        return self._reverse

    def __eq__(self, other):
        if isinstance(other, Relation):
            return self._rid == other._rid
        return False

    def __hash__(self):
        return hash(self._rid)


class Sentence:
    def __init__(self, sentence_id: str, tokens: List[SingleToken], entities: List[Entity], relations: List[Relation],
                 encoding: List[int]):
        self._sentence_id = sentence_id  # ID within the corresponding dataset

        self._tokens = tokens
        self._entities = entities
        self._relations = relations

        # byte-pair sentence encoding including special tokens ([CLS] and [SEP])
        self._encoding = encoding

    @property
    def sentence_id(self):
        return self._sentence_id

    @property
    def entities(self):
        return self._entities

    @property
    def relations(self):
        return self._relations

    @property
    def tokens(self) -> TokenSpan:
        return TokenSpan(self._tokens)

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    def __eq__(self, other):
        if isinstance(other, Sentence):
            return self._sentence_id == other._sentence_id
        return False

    def __hash__(self):
        return hash(self._sentence_id)
