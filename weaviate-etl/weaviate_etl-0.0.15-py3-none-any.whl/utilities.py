""" This module contains general utulity functions """

import os
import math
import weaviate
from .exceptions import UnableToGetWeaviateClient


DEFAULT_WEAVIATE = 'http://localhost:8080'
DEFAULT_MAX_BATCH = 1000
DEFAULT_VERBOSE = False
DEFAULT_CSV_DELIMITER = ','
DEFAULT_MODULE = "text2vec-contextionary"
DEFAULT_VALIDATION_PERCENTAGE = 20
DEFAULT_RANDOM_SELECTION = True


def get_maxbatch(instance: dict=None) -> int:
    """
    Returns the maximum batch size

    Parameters
    ----------
    instance: dict
        A dict that contains all the weaviate parameters

    Returns
    -------
    int
        the maximum batch size
    """

    maxbatch = DEFAULT_MAX_BATCH
    if instance is not None and 'max_batch_size' in instance:
        maxbatch = instance['max_batch_size']
    return maxbatch


def get_verbose(instance: dict) -> bool:
    """
    Returns whether verbose is on or off

    Parameters
    ----------
    instance: dict
        A dict that contains all the weaviate parameters

    Returns
    -------
    bool
        indicates whether verbose is on (True) or off (False)
    """

    verbose = DEFAULT_VERBOSE
    if instance is not None and 'verbose' in instance:
        verbose = instance['verbose']
    return verbose


def get_validation_percentage(classification: dict=None) -> int:
    """
    Returns the validation percentage

    Parameters
    ----------
    classification: dict
        A dict that contains all the classification parameters

    Returns
    -------
    int
        the validation percentage
    """

    percentage = DEFAULT_VALIDATION_PERCENTAGE
    if classification is not None and 'validation_percentage' in classification:
        percentage = classification['validation_percentage']

    return percentage


def get_random_selection(classification: dict=None) -> int:
    """
    Returns the random selection parameter

    Parameters
    ----------
    classification: dict
        A dict that contains all the classification parameters

    Returns
    -------
    int
        the random selection parameter (true or false)
    """

    random = DEFAULT_RANDOM_SELECTION
    if classification is not None and 'random_selection' in classification:
        random = classification['random_selection']

    return random


def get_weaviate_client(instance: dict) -> weaviate.client:
    """
    Returns the Weaviate client indicated by the argument instance

    Parameters
    ----------
    instance: dict
        A dict that contains all the weaviate parameters

    Raises
    ------
    UnableToGetWeaviateClient
        if we are unable to get the Weaviate client

    Returns
    -------
    weaviate:client
        the weaviate client indicated to by the argument dict instance
    """

    client = None

    # determine the path to the weaviate
    weaviatepath = DEFAULT_WEAVIATE
    if instance is not None and 'url' in instance:
        weaviatepath = instance['url']

    # check if authorization is needed: if username and password are in instance
    if 'username' in instance and 'password' in instance:

        username = os.getenv(instance['username'])
        password = os.getenv(instance['password'])

        if username is not None and password is not None:

            # get the authorization and get the client with the authorization
            auth = weaviate.AuthClientPassword(username, password)
            client = weaviate.Client(weaviatepath, auth_client_secret=auth)

        # if not authorization is needed or possible, return client without authorization
        else:
            client = weaviate.Client(weaviatepath)
    else:
        client = weaviate.Client(weaviatepath)

    if client is None:
        raise UnableToGetWeaviateClient()

    return client


def get_class_name_from_reference_property(prop):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence score field name = flavourConfidenceScore
            confidence bucket field name = flavourConfidenceBucket
    """
    # turns "ofFlavour" into "Flavour" - note the upper case 'F' at the start
    return prop[2:]


def get_field_name_from_reference_property(prop):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence score field name = flavourConfidenceScore
            confidence bucket field name = flavourConfidenceBucket
    """
    # turns "ofFlavour" into "flavour" - note the lower case 'f' at the start
    return prop[2].lower() + prop[3:]


def get_reference_property_name_from_field(field):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence score field name = flavourConfidenceScore
            confidence bucket field name = flavourConfidenceBucket
    """
    # turns "flavour" into "ofFlavour"
    return 'of' + field[:1].upper() + field[1:]


def get_reference_class_name_from_field(field):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence score field name = flavourConfidenceScore
            confidence bucket field name = flavourConfidenceBucket
    """
    # turns "flavour" into "Flavour" - note the upper case 'F' at the start
    return field[:1].upper() + field[1:]


def get_class_name_from_key(key):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence field name = ofFlavourConfidence
    """
    # turns "flavour" into "Flavour" - note the upper case 'F' at the start
    return key[:1].upper() + key[1:]


def get_conf_score_field_name_from_ref_prop(prop):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence score field name = flavourConfidenceScore
            confidence bucket field name = flavourConfidenceBucket
    """
    # turns "ofFlavour" into "flavourConfidenceScore"
    return prop[2].lower() + prop[3:] + "ConfidenceScore"


def get_conf_bucket_field_name_from_ref_prop(prop):
    """ This function generates the right name of the property / class based on the input
        example:
            field name = flavour
            reference property name = ofFlavour
            entity class name = Flavour
            confidence score field name = flavourConfidenceScore
            confidence bucket field name = flavourConfidenceBucket
    """
    # turns "ofFlavour" into "flavourConfidenceScore"
    return prop[2].lower() + prop[3:] + "ConfidenceBucket"


def calculate_size_training_set(datapoints: list, maxbatch: int, percentage: int, random: bool) -> dict:
    """
    sets the validated flag for all datapoints to the argument flag

    Parameters
    ----------
    datapoints: list
        A list of all datapoints
    maxbatch: int
        The maximum size for batching
    percentages: int
        the percentage of the data that will be used for validation purposes (rest will be training)
    random: bool
        do we select the training data at random (True) or not (False)

    Returns
    ------
    dict
        The dict containing all size variables
    """

    size = {}
    size['validation_percentage'] = percentage
    size['max_batch_size'] = maxbatch
    size['random_selection'] = random
    size['total'] = len(datapoints)
    size['training_size'] = 0
    size['validation_size'] = 0
    size['modulus'] = 10


    # Check if the validation size will not exceed the max batch size
    if round(size['total'] * (size['validation_percentage'] / 100)) > size['max_batch_size']:
        size['validation_percentage'] = math.floor((size['max_batch_size'] / size['total']) * 100) - 1
        if size['validation_percentage'] == 0:
            size['validation_percentage'] = 1
        print("Warning: validation size exceeds limit, resetting to:", size['validation_percentage'])

    size['modulus'] = round(size['total'] / (size['total'] * (size['validation_percentage'] / 100)))

    return size


def check_batch_result(results: dict):
    """
    checks the outcome of a batch request to Weaviate

    Parameters
    ----------
    results: dict
        A dict that contains the outcome of a batch request
    """

    if results is not None:
        for result in results:
            if 'result' in result and 'errors' in result['result'] and 'error' in result['result']['errors']:
                for message in result['result']['errors']['error']:
                    print(message['message'])


def get_cellid_of_field(model, field):
    """ get the id if a cell in excel """

    # first get the number of the column for this field
    for dataclass in model['classes']:
        for col in dataclass['columns']:
            if col['name'] == field:
                number = col['number']

    # then translate the number of the column to a excel string
    string = ""
    while number > 0:
        number, remainder = divmod(number - 1, 26)
        string = chr(65 + remainder) + string
