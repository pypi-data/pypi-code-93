from minutes.models import Theme
from rest_framework import serializers


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"
