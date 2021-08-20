from rest_framework import serializers


class PointSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()


class MoveSerializer(serializers.Serializer):
    type = serializers.CharField()
    index = serializers.IntegerField()
    current = PointSerializer()
    to = PointSerializer()
    build = PointSerializer()
