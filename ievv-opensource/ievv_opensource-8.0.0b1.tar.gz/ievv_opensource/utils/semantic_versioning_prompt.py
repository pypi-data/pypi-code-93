import re

from PyInquirer import prompt


class VersionValidationError(Exception):
    """"""
    pass


class SemanticVersioning(object):
    """
    Updates an existing version number using semantic versioning.
    The incoming version number is expected to be a string without ``alpha`` in the end.

    Example::
        SemanticVersioning(version_string='10.0.0', project_name='My project').start()

        The user will be prompted with 3 choices in the terminal::
            * Patch (10.0.1)
            * Minor (10.1.0)
            * Major (11.0.0)

        A confirmation is asked for the choice.
        If the confirmation is ``False``, the 3 choices are prompted again until the confirmation is ``True``, then
        the version number is updated and returned
    """
    def __init__(self, version_string, project_name):
        self.project_name = project_name
        self.current_version = self.__validate_version_number(version_string=version_string)
        self.current_version_dict = self.__version_list_as_dict_with_ints(
            version_list=self.__split_string(version_string=self.current_version))

    def start(self):
        """
        Method which is called after initialising of the class :class:`SemanticVersioning` to make the update of an
        existing version number to a new one.
        Makes it possible for users to regret their choice of version number.

        :return: str(updated version)
        """
        new_version = self.__set_new_semantic_version_number()
        confirm_version = prompt(self.__confirm_new_version(chosen_version=new_version))
        while confirm_version['confirmed'] is False:
            new_version = self.__set_new_semantic_version_number()
            confirm_version = prompt(self.__confirm_new_version(chosen_version=new_version))
        validated_new_version = self.__validate_version_number(version_string=new_version)
        return validated_new_version

    def __set_new_semantic_version_number(self):
        """
        Validates the incoming version number and performs the update of the version before it is returned.
        Prompts the user to chose on of the three possible versions.
        Updates the old version number to the new one based on the user's choice.

        :return: str(new version number)
        """
        version_answer = prompt(
            self.__release_type_choices()
        )

        possible_new_version_dict = self.__set_possible_new_version_dict_with_strings()

        if version_answer.get('new_version', '').startswith('Patch'):
            new_version_number = possible_new_version_dict["new_patch"]
        elif version_answer.get('new_version', '').startswith('Minor'):
            new_version_number = possible_new_version_dict["new_minor"]
        else:
            new_version_number = possible_new_version_dict["new_major"]

        return new_version_number

    def __validate_version_number(self, version_string):
        """
        Validate version number.

        :param version_string: str()
        :return: str(validated version number) or Raises an error
        """
        if re.match(r'^\d+.\d+.\d+$', version_string):
            return version_string
        raise VersionValidationError(f'The provided version {version_string} does not match the expected pattern')

    def __split_string(self, version_string):
        """
        Makes a list of the version number before update with major, minor and patch as elements.

        :param version_string: str(version number before update)
        :return: list(old version number)
        """
        return version_string.split('.')

    def __version_list_as_dict_with_ints(self, version_list):
        """
        Makes a list with the keys ``major``, ``minor`` and ``patch`` where the values are the corresponding number
        from the old version number.

        :param version_list: list(Old version number as list)
        :return: dict(old version number as dict)
        """
        version_as_dict = {'major': int(version_list[0]), 'minor': int(version_list[1]), 'patch': int(version_list[2])}
        return version_as_dict

    def __set_possible_new_version_dict_with_strings(self):
        """
        Updates version number to match the possible kind of releases (major, minor and patch)

        :return: dict(Possible new version numbers with values as strings)
        """
        new_versions = {
            'new_major': self.get_next_major(),
            'new_minor': self.get_next_minor(),
            'new_patch': self.get_next_patch()
        }
        return new_versions

    def get_next_patch(self):
        """
        Get the next patch version based on the current version. Patch version is incremented by 1.

        :return: New version as string.
        """
        return f'{self.current_version_dict["major"]}.{self.current_version_dict["minor"]}.{self.current_version_dict.get("patch") + 1}'

    def get_next_minor(self):
        """
        Get the minor version based on the current version. Minor version is incremented by 1

        :return: New version as string.
        """
        return f'{self.current_version_dict["major"]}.{self.current_version_dict.get("minor") + 1}.0'

    def get_next_major(self):
        """
        Get the major version based on the current version. Major version is incremented by 1.

        :return: New version as string.
        """
        return f'{self.current_version_dict.get("major") + 1}.0.0'

    def __release_type_choices(self):
        """
        Uses ``PyInquirer`` to present the choices nicely

        :return: list(Release type choices as prompted to the user))
        """
        return [
            {
                'type': 'list',
                'name': 'new_version',
                'message': f'Select a new version of {self.project_name}. Currently at {self.current_version}',
                'choices': [
                    f"Patch ({self.get_next_patch()})",
                    f"Minor ({self.get_next_minor()})",
                    f"Major ({self.get_next_major()})"
                ]
            },
        ]

    def __confirm_new_version(self, chosen_version):
        """
        Uses ``PyInquirer`` to prompt the user a confirmation of the release choice
        :param chosen_version: str()
        :return: list(Confirmation of new release choice promted to the user)
        """
        return [
            {
                'type': 'confirm',
                'name': 'confirmed',
                'message': f'You have chosen {chosen_version} as new version number. Is this correct?'

            }
        ]


# Used for testing script in terminal
if __name__ == '__main__':
    SemanticVersioning(version_string="198.2.1", project_name='Test project').start()
