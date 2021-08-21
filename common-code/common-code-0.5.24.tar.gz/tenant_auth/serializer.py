from rest_framework import serializers

from tenant_auth.models import Tenant, IoT


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        # fields = '__all__'
        exclude = ("password",)


class IoTSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoT
        # fields = '__all__'
        exclude = ("password",)
