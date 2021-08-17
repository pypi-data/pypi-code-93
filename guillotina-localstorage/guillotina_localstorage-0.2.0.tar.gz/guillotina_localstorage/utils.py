import os
import posixpath

_os_alt_seps = list(
    sep for sep in [os.path.sep, os.path.altsep] if sep not in (None, "/")
)


# https://github.com/pallets/werkzeug/blob/53d25c1f6273adf7612e7f0a2eebfc06a666709f/src/werkzeug/security.py#L224
def safe_join(directory, *pathnames):
    """Safely join zero or more untrusted path components to a base
    directory to avoid escaping the base directory.
    :param directory: The trusted base directory.
    :param pathnames: The untrusted path components relative to the
        base directory.
    :return: A safe path, otherwise ``None``.
    """
    parts = [directory]

    for filename in pathnames:
        if filename != "":
            filename = posixpath.normpath(filename)

        if (
            any(sep in filename for sep in _os_alt_seps)
            or os.path.isabs(filename)
            or filename == ".."
            or filename.startswith("../")
        ):
            return None

        parts.append(filename)

    return posixpath.join(*parts)
