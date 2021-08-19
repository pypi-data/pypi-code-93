from minutes.models import Edition, Vertical
from rest_framework import serializers
from .minute import MinuteSerializer
from .sponsor import SponsorSerializer
from .vertical import VerticalSerializer
from .interstitial_instance import InterstitialInstanceSerializer


class EditionBaseSerializer(serializers.ModelSerializer):
    def get_is_latest_live(self, obj):
        return obj == Edition.objects.latest_live(obj.vertical)

    def get_byline(self, obj):
        all_bylines = [
            {
                "id": minute.author.id,
                "name": "{} {}".format(
                    minute.author.user.first_name, minute.author.user.last_name
                ),
                "link": minute.author.bio_link,
            }
            for minute in obj.minutes.all()
        ]

        unique_bylines = list({v["id"]: v for v in all_bylines}.values())

        return unique_bylines


class EditionListSerializer(EditionBaseSerializer):
    is_latest_live = serializers.SerializerMethodField()
    byline = serializers.SerializerMethodField()
    minutes = serializers.SerializerMethodField()

    def get_minutes(self, obj):
        minutes = obj.minutes.filter(type__is_meta=False)
        return [minute.handle for minute in minutes]

    class Meta:
        model = Edition
        fields = (
            "id",
            "is_latest_live",
            "live",
            "publish_datetime",
            "byline",
            "minutes",
        )


class VerticalEditionsSerializer(serializers.ModelSerializer):
    live_editions = serializers.SerializerMethodField()
    logos = serializers.SerializerMethodField()

    def get_logos(self, obj):
        return {
            "horizontal": obj.horizontal_logo,
            "vertical": obj.vertical_logo,
            "centered": obj.centered_logo,
        }

    def get_live_editions(self, obj):
        e = obj.editions.filter(live=True)
        return EditionListSerializer(e, many=True).data

    class Meta:
        model = Vertical
        fields = ("id", "name", "slug", "logos", "live_editions")


class EditionSerializer(EditionBaseSerializer):
    cards = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()
    is_latest_live = serializers.SerializerMethodField()
    byline = serializers.SerializerMethodField()
    sponsor = SponsorSerializer()
    vertical = VerticalSerializer()

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

    class Meta:
        model = Edition
        fields = (
            "id",
            "theme",
            "vertical",
            "is_latest_live",
            "live",
            "publish_datetime",
            "byline",
            "sponsor",
            "cards",
            "meta",
        )
