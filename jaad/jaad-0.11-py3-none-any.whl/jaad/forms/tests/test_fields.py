from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import SimpleTestCase

from jaad.forms import fields

HELP_TEXT = "Help text"
SOME_STRING = "SOME_STRING"
SOME_STRING_1 = "SOME_STRING_1"
SOME_STRING_2 = "SOME_STRING_2"
SOME_STRING_3 = "SOME_STRING_3"
SOME_STRING_4 = "SOME_STRING_4"
UNKNOWN_STRING = "UNKNOWN_STRING"
LIST_OF_DECIMALS = [1.0, 3, 5.0]
LIST_OF_DECIMALS_AS_CSV_STRING = "1.0,3,5.0"
LIST_OF_STRINGS = [SOME_STRING_1, SOME_STRING_2, SOME_STRING_3]
SOME_RANGE_AS_STRING = "8-17"
SOME_BAD_RANGE_AS_STRING = "17-8"
SOME_BAD_RANGE_LOWER_BOUNDARY_AS_STRING = "17"
SOME_BAD_RANGE_UPPER_BOUNDARY_AS_STRING = "8"
SOME_RANGE = {"start": 8, "stop": 17}
SINGLETON_RANGE_AS_STRING = "40-40"
SINGLETON_RANGE = {"start": 40, "stop": 40}


