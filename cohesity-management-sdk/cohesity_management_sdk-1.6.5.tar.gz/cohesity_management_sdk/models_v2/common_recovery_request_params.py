# -*- coding: utf-8 -*-


class CommonRecoveryRequestParams(object):

    """Implementation of the 'Common Recovery Request Params.' model.

    Specifies the common request parameters to create a Recovery.

    Attributes:
        name (string): Specifies the name of the Recovery.
        snapshot_environment (SnapshotEnvironmentEnum): Specifies the type of
            environment of snapshots for which the Recovery has to be
            performed.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "snapshot_environment":'snapshotEnvironment'
    }

    def __init__(self,
                 name=None,
                 snapshot_environment=None):
        """Constructor for the CommonRecoveryRequestParams class"""

        # Initialize members of the class
        self.name = name
        self.snapshot_environment = snapshot_environment


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
        name = dictionary.get('name')
        snapshot_environment = dictionary.get('snapshotEnvironment')

        # Return an object of this model
        return cls(name,
                   snapshot_environment)


