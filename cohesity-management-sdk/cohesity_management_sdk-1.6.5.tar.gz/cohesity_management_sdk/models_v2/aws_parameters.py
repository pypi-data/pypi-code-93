# -*- coding: utf-8 -*-


class AWSParameters(object):

    """Implementation of the 'AWS Parameters.' model.

    Specifies various resources when converting and deploying a VM to AWS.

    Attributes:
        region (long|int): Specifies id of the AWS region in which to deploy
            the VM.
        vpc_id (long|int): Specifies id of the Virtual Private Cloud to chose
            for the instance type.
        subnet_id (long|int): Specifies id of the subnet within above VPC.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "region":'region',
        "vpc_id":'vpcId',
        "subnet_id":'subnetId'
    }

    def __init__(self,
                 region=None,
                 vpc_id=None,
                 subnet_id=None):
        """Constructor for the AWSParameters class"""

        # Initialize members of the class
        self.region = region
        self.vpc_id = vpc_id
        self.subnet_id = subnet_id


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
        region = dictionary.get('region')
        vpc_id = dictionary.get('vpcId')
        subnet_id = dictionary.get('subnetId')

        # Return an object of this model
        return cls(region,
                   vpc_id,
                   subnet_id)


