"""Supported SQL drivers.

To use another JDBC driver, add the driver's JAR to :attr:`~atoti.config.session_config.SessionConfig.extra_jars`.

For instance JARs to connect to Google BigQuery can be found on `BigQuery documentation <https://cloud.google.com/bigquery/docs/reference/odbc-jdbc-drivers>`_.
Once added to the extra JARs, ``driver="com.simba.googlebigquery.jdbc.Driver"`` can be used.
"""

import re

from atoti._jdbc_utils import _JDBC_PREFIX

H2 = "org.h2.Driver"
"""H2 driver."""

IBM_DB2 = "com.ibm.db2.jcc.DB2Driver"
"""IBM DB2 driver."""

MARIADB = "org.mariadb.jdbc.Driver"
"""MariaDB driver."""

MYSQL = "com.mysql.cj.jdbc.Driver"
"""MySQL driver."""

ORACLE = "oracle.jdbc.OracleDriver"
"""Oracle driver."""

POSTGRESQL = "org.postgresql.Driver"
"""PostgreSQL driver."""

MICROSOFT_SQL_SERVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
"""Microsoft SQL Server driver."""


_DRIVER_PER_PATH = {
    "db2": IBM_DB2,
    "h2": H2,
    "mariadb": MARIADB,
    "mysql": MYSQL,
    "oracle": ORACLE,
    "postgresql": POSTGRESQL,
    "sqlserver": MICROSOFT_SQL_SERVER,
}

_DRIVER_PATH_PATTERN = f"{_JDBC_PREFIX}(?P<driver>[^:]+):"


def _infer_driver(url: str) -> str:
    match = re.search(_DRIVER_PATH_PATTERN, url)

    if match:
        driver = match.group("driver")

        if driver in _DRIVER_PER_PATH:
            return _DRIVER_PER_PATH[driver]

    raise ValueError(f"Cannot infer driver from URL: {url}")
