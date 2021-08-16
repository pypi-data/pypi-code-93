""" This module stores all the data manipulations functions """

import fnmatch
import csv
import openpyxl
from weaviate_etl.utilities import get_weaviate_client
from weaviate_etl.utilities import get_maxbatch
from weaviate_etl.utilities import get_verbose
from weaviate_etl.utilities import DEFAULT_CSV_DELIMITER

from weaviate_etl.exceptions import NoModelLoaded
from weaviate_etl.exceptions import UnableToGetWeaviateClient

from .parser import parse_excel
from .parser import parse_csv
from .imports import import_entities
from .imports import import_datapoints
from .imports import set_cross_references


class Data:
    """ This class stores all the data manipulations functions """

    def __init__(self, model: dict, instance: dict) -> None:
        """
        Initialize a Data class instance.
        """

        if model is not None and 'model' in model and 'type' in model:
            self.instance = instance
            self.client = get_weaviate_client(self.instance)
            self.model = model['model']
            self.type = model['type']


    def parse(self, path: str, delimiter:str=None) -> dict:
        """
        parses the data from file indicated by path and that fits the argument model

        Parameters
        ----------
        path: str
            A string that indicates where the datafile can be found
        delimiterer: str
            A str that indicates the delimiter (in case of a csv file)

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        NoModelLoaded
            If no model was loaded yet

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        if not isinstance(path, str):
            raise TypeError("path is expected to be str but is " + str(type(path)))
        if self.model is None:
            raise NoModelLoaded()

        # initialize the return value
        data = None

        if fnmatch.fnmatch(path, "*.xlsx") or fnmatch.fnmatch(path, "*.xls"):
            workbook = openpyxl.load_workbook(path, data_only=True)
            if workbook is not None:
                sheet = workbook.active
                if sheet is not None:
                    data = parse_excel(self.model, sheet)

        elif fnmatch.fnmatch(path, "*.csv") or fnmatch.fnmatch(path, "*.txt"):
            with open(path) as csvfile:
                if delimiter is None:
                    reader = csv.reader(csvfile, delimiter=DEFAULT_CSV_DELIMITER)
                else:
                    reader = csv.reader(csvfile, delimiter=delimiter)
                data = parse_csv(self.model, reader)

        return data


    def import_entities(self, entities: dict):
        """
        imports the data into Weaviate according to the argument model

        Parameters
        ----------
        entities: dict
            A dict that contains the entities

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        NoModelLoaded
            If no model was loaded yet
        UnableToGetWeaviateClient
            If we can't connect to a Weaviate client

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        if not isinstance(entities, dict):
            raise TypeError("entities is expected to be dict but is " + str(type(entities)))
        if self.model is None:
            raise NoModelLoaded()

        maxbatch = get_maxbatch(self.instance)
        verbose = get_verbose(self.instance)

        if self.client is None:
            self.client = get_weaviate_client(self.instance)
            if self.client is None:
                raise UnableToGetWeaviateClient()

        import_entities(self.client, entities, maxbatch, verbose)


    def import_datapoints(self, datapoints: list):
        """
        imports the data into Weaviate according to the argument model

        Parameters
        ----------
        datapoints: list
            A list that contains the datapoints

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        NoModelLoaded
            If no model was loaded yet

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        if not isinstance(datapoints, list):
            raise TypeError("datapoints is expected to be list but is " + str(type(datapoints)))
        if self.model is None:
            raise NoModelLoaded()

        maxbatch = get_maxbatch(self.instance)
        verbose = get_verbose(self.instance)

        import_datapoints(self.client, self.model, datapoints, maxbatch, verbose)


    def set_cross_references(self, datapoints: list, entities: dict):
        """
        Sets the cross references between the datapoints and the entities

        Parameters
        ----------
        datapoints: list
            A list that contains the datapoints
        entities: dict
            A dict that contains the entities

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        NoModelLoaded
            If no model was loaded yet
        """

        if not isinstance(datapoints, list):
            raise TypeError("datapoints is expected to be list but is " + str(type(datapoints)))
        if not isinstance(entities, dict):
            raise TypeError("entities is expected to be dict but is " + str(type(entities)))
        if self.model is None:
            raise NoModelLoaded()

        maxbatch = get_maxbatch(self.instance)
        verbose = get_verbose(self.instance)
        set_cross_references(self.client, self.model, datapoints, entities, maxbatch, verbose)


    def set_classification_flags(self, datapoints: list, validated: bool=True, preClassified: bool=False):
        #pylint: disable=no-self-use
        """
        sets the validated flag for all datapoints to the argument flag

        Parameters
        ----------
        datapoints: list
            A list of all datapoints
        validated: bool
            A boolean that indicates how the flag should be set
        preClassified: bool
            A boolean that indicates how the flag should be set

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        if not isinstance(datapoints, list):
            raise TypeError("datapoints is expected to be list but is " + str(type(datapoints)))

        for datapoint in datapoints:
            datapoint['validated'] = validated
            datapoint['preClassified'] = preClassified
