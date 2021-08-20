from minutes.models import Minute
from rest_framework import serializers


class MinuteSerializer(serializers.ModelSerializer):
    editing_session = serializers.SerializerMethodField()

    def get_editing_session(self, obj):
        if obj.editing_session and obj.editing_session.count() > 0:
            return obj.editing_session.first().id
        else:
            return None

    class Meta:
        model = Minute
        fields = (
            "id",
            "handle",
            "slug",
            "type",
            "author",
            "edition",
            "last_published",
            "last_updated",
            "content",
            "version",
            "editing_session",
        )
