""" This module contains general query functions """

import math
from .utilities import get_field_name_from_reference_property
from .utilities import get_class_name_from_reference_property


def get_max_batch_number(client, classname: str) -> int:
    """
    Returns the maximum batch number

    Parameters
    ----------
    instance: str
        A string that contains the relevant classname

    Returns
    -------
    int
        the maximum batch number
    """

    template = """ { Aggregate { %s { batchNumber { maximum } } } }"""
    maxnumber = 0
    if classname is not None:
        query = template % (classname)
        result = client.query.raw(query)
        if result is not None and 'errors' not in result and len(result['data']['Aggregate'][classname]) > 0:
            maxnumber = int(result['data']['Aggregate'][classname][0]['batchNumber']['maximum'])
    return maxnumber


def get_classification_configuration(client):
    """ get the classification configuration from Weaviate """

    ccuuid = None
    query = """ { Get { ClassificationConfiguration { _additional { id } } } } """

    if client is not None:
        result = client.query.raw(query)

        if result is not None and 'errors' not in result:
            if len(result['data']['Get']["ClassificationConfiguration"]) > 0:
                ccuuid = result['data']['Get']["ClassificationConfiguration"][0]["_additional"]["id"]

    return ccuuid


def count_number_of_datapoints(client, classname):
    """ Count the number of datapoints in Weaviate """

    count = 0
    template = """ { Aggregate { %s { meta { count } } } }"""
    query = template % (classname)
    result = client.query.raw(query)

    if result is not None:
        if errors not in result:
            count = result['data']['Aggregate'][classname][0]["meta"]["count"]
        else:
            print(result['errors'])
    return count


def count_number_of_unvalidated_datapoints(client, classname):
    """ Count the number of datapoints in Weaviate """

    count = 0
    template = """ { Aggregate { %s (where: { operator:Equal path:["validated"] valueBoolean:false }) { meta { count } } } }"""
    query = template % (classname)
    result = client.query.raw(query)

    if result is not None:
        if 'errors' not in result:
            count = result['data']['Aggregate'][classname][0]["meta"]["count"]
        else:
            print(result['errors'])
    return count


def count_number_of_datapoints(client, classname):
    """ Count the number of datapoints in Weaviate """

    count = 0
    template = """ { Aggregate { %s { meta { count } } } } """
    query = template % (classname)
    result = client.query.raw(query)

    if result is not None:
        if 'errors' not in result:
            count = result['data']['Aggregate'][classname][0]["meta"]["count"]
        else:
            print(result['errors'])
    return count


def _create_base_whereclause_row_numbers(minrow, maxrow):

    whereclause = {}

    # the basic clause includes a number of operands that all need to be True.
    whereclause = {}
    whereclause['operator'] = "And"
    whereclause['operands'] = []

    # add the operand that selects only those data points that have not yet been verified
    operand = {}
    operand["path"] = ["validated"]
    operand["operator"] = "Equal"
    operand["valueBoolean"] = False
    whereclause['operands'].append(operand)

    # add the operand that selects data points from a row higher than (or equal to) minrow
    operand = {}
    operand["path"] = ["row"]
    operand["operator"] = "GreaterThanEqual"
    operand["valueInt"] = minrow
    whereclause['operands'].append(operand)

    # add the operand that selects data points from a row lower than maxrow
    operand = {}
    operand["path"] = ["row"]
    operand["operator"] = "LessThan"
    operand["valueInt"] = maxrow
    whereclause['operands'].append(operand)

    return whereclause


def create_get_query_row_numbers(client, config, dataconfig, minrow, maxrow):
    """ create get query """

    if client is not None and config is not None and dataconfig is not None:

        thingname = dataconfig['classname']

        # Get the names of the properties that we are classifying
        properties = ['row', 'validated', 'batchNumber']
        if 'classification' in config and 'classify_properties' in config['classification']:
            for prop in config['classification']['classify_properties']:
                field = get_field_name_from_reference_property(prop)
                properties.append(field)

                classname = get_class_name_from_reference_property(prop)
                properties.append("""%s { ...on %s { name } }""" % (prop, classname))

        whereclause = _create_base_whereclause_row_numbers(minrow, maxrow)

        query = client.query\
            .get(thingname, properties)\
            .with_limit(10000)\
            .with_where(whereclause)\
            .build()

    return query


def _create_base_whereclause_batch_number(batch):

    # initialize the return value
    whereclause = {}

    # the basic clause includes a number of operands that all need to be True.
    whereclause['operator'] = "And"
    whereclause['operands'] = []

    # add the operand that selects only those data points that have not yet been verified
    operand = {}
    operand["path"] = ["validated"]
    operand["operator"] = "Equal"
    operand["valueBoolean"] = False
    whereclause['operands'].append(operand)

    # add the operand that selects the right batch number
    operand = {}
    operand["path"] = ["batchNumber"]
    operand["operator"] = "Equal"
    operand["valueInt"] = batch
    whereclause['operands'].append(operand)

    return whereclause


def create_get_query_batch_number(client, classification, batch, fields=None):
    """ create get query """

    if client is not None and classification is not None:

        thingname = classification['classify_class']

        properties = ['_additional { id }', 'row', 'validated', 'batchNumber', 'preClassified']
        if fields is not None:
            for field in fields:
                properties.append(field)

        for prop in classification['classify_properties']:
            field = get_field_name_from_reference_property(prop)
            properties.append(field)

            classname = get_class_name_from_reference_property(prop)
            properties.append("""%s { ...on %s { name } }""" % (prop, classname))

        whereclause = _create_base_whereclause_batch_number(batch)

        query = client.query\
            .get(thingname, properties)\
            .with_limit(10000)\
            .with_where(whereclause)\
            .build()

    return query


def get_classified_datapoints(client, classification, maxbatch, fields=None):
    """ pulls all points that have been classified from Weaviate """

    datapoints = []
    if client is not None:

        classname = classification['classify_class']
        number = get_max_batch_number(client, classname)
        for batch in range(1, number + 1):

            query = create_get_query_batch_number(client, classification, batch, fields)
            result = client.query.raw(query)
            if result is not None and 'data' in result:
                datapoints += result['data']['Get'][classname]

    return datapoints
