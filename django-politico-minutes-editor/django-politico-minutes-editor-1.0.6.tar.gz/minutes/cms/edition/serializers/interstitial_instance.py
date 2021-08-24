from rest_framework import serializers
from minutes.models import InterstitialInstance
from minutes.cms.common.serializers import InterstitialSerializer


class InterstitialInstanceSerializer(serializers.ModelSerializer):
    interstitial_data = None
    model = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_interstitial(self, obj):
        if not hasattr(self, "cached") or self.cached != obj.interstitial.id:
            data = obj.interstitial
            self.interstitial_data = InterstitialSerializer(data).data
            self.cached = obj.interstitial.id

    def get_model(self, obj):
        return "Interstitial"

    def get_type(self, obj):
        self.get_interstitial(obj)
        return self.interstitial_data["type"]

    def get_name(self, obj):
        self.get_interstitial(obj)
        return self.interstitial_data["name"]

    def get_content(self, obj):
        self.get_interstitial(obj)
        return self.interstitial_data["content"]

    class Meta:
        model = InterstitialInstance
        fields = ("model", "id", "type", "edition_sort", "name", "content")
