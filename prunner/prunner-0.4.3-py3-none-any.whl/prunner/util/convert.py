COMPONENT_DELIMITER = "#"


def split_file_component(text):
    filename = None
    if COMPONENT_DELIMITER in text:
        i = text.index(COMPONENT_DELIMITER)
        filename = text[:i]
        function_name = text[i + 1 :]
    else:
        function_name = text

    return function_name, filename
