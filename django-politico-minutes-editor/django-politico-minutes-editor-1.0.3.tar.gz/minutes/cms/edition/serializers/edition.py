from minutes.models import Edition
from rest_framework import serializers
from .minute import MinuteSerializer
from .interstitial_instance import InterstitialInstanceSerializer
from minutes.cms.common.serializers.sponsor import SponsorSerializer


class EditionSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()
    should_publish = serializers.SerializerMethodField()
    sponsor = SponsorSerializer()

    def get_cards(self, obj):
        minutes = self.get_minutes(obj)
        interstitials = self.get_interstitials(obj)

        cards = minutes + interstitials
        return cards

    def get_minutes(self, obj):
        minutes = obj.minutes.filter(type__is_meta=False)
        return MinuteSerializer(minutes, many=True).data

    def get_interstitials(self, obj):
        interstitials = obj.interstitials.all()
        return InterstitialInstanceSerializer(interstitials, many=True).data

    def get_meta(self, obj):
        minutes = obj.minutes.filter(type__is_meta=True)
        return MinuteSerializer(minutes, many=True).data

    def get_should_publish(self, obj):
        return obj.should_publish()

    class Meta:
        model = Edition
        fields = (
            "id",
            "theme",
            "vertical",
            "live",
            "should_publish",
            "publish_datetime",
            "last_updated",
            "sponsor",
            "cards",
            "meta",
            "preview_link",
            "production_link",
        )


class EditionContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = ("id", "theme", "vertical", "live", "publish_datetime")
