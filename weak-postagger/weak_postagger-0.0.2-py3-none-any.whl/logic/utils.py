from logic import FILE_NAME_DIVIDERS


def get_class_name_from_file(file_name: str) -> str:
    """
        Retrieves the POS Tag class name from the file name.

        This method expects that the file name will be of the format `classname_specifier.txt`

    :param file_name: The file name containing the POS Tag name.
    :type file_name: `str`
    :return: POS Tag class name as specified on the file name.
    :rtype: `str`
    """
    return file_name[:min(map(lambda x: (file_name.index(x) if (x in file_name) else len(file_name)),
                              FILE_NAME_DIVIDERS))]
