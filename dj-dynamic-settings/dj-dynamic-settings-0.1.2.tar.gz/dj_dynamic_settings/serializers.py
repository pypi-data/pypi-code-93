from rest_framework import serializers

from dj_dynamic_settings.models import Setting
from dj_dynamic_settings.registry import Unset, registry


class DynamicSettingSerializer(serializers.ModelSerializer):
    default = serializers.SerializerMethodField(method_name="get_default_")
    description = serializers.SerializerMethodField()

    def get_default_(self, instance):
        setting = registry[instance.key]
        default = setting.default
        if default is Unset:
            default = default.__name__
        return default

    def get_description(self, instance):
        setting = registry[instance.key]
        return setting.description

    def validate(self, attrs):
        if self.instance:
            key = attrs.get("key", self.instance.key)
            value = attrs.get("value", self.instance.value)
        else:
            key = attrs["key"]
            value = attrs["value"]
        validators = registry[key].validators
        for validator in validators:
            validator(value)
        return attrs

    class Meta:
        model = Setting
        fields = [
            "pk",
            "key",
            "value",
            "default",
            "is_active",
            "description",
            "created_date",
            "modified_date",
        ]
        extra_kwargs = {
            "created_date": {"read_only": True},
            "modified_date": {"read_only": True},
        }


class RegistryItemSerializer(serializers.Serializer):
    key = serializers.CharField()
    description = serializers.CharField()
    default = serializers.SerializerMethodField(method_name="get_default_")
    validators = serializers.SerializerMethodField(method_name="get_validators_")

    def get_default_(self, instance):  # noqa
        default = instance.default
        if default is Unset:
            default = default.__name__
        return default

    def get_validators_(self, instance):  # noqa
        return [
            validator.detail
            for validator in instance.validators
            if hasattr(validator, "detail")
        ]
