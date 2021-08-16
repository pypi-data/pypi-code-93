""" This module parses ex-factory excel file from PVM """

import uuid
import weaviate
from weaviate_etl.utilities import get_reference_class_name_from_field
from weaviate_etl.utilities import check_batch_result
from weaviate_etl.query import get_max_batch_number


def generate_uuid_for_entity(entity: str, name: str) -> str:
    """
    generates a uuid for an entity based on a data model in the argument

    Parameters
    ----------
    entity: dict
        The general name of the entity (e.g. "Flavour")
    name: list
        The name of this specific instantiation of this entity (e.g. "Strawberry")

    Returns
    -------
    str
        the new uuid for this entity
    """

    newuuid = ""

    uuidstring = entity + "_" + name
    newuuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuidstring))

    return newuuid


def generate_uuid_for_datapoint(model: dict, point: dict) -> str:
    """
    generates a uuid for a datapoints based on a data model in the argument

    Parameters
    ----------
    model: dict
        A dict that contains the data model
    datapoints: list
        A list of all the datapoints

    Returns
    -------
    str
        the new uuid for this datapoint
    """

    newuuid = ""
    if model is not None and point is not None:
        for dataclass in model['classes']:

            if dataclass['classname'] == point['classname']:
                string = "point_"

                for col in dataclass['columns']:
                    if col['id']:
                        string = string + point[col['name']]

                newuuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, string))
                break

    return newuuid


def set_cross_references(client: weaviate.client, model: dict, datapoints: list, entities: list, maxbatch: int, verbose: bool):
    #pylint: disable=too-many-nested-blocks
    """
    imports the entities into Weaviate according to the argument model

    Parameters
    ----------
    client: weaviate.client
        The Weaviate client
    model: dict
        A dict that contains the data model
    datapoints: list
        A list of all the datapoints
    entities: list
        A list of all the entities
    maxbatch: int
        Indicates the maximum batch size for importing into Weaviate
    verbose: bool
        Indicates whether debug / info print statements should be on
    """

    # initialize the batch variables
    pointcount = batchcount = 0
    client.batch.shape

    if len(datapoints) > 0:
        for point in datapoints:

            pointcount += 1
            produuid = generate_uuid_for_datapoint(model, point)

            for key in point:
                if key != 'classname' and point[key] is not None and point[key] != '':
                    entity = get_reference_class_name_from_field(key)
                    if entity in entities:

                        entuuid = generate_uuid_for_entity(entity, point[key])
                        client.batch.add_reference(produuid, point['classname'], "of" + entity, entuuid)

                        batchcount += 1
                        if batchcount >= maxbatch:
                            result = client.batch.create_references()
                            check_batch_result(result)
                            client.batch.shape
                            batchcount = 0
                            if verbose:
                                print("Cross reference data points -----------:", pointcount, end="\r")

        if batchcount > 0:
            result = client.batch.create_references()
            check_batch_result(result)
            if verbose:
                print("Cross reference data points -----------:", pointcount)


def import_entities(client: weaviate.client, entities: list, maxbatch: int, verbose: bool):
    """
    imports the entities into Weaviate according to the argument model

    Parameters
    ----------
    client: weaviate.client
        The Weaviate client
    entities: list
        A list of all the entities
    maxbatch: int
        Indicates the maximum batch size for importing into Weaviate
    verbose: bool
        Indicates whether debug / info print statements should be on
    """

    totalcount = batchcount = 0
    #batch = weaviate.ObjectsBatchRequest()
    client.batch.shape

    for entity in entities:
        for name in entities[entity]:
            thing = {}
            thing['name'] = name
            newuuid = generate_uuid_for_entity(entity, name)
            client.batch.add_data_object(thing, entity, newuuid)

            batchcount += 1
            totalcount += 1
            if batchcount >= maxbatch:
                if verbose:
                    print("Entities imported into Weaviate -------:", totalcount, end="\r")
                result = client.batch.create_objects()
                check_batch_result(result)
                client.batch.shape
                batchcount = 0

    if batchcount > 0:
        result = client.batch.create_objects()
        check_batch_result(result)
        if verbose:
            print("Entities imported into Weaviate -------:", totalcount)
    elif verbose:
        print("")


def _check_importlist(importlist):
    count = 0
    for point in importlist:
        if not point['validated']:
            count += 1
    print("At this point", count)


def import_datapoints(client: weaviate.client, model: dict, datapoints: list, maxbatch: int, verbose: bool):
    """
    imports the datapoints into Weaviate according to the argument model

    Parameters
    ----------
    client: weaviate.client
        The Weaviate client
    model: dict
        A dict that contains the data model
    datapoints: list
        A list of all the datapoints
    maxbatch: int
        Indicates the maximum batch size for importing into Weaviate
    verbose: bool
        Indicates whether debug / info print statements should be on
    """

    totalcount = batchcount = 0
    client.batch.shape

    if len(datapoints) > 0:
        classname = datapoints[0]['classname']
        batchNumber = get_max_batch_number(client, classname) + 1
        for point in datapoints:

            thing = {}
            for key in point:
                if key != 'classname':
                    if key == 'batchNumber':
                        thing[key] = batchNumber
                    else:
                        thing[key] = point[key]

            newuuid = generate_uuid_for_datapoint(model, point)

            client.batch.add_data_object(thing, point['classname'], newuuid)
            batchcount += 1
            totalcount += 1

            if batchcount >= maxbatch:
                result = client.batch.create_objects()
                check_batch_result(result)
                client.batch.shape
                batchcount = 0
                batchNumber += 1
                if verbose:
                    print("Data points imported into Weaviate ----:", totalcount, end="\r")

        # if there are left over points in the last batch, import these last data points
        if batchcount > 0:
            result = client.batch.create_objects()
            check_batch_result(result)
            if verbose:
                print("Data points imported into Weaviate ----:", totalcount)


def import_datapoints_nonbatch(client: weaviate.client, model: dict, datapoints: list, maxbatch: int, verbose: bool):
    """ Just for debugging """

    totalcount = 0
    for point in datapoints:
        totalcount += 1

        print("row", point['row'])
        thing = {}
        for key in point:
            if key != 'classname':
                thing[key] = point[key]

        newuuid = generate_uuid_for_datapoint(model, point)
        client.data_object.create(thing, point['classname'], newuuid)
