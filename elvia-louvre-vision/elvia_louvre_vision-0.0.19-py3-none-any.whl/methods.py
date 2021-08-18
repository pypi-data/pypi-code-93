import csv
from io import BytesIO
from louvre_vision.config import Config
import os
import requests
from typing import List, Union


class Methods():
    """
    Helper methods.
    """
    @staticmethod
    def cast_to_float(input_string: Union[str, None]) -> Union[float, None]:
        if input_string is None: return None

        try:
            return float(input_string)
        except ValueError:
            return None

    @staticmethod
    def extract_filename(file_path: str) -> str:
        """
        Extract the file name from a file path.

        :param str file_path:
        :rtype: str
        """
        file_name, file_extension = os.path.splitext(
            file_path.rsplit('/', 1)[-1])
        return file_name + file_extension

    @classmethod
    def fetch_file_from_url(cls, file_url: str) -> BytesIO:
        """
        Fetch file from URL, return a stream object.

        :param str file_url:
        :rtype: BytesIO
        :raises RequestException:
        """
        _response = requests.get(url=file_url)
        _file_bytes = BytesIO(_response.content)
        return _file_bytes

    @staticmethod
    def get_dataset_from_csv(
            dataset_path: str,
            remove_titles: bool = False,
            delimiter: Union[str, List[str], None] = None) -> tuple:
        """Fetches a dataset in CSV format and returns a list of lists.
           If not provided, deduce the delimiter where possible.
           Raises: ValueError, NotImplementedError, OSError 
        """
        _delimiter = Methods.get_delimiter(file_path=dataset_path,
                                           sorted_allowed_choices=delimiter)
        if _delimiter is None:
            raise ValueError('Delimiter not found')
        dataset_list = []
        # open() can raise OSError if the dataset file doesn't exist
        with open(dataset_path, encoding='utf-8') as csvfile:
            dataset_reader = csv.reader(csvfile, delimiter=_delimiter)
            for row in dataset_reader:
                dataset_list.append(row)
        # If remove_titles is True, return titles separately
        if remove_titles:
            return dataset_list[0], dataset_list[1:]
        return None, dataset_list

    @staticmethod
    def get_delimiter(
        file_path: str,
        sorted_allowed_choices: Union[str, List[str], None] = [';', ',']
    ) -> Union[str, None]:
        '''
        Find the delimiter, given a file and a sorted list of possible delimiter candidates. 
        If none of the delimiter candidates from sorted_allowed_choices is found, return None.
        If sorted_allowed_choices is None, it attempts to use the default value from Config.
        We know that if semicolons are present, they are the delimiter. 
        Commas may be present as the main delimiter, but also as an internal
        delimiter in serialised objects, like for example serialised regions.
        
        Raises: ValueError, OSError, NotImplementedError
        '''
        candidates: List[str] = []
        if sorted_allowed_choices is None:
            try:
                sorted_allowed_choices = Config.default_delimiter
            except Exception:
                raise ValueError(
                    'No allowed delimiters provided, default value unreachable'
                )
        candidates.extend(sorted_allowed_choices)
        # Check that the number of candidates is not zero, that all of them are of type string
        # and that they are not empty strings
        if not len(candidates) or not all(
            [isinstance(item, str) and len(item) for item in candidates]):
            raise ValueError('Missing or invalid allowed delimiter provided')
        try:
            # open() can raise OSError if the dataset file doesn't exist
            with open(file_path, "r") as f:
                f.seek(0)
                first_line = f.readline()
                f.close()
                # Go through the candidates in the order they were given
                for delimiter in candidates:
                    # Are they in the data?
                    if first_line.count(delimiter):
                        return delimiter
                # None of the candidates were found in the input
                return None
        except OSError as os_error:
            raise OSError(os_error)
        except Exception as exception:
            raise NotImplementedError(exception)

    @classmethod
    def get_remote_file_size(cls, file_url: str) -> Union[int, None]:
        """
        Return remote file size, if possible.
        
        :param str file_url:
        :rtype: int | None
        """
        try:
            response = requests.head(file_url).headers['Content-Length']
            return int(response)
        except:  # NOSONAR, Same functionality regardless of exception thrown
            # TODO: We should probably do something useful here
            return None

    @classmethod
    def is_file_empty(cls,
                      stream: BytesIO,
                      min_size_bytes: int = 1000) -> bool:
        """
        Check whether the file size is larger than a threshold value.
        
        :param BytesIO stream:
        :param int min_size_bytes:
        :rtype: bool
        """
        try:
            if stream.getbuffer().nbytes < min_size_bytes:
                return True
            return False
        except:  #NOSONAR, No matter what exception is thrown here we will label the file as empty
            # TODO: We should probably do something useful here
            return True

    @staticmethod
    def is_string_url(input_str: str) -> bool:
        """Check if a string is a URL."""
        return bool('https://' in input_str)

    @staticmethod
    def save_dataset_to_csv(file_path: str,
                            dataset: list,
                            delimiter: Union[str, None] = None,
                            append: bool = False) -> None:
        """Writes a dataset list to CSV format. If append is False, existing files will be 
        overwritten."""
        # TODO: Add default delimiter in the config and update this with it
        if delimiter is None:
            delimiter = ';'
        if append:
            mode = 'a'
        else:
            mode = 'w'
        with open(file=file_path, mode=mode, newline='',
                  encoding='utf-8') as result_file:
            writer = csv.writer(result_file, delimiter=delimiter)
            writer.writerows(dataset)
