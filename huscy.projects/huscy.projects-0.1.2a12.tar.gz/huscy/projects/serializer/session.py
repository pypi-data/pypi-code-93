from rest_framework import serializers

from huscy.projects.models import Session
from huscy.projects.serializer import DataAcquisitionMethodSerializer
from huscy.projects.services import create_session


class SessionSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = Session
        fields = (
            'duration',
            'experiment',
            'id',
            'operator',
            'order',
            'title',
        )

    def create(self, validated_data):
        return create_session(**validated_data)

    def to_representation(self, session):
        response = super().to_representation(session)
        response['data_acquisition_methods'] = \
            DataAcquisitionMethodSerializer(session.dataacquisitionmethod_set.all(), many=True).data
        return response
