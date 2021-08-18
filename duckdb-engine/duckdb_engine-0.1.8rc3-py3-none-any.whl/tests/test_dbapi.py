# from dbapi20 import DatabaseAPI20Test
# from functools import cache
# import duckdb


# class Proxy:
#     Error = RuntimeError

#     @cache
#     def __getattr__(self, name):
#         return getattr(duckdb, name)

# import pytest

# @pytest.mark.xfail(reason='doop')
# class test_DuckDB(DatabaseAPI20Test):
#     proxy = Proxy()
