#!/usr/bin/env python
# coding: utf-8

import json

import pandas as pd

import random

from tqdm import tqdm
from pathlib import Path
from itertools import combinations
from typing import List, Dict, Tuple, Set, Optional

from allennlp_datalawyer.data.dataset_readers.entity_marker import EntityMarker

entity_marker = EntityMarker()

random_seed: int = 13370
random.seed(random_seed)

valid_relations_mappings = {
    'PESSOA': ['FUNCAO'],
    'ORGANIZACAO': ['FUNCAO'],
    'PEDIDO': ['ATRIBUICAO', 'DECISAO', 'VALOR_PEDIDO'],
    'REFLEXO': ['ATRIBUICAO', 'DECISAO', 'VALOR_PEDIDO']
}


def is_relation_valid(entity_1: Dict, entity_2: Dict) -> bool:
    if entity_1['type'] in valid_relations_mappings.keys():
        return entity_2['type'] in valid_relations_mappings[entity_1['type']]
    return False


def create_cp_item(tokens: List[str], head_entity: Dict, tail_entity: Dict, relation_type: str) -> Dict:
    head_position = [head_entity['start'], head_entity['end']]
    tail_position = [tail_entity['start'], tail_entity['end']]
    return {
        'token': entity_marker.tokenize_raw(raw_text=tokens, head_position=head_position, tail_position=tail_position),
        'h': {
            'name': ' '.join(tokens[head_entity['start']:head_entity['end']]),
            'pos': head_position,
            'type': head_entity['type'],
            'idx': head_entity['idx'],
            'id': head_entity['id']
        },
        't': {
            'name': ' '.join(tokens[tail_entity['start']:tail_entity['end']]),
            'pos': tail_position,
            'type': tail_entity['type'],
            'idx': tail_entity['idx'],
            'id': tail_entity['id']
        },
        'relation': relation_type
    }


def convert_to_recorn_item(item: Dict, relation: Dict) -> Dict:
    head_entity = item['entities'][relation['head']]
    tail_entity = item['entities'][relation['tail']]
    relation_type = relation['type'] if type in relation else None
    return create_cp_item(item['tokens'], head_entity, tail_entity, relation_type)


def convert_to_recorn_items(item: Dict) -> List[Dict]:
    items = []
    for relation in item['relations']:
        items.append(convert_to_recorn_item(item, relation))
    return items


def parse_entity_to_cpdata(data_item: Dict, entity: Dict) -> Dict:
    tokens_positions = list(range(entity['start'], entity['end']))
    first_position = tokens_positions[0]
    last_position = tokens_positions[-1]
    assert data_item['tokens'][first_position:last_position + 1] == entity['text']
    return {
        'name': ' '.join(entity['text']),
        'pos': [tokens_positions]
    }


def matches_entities(entity_1: Dict, entity_2: Dict, head_entity: Dict, tail_entity: Dict):
    head_matches_e1 = entity_1['id'] == head_entity['id']
    head_matches_e2 = entity_2['id'] == head_entity['id']
    tail_matches_e1 = entity_1['id'] == tail_entity['id']
    tail_matches_e2 = entity_2['id'] == tail_entity['id']
    return (head_matches_e1 and tail_matches_e2) or (tail_matches_e1 and head_matches_e2)


def get_relation_for_entities_pair(entity_1: Dict, entity_2: Dict,
                                   relations: List[Dict], entities: List[Dict]) -> Optional[Dict]:
    for relation in relations:
        if matches_entities(entity_1, entity_2, entities[relation['head']], entities[relation['tail']]):
            return relation
    return None


def get_head_tail_entities(entity_1: Dict, entity_2: Dict) -> Tuple[Dict, Dict]:
    if entity_1['type'] in valid_relations_mappings.keys():
        return entity_1, entity_2
    elif entity_2['type'] in valid_relations_mappings.keys():
        return entity_2, entity_1
    else:
        return entity_1, entity_2


