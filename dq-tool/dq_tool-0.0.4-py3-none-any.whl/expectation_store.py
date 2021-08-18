"""A store to keep expectation definitions, typically in a database. An interface lying on the dq_tool object."""

from typing import Union, List, Any, Callable

from .expectation_attributes.expectation_suite import ExpectationSuite
from .expectation_attributes.expectation import Expectation
from .hive_metastore import HiveMetastore
from .expectation_suite_store import ExpectationSuiteStore


class ExpectationStore:
    """The store class, its instance is available under dq_tool.expectation_store.
    The approach when using this class is to have an interface, like for a command line tool.
    The user is supposed to be write and run the code only once - while defining / editing expectations.
    """
    def __init__(self, dq_tool: 'DQTool'):
        self._dq_tool = dq_tool
        self._expectation_suite_store = ExpectationSuiteStore(
            ge_context=dq_tool._context
        )

    def add(
        self,
        expectation: Union[dict, Expectation, 'ExpectationConfiguration', 'ExpectationValidationResult'],
        # suite level params:
        table_name: str,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY,
        # expectation level params (if not provided in meta).
        # Here it makes more sense, as the user thinks about these at the time they're adding it to the store.
        severity: str = None,
        agreement: str = None,
        tags: List[str] = None
    ):
        """Add an expectation to the store. If it already exists, throws a ValueError."""
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )

        # create an expectation instance, setting just user fields
        expectation = Expectation(
            expectation=expectation,
            severity=severity,
            agreement=agreement,
            tags=tags
        )

        # add the expectation to the suite
        suite.add(expectation)

        # save it
        self._expectation_suite_store.save_suite(suite)

    def list(
        self,
        table_name: str,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ) -> List[Expectation]:
        """List expectations for the table, db, key"""
        # get or create a suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        return suite.list()

    def count(
        self,
        table_name: str,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ) -> int:
        """Expectation count for the given table_name, database_name, suite_key"""
        # get or create a suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        return suite.count()

    def print(
        self,
        table_name: str,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ):
        """Pretty print all expectations that satisfy the conditions given in params. Conditions are ANDed.
        For now only one database, table, suite_key combination."""
        # print the suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        print(suite)

        # next version (maybe): get suite names for suites that should be printed
        #  list_suites
        # get the suites
        # filter out what shouldn't be printed
        # group the suites
        # print them, highlight ids

    def get(
        self,
        table_name: str,
        expectation_id: int,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ) -> Expectation:
        """Get a single expectation so that it can be edited or re-run."""
        # get the suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        # get the expectation by id, from the suite and return it
        return suite.get(expectation_id=expectation_id)

    def update(
        self,
        expectation: 'Expectation',
        table_name: str = None,
        database_name: str = None,
        suite_key: str = None,
        expectation_id: int = None
    ):
        """Update the expectation with the identification
        (table_name, database_name, suite_key, expectation_id) that are inside the expectation.
        Identification taken from the expectation.
        If the type doesn't match, throws a ValueError - they should add it instead.
        """
        # resolve - parent_suite table_name, database_name, suite_key
        # vs values that came in params
        # get the "normalized" values first
        database_name, table_name = HiveMetastore.get_database_table_name(
            database_name=database_name,
            table_name=table_name,
            keep_nones=True
        )
        # resolve
        parent_suite = expectation._parent_suite  # pylint: disable=W0212
        database_name, table_name, suite_key, expectation_id = (
            self._resolve_param(
                param_name=pnm,
                param_value=pvl,
                parent_obj=prnt,
                default_value=dflt
            ) for pnm, pvl, prnt, dflt in (
                ('database_name', database_name, parent_suite, HiveMetastore.DEFAULT_DATABASE_NAME),
                # no default for table and id - must be somewhere
                ('table_name', table_name, parent_suite, None),
                ('suite_key', suite_key, parent_suite, ExpectationSuite.DEFAULT_SUITE_KEY),
                ('expectation_id', expectation_id, expectation, None)
            )
        )
        # get the suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        # update it there
        suite.update(expectation=expectation, expectation_id=expectation_id)
        # save it
        self._expectation_suite_store.save_suite(suite)

    def remove(
        self,
        table_name: str,
        expectation_id: int,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ) -> Expectation:
        """Remove the expectation with the identification from the store and return it.
        """
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        removed = suite.remove(expectation_id=expectation_id)
        self._expectation_suite_store.save_suite(suite)
        return removed

    def clear(
        self,
        table_name: str,
        database_name: str = None,
        suite_key: str = None
    ):
        """Delete all expectations for a given database / table / suite_key"""
        # get or create a suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )

        # clear and save
        suite.clear()
        self._expectation_suite_store.save_suite(suite)

    def clear_and_reset(
        self,
        table_name: str,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ):
        """Delete all expectations and clear the revision, id counter, etc."""
        # get or create a suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )

        # clear, reset and save
        suite.clear_and_reset()
        self._expectation_suite_store.save_suite(suite)

    def validate_table(
        self,
        table_name: str,
        database_name: str = None,
        suite_key: str = ExpectationSuite.DEFAULT_SUITE_KEY
    ) -> 'ValidationResult':
        """Run a validations using expectaions defined for a table. Runs one suite.
        """
        # Adding the method to this class instead of DQTool as this can't be done without a store.

        # get or create a suite
        suite = self._get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )

        dot_table_name = HiveMetastore.get_dot_table_name(
            table_name=table_name,
            database_name=database_name
        )
        # get a df and validate it
        df = self._dq_tool._spark.table(dot_table_name)  # pylint: disable=W0212
        result = self._dq_tool.validate(
            df=df,
            expectations=suite,
            save_suite=False
        )
        return result

    def list_database_names(self) -> List[str]:
        """Get a list of database names where there are expectations defined"""
        return self._list_suite_attribute_unique_values(attr_name='database_name')

    def list_table_names(
        self,
        database_name: str = HiveMetastore.DEFAULT_DATABASE_NAME
    ) -> List[str]:
        """Get a list of table names in the given database where there are expectations defined"""
        return self._list_suite_attribute_unique_values(
            attr_name='table_name',
            include_suite=lambda suite: suite.database_name == database_name
        )

    def list_suite_keys(
        self,
        table_name: str,
        database_name: str = HiveMetastore.DEFAULT_DATABASE_NAME
    ) -> List[str]:
        """Get a list of suite keys for a given table in the given database"""
        return self._list_suite_attribute_unique_values(
            attr_name='suite_key',
            include_suite=lambda suite: suite.database_name == database_name and suite.table_name == table_name
        )

    # 'private' stuff
    def _list_suite_attribute_unique_values(
        self,
        attr_name: str,
        include_suite: Callable = lambda suite: True
    ) -> List[Any]:
        """List attribute values in all available suites. Remove empty values, remove duplicates"""
        suites = self._expectation_suite_store.list_suites()
        return list(set(
            getattr(suite, attr_name)
            for suite in suites
            if getattr(suite, attr_name) and include_suite(suite)
        ))

    def _get_or_create_suite(
        self,
        table_name: str,
        database_name: str,
        suite_key: str
    ) -> ExpectationSuite:
        """Get an expectation suite from the store."""
        # handle the dots and other stuff
        database_name, table_name = HiveMetastore.get_database_table_name(
            database_name=database_name,
            table_name=table_name
        )
        database_name = database_name or HiveMetastore.DEFAULT_DATABASE_NAME
        # get or create a suite
        return self._expectation_suite_store.get_or_create_suite(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key,
            user_identity_provider=self._dq_tool._user_identity_provider  # pylint: disable=W0212
        )

    @classmethod
    def _resolve_param(
        cls,
        param_name: str,
        param_value: str,
        parent_obj: Union[ExpectationSuite, 'Expectation'],
        default_value: str
    ) -> str:
        """Resolve method param vs. what came in expectation. The priorities are:
        1. param_value
        2. value in parent_obj
        3. default_value.
        If none of these passed and there's no default, raise a ValueError"""
        # param
        if param_value:
            return param_value
        # parent suite:
        parent_value = getattr(parent_obj, param_name) if parent_obj else None
        if parent_value:
            return parent_value
        # default:
        if not default_value:
            raise ValueError((
                "No value provided for {}, there's no default value either."
                "You need to provide the value in method parameter or the expectation."
            ).format(param_name))
        return default_value