class FieldsTests(SimpleTestCase):
    """Test fields.py"""

    def test_set_default_value_should_set_default_value(self):
        test_field = forms.Field()
        fields.set_field_default_value(test_field, HELP_TEXT)
        self.assertEqual(test_field.default_value, HELP_TEXT)

    def test_set_default_value_should_update_help_text(self):
        test_field = forms.Field(help_text=HELP_TEXT)
        self.assertEqual(test_field.help_text, HELP_TEXT)
        fields.set_field_default_value(test_field, SOME_STRING)
        self.assertEqual(
            test_field.help_text,
            f"{HELP_TEXT} <br />\n*Default to `{SOME_STRING}`.*",
        )

    def test_has_help_text_should_be_True_if_help_text(self):
        test_field = forms.Field(help_text=HELP_TEXT)
        self.assertTrue(fields.has_help_text(test_field))

    def test_has_help_text_should_return_False_if_no_help_text(self):
        test_field = forms.Field()
        self.assertFalse(fields.has_help_text(test_field))

    def test_ChoiceField_help_text_should_be_as_defined(self):
        test_choice_field = fields.ChoiceField(
            choices=(("c1", "choice1"), ("c2", "choice2"))
        )
        help_text_should_be = "Can be `c1` (choice1) or `c2` (choice2)."
        self.assertEqual(help_text_should_be, test_choice_field.help_text)

    def test_CommaSeparatedDecimalField_help_text_should_be_explicit(self):
        test_choice_field = fields.CommaSeparatedDecimalField()
        help_text_should_be = "Comma separated values. Each value must be a float"
        self.assertEqual(help_text_should_be, test_choice_field.help_text)

    def test_CommaSeparatedDecimalField_help_text_should_contains_boundaries_if_defined(
        self,
    ):
        test_choice_field = fields.CommaSeparatedDecimalField(
            sub_fields_args={"min_value": 1.0, "max_value": 30.0}
        )
        help_text_should_be = (
            "Comma separated values. Each value must be a float " "between 1.0 and 30.0"
        )
        self.assertEqual(help_text_should_be, test_choice_field.help_text)

    def test_DateField_help(self):
        test_date_field = fields.DateField(input_formats=["%Y-%m-%d"])
        help_text_should_be = "Date (`YYYY-MM-DD`).\n<br />"
        self.assertEqual(help_text_should_be, test_date_field.help_text)

    def test_CommaSeparatedCharField_should_display_CSV_value(self):
        field = fields.CommaSeparatedCharField()
        values_to_display = field.bound_data(LIST_OF_STRINGS, None)
        self.assertEqual(values_to_display, ",".join(LIST_OF_STRINGS))

    def test_CommaSeparatedCharField_should_parse_CSV_value_as_a_list_of_string(self):
        field = fields.CommaSeparatedCharField()
        parsed_values = field.to_python(",".join(LIST_OF_STRINGS))
        self.assertEqual(parsed_values, LIST_OF_STRINGS)

    def test_CommaSeparatedCharField_should_handle_none_value(self):
        field = fields.CommaSeparatedCharField()
        parsed_values = field.to_python(None)
        self.assertEqual(parsed_values, None)

    def test_CommaSeparatedDecimalField_should_parse_CSV_value_as_a_list_of_decimals(
        self,
    ):
        field = fields.CommaSeparatedDecimalField()
        parsed_values = field.to_python(LIST_OF_DECIMALS_AS_CSV_STRING)
        self.assertEqual(parsed_values, LIST_OF_DECIMALS)

    def test_CommaSeparatedChoiceField_should_handle_one_of_the_defined_choice(self):
        class SomeForm(forms.Form):
            my_field = fields.CommaSeparatedChoiceField(
                sub_fields_args={
                    "choices": [
                        (SOME_STRING_1, SOME_STRING_2),
                        (SOME_STRING_3, SOME_STRING_4),
                    ]
                }
            )

        form = SomeForm({"my_field": f"{SOME_STRING_1},{SOME_STRING_3}"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean()["my_field"], [SOME_STRING_1, SOME_STRING_3])

    def test_CommaSeparatedChoiceField_should_not_be_valid_with_unknown_value(self):
        class SomeForm(forms.Form):
            my_field = fields.CommaSeparatedChoiceField(
                sub_fields_args={
                    "choices": [
                        (SOME_STRING_1, SOME_STRING_2),
                        (SOME_STRING_3, SOME_STRING_4),
                    ]
                }
            )

        form = SomeForm({"my_field": f"{SOME_STRING_1},{UNKNOWN_STRING}"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            {field: list(errors) for field, errors in form.errors.items()},
            {
                "my_field": [
                    "Error while validating one of the comma-separated value: "
                    "Select a valid choice. "
                    "{} is not one of the available choices.".format(UNKNOWN_STRING)
                ]
            },
        )

    def test_NullableCharField_should_support_none(self):
        field = fields.NullableCharField()
        value = None
        parsed_value = field.to_python(value)
        self.assertEqual(parsed_value, None)

    def test_NullableCharField_should_support_any_string(self):
        field = fields.NullableCharField()
        value = SOME_STRING
        parsed_value = field.to_python(value)
        self.assertEqual(parsed_value, SOME_STRING)

    def test_IntegerRangeField_should_support_any_range(self):
        field = fields.IntegerRangeField()
        value = SOME_RANGE_AS_STRING
        parsed_value = field.to_python(value)
        self.assertEqual(parsed_value, SOME_RANGE)

    def test_IntegerRangeField_should_support_singleton_as_range(self):
        field = fields.IntegerRangeField()
        value = SINGLETON_RANGE_AS_STRING
        parsed_value = field.to_python(value)
        self.assertEqual(parsed_value, SINGLETON_RANGE)

    def test_IntegerRangeField_should_throw_when_upper_boundary_is_lower_than_lower_boundary(
        self,
    ):
        field = fields.IntegerRangeField()
        value = SOME_BAD_RANGE_AS_STRING
        with self.assertRaises(DjangoValidationError) as cm:
            field.to_python(value)
        the_exception = cm.exception

        self.assertEqual(
            the_exception.messages,
            [
                "Bad interval: {} is lower than {} in {}".format(
                    SOME_BAD_RANGE_UPPER_BOUNDARY_AS_STRING,
                    SOME_BAD_RANGE_LOWER_BOUNDARY_AS_STRING,
                    SOME_BAD_RANGE_AS_STRING,
                )
            ],
        )
