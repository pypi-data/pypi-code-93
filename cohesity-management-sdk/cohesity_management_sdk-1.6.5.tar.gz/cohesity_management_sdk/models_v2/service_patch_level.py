# -*- coding: utf-8 -*-


class ServicePatchLevel(object):

    """Implementation of the 'ServicePatchLevel' model.

    Patch level of a service. It is the number of patches applied for the
    service on the cluster. If a service is never patched the patch level is
    0. If two patches were applied, patch level is 2.

    Attributes:
        service (string): Specifies the name of the service.
        patch_level (long|int): Specifies patch level of the service.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "patch_level":'patchLevel'
    }

    def __init__(self,
                 service=None,
                 patch_level=None):
        """Constructor for the ServicePatchLevel class"""

        # Initialize members of the class
        self.service = service
        self.patch_level = patch_level


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
        service = dictionary.get('service')
        patch_level = dictionary.get('patchLevel')

        # Return an object of this model
        return cls(service,
                   patch_level)


