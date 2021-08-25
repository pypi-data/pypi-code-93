from minutes.models import NativeAd
from rest_framework import serializers

PIXEL_DELIMETER = '>|<'


class NativeAdSerializer(serializers.ModelSerializer):
    pixels = serializers.SerializerMethodField()

    def get_pixels(self, obj):
        pixel_list = obj.pixels.split(PIXEL_DELIMETER)
        return pixel_list

    class Meta:
        model = NativeAd
        fields = (
            "id",
            "handle",
            "sponsor",
            "lede",
            "body",
            "image",
            "campaign_title",
            "campaign_link",
            "pixels"
        )
