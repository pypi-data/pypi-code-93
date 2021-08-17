try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    # For Python <3.8 add 'importlib_metadata' as a dependency.
    import importlib_metadata  # type: ignore


# NOTE: Must match the name in `pyproject.toml`!
PACKAGE_NAME = "myst-alpha"


def get_package_version() -> str:
    """Returns the package version."""
    metadata = importlib_metadata.metadata(PACKAGE_NAME)  # type: ignore
    version = metadata["Version"]

    return version
