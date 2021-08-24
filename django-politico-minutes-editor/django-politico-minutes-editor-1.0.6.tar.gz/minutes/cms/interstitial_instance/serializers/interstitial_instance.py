from minutes.models import InterstitialInstance
from rest_framework import serializers


class InterstitialInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterstitialInstance
        fields = ("id", "edition_sort", "interstitial", "edition")
