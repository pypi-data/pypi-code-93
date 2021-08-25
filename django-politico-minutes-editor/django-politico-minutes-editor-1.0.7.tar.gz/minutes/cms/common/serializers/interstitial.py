from minutes.models import Interstitial
from rest_framework import serializers


class InterstitialSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_type(self, obj):
        return obj.type.name

    def get_content(self, obj):
        if obj.type.context:
            return {**obj.type.context, **obj.content}
        else:
            return obj.content

    class Meta:
        model = Interstitial
        fields = ("id", "name", "type", "content", "favorite")
