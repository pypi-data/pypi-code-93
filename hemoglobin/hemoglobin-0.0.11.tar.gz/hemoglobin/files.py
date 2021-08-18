import warnings
import logging


class HemoglobinFile(object):
    """An object that represents files on your system to run the tests against."""

    OPEN_MODE = "r"

    @classmethod
    def from_path(cls, file_path, cli):
        """Initialise this class when you don't have a file object, but do have
        the file path.

        :param file_path: Path to file to process
        :type file_path: str
        :param cli: parent config object
        """
        return cls(open(file_path, cls.OPEN_MODE), cli)

    def __init__(self, f, hemoglobin):
        """
        :param f: file object to run methods in this function over
        :param cli: parent CLI object to get config from
        """
        self.f = f
        self.hemoglobin = hemoglobin

        self._text = None
        self._response = None

    @property
    def text(self):
        """Get the contents of the file (memory inefficent)

        :return: Contents of file object this class was initialised with
        :rtype: str
        """
        if not self._text:
            self._text = self.f.read()
        return self._text

    @property
    def response(self):
        if not self._response:
            self._response = self.get_grammarbot_response()
        return self._response

    @property
    def matches(self):
        return self.response.matches

    def get_grammarbot_response(self):
        logging.info(
            "Length of file {file_name} is {file_length}".format(
                file_name=self.f.name, file_length=len(self.text),
            )
        )
        if len(self.text) > self.hemoglobin.grammarbot.MAX_CHARS:
            warnings.warn(
                "File '{file_path}' is {file_length} characters log, and over {max_chars} characters the GrammarBot API allows. The contents of the file will be broken up to be processed.".format(
                    file_path=self.f.name,
                    file_length=len(self.text),
                    max_chars=self.hemoglobin.grammarbot.MAX_CHARS,
                )
            )
        return self.hemoglobin.grammarbot.check(self.text)

    def to_dict(self):
        """For all of the tests/methods available in textstat, run through them
        all and produce the results as a dictionary.

        :return: A dictionary representation of the results
        :rtype: dict
        """
        return self.get_grammarbot_response().to_dict()