def create_negative_samples(item: Dict, max_negative_valid_samples: int, max_negative_invalid_samples: int) \
        -> List[Dict]:
    items = []
    tokens = item['tokens']
    entities = item['entities']
    relations = item['relations']

    negative_tuples = [(entity_1, entity_2) for entity_1, entity_2 in combinations(entities, 2)
                       if get_relation_for_entities_pair(entity_1, entity_2, relations, entities) is None]

    negative_valid_tuples = [negative_tuple for negative_tuple in negative_tuples if
                             is_relation_valid(negative_tuple[0], negative_tuple[1])]

    samples_valid_size = min(len(negative_valid_tuples), max_negative_valid_samples)

    training_negative_valid_tuples = random.sample(negative_valid_tuples, samples_valid_size)

    negative_invalid_tuples = [negative_tuple for negative_tuple in negative_tuples if
                               not is_relation_valid(negative_tuple[0], negative_tuple[1])]

    samples_invalid_size = min(len(negative_invalid_tuples), max_negative_invalid_samples)

    training_negative_invalid_tuples = random.sample(negative_invalid_tuples, samples_invalid_size)

    for idx, (entity_1, entity_2) in enumerate(
            training_negative_valid_tuples + training_negative_invalid_tuples
    ):
        head_entity, tail_entity = get_head_tail_entities(entity_1, entity_2)
        items.append(create_cp_item(tokens, head_entity, tail_entity, 'NO_RELATION'))

    return items


def load_data_items(data_path: Path, relation_types: Set[str],
                    max_negative_valid_samples: int,
                    max_negative_invalid_samples: int) -> List[Dict]:
    data_items = json.load(data_path.open(mode='r', encoding='utf8'))
    recorn_items = []
    for item in tqdm(data_items, 'Loading items from %s' % str(data_path)):
        if len(item['relations']) > 0:
            for cp_item in convert_to_recorn_items(item):
                relation_types.add(cp_item['relation'])
                recorn_items.append(cp_item)
        for cp_item in create_negative_samples(item,
                                               max_negative_valid_samples=max_negative_valid_samples,
                                               max_negative_invalid_samples=max_negative_invalid_samples):
            relation_types.add(cp_item['relation'])
            recorn_items.append(cp_item)
    return recorn_items


def save_cp_training_files(max_negative_valid_samples: int = 10,
                           max_negative_invalid_samples: int = 10,
                           source_version: str = "0.16"):
    target_version: str = "0.16_{}_{}".format(max_negative_valid_samples, max_negative_invalid_samples)
    datalawyer_source_path = Path(
        '/media/discoD/repositorios/entidades/dataset/datalawyer/relacao/versao_{}'.format(source_version))
    datalawyer_target_path = Path(
        '/media/discoD/repositorios/entidades/dataset/datalawyer/relacao/versao_{}'.format(target_version))
    datalawyer_target_path.mkdir(parents=True, exist_ok=True)
    datalawyer_recorn_base_path = Path(
        '/media/discoD/repositorios/RE-Context-or-Names/finetune/supervisedRE/data/datalawyer'
    )
    datalawyer_recorn_base_path.mkdir(exist_ok=True)

    relation_types = set()
    all_data_items = []
    for set_type in ['train', 'test', 'dev']:
        datalawyer_data_path = datalawyer_source_path / 'datalawyer_spert_{}_all.json'.format(set_type)
        recorn_data_path = datalawyer_recorn_base_path / '{}_cp.txt'.format(set_type)
        datalawyer_cp_data_path = datalawyer_target_path / 'datalawyer_cp_{}_all.json'.format(set_type)
        data_items = load_data_items(datalawyer_data_path, relation_types,
                                     max_negative_valid_samples=max_negative_valid_samples,
                                     max_negative_invalid_samples=max_negative_invalid_samples)
        all_data_items.extend(data_items)
        pd.DataFrame(data_items).to_json(recorn_data_path, orient='records', lines=True)
        pd.DataFrame(data_items).to_json(datalawyer_cp_data_path, orient='records', lines=True)
        print('Done saving %d items for %s set' % (len(data_items), set_type))
    datalawyer_cp_full_data_path = datalawyer_target_path / 'datalawyer_cp_full_all.json'
    pd.DataFrame(all_data_items).to_json(datalawyer_cp_full_data_path, orient='records', lines=True)
    print('Done saving %d items for full set' % len(all_data_items))

    rel2id_path = datalawyer_recorn_base_path / 'rel2id.json'
    rel_types_list = ['NO_RELATION'] + [relation_type for relation_type in relation_types if
                                        relation_type != 'NO_RELATION']
    json.dump({relation_type: idx for idx, relation_type in enumerate(rel_types_list)},
              rel2id_path.open(mode='w', encoding='utf8'))

# save_cp_training_files(max_negative_valid_samples=50, max_negative_invalid_samples=0, source_version="0.16")
