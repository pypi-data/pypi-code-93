from rest_framework import serializers

from dj_dynamic_settings.registry import BaseSetting, registry
from dj_dynamic_settings.validators import (
    DateTimeValidator,
    ModulePathValidator,
    SerializerValidator,
    TypeValidator,
)


class FeatureConfigurationSerializer(serializers.Serializer):
    value_a = serializers.BooleanField()
    value_b = serializers.FloatField()


class FeatureRuleSerializer(serializers.Serializer):
    value_c = serializers.BooleanField()
    value_d = serializers.FloatField()
    value_e = serializers.CharField(validators=[ModulePathValidator()])


@registry.register
class FeatureActive(BaseSetting):
    key = "X_FEATURE_ACTIVE"
    validators = [TypeValidator(bool)]


@registry.register
class DefaultFeatureActive(BaseSetting):
    key = "Y_FEATURE_ACTIVE"
    validators = [TypeValidator(bool)]
    default = True


@registry.register
class TrialCount(BaseSetting):
    key = "X_TRIAL_COUNT"
    validators = [TypeValidator(int)]


@registry.register
class ServiceClass(BaseSetting):
    key = "X_SERVICE_CLASS"
    validators = [ModulePathValidator()]


@registry.register
class FeatureConfiguration(BaseSetting):
    key = "X_FEATURE_CONFIGURATION"
    validators = [SerializerValidator(FeatureConfigurationSerializer)]


@registry.register
class FeatureRulesConfiguration(BaseSetting):
    key = "X_FEATURE_RULES"
    validators = [
        SerializerValidator(FeatureRuleSerializer, serializer_kwargs={"many": True})
    ]


@registry.register
class FeatureConfigurationWithDefaultValue(BaseSetting):
    key = "X_FEATURE_CONFIGURATION_WITH_DEFAULT_VALUE"
    validators = [TypeValidator(str)]
    default = "default_value"


@registry.register
class FeatureDateTimeConfiguration(BaseSetting):
    key = "X_DATETIME_CONFIGURATION"
    validators = [DateTimeValidator("%d-%m-%Y")]
