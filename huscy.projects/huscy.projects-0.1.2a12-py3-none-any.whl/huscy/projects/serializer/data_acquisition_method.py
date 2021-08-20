from rest_framework import serializers

from huscy.projects.models import DataAcquisitionMethod
from huscy.projects.services import add_data_acquisition_method


class DataAcquisitionMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAcquisitionMethod
        fields = (
            'id',
            'location',
            'order',
            'session',
            'type',
        )

    def create(self, validated_data):
        return add_data_acquisition_method(**validated_data)
