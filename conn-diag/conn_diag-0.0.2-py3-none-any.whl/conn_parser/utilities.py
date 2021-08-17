import os
from conn_diag.conn_parser.models import Connection
from conn_diag.conn_parser.constants import CONTENTS_DIR
from conn_diag.conn_parser.exceptions import NotValidConnectionError
from conn_diag.conn_parser.exceptions import ParseError


def is_namedtuple_instance(x):
    _type = type(x)
    bases = _type.__bases__
    print(_type, bases)
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, '_fields', None)
    print(fields)
    if not isinstance(fields, tuple):
        return False
    return all(type(i) == str for i in fields)


def validate_connections(connections):
    for connection in connections:
        if not isinstance(type(connection).__bases__, tuple):
            raise NotValidConnectionError('Connection type is not tuple')
        if not isinstance(connection, Connection):
            raise NotValidConnectionError('Connection type is Connection')
        yield connection


def get_files_from_path(path):
    pdf_paths = []

    if os.path.isdir(path):
        for file in os.listdir(path):
            pdf_path = os.path.join(path, file)
            if os.path.isfile(pdf_path):
                pdf_paths.append(pdf_path)
    elif os.path.isfile(path):
        pdf_paths.append(path)
    else:
        pass

    return pdf_paths


def write_content(name, content):
    content_path = os.path.join(CONTENTS_DIR, name)
    with open(file=content_path, mode='w') as file:
        file.write(content)


def validate_file(file):
    if not os.path.exists(file):
        raise ParseError('No such file or directory: {}'.format(file))
    return file
