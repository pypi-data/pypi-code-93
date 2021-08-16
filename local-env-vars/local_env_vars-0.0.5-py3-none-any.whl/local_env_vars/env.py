import os.path
import json


class LocalEnvVars():

    def __init__(self, *argv):
        assert len(argv) > 0, "Supply at least 1 argument."

        self._env_file = '.env'
        self._ignore_file = '.gitignore'

        if(not LocalEnvVars.file_exists(self._ignore_file)):
            with open(self._ignore_file, "w") as filewriter:
                filewriter.write(self._env_file)
        else:
            ignore_found = [False]
            with open(self._ignore_file, "r") as filereader:
                ignore_found = [line for line in filereader.readlines(
                ) if line == self._env_file or line == self._env_file + '\n']

            if(not ignore_found):
                with open(self._ignore_file, "a") as filewriter:
                    filewriter.write('\n' + self._env_file)

        # Create env file if it does not exist.
        if(not LocalEnvVars.file_exists(self._env_file)):
            self.create_file(self._env_file)
            LocalEnvVars.dictionary_to_json_file(
                self._env_file, self.args_to_empty_dictionary(*argv))
            raise LocalEnvVarsException(
                "New .env file created with keys. Add their values and try again.")

        self.vars = LocalEnvVars.json_file_to_dictionary(
            self._env_file)

        # Check that application and env file's keys match, otherwise update env file.
        if(not LocalEnvVars.dict_has_equal_keys(LocalEnvVars.args_to_empty_dictionary(*argv), self.vars)):
            self.vars = LocalEnvVars.merge_dictionary_with_keys(
                self.vars, *argv)
            LocalEnvVars.dictionary_to_json_file(
                self._env_file, self.vars)
            raise LocalEnvVarsException(
                "Environment keys differ. Keys will be added/removed. Add the values and try again.")

        # Check that all variables are populated.
        if(not LocalEnvVars.dict_has_values(self.vars)):
            raise LocalEnvVarsException(
                "Environment keys are set up. Some values are missing, please add them and try again.")

    @staticmethod
    def args_to_empty_dictionary(*argv):
        dictionary = {}
        for arg in argv:
            dictionary[arg] = ""

        return dictionary

    @staticmethod
    def create_file(filename):
        assert not os.path.exists(filename), "File already exists."

        filewriter = open(filename, "w+")
        filewriter.close()

    @staticmethod
    def dict_has_equal_keys(dict1={}, dict2={}):
        return set(dict1.keys()) == set(dict2.keys())

    @staticmethod
    def dict_has_values(dict1={}):
        assert len(dict1) > 0, "Dictionary must contain at least one value."

        for key, value in dict1.items():
            if (not value):
                return False

        return True

    @staticmethod
    def dictionary_to_json_file(filename, dictionary={}):
        with open(filename, 'w') as filewriter:
            json.dump(dictionary, filewriter)

    @staticmethod
    def file_exists(filename):
        return os.path.exists(filename)

    @staticmethod
    def json_file_to_dictionary(filename):
        dictionary = {}

        with open(filename, 'r') as filereader:
            dictionary = json.load(filereader)

        return dictionary

    @staticmethod
    def merge_dictionary_with_keys(dict1={}, *argv):
        dictionary = {}
        for arg in argv:
            if arg in dict1:
                dictionary[arg] = dict1[arg]
            else:
                dictionary[arg] = ""

        return dictionary


class LocalEnvVarsException(Exception):
    """
    Exception raised for an environment setup issue.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
