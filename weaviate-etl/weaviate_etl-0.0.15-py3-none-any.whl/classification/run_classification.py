""" This module classifies objects in Weaviate """

import time
from weaviate_etl.data.imports import import_datapoints
from weaviate_etl.query import get_classification_configuration
from weaviate_etl.utilities import get_weaviate_client
from weaviate_etl.utilities import get_maxbatch
from weaviate_etl.utilities import get_verbose


def reset_classification_configuration(instance, client, classification):
    """ resets the classification configuration at the start of a new classification """

    ccuuid = None
    if client is not None and classification is not None:

        thing = {}
        thing['classname'] = classification['classify_class']
        thing['type'] = classification['classification_type']
        thing['numberOfNeighbors'] = classification['number_of_neighbors']
        thing['batchCount'] = 1
        thing['maxBatchSize'] = get_maxbatch(instance)

        properties = ""
        for prop in classification['classify_properties']:
            if properties != "":
                properties += " "
            properties += prop
        thing['properties'] = properties

        thing['confidenceBuckets'] = 1
        if 'confidence_buckets' in classification:
            length = len(classification['confidence_buckets']) - 1
            if length > 0:
                thing['confidenceBuckets'] = length

        ccuuid = get_classification_configuration(client)
        if ccuuid is None:
            ccuuid = client.data_object.create(thing, "ClassificationConfiguration")
        else:
            client.data_object.update(thing, "ClassificationConfiguration", ccuuid)

    return ccuuid


def _is_finished(status):
    return status["status"] == "completed" or status["status"] == "failed"


def _print_classification_status(client, status):
    print("Started classifying -------------------:", status["status"])
    status = client.classification.get(status["id"])
    while not _is_finished(status):
        time.sleep(1.0)
        status = client.classification.get(status["id"])
    print("Finished classifying ------------------:", status["status"])
    print(status, "\n")


def create_default_where_clause():
    """ creates a default where clause """
    clause = {}

    clause['path'] = ['validated']
    clause['operator'] = "Equal"
    clause['valueBoolean'] = True

    return clause


def execute_classification(instance, client, classification):
    """ This function classifies the data specified in the argument config dict. It uses the
    methodology also specified in the config dict.
    Args:
        - instance (dict): the dict containing the parameters of Weaviate
        - client (weaviate): The Weaviate client in which the data is to be classified
        - config (dict): a dict with the configuration for the classification.
    Returns:
        - nothing
    """
    #pylint: disable=protected-access
    #pylint: disable=too-many-branches

    clause = create_default_where_clause()

    if 'classification_type' in classification:
        ctype = classification['classification_type']
    else:
        ctype = "knn"

    # Next determine which class and which property must be classified
    keys = ['classify_class', 'classify_properties', 'based_on_properties']
    if all (key in classification for key in keys):
        cclass = classification['classify_class']
        cprop = classification['classify_properties']
        cbase = classification['based_on_properties']

        # First determine the type of classification. This can either be "knn" or "contextual"
        if ctype == "knn":

            nn = 5
            if 'number_of_neighbors' in classification:
                nn = classification['number_of_neighbors']

            # Get the base configuration for the classification
            baseconfig = client.classification.schedule()\
                .with_type('knn')\
                .with_class_name(cclass)\
                .with_classify_properties(cprop)\
                .with_based_on_properties(cbase)\
                .with_k(nn)\
                .with_training_set_where_filter(clause)

        elif ctype == "contextual":
            # Get the base configuration for the classification
            baseconfig = client.classification.schedule() \
                .with_type('contextual')\
                .with_class_name(cclass)\
                .with_classify_properties(cprop)\
                .with_based_on_properties(cbase)

        else:
            print("Error: unknow classification type")

    status = baseconfig.do()
    _print_classification_status(client, status)


def import_and_classify(instance, model, classification, datapoints):
    """ import and classifiy data"""

    client = get_weaviate_client(instance)
    maxbatch = get_maxbatch(instance)
    verbose = get_verbose(instance)
    ccuuid = reset_classification_configuration(instance, client, classification)

    iterations = total = count = 0
    importlist = []
    for point in datapoints:
        count += 1
        total += 1
        point['batchNumber'] = iterations + 1
        importlist.append(point)

        if count >= maxbatch:
            iterations += 1
            import_datapoints(client, model, importlist, maxbatch, verbose)

            print("Starting classifying batch", iterations, "with size :", count)
            execute_classification(instance, client, classification)
            count = 0
            importlist = []

    if count > 0:
        iterations += 1
        import_datapoints(client, model, importlist, maxbatch, verbose)

        print("Starting classifying batch", iterations, "with size :", count)
        execute_classification(instance, client, classification)

    # update the number of batches in the classification configuration in Weaviate
    if ccuuid is not None:
        thing = {}
        thing['batchCount'] = iterations
        client.data_object.update(thing, "ClassificationConfiguration", ccuuid)
