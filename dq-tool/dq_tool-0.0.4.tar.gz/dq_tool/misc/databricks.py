"""Databricks-related functions"""

from .user_identity_provider import UserIdentityProvider


class DatabricksIdentityProvider(UserIdentityProvider):
    """Something that tells you who the current user is - with method get_current_user()
    For passing into Expectation - to fill in created_by and last_modified_by.
    Could be passed as string instead, but this at least support changing users over time."""

    def __init__(self, spark: 'SparkSession'):
        self._spark = spark
        self._dbutils = self._get_dbutils()

    def get_current_user(self) -> str:
        """Get current databricks user's email. Returns None if not available."""
        if not self._dbutils:
            return None
        try:
            return self._dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
        except AttributeError as e:
            print("Can't get current databricks user, error: {}".format(e))
            return None

    def _get_dbutils(self) -> 'DBUtils':
        """Get db utils in an installed wheel
        https://docs.microsoft.com/en-gb/azure/databricks/dev-tools/databricks-connect#access-dbutils
        Returns a None if dbutils aren't available
        """
        if not self._spark:
            return None
        try:
            if self._spark.conf.get('spark.databricks.service.client.enabled') == 'true':
                # pylint - these are not hard dependencies, use then when available
                from pyspark.dbutils import DBUtils  # pylint: disable=C0415,E0401,E0611
                return DBUtils(self._spark)
            import IPython  # pylint: disable=C0415,E0401
            return IPython.get_ipython().user_ns['dbutils']
        except AttributeError as e:
            print("Can't get dbutils, error: {}".format(e))
            return None
