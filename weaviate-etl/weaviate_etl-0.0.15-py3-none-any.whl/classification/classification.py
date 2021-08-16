""" This module stores all the classification functions """

import weaviate
import random

from weaviate_etl.utilities import get_weaviate_client
from weaviate_etl.utilities import get_maxbatch
from weaviate_etl.utilities import get_verbose
from weaviate_etl.utilities import get_validation_percentage
from weaviate_etl.utilities import get_random_selection
from weaviate_etl.utilities import calculate_size_training_set

from weaviate_etl.exceptions import NoModelLoaded
from weaviate_etl.exceptions import UnableToGetWeaviateClient
from weaviate_etl.exceptions import NoClassificationSet
from weaviate_etl.exceptions import NoInstanceLoaded

from weaviate_etl.query import get_classified_datapoints

from weaviate_etl.process_result import calculate_validation_score

from .run_classification import execute_classification
from .run_classification import import_and_classify
from .run_classification import reset_classification_configuration


class Classification:
    """ This class stores all the classification functions """

    def __init__(self, model: dict, instance: dict, classification: dict=None) -> None:
        #pylint: disable=duplicate-code
        """
        Initialize a Data class instance.
        """

        if model is not None and 'model' in model and 'type' in model:
            self.model = model['model']
            self.type = model['type']
            self.instance = instance
            self.client = get_weaviate_client(self.instance)
            self.buckets = None
            self.classification = classification


    def set_instance(self, client: weaviate.client, instance: dict) -> None:
        """
        Sets the Weaviate instance for this model

        Parameters
        ----------
        client: weaviate.client
            The weaviate client
        instance: dict
            A dict that contains all the weaviate parameters

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        UnableToGetWeaviateClient
            if we are unable to get the Weaviate client

        Returns
        -------
        weaviate:client
            the weaviate client indicated to by the argument dict instance
        """

        if not isinstance(instance, dict):
            raise TypeError("instance is expected to be dict but is " + str(type(instance)))

        self.instance = instance
        if client is not None:
            self.client = client
        else:
            self.client = get_weaviate_client(instance)


    def set(self, classification):
        """
        Sets the classification parameters

        Parameters
        ----------
        classification: dict
            A dict that contains all the classification parameters

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        """

        if not isinstance(classification, dict):
            raise TypeError("classification is expected to be dict but is " + str(type(classification)))

        self.classification = classification


    def get(self):
        """
        returns the classification parameters

        Raises
        ------
        NoClassificationSet
            If no classification has been set
        """

        if self.classification is None:
            raise NoClassificationSet()

        return self.classification


    def get_classified_datapoints(self, fields: list=None) -> list:
        """
        Gets all the classified points from Weaviate

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        NoModelLoaded
            If no model was loaded yet
        UnableToGetWeaviateClient
            If no client is in the model
        NoClassificationSet
            If no classification is in the model

        Returns
        ------
        list
            The list of all classified datapoints
        """

        if self.model is None:
            raise NoModelLoaded()
        if self.client is None:
            raise UnableToGetWeaviateClient()
        if self.classification is None:
            raise NoClassificationSet()

        maxbatch = get_maxbatch(self.instance)

        return get_classified_datapoints(self.client, self.classification, maxbatch, fields)


    def select_training_data(self, datapoints: list):
        """
        Splits the data in the argument into training data and non training data
        """

        percentage = get_validation_percentage(self.classification)
        ransel = get_random_selection(self.classification)
        maxbatch = get_maxbatch(self.instance)

        if datapoints is not None:
            size = calculate_size_training_set(datapoints, maxbatch, percentage, ransel)

            count = total = 0
            for point in datapoints:

                count += 1
                total += 1
                if size['random_selection']:
                    # pick a random number and see if this is control group or training group
                    if random.uniform(0, 100) < size['validation_percentage']:
                        training = False
                    else:
                        training = True
                else:
                    # if count equals the modulus, this is control data
                    if count == size['modulus']:
                        training = False
                        count = 0
                    else:
                        training = True

                if training:
                    point['validated'] = True
                    size['training_size'] += 1
                else:
                    point['validated'] = False
                    size['validation_size'] += 1

            if get_verbose(self.instance):
                print("Total number of datapoints ------------:", size['total'])
                print("Validation percentage -----------------:", size['validation_percentage'])
                print("Random selection of validation sample -:", size['random_selection'])
                print("Number of datapoints in training ------:", size['training_size'])
                print("Number of datapoints in validation ----:", size['validation_size'])


    def calculate_validation_score(self, datapoints: list):
        """
        Calculates the result of a validation run - only used in simple testing

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        NoModelLoaded
            If no model was loaded yet
        UnableToGetWeaviateClient
            If no client is in the model
        NoClassificationSet
            If no classification is in the model

        Returns
        ------
        list
            The list of all classified datapoints
        """

        if not isinstance(datapoints, list):
            raise TypeError("datapoints is expected to be list but is " + str(type(datapoints)))
        if self.model is None:
            raise NoModelLoaded()
        if self.client is None:
            raise UnableToGetWeaviateClient()
        if self.classification is None:
            raise NoClassificationSet()

        maxbatch = get_maxbatch(self.instance)

        properties = []
        if 'classify_properties' in self.classification:
            for prop in self.classification['classify_properties']:
                properties.append(prop)

        calculate_validation_score(self.client, self.model, self.classification, datapoints, maxbatch)


    def get_buckets(self) -> dict:
        """
        returns the confidence buckets for the classification

        Raises
        ------
        NoClassificationSet
            If no classification is in the model

        Returns
        ------
        dict
            The dict with the confidence buckets
        """

        if self.classification is None:
            raise NoClassificationSet()

        if self.buckets is not None:
            return self.buckets

        self.buckets = {}
        if 'confidence_buckets' in self.classification:
            intervals = self.classification['confidence_buckets']
        else:
            intervals = [0.0, 1.0]

        length = len(intervals)
        for count in range(length-1):
            self.buckets[count] = {}
            self.buckets[count]['lower'] = intervals[count]
            self.buckets[count]['upper'] = intervals[count+1]
            self.buckets[count]['correct'] = 0
            self.buckets[count]['incorrect'] = 0
            self.buckets[count]['count'] = 0

        return self.buckets


    def get_bucket_id(self, score: float) -> int:
        """
        returns the confidence bucket id for a given score

        Returns
        ------
        int
            The id of the correct confidence bucket
        """

        if self.buckets is None:
            self.get_buckets()

        result = 0
        if score > 0.0:
            for bid in self.buckets:
                if self.buckets[bid]['lower'] < score <= self.buckets[bid]['upper']:
                    result = bid

        return result


    def classify(self, datapoints: list=None):
        """
        imports the argument data points and classifies them. This function is needed because
        the number of data points may exceed the max batch of Weaviate

        Parameters
        ----------
        datapoints: list
            A list that contains the datapoints to be imported and classified
        entities: list
            A list that contains the entities

        Raises
        ------
        NoInstanceLoaded
            If no instance of Weaviate is set
        NoModelLoaded
            If no model is loaded yet
        NoClassificationSet
            If no classification is set
        """

        if self.instance is None:
            raise NoInstanceLoaded()
        if self.model is None:
            raise NoModelLoaded()
        if self.classification is None:
            raise NoClassificationSet()

        if datapoints is None:
            reset_classification_configuration(self.instance, self.client, self.classification)
            execute_classification(self.instance, self.client, self.classification)
        else:
            import_and_classify(self.instance, self.model, self.classification, datapoints)
