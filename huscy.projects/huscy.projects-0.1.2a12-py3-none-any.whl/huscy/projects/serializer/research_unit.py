from rest_framework import serializers

from huscy.projects.models import ResearchUnit


class ResearchUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchUnit
        fields = (
            'code',
            'id',
            'name',
            'principal_investigator',
        )
