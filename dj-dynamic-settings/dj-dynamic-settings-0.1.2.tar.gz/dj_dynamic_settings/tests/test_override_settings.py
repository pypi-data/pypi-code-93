from django.test import TestCase

from dj_dynamic_settings.conf import settings
from dj_dynamic_settings.registry import Unset, registry
from dj_dynamic_settings.utils import override_settings


class OverrideSettingsTestCase(TestCase):
    def setUp(self):
        from dj_dynamic_settings.tests import definitions  # NoQA

        # in order to register test settings

    def test_setting_default_value(self):
        self.assertIsNotNone(settings.X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE)
        self.assertNotEqual(settings.X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE, Unset)

    def test_setting_with_statement(self):
        default_value = settings.X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE
        new_value = "override_settings"

        with override_settings(X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE=new_value):
            self.assertEqual(
                settings.X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE, new_value
            )

        self.assertEqual(
            settings.X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE, default_value
        )

    @override_settings(X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE="override_settings")
    def test_setting_with_decoration(self):
        self.assertEqual(
            settings.X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE, "override_settings"
        )

    def test_setting_without_default_value(self):
        with self.assertRaises(AttributeError):
            settings.X_TRIAL_COUNT

        self.assertTrue("X_TRIAL_COUNT" in registry)

        with override_settings(X_TRIAL_COUNT=3):
            self.assertEqual(3, settings.X_TRIAL_COUNT)


@override_settings(X_TRIAL_COUNT=3)
class OverrideSettingsWithDecoratorTestCase(TestCase):
    def setUp(self):
        from dj_dynamic_settings.tests import definitions  # NoQA

        # in order to register test settings

    def test_decorator(self):
        self.assertEqual(settings.X_TRIAL_COUNT, 3)

    def test_decorator_with_nested(self):
        with override_settings(X_TRIAL_COUNT=4, X_FEATURE_ACTIVE=True):
            with override_settings(X_TRIAL_COUNT=5):
                self.assertEqual(settings.X_TRIAL_COUNT, 5)
                self.assertTrue(settings.X_FEATURE_ACTIVE)

            self.assertEqual(settings.X_TRIAL_COUNT, 4)
            self.assertTrue(settings.X_FEATURE_ACTIVE)

        self.assertEqual(settings.X_TRIAL_COUNT, 3)
