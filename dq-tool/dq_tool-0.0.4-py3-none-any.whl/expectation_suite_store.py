"""An abstraction lying between GE's ExpectationsStore and DQTool ExpectationStore"""
from typing import List

from great_expectations.data_context.types.resource_identifiers import (
    ExpectationSuiteIdentifier as GEExpectationSuiteIdentifier
)
from great_expectations.core import expectationSuiteSchema as GEexpectationSuiteSchema
from great_expectations.core import ExpectationSuite as GEExpectationSuite
from .expectation_attributes.expectation_suite import ExpectationSuite


class ExpectationSuiteStore:
    """An abstraction lying between GE's ExpectationsStore and DQTool ExpectationStore.
    Has all the GE dependencies, so that ExpectationSuite doesn't need to have any.
    Represents expectation suites stored in GE.
    In future could be replaced by a store with a single expectation granularity.
    Additionaly it can notify the backend / send the suite to a queue.
    Works with the whole trinity, doesn't leak expectation_suite_name anywhere.
    """
    def __init__(self, ge_context: 'BaseDataContext'):
        self._context = ge_context

    def _suite_exists(self, expectation_suite_name: str) -> bool:
        """Does a suite with the given expectation_suite_name exist?"""
        key = self._get_ge_key(expectation_suite_name)
        return self._ge_store.has_key(key)  # noqa: W601

    def get_or_create_suite(
        self,
        table_name: str,
        database_name: str,
        suite_key: str,
        user_identity_provider: 'IdentityProvider'
    ) -> ExpectationSuite:
        """If suite with given expectation_suite_name exists, return it, if not create a new empty one"""
        expectation_suite_name = ExpectationSuite.get_expectation_suite_name(
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )
        if self._suite_exists(expectation_suite_name):
            # get existing
            ge_suite = self._context.get_expectation_suite(
                expectation_suite_name=expectation_suite_name
            )
            return ExpectationSuite(
                expectation_suite=ge_suite,
                user_identity_provider=user_identity_provider
            )

        # create an empty one
        ge_suite = GEExpectationSuite(
            expectation_suite_name=expectation_suite_name
        )
        # return our ExpectationSuite
        return ExpectationSuite(
            expectation_suite=ge_suite,
            user_identity_provider=user_identity_provider,
            table_name=table_name,
            database_name=database_name,
            suite_key=suite_key
        )

    def save_suite(self, expectation_suite: ExpectationSuite):
        """Save suite to the store. Overwrites an existing with the same expectation_suite_name"""
        if not expectation_suite.table_name:
            raise ValueError('The table_name needs to be filled for the expectation suite')
        key = self._get_ge_key(expectation_suite._expectation_suite_name)  # pylint: disable=W0212
        ge_suite = GEexpectationSuiteSchema.load(expectation_suite.to_dict())
        self._ge_store.set(key, ge_suite)

    @property
    def _ge_store(self):
        """Get the GE store that acts like a key-value storage"""
        return self._context.stores[self._context.expectations_store_name]

    @classmethod
    def _get_ge_key(cls, expectation_suite_name: str) -> 'ExpectationSuiteIdentifier':
        """Get the GE key from the name - useful when accessing the store"""
        return GEExpectationSuiteIdentifier(expectation_suite_name=expectation_suite_name)

    def list_suites(self, user_identity_provider: 'IdentityProvider' = None) -> List[ExpectationSuite]:
        """List all available expectation suites"""
        suites = [
            ExpectationSuite(
                expectation_suite=self._context.get_expectation_suite(
                    expectation_suite_name=expectation_suite_name
                ),
                user_identity_provider=user_identity_provider
            )
            for expectation_suite_name in self._context.list_expectation_suite_names()
        ]
        return suites
