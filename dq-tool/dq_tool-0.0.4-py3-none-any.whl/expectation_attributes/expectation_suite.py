"""A user friendly way to view and edit expectations"""
from typing import Union, Any, Callable
import copy

from .import read_only_attributes as ra
from .expectation import Expectation
from ..misc.printing import pretty_repr, yamlize


@ra.add_read_only_auto_attributes
@ra.add_read_only_user_attributes
class ExpectationSuite:
    """A set of expectations to be run together.
    Holds all the logic related to metadata and ids.
    Has minimal dependencies on GE, so that it can be taken away easily and re-used in web app backend.
    Should be invisible to a casual python inteface user.
    This is a single-operation, throw-away thing.
    So create it, add OR remove OR clear OR update, save it and throw away.
    All fields are stored in private attributes as in Expectation, the difference is that  none of them can be set.
    The private auto fields can't be read either.
    """
    META_KEY = 'dq_tool'
    _META_USER_FIELDS = (
        'table_name',
        'database_name',
        'suite_key'
    )
    _META_AUTO_FIELDS = (
        'revision',
        '_last_expectation_id'  # this shouldn't be visible as a property
    )
    # Design thoughts: Immutable from the outside perspective - might make sense - that's the way
    # this is going to be stored in db - instance represents one revision.
    # ??? maybe not - you don't want the old version floating around, you want to throw it away anyways
    # It would mean doing all the changes on the dict and then returning a new instance based on that dict
    # Does it make sense?
    # Conclusion: no. Nothing gained from immutability, adds complexity, unnecessary copying.

    def __init__(
        self,
        expectation_suite: Union[dict, 'ExpectationSuite', 'GEExpectationSuite'] = None,
        # to use this with GE you should pass an empty GE suite dict
        user_identity_provider: 'UserIdentityProvider' = None,  # something that has a .get_current_user() method
        **meta_fields  # see _META_USER_FIELDS for what can be passed here
    ):
        # validate
        ra.validate_meta_fields(
            meta_fields=meta_fields,
            meta_user_fields=self._META_USER_FIELDS,
            meta_auto_fields=self._META_AUTO_FIELDS
        )

        # turn expectation_suite into a dict
        expectation_suite = expectation_suite or {}
        if not isinstance(expectation_suite, dict):
            expectation_suite = expectation_suite.to_json_dict()
        expectation_suite = copy.deepcopy(expectation_suite)

        # expectations are stored outside of the dict as Expectation instances
        expectations = expectation_suite.pop('expectations', [])
        self._expectations = [
            Expectation(expectation=exp, parent_suite=self)
            for exp in expectations
        ]

        self._incoming_suite_name = expectation_suite.pop('expectation_suite_name', None)

        # ensure ['meta']['dq_tool'] is there
        self._dict = expectation_suite
        self._dict.setdefault('meta', {})
        meta_dq_tool = self._dict['meta'].pop(self.META_KEY, {})

        # set values incoming dict's meta vs the params.
        # conflicts between expectation_suite meta and the params are an error, raise it.
        for field_name in self._META_USER_FIELDS + self._META_AUTO_FIELDS:
            self._resolve_meta_value(
                meta_dq_tool=meta_dq_tool,
                param_name=field_name,
                param_value=meta_fields.get(field_name)
            )
        # resolve the suite name from incoming dict vs. what's in the attrs
        names_unempty = self._incoming_suite_name and self._expectation_suite_name
        if names_unempty and self._incoming_suite_name != self._expectation_suite_name:
            raise ValueError((
                'The expectation_suite_name that come in the expectation_suite param: {} '
                "isn't consistent with the name we got from params: {}").format(
                    self._incoming_suite_name,
                    self._expectation_suite_name
            ))

        # auto fields - like id
        self._init_meta_auto_fields()

        # keep the identity provider
        self._user_identity_provider = user_identity_provider

    def add(self, expectation: Expectation):
        """Add expectation to the suite"""
        # check if it isn't already there
        same_ones = self._filter_same_as(expectation)
        if same_ones:
            raise ValueError((
                "The suite already contains an expectation that is equivalent to the one you're adding."
                'This is already there: {}').format(same_ones)
            )
        # copy it so that we don't run into shared-dict situations, pass the reference
        expectation = Expectation(
            expectation=expectation,
            parent_suite=self
        )
        # fill in autofieldslast_updated_by and at, id, etc. in the exp -
        # ignore what's already there - act as if it didn't exist before adding to the suite
        expectation._expectation_id = self._next_expectation_id()  # pylint: disable=W0212
        expectation._bump_revision(  # pylint: disable=W0212
            user_identity_provider=self._user_identity_provider,
            new_one=True,
        )

        # bump suite revision
        self._bump_revision()

        # append it to the expectations
        self._expectations.append(expectation)

    def get(self, expectation_id: int) -> Expectation:
        """Get expectation based on the id"""
        return self._get_with_list_index(expectation_id=expectation_id)[1]

    def remove(self, expectation_id: int):
        """Remove expectation with the given id from the suite and return it."""
        list_index, exp = self._get_with_list_index(expectation_id=expectation_id)
        del self._expectations[list_index]
        return exp

    def clear(self):
        """Remove all expectations from the suite"""
        self._expectations = []

    def clear_and_reset(self):
        """Remove all expectations and reset the revision, id counter etc."""
        self.clear()
        self._reset()

    def update(
        self,
        expectation: Expectation,
        expectation_id: int = None
    ):
        """Update the expectation - based on its id.
        The id is taken from the param (higher priority) or expectation.expectation_id.
        If the type doesn't match the existing expectation, throws an error - they should add it instead."""
        # if id was passed, create a new expectation with that id
        if expectation_id:
            expectation = Expectation(expectation=expectation, expectation_id=expectation_id)
        i_exp, existing_exp = self._get_with_list_index(
            expectation_id=expectation.expectation_id
        )
        expectation._copy_auto_field_values_from(expectation=existing_exp)  # pylint: disable=W0212
        if expectation.expectation_type != existing_exp.expectation_type:
            raise ValueError((
                "The expectation_type {} of the existing expectation"
                "doesn't match the expectation_type {} of the updated expectation. You may want to add it instead."
            ).format(existing_exp.expectation_type, expectation.expectation_type))
        # bump the expectation revision
        expectation._bump_revision(  # pylint: disable=W0212
            user_identity_provider=self._user_identity_provider,
            new_one=False
        )
        # replace it in the list
        self._expectations[i_exp] = expectation
        # bump the suite revision too
        self._bump_revision()

    def list(self):
        """Get a list of expectations that are in the suite"""
        return self._expectations

    def to_dict(self):
        """GE friendly dict"""
        # if any of the fields are non-empty, add dq_tool section to meta, otherwise leave empty
        field_values = {
            field: getattr(self, field) for field in self._META_USER_FIELDS + self._META_AUTO_FIELDS
        }
        dq_tool_meta = {
            self.META_KEY: {
                **field_values
            }
        } if any(field_values.values()) else {}
        # deepcopy just in case there are some nested things in meta
        return copy.deepcopy({
            **self._dict,
            **{
                'expectation_suite_name': self._expectation_suite_name,
                'expectations': [
                    exp.to_dict()
                    for exp in self._expectations
                ],
                'meta': {
                    **self._dict['meta'],
                    **dq_tool_meta
                }
            }
        })

    def to_json_dict(self) -> dict:
        """To have the same method as GE's ExpectationConfiguration"""
        return self.to_dict()

    DEFAULT_SUITE_KEY = 'default'

    @classmethod
    def get_expectation_suite_name(
        cls,
        table_name: str,
        database_name: str,
        suite_key: str = DEFAULT_SUITE_KEY
    ) -> str:
        """Get a suite name from the id tuple"""
        return '{}_{}_{}'.format(
            database_name,
            table_name,
            suite_key
        )

    def count(self) -> int:
        """Expectation count in the suite"""
        return len(self._expectations)

    def pretty_print(self):
        """Print indented json"""
        print(pretty_repr(self.to_dict()))

    def __repr__(self) -> str:
        """Pretty printed expectation dict"""
        return pretty_repr(self.to_dict())

    def __str__(self):
        """A human-friendly representation of the suite"""
        return yamlize(self._get_str_dict())

    # "private" methods
    def _get_with_list_index(self, expectation_id: int) -> (int, Expectation):
        """Get the expectation index in the self._expectations list, and the expectation itself as a tuple.
        ValueError raised if not found."""
        # find the exp by id, raise an ValueError if not found
        found_exps = [(i, exp) for i, exp in enumerate(self._expectations) if exp.expectation_id == expectation_id]
        assert len(found_exps) <= 1
        if not found_exps:
            raise ValueError((
                "The expectation_id {} doesn't exist for the given database_name: {},"
                "table_name: {}, suite_key: {} combination. Valid ids are: {}").format(
                expectation_id,
                self.database_name,  # pylint: disable=E1101
                self.table_name,  # pylint: disable=E1101
                self.suite_key,  # pylint: disable=E1101
                [exp.expectation_id for exp in self._expectations]
            ))
        return found_exps[0]

    def _get_str_dict(
        self,
        # now we can rely on expectation_id being populated when it's in a suite:
        process_exp: Callable = lambda exp: '{}: {}'.format(exp.expectation_id, exp.call_str)
    ) -> dict:
        """Get a dictionary of processed expectations. The expectation-processing function is the get_exp_str param"""
        # init empty, add exps according to percieved type
        res = {
            'expectation_suite_name': self._expectation_suite_name
        } if self.table_name is None else {  # pylint: disable=E1101
            'database_name': self.database_name,  # pylint: disable=E1101
            'table_name': self.table_name,  # pylint: disable=E1101
            'suite_key': self.suite_key  # pylint: disable=E1101
        }
        res = {
            **res,
            **{
                'table_expectations': [],
                'column_expectations': {},
                'expectations_with_expressions': [],
                'other_expectations': []
            }
        }
        for exp in self.list():
            exp_str = process_exp(exp)
            # table shape expectation
            if 'table' in exp.expectation_type:
                res['table_expectations'].append(exp_str)
                continue
            # a "column" expectation -there's a list for each column
            column = exp.kwargs.get('column')
            if column:
                if column in res['column_expectations']:
                    res['column_expectations'][column].append(exp_str)
                else:
                    res['column_expectations'][column] = [exp_str]
                continue
            # expressions
            if 'expression' in exp.expectation_type:
                res['expectations_with_expressions'].append(exp_str)
                continue
            res['other_expectations'].append(exp_str)
        # only keep the non-empty ones
        return {k: v for k, v in res.items() if v}

    @property
    def _expectation_suite_name(self):
        # this is the manage suites-yourself mode - the name that came in
        # pylint catches these, but these are defined dynamically
        if self.table_name is None:  # pylint: disable=E1101
            return self._incoming_suite_name
        return self.get_expectation_suite_name(
            table_name=self.table_name,  # pylint: disable=E1101
            database_name=self.database_name,  # pylint: disable=E1101
            suite_key=self.suite_key  # pylint: disable=E1101
        )

    _FIRST_REVISION = 0  # first one will have something added so it will be 1 for the user
    _FIRST_LAST_EXPECTATION_ID = 0  # same here, first expectation will get 1

    def _next_expectation_id(self) -> int:
        """Get the expectation id for a newly added expectation"""
        self._last_expectation_id += 1
        return self._last_expectation_id

    def _reset(self):
        """Reset the auto fields to its initial values"""
        # pylint - attributes are not defined if there's no id'ing / versioning
        self._revision = self._FIRST_REVISION  # pylint: disable=W0201
        self._last_expectation_id = self._FIRST_LAST_EXPECTATION_ID  # pylint: disable=W0201

    def _init_meta_auto_fields(self):
        """Initialize the auto fields - like revision, next id if empty.
        Verify all the auto fields are set, or none of them.
        """
        # how many auto fields are already set
        field_values = {name: getattr(self, name) for name in self._META_AUTO_FIELDS}
        # all set -> done
        if all(field_values.values()):
            return

        # none set -> initialize
        if not any(field_values.values()):
            self._reset()
            # initialize the underlying expectations
            for exp in self.list():
                exp._initialize_loaded(expectation_id=self._next_expectation_id())  # pylint: disable=W0212
        else:
            # something's wrong - some are there but not all
            raise ValueError((
                "There are some auto meta fields set, but not all of them. "
                "You need to set all or nothing. These are set: {}, These are all the params: {}"
            ).format(
                field_values,
                self._META_AUTO_FIELDS
            ))

    def _bump_revision(self):
        self._revision += 1

    def _resolve_meta_value(
        self,
        meta_dq_tool: dict,
        param_name: str,
        param_value: Any
    ):
        """Set the attribute called <private version of param_name> to param_value.
        If it's already in meta_dq_tool, raise an Error"""
        meta_value = meta_dq_tool.get(param_name)
        # meta inconsistent with param -> raise an error
        if meta_value and param_value and meta_value != param_value:
            raise ValueError(
                "Invalid parameter {}, with value {}. The parameter is already present in the meta: {}".format(
                    param_name,
                    param_value,
                    meta_dq_tool
                )
            )
        # otherwise just set what we have, even if it's none
        value = param_value or meta_value
        attr_name = ra.get_private_attribute_name(name=param_name, ignore_private=True)
        setattr(self, attr_name, value)

    def _filter_same_as(self, expectation: Expectation) -> bool:
        """Filter the expectations in the suite that have the same kwargs and type as `expectation`.
        Not taking into account default kwargs defined in GE."""
        return [
            exp for exp in self._expectations
            if exp.expectation_type == expectation.expectation_type and exp.kwargs == expectation.kwargs
        ]
