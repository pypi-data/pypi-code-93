"""Plugin to load CSV and parquet files from Google Cloud Storage into atoti tables.

This package is required to load files with GCP paths starting with ``gs://``.

Authentication is handled by the underlying GCS SDK for Java library.
Automatic credentials retrieval is explained in `their documentation <https://cloud.google.com/docs/authentication/production#automatically>`__.
"""

from ._version import VERSION as __version__
