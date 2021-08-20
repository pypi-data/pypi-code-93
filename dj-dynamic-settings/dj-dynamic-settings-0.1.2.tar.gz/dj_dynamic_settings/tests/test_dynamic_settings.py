from django.test import TestCase

from dj_dynamic_settings.conf import settings
from dj_dynamic_settings.models import Setting
from dj_dynamic_settings.registry import registry
from dj_dynamic_settings.serializers import (
    DynamicSettingSerializer,
    RegistryItemSerializer,
)


class DynamicSettingsTestCase(TestCase):
    def setUp(self):
        from dj_dynamic_settings.tests import definitions

        # in order to register test settings

    def test_existing_and_active_setting(self):
        Setting.objects.create(
            key="X_FEATURE_ACTIVE",
            value=True,
            is_active=True,
        )
        self.assertTrue(settings.X_FEATURE_ACTIVE)

    def test_existing_and_inactive_setting(self):
        Setting.objects.create(
            key="X_FEATURE_ACTIVE",
            value=True,
            is_active=False,
        )
        with self.assertRaises(AttributeError):
            _ = settings.X_FEATURE_ACTIVE

    def test_default_setting(self):
        self.assertEqual(settings.Y_FEATURE_ACTIVE, True)

    def test_non_existing_setting(self):
        with self.assertRaises(AttributeError):
            _ = settings.NON_EXISTING_SETTING


class DynamicSettingsValidationTestCase(TestCase):
    def setUp(self):
        from dj_dynamic_settings.tests import definitions

        # in order to register test settings
        self.serializer_class = DynamicSettingSerializer

    def test_type_validated_setting(self):
        data = {
            "key": "X_FEATURE_ACTIVE",
            "value": 1,
            "is_active": True,
        }
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())

        data["value"] = True
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())

        data = {
            "key": "X_TRIAL_COUNT",
            "value": "abc",
            "is_active": True,
        }
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())

        data["value"] = 1
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())

    def test_module_path_validated_setting(self):
        data = {
            "key": "X_SERVICE_CLASS",
            "value": "django.test.TestCase",
            "is_active": True,
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())

        data["value"] = "invalid.module.path"
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())

    def test_serializer_validated_setting(self):
        data = {
            "key": "X_FEATURE_CONFIGURATION",
            "value": {"value_a": True, "value_b": 1.2},
            "is_active": True,
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())

        data["value"] = {"value_a": "abc", "value_b": "cde"}
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())

        data = {
            "key": "X_FEATURE_RULES",
            "value": [
                {"value_c": True, "value_d": 6.1, "value_e": "django.db.models"},
                {
                    "value_c": False,
                    "value_d": 4.9,
                    "value_e": "django.core.validators.RegexValidator",
                },
            ],
            "is_active": True,
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())

    def test_datetime_validated_setting(self):
        data = {
            "key": "X_DATETIME_CONFIGURATION",
            "value": "01/04/2017",
            "is_active": True,
        }
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())

        data["value"] = "01-04-2017"

        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validator_details(self):
        items = [registry[key] for key in registry.keys()]
        serializer = RegistryItemSerializer(items, many=True)
        data = serializer.data
        self.assertGreater(len(data), 0)
        for item in data:
            self.assertTrue(item.get("validators"))
