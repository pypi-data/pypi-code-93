import logging

from rest_framework import serializers

from huscy.projects.helpers import get_client_ip
from huscy.projects.models import Project
from huscy.projects.services import create_project

logger = logging.getLogger('projects')


class ProjectSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    participating = serializers.SerializerMethodField()
    principal_investigator_name = serializers.SerializerMethodField()
    research_unit_name = serializers.SerializerMethodField()

    # default=None is used as required=False does not work together with the unique_together
    # constraint, however this defaut=None is a workaround, see:
    # https://github.com/encode/django-rest-framework/issues/4456
    local_id = serializers.IntegerField(min_value=1, default=None)

    class Meta:
        model = Project
        fields = (
            'creator',
            'description',
            'id',
            'local_id',
            'local_id_name',
            'participating',
            'principal_investigator',
            'principal_investigator_name',
            'research_unit',
            'research_unit_name',
            'title',
        )

    def get_participating(self, project):
        user = self.context['request'].user
        return (project.principal_investigator == user or
                user.pk in project.membership_set.values_list('user', flat=True))

    def get_principal_investigator_name(self, project):
        return project.principal_investigator.get_full_name()

    def get_research_unit_name(self, project):
        return project.research_unit.name

    def create(self, validated_data):
        request = self.context.get('request')
        logger.info('User %s from IP %s requested creation of new project',
                    request.user.username, get_client_ip(request))
        return create_project(**validated_data)
