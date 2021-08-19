from minutes.models import EditingSession
from rest_framework import serializers


class EditingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditingSession
        fields = "__all__"
