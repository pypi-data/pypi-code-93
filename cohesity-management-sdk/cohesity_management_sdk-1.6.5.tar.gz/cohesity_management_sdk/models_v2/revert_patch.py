# -*- coding: utf-8 -*-


class RevertPatch(object):

    """Implementation of the 'Revert patch.' model.

    Specifies the request to revert a patch. An optional patch level can be
    specified. When a patch level is specified, system keeps reverting patches
    until the given patch level is reverted. If no patch level is specified,
    just the last applied patch is reverted. Patch level should be 1 or
    above.

    Attributes:
        service (string): Specifies the name of the service whose patch should
            be reverted.
        patch_level (long|int): Specifies optional patch level upto which the
            patches should be reverted. Patch level should be 1 or above.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "patch_level":'patchLevel'
    }

    def __init__(self,
                 service=None,
                 patch_level=None):
        """Constructor for the RevertPatch class"""

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


