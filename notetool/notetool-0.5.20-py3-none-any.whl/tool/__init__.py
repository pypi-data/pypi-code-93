from notetool.tool.build import get_version, version_add

from .compress import decompress
from .log import log, logger
from .path import delete_file, exists_file, path_parse, rename
from .secret import SecretManage, read_secret, set_secret_path, write_secret
