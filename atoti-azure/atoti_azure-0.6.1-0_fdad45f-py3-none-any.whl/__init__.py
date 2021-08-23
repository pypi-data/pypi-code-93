r"""Plugin to load CSV and parquet files from Azure Blob Storage into atoti tables.

This package is required to load files with path like ``https://{ACCOUNT_NAME}.blob.core.windows.net/path/to/data-*``.

Authentication is done with a `connection string <https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string?toc=/azure/storage/blobs/toc.json#store-a-connection-string>`__ that will be read from the ``AZURE_CONNECTION_STRING`` environment variable or, if it does not exist, from the file at ``~/.azure/credentials`` (``C:\\Users\\{USERNAME}\\.azure\\credentials`` on Windows).

See Also:
    :class:`~atoti.config.azure.AzureConfig` to configure how atoti interacts with Azure.
"""

from ._version import VERSION as __version__
