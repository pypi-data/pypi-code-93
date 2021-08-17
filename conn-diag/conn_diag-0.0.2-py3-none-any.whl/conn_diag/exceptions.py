class ConnDiagError(Exception):
    """Base exception for this module"""


class NARReaderCLIError(ConnDiagError):
    """Generic exception"""


class NARReaderCommandError(ConnDiagError):
    """Generic exception"""


class SSHConnectionError(ConnDiagError):
    """Generic exception"""


class NARReaderFieldParseError(ConnDiagError):
    """Generic exception"""


class NARReaderLoadError(ConnDiagError):
    """Generic exception"""


class BashScriptTypeError(ConnDiagError):
    """Generic exception"""


class InventoryFileNotFound(ConnDiagError):
    """Generic exception"""


class HostsNoInInventory(ConnDiagError):
    """Generic exception"""
