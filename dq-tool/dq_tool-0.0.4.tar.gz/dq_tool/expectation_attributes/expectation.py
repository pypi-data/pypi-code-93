"""The Expectation class"""
from typing import Union, Any, Callable
import itertools
import copy
import datetime

from .import read_only_attributes as ra
from ..misc.printing import pretty_repr


@ra.add_read_only_auto_attributes
class Expectation:
    """A single expectation definition. Mutable.
    Minimal logic contained.
    _META_USER_FIELDS are provided by the user.
    _META_AUTO_FIELDS are set by the suite when adding / updating.
    Meta Fields are stored in attributes and are put to meta only in to_dict().
    The meta attribute contains meta minus dq tool.
    """
    META_KEY = 'dq_tool'
    _META_USER_FIELDS = (
        'severity',
        'agreement',
        'tags'
    )
    _META_AUTO_FIELDS = (
        'expectation_id',
        'revision',
        'last_updated_by',
        'last_updated_at',
        'created_by',
        'created_at',
    )

    _DATETIME_FIELDS = (
        'last_updated_at',
        'created_at'
    )
    # revision for an expectation that was created manually
    _FIRST_REVISION = 1
    # revision for an expectation that was created elsewhere and loaded
    _LOADED_REVISION = 0

    def __init__(
        self,
        expectation: Union[dict, 'Expectation', 'ExpectationConfiguration', 'ExpectationValidationResult'],
        parent_suite: 'ExpectationSuite' = None,
        **meta_fields  # see _META_USER_FIELDS and _META_AUTO_FIELDS for what can be passed here.
    ):
        # validate meta_fields
        ra.validate_meta_fields(
            meta_fields=meta_fields,
            meta_user_fields=self._META_USER_FIELDS,
            meta_auto_fields=self._META_AUTO_FIELDS
        )

        # turn expectation into a dict
        # if it's a result, take config from it
        if hasattr(expectation, 'expectation_config'):
            expectation = expectation.expectation_config
        # get a dict from it
        if hasattr(expectation, 'to_json_dict'):
            expectation = expectation.to_json_dict()
        # we'll be changing the dict, so deepcopy it
        expectation = copy.deepcopy(expectation)
        # resolve param value vs. what's in meta.dq_tool - auto are private, deserialize
        self.meta = expectation.get('meta', {})

        # pop the whole thing under META_KEY - it's all ours, put it back in when needed in to_dict()
        # meta will be just what was in meta - no dq_tool stuff
        meta_dq_tool = self._json_deserialize_meta(self.meta.pop(self.META_KEY, {}))
        # serialize the params, surprisingly when doing ** for passing params the reference is kept there
        # so rather do a deepcopy
        meta_fields = self._json_deserialize_meta(copy.deepcopy(meta_fields))

        user_fields_tuples = list(zip(self._META_USER_FIELDS, itertools.repeat(False)))
        auto_fields_tuples = list(zip(self._META_AUTO_FIELDS, itertools.repeat(True)))

        for field_name, private_attr in user_fields_tuples + auto_fields_tuples:
            self._resolve_meta_value(
                meta_dq_tool=meta_dq_tool,
                param_name=field_name,
                param_value=meta_fields.get(field_name),
                private_attr=private_attr
            )

        # set kwargs, expectation_type and _parent_suite directly
        self.kwargs = expectation.get('kwargs', {})
        self.expectation_type = expectation['expectation_type']
        self._parent_suite = parent_suite

    def to_dict(self) -> dict:
        """Return the GE-friendly dict"""
        # if any of the fields are non-empty, add dq_tool section to meta, otherwise leave empty
        field_values = {
            field: getattr(self, field)
            for field in self._META_USER_FIELDS + self._META_AUTO_FIELDS
        }
        dq_tool_meta = {
            self.META_KEY: {
                **self._json_serialize_meta(field_values)
            }
        } if any(field_values.values()) else {}
        # deepcopy to loose the reference - so that when someone changes the exported dict, the object stays the same
        return copy.deepcopy({
            'expectation_type': self.expectation_type,
            'kwargs': self.kwargs,
            'meta': {
                **self.meta,
                **dq_tool_meta
            }
        })

    def to_json_dict(self) -> dict:
        """To have the same method as GE's ExpectationConfiguration"""
        return self.to_dict()

    @property
    def call_str(self):
        """Get a method call that define the expectations (with no meta)"""
        return '{}({})'.format(
            self.expectation_type,
            ', '.join('{}={}'.format(
                k, v.__repr__())
                for k, v in self.kwargs.items()
                # don't show the result_format: BASIC in the call str, adds no information
                if not(k == 'result_format' and v == 'BASIC')
            )
        )

    def __repr__(self) -> str:
        """Pretty printed expectation dict"""
        return pretty_repr(self.to_dict())

    def __str__(self) -> str:
        """Call string - easily readable and re-runable"""
        return self.call_str

    def _resolve_meta_value(
        self,
        meta_dq_tool: dict,
        param_name: str,
        param_value: Any,
        private_attr: bool = False
    ):
        """Set the self property to param_value (has precedence) or the corresponding value from meta."""
        meta_value = meta_dq_tool.get(param_name)
        value = param_value or meta_value
        # private attribute if it should be done so
        attr_name = (
            ra.get_private_attribute_name(param_name)
            if private_attr and not ra.is_private_attribute(param_name)
            else param_name
        )
        setattr(self, attr_name, value)

    def _init_revision(self):
        # pylint - no revision attribute when there's no versioning
        self._revision = self._FIRST_REVISION  # pylint: disable=W0201

    @classmethod
    def _process_meta(cls, meta: dict, fnc: Callable) -> dict:
        """Process meta (shallow), using the given function"""
        return {
            **meta,
            **{
                k: fnc(meta[k])
                for k in cls._DATETIME_FIELDS
                if k in meta
            }
        }

    @classmethod
    def _serialize_date(cls, d) -> str:
        """Turn the date into string"""
        return d.isoformat() if isinstance(d, datetime.datetime) else d

    @classmethod
    def _deserialize_date(cls, s) -> datetime.datetime:
        """Turn the string into date"""
        return datetime.datetime.fromisoformat(s) if isinstance(s, str) else s

    @classmethod
    def _json_serialize_meta(cls, meta: dict) -> dict:
        """Serialize datetime values into isoformat, keep unchanged for any other value"""
        return cls._process_meta(meta, cls._serialize_date)

    @classmethod
    def _json_deserialize_meta(cls, meta: dict) -> dict:
        """Deserialize datetime from iso string to datetime"""
        return cls._process_meta(meta, cls._deserialize_date)

    def _initialize_loaded(self, expectation_id: int):
        """Initialize an expectation that was loaded (created elsewhere)"""
        self._expectation_id = expectation_id  # pylint: disable=W0201
        self._revision = self._LOADED_REVISION  # pylint: disable=W0201

    def _bump_revision(
        self,
        user_identity_provider: 'UserIdentityProvider' = None,
        new_one: bool = False
    ):
        """Increase revision and sets all related fields - last_updated_by / at, created etc.
        Called when the expectation is added or updated."""
        editor = (
            user_identity_provider.get_current_user()
            if user_identity_provider
            else None
        )
        time_now = datetime.datetime.now().astimezone()
        # pylint doesn't recognize them, but these were already created in init
        self._last_updated_at = time_now  # pylint: disable=W0201
        self._last_updated_by = editor  # pylint: disable=W0201
        if new_one:
            self._init_revision()
            self._created_by = editor  # pylint: disable=W0201
            self._created_at = time_now  # pylint: disable=W0201
        else:
            self._revision += 1

    def _copy_auto_field_values_from(
        self,
        expectation: 'Expectation'
    ):
        """Copy attributes named in _META_AUTO_FIELDS to attributes in self.
        Useful when you get a new object and want to update an existing object,
        but the _created_at, _by etc. should stay
        """
        for attr_name in self._META_AUTO_FIELDS:
            setattr(
                self,
                ra.get_private_attribute_name(attr_name),
                getattr(expectation, attr_name)
            )
