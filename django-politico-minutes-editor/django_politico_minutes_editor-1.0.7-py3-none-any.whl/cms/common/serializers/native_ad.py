from minutes.models import NativeAd
from rest_framework import serializers


class NativeAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = NativeAd
        fields = (
            "id",
            "handle",
            "sponsor",
            "lede",
            "image",
            "body",
            "campaign_title",
            "campaign_link",
            "pixels"
        )


class NativeAdLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NativeAd
        fields = (
            "id",
            "handle",
        )
