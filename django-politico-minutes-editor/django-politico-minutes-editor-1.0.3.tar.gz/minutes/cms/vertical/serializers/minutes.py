from minutes.models import Minute
from rest_framework import serializers


class MinuteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Minute
        fields = ("handle", "id", "edition_sort")


class EndMinuteSerializer(serializers.ModelSerializer):
    tease = serializers.SerializerMethodField()

    def get_tease(self, obj):
        if obj.content is not None:
            return obj.content.get("tease", "")
        return ""

    class Meta:
        model = Minute
        fields = ("handle", "id", "tease", "edition_sort")
