""" This module calculates the confidence score from classification by Weaviate """


def _extract_classification_scores(classification, point):

    score = {}
    preclass = False
    if 'preClassified' in point['properties'] and point['properties']['preClassified']:
        preclass = True

    for prop in classification['classify_properties']:
        if 'properties' in point and prop in point['properties'] and len(point['properties'][prop]) > 0:
            if preclass:
                score[prop] = 1.0
            elif 'classification' in point['properties'][prop][0]:
                outcome = point['properties'][prop][0]['classification']
                score[prop] = outcome['winningCount'] / outcome['overallCount']

    return score


def get_bucket_id(buckets, score):
    """ returns the right bucket identifier for the argument score """

    # initialize the return value
    result = 0
    if score > 0.0:
        for bid in buckets:
            if buckets[bid]['lower'] < score <= buckets[bid]['upper']:
                result = bid

    return result


def get_confidence_buckets(classification):
    """ reads the confidence buckets from the file indicated by argument classification """

    buckets = {}

    # get the confidence score intervals from the classification file (if present). Default = [0.0, 1.0]
    if classification is not None and 'confidence_buckets' in classification:
        intervals = classification['confidence_buckets']
    else:
        intervals = [0.0, 1.0]

    length = len(intervals)
    for count in range(length-1):
        buckets[count] = {}
        buckets[count]['lower'] = intervals[count]
        buckets[count]['upper'] = intervals[count+1]
        buckets[count]['correct'] = 0
        buckets[count]['incorrect'] = 0
        buckets[count]['count'] = 0

    return buckets


def calculate_confidence_score_for_point(client, classification, puuid):
    """ calculate the confidence score for a datapoint """
    # pylint: disable=protected-access

    score = None
    if client is not None and classification is not None:
        path = "/objects/" + puuid + "?include=classification"
        result = client._connection.run_rest(path, 0)
        score = _extract_classification_scores(classification, result.json())

    return score
