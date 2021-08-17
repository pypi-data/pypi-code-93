from rest_framework import serializers

from tenant_auth.models import AuthTenant, AuthIoT


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthTenant
        # fields = '__all__'
        exclude = ("password",)



class IoTSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthIoT
        # fields = '__all__'
        exclude = ("password",)
