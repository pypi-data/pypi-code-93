from minutes.models import Sponsor
from .native_ad import NativeAdLiteSerializer
from rest_framework import serializers


class SponsorSerializer(serializers.ModelSerializer):
    ads = serializers.SerializerMethodField()

    def get_ads(self, obj):
        ads = obj.ads.all()
        return NativeAdLiteSerializer(ads, many=True).data

    class Meta:
        model = Sponsor
        fields = (
            "id",
            "name",
            "logo",
            "last_updated",
            "sponsored_text",
            "ads"
        )
