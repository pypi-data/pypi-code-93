from minutes.models import Sponsor
from rest_framework import serializers


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = ("id", "name", "logo", "last_updated", "sponsored_text")
