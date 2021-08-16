from rest_framework import serializers
from .models import ExampleModel


class ExmapleReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = '__all__'
        execlude = ['id']


class ExampleResSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = '__all__'
