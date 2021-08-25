# -*- coding: utf-8 -*-


class TargetMailboxParam(object):

    """Implementation of the 'TargetMailboxParam' model.

    Specifies the target Mailbox to recover to.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the object.
        target_folder_path (string): Specifies the path to the target folder.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "target_folder_path":'targetFolderPath',
        "name":'name'
    }

    def __init__(self,
                 id=None,
                 target_folder_path=None,
                 name=None):
        """Constructor for the TargetMailboxParam class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.target_folder_path = target_folder_path


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
        target_folder_path = dictionary.get('targetFolderPath')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(id,
                   target_folder_path,
                   name)


