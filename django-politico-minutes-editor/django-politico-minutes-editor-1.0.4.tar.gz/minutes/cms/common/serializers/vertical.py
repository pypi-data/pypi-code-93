from minutes.models import Vertical
from rest_framework import serializers


class VerticalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertical
        fields = "__all__"
