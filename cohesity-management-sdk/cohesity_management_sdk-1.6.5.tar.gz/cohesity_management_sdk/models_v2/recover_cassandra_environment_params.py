# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_cassandra_params

class RecoverCassandraEnvironmentParams(object):

    """Implementation of the 'Recover Cassandra environment params.' model.

    Specifies the recovery options specific to Cassandra environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_cassandra_params (RecoverCassandraParams): Specifies the
            parameters to recover Cassandra objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_cassandra_params":'recoverCassandraParams'
    }

    def __init__(self,
                 recovery_action='RecoverObjects',
                 recover_cassandra_params=None):
        """Constructor for the RecoverCassandraEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_cassandra_params = recover_cassandra_params


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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverObjects'
        recover_cassandra_params = cohesity_management_sdk.models_v2.recover_cassandra_params.RecoverCassandraParams.from_dictionary(dictionary.get('recoverCassandraParams')) if dictionary.get('recoverCassandraParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_cassandra_params)


