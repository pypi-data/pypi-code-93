from rest_framework import serializers

from lab_orchestrator_lib_django_adapter.models import LabModel, LabInstanceModel, DockerImageModel


class DockerImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockerImageModel
        fields = '__all__'


class LabModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabModel
        fields = '__all__'


class LabInstanceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabInstanceModel
        fields = '__all__'


class LabInstanceKubernetesSerializer(serializers.Serializer):
    lab_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    jwt_token = serializers.CharField()
