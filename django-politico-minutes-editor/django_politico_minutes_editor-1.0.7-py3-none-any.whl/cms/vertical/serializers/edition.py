from minutes.models import Edition, Minute
from rest_framework import serializers
from .minutes import MinuteSerializer, EndMinuteSerializer
from minutes.cms.common.serializers import SponsorSerializer


class EditionSerializer(serializers.ModelSerializer):
    minutes = serializers.SerializerMethodField()
    end_minute = serializers.SerializerMethodField()
    sponsor = SponsorSerializer()

    def get_minutes(self, obj):
        minutes = obj.minutes.filter(type__is_meta=False)
        return MinuteSerializer(minutes, many=True).data

    def get_end_minute(self, obj):
        try:
            end_minute = obj.minutes.get(type__name="End Card")
        except Minute.DoesNotExist:
            return None

        return EndMinuteSerializer(end_minute).data

    class Meta:
        model = Edition
        fields = (
            "id",
            "live",
            "publish_datetime",
            "minutes",
            "end_minute",
            "sponsor",
        )
