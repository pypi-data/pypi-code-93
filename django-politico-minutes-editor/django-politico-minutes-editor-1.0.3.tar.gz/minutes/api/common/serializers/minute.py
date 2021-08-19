from minutes.models import Minute
from rest_framework import serializers


class MinuteSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    context = serializers.SerializerMethodField()

    def get_model(self, obj):
        return "Minute"

    def get_type(self, obj):
        return obj.type.name

    def get_context(self, obj):
        return obj.type.context

    class Meta:
        model = Minute
        fields = (
            "model",
            "slug",
            "handle",
            "id",
            "type",
            "edition_sort",
            "content",
            "context",
        )
