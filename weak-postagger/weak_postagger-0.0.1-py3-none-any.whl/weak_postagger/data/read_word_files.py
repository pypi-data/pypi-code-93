import os
import typing as tp

from take_text_preprocess.presentation import pre_process


def read_file(file_name: str, pre_processing_opt: tp.List[str] = []) -> tp.List[str]:
    """
        Reads a list of strings from a file.
        
    :param file_name: File path.
    :type file_name: `str`
    :param pre_processing_opt: Optional pre processing options to be applied. Defaults to basic pre processing.
    :type pre_processing_opt: `tp.List[str]`
    :rtype: `tp.List[str]`
    """
    with open(file_name, 'rb') as f:
        words = [pre_process(str(line), pre_processing_opt)
                 for line in f.readlines()]
    return words


def get_files_in_dir(directory_name: str) -> tp.List['str']:
    """
        Retrieves all files from a directory.

    :param directory_name: Directory containing files to be read.
    :type directory_name: `str`
    :return: List containing all the names of the files in the directory.
    :rtype: `tp.List['str']`
    """
    try:
        return os.listdir(directory_name)
    except OSError as e:
        raise e
