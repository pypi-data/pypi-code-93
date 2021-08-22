from rest_framework import serializers
from .models import ApiStatSpr

class ApiStatSprSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApiStatSpr
        fields = ['id', 'shortName', 'title', 'sql']




