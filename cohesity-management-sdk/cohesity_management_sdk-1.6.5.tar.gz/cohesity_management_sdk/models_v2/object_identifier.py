# -*- coding: utf-8 -*-


class ObjectIdentifier(object):

    """Implementation of the 'Object Identifier.' model.

    Specifies the basic info to identify an object.

    Attributes:
        id (long|int): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        environment (EnvironmentEnum): Specifies the environment of the
            object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "environment":'environment'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 source_id=None,
                 source_name=None,
                 environment=None):
        """Constructor for the ObjectIdentifier class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name
        self.environment = environment


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        id = dictionary.get('id')
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        environment = dictionary.get('environment')

        # Return an object of this model
        return cls(id,
                   name,
                   source_id,
                   source_name,
                   environment)


