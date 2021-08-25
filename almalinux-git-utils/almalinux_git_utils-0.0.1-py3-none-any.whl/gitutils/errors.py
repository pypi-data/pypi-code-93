"""AlmaLinux Git server utilities error classes"""


class ChecksumError(Exception):

    """File checksum mismatch exception"""

    pass


class NetworkError(Exception):

    """Network error exception"""

    pass
