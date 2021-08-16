from rest_framework import serializers

from tenant_auth.models import AuthTenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthTenant
        # fields = '__all__'
        exclude = ("password",)
