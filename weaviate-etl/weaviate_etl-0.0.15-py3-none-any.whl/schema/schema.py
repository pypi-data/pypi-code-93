""" This module creates a Weaviate schema from a data configuration file """

from weaviate_etl.utilities import get_weaviate_client

from weaviate_etl.exceptions import UnableToCreateSchema
from weaviate_etl.exceptions import NoClassificationSet
from weaviate_etl.exceptions import NoModelLoaded
from weaviate_etl.exceptions import UnableToLoadSchema

from .generate_schema import create_schema_from_model
from .generate_schema import merge_schemas
from .generate_schema import add_classification_to_schema


class Schema:
    """ Class that has all the schema parameters """

    def __init__(self, model: dict, instance: dict, classification: dict=None) -> None:
        """
        Initialize a Schema class instance.

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        UnableToCreateSchema
            If schema can not generated from the model
        """

        if not isinstance(model, dict):
            raise TypeError("model is expected to be dict but is " + str(type(model)))

        if model is not None and 'model' in model and 'type' in model:
            self.model = model['model']
            self.type = model['type']
            self.schema = {}
            self.instance = instance
            self.client = get_weaviate_client(self.instance)
            self.classification = classification
        else:
            raise UnableToCreateSchema()


    def create(self, instance: dict) -> dict:
        """
        Create a schema from the model stored in self.model

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        UnableToCreateSchema
            If schema can not generated from the model

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        if not isinstance(instance, dict):
            raise TypeError("instance is expected to be dict but is " + str(type(instance)))
        if self.model is None:
            raise NoModelLoaded()

        if self.instance is not None and 'module_name' in self.instance:
            self.schema = create_schema_from_model(self.model, self.type, modulename=self.instance['module_name'])
        else:
            self.schema = create_schema_from_model(self.model, self.type)

        if self.schema is None or self.schema == {}:
            raise UnableToCreateSchema()

        return self.schema


    def get(self) -> dict:
        """
        Create a schema from the model stored in self.model

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        return self.schema


    def set(self, schema: dict) -> None:
        """
        sets the schema to the argument schema

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;

        Returns
        ------
        dict
            The dict describing the Weaviate schema
        """

        if not isinstance(schema, dict):
            raise TypeError("schema is expected to be dict but is " + str(type(schema)))

        self.schema = schema


    def load(self, instance: dict, schema: dict=None, replace: bool=True) -> None:
        """
        Loads the schema into Weaviate

        Parameters
        ----------
        schema: dict
            A dict that contains the schema (optional argument)
        replace: bool (optional argument)
            A boolean that indicates whether the current schema in Weaviate needs to be replaced

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        UnableToLoadSchema
            If schema can not be loaded
        """

        if schema is None:
            if self.schema is None:
                raise UnableToLoadSchema()
        else:
            self.schema = schema

        if self.client is None:
            self.client = get_weaviate_client(instance)

        if replace:
            if self.client.schema.contains():
                self.client.schema.delete_all()
            self.client.schema.create(self.schema)

        elif not self.client.schema.contains():
            self.client.schema.create(self.schema)



    def merge(self, schema1: dict, schema2: dict) -> dict:
        #pylint: disable=no-self-use
        """
        Merges two schemas

        Parameters
        ----------
        schema1: dict
            A dict that contains the schema that needs to be merged with schema2
        schema2: dict
            A dict that contains the schema that needs to be merged with schema1

        Raises
        ------
        TypeError
            If arguments are of a wrong data type;
        UnableToOpenCreateSchema
            If schema can not generated from the model

        Returns
        ------
        dict
            The dict describing the combined Weaviate schema
        """

        if not isinstance(schema1, dict):
            raise TypeError("schema is expected to be dict but is " + str(type(schema1)))
        if not isinstance(schema2, dict):
            raise TypeError("schema is expected to be dict but is " + str(type(schema2)))

        schema = merge_schemas(schema1, schema2)

        return schema


    def add_classification(self, classification: dict=None):
        """
        Add classification classes and properties to schema

        Raises
        ------
        UnableToLoadSchema
            If no schema is in model
        NoClassificationSet
            If no classification is set for model
        """

        if self.schema is None:
            raise UnableToLoadSchema()

        if classification is None:
            if self.classification is None:
                raise NoClassificationSet()
        else:
            self.classification = classification

        if self.instance is not None and 'module_name' in self.instance:
            add_classification_to_schema(self.schema, self.classification, modulename=self.instance['module_name'])
        else:
            add_classification_to_schema(self.schema, self.classification)
