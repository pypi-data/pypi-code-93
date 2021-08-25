from minutes.models import InterstitialType
from rest_framework import serializers


class InterstitialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterstitialType
        fields = "__all__"
