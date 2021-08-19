from minutes.models import MinuteType
from rest_framework import serializers


class MinuteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinuteType
        fields = ("id", "name")
