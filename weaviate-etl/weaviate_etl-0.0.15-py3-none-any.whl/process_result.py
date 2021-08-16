""" This module processes the classification result """

import math

from .data.imports import generate_uuid_for_datapoint
from .utilities import get_field_name_from_reference_property
from .query import count_number_of_unvalidated_datapoints
from .query import create_get_query_batch_number
from .query import get_max_batch_number
from .classification.confidence import calculate_confidence_score_for_point
from .classification.confidence import get_confidence_buckets
from .classification.confidence import get_bucket_id


NON_PROPERTIES = ['classname', 'row', 'validated', 'preClassified', 'batchNumber']


############################################################################################################
##
## calculate_classification_score is only used in a validation run. It calculates which percentage of the
## classified items was correctly classified.
##
############################################################################################################


def _initialize_result_score(classification, properties):
    score = {}
    score['total'] = 0
    for prop in properties:
        score[prop] = {}
        score[prop]['count'] = 0
        score[prop]['correct'] = 0
        score[prop]['incorrect'] = 0
        score[prop]['buckets'] = get_confidence_buckets(classification)

    return score


def _index_datapoints_by_uuid(model, datapoints):
    index = {}
    for point in datapoints:
        temp = generate_uuid_for_datapoint(model, point)
        index[temp] = point
    return index


def _score_query_result(client, classification, index, result, classname, properties, score):
    """ score the result of the classification by Weaviate """

    if result is None or 'data' not in result:
        print("No classified datapoints found --------:")
        return

    points = result['data']['Get'][classname]
    for point in points:

        score['total'] += 1
        puuid = point['_additional']['id']
        datapoint = index[puuid]

        confscore = calculate_confidence_score_for_point(client, classification, puuid)
        for prop in properties:

            bid = get_bucket_id(score[prop]['buckets'], confscore[prop])

            field = get_field_name_from_reference_property(prop)
            if prop in point and point[prop] is not None:

                score[prop]['count'] += 1
                score[prop]['buckets'][bid]['count'] += 1
                if point[prop][0]['name'] == datapoint[field]:
                    score[prop]['correct'] += 1
                    score[prop]['buckets'][bid]['correct'] += 1
                else:
                    score[prop]['incorrect'] += 1
                    score[prop]['buckets'][bid]['incorrect'] += 1
            else:
                print(point['row'], ";Warning: property", prop, "not found.")


def calculate_validation_score(client, model, classification, datapoints, maxbatch):
    """ process result """

    properties = []
    if 'classify_properties' in classification:
        for prop in classification['classify_properties']:
            properties.append(prop)

    count = count_number_of_unvalidated_datapoints(client, classification['classify_class'])
    score = _initialize_result_score(classification, properties)
    index = _index_datapoints_by_uuid(model, datapoints)

    classname = classification['classify_class']
    number = get_max_batch_number(client, classname)
    for batch in range(1, number + 1):

        query = create_get_query_batch_number(client, classification, batch)
        result = client.query.raw(query)
        _score_query_result(client, classification, index, result, classification['classify_class'], properties, score)
        print("Total number of datapoints found ------:", score['total'])

    if score['total'] > 0:
        for prop in properties:
            print(round((score[prop]['correct']/score['total'])*100),"%", "-", prop, "over buckets:")
            for index in score[prop]['buckets']:
                buc = score[prop]['buckets'][index]
                print('\t', round((buc['correct']/buc['count'])*100), '% =', buc['correct'], '/', buc['count'], end='\t')
                print("[", buc['lower'], ",", buc['upper'], "]")

    else:
        print("Warning: zero classified data points --:")
