# -*- coding: utf-8 -*-


class SearchPublicFolderRequestParams(object):

    """Implementation of the 'Search Public Folder request params.' model.

    Specifies the request parameters to search for Public Folder items.

    Attributes:
        search_string (string): Specifies the search string to filter the
            items. User can specify a wildcard character '*' as a suffix to a
            string where all item names are matched with the prefix string.
        types (list of Type31Enum): Specifies a list of public folder item
            types. Only items within the given types will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "search_string":'searchString',
        "types":'types'
    }

    def __init__(self,
                 search_string=None,
                 types=None):
        """Constructor for the SearchPublicFolderRequestParams class"""

        # Initialize members of the class
        self.search_string = search_string
        self.types = types


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
        search_string = dictionary.get('searchString')
        types = dictionary.get('types')

        # Return an object of this model
        return cls(search_string,
                   types)


