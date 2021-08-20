from minutes.models import Vertical
from rest_framework import serializers


class VerticalSerializer(serializers.ModelSerializer):
    logos = serializers.SerializerMethodField()

    def get_logos(self, obj):
        return {
            "horizontal": obj.horizontal_logo,
            "vertical": obj.vertical_logo,
            "centered": obj.centered_logo,
        }

    class Meta:
        model = Vertical
        fields = ("id", "name", "slug", "intro", "logos")
