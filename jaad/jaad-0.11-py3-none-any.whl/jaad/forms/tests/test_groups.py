from django.test import SimpleTestCase

from jaad.forms.groups import validate_group_of_field

FIELD1 = "FIELD1"
FIELD2 = "FIELD2"
FIELD3 = "FIELD3"
FIELD4 = "FIELD4"
SOME_GROUP = [[FIELD3], [FIELD4]]
SOME_COMPLEX_GROUP = [[FIELD2], [FIELD3, FIELD4]]
FULL_DATA = {FIELD1: "DATA1", FIELD2: "DATA2", FIELD3: "DATA3", FIELD4: "DATA4"}
SOME_DATA_FOR_THIS_GROUP = {FIELD3: "DATA3", FIELD4: "DATA4"}
SOME_DATA_FOR_THIS_GROUP_WITH_NONE = {FIELD3: None, FIELD4: "DATA4"}
SOME_DATA_FOR_THIS_GROUP_WITH_OTHER_STUFF = {
    FIELD1: "DATA2",
    FIELD3: "DATA3",
    FIELD4: "DATA4",
}
NO_DATA = {}
PARTIAL_DATA = {FIELD4: "DATA4"}

MORE_THAN_ONE_GROUP_DEFINED_ERRORS = {
    FIELD3: [
        "At most one of those fields or groups of fields can be defined: '{}', '{}'".format(
            FIELD3, FIELD4
        )
    ],
    FIELD4: [
        "At most one of those fields or groups of fields can be defined: '{}', '{}'".format(
            FIELD3, FIELD4
        )
    ],
}

LESS_THAN_TWO_GROUPS_DEFINED_ERRORS = {
    FIELD3: [
        "At least 2 of those fields or groups of fields must be defined: '{}', '{}'".format(
            FIELD3, FIELD4
        )
    ],
    FIELD4: [
        "At least 2 of those fields or groups of fields must be defined: '{}', '{}'".format(
            FIELD3, FIELD4
        )
    ],
}

LESS_THAN_TWO_GROUPS_DEFINED_ERRORS_FOR_COMPLEX_GROUPS_ERROR_MESSAGE = (
    "At least 2 of those fields or groups of fields must be defined: "
    "'{}', [{}' and '{}]".format(FIELD2, FIELD3, FIELD4)
)

LESS_THAN_TWO_GROUPS_DEFINED_ERRORS_FOR_COMPLEX_GROUPS = {
    FIELD2: [LESS_THAN_TWO_GROUPS_DEFINED_ERRORS_FOR_COMPLEX_GROUPS_ERROR_MESSAGE],
    FIELD3: [LESS_THAN_TWO_GROUPS_DEFINED_ERRORS_FOR_COMPLEX_GROUPS_ERROR_MESSAGE],
    FIELD4: [LESS_THAN_TWO_GROUPS_DEFINED_ERRORS_FOR_COMPLEX_GROUPS_ERROR_MESSAGE],
}


class GroupsTests(SimpleTestCase):
    """Test fields.py"""

    def test_validate_group_of_field_should_return_empty_dict_when_no_errors(self):
        errors = validate_group_of_field(
            SOME_GROUP, SOME_DATA_FOR_THIS_GROUP, min_defined=2, max_defined=2
        )
        self.assertEqual(errors, {})

    def test_validate_group_of_field_should_ignore_none_values(self):
        errors = validate_group_of_field(
            SOME_GROUP, SOME_DATA_FOR_THIS_GROUP_WITH_NONE, min_defined=1, max_defined=1
        )
        self.assertEqual(errors, {})

    def test_validate_group_of_field_should_ignore_other_keys(self):
        errors = validate_group_of_field(
            SOME_GROUP, FULL_DATA, min_defined=2, max_defined=2
        )
        self.assertEqual(errors, {})

    def test_validate_group_of_field_should_returns_errors_if_too_many_groups_are_defined(
        self,
    ):
        errors = validate_group_of_field(
            SOME_GROUP, SOME_DATA_FOR_THIS_GROUP, max_defined=1
        )
        self.assertEqual(errors, MORE_THAN_ONE_GROUP_DEFINED_ERRORS)

    def test_validate_group_of_field_should_returns_errors_if_too_few_groups_are_defined(
        self,
    ):
        errors = validate_group_of_field(SOME_GROUP, PARTIAL_DATA, min_defined=2)
        self.assertEqual(errors, LESS_THAN_TWO_GROUPS_DEFINED_ERRORS)

    def test_validate_group_of_field_should_returns_errors_if_no_groups_are_defined_are_min_is_not_zero(
        self,
    ):
        errors = validate_group_of_field(SOME_GROUP, PARTIAL_DATA, min_defined=2)
        self.assertEqual(errors, LESS_THAN_TWO_GROUPS_DEFINED_ERRORS)

    def test_validate_group_of_field_should_handle_sub_groups_whn_data_is_correct(self):
        errors = validate_group_of_field(SOME_COMPLEX_GROUP, FULL_DATA, min_defined=2)
        self.assertEqual(errors, {})

    def test_validate_group_of_field_should_handle_sub_groups_whn_data_is_incorrect(
        self,
    ):
        errors = validate_group_of_field(
            SOME_COMPLEX_GROUP, PARTIAL_DATA, min_defined=2
        )
        self.assertEqual(errors, LESS_THAN_TWO_GROUPS_DEFINED_ERRORS_FOR_COMPLEX_GROUPS)
