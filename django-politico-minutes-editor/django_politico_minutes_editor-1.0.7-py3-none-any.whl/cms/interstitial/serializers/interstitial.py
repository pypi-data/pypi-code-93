from minutes.models import Interstitial
from rest_framework import serializers


class InterstitialSerializer(serializers.ModelSerializer):
    editing_session = serializers.SerializerMethodField()

    def get_editing_session(self, obj):
        if obj.editing_session and obj.editing_session.count() > 0:
            return obj.editing_session.first().id
        else:
            return None

    class Meta:
        model = Interstitial
        fields = (
            "id",
            "type",
            "name",
            "content",
            "version",
            "editing_session",
        )


class InterstitialListSerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField()

    def get_type_name(self, obj):
        return str(obj.type)

    class Meta:
        model = Interstitial
        fields = ("id", "name", "favorite", "type", "type_name")
