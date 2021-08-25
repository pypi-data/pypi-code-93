from minutes.models import Minute
from rest_framework import serializers


class MinuteSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_model(self, obj):
        return "Minute"

    def get_type(self, obj):
        return obj.type.name

    class Meta:
        model = Minute
        fields = (
            "model",
            "handle",
            "id",
            "type",
            "edition_sort",
            "content",
            "production_link",
            "last_published",
            "ready_to_publish"
        )
