from rest_framework import serializers

from huscy.projects.models import Membership
from huscy.projects.services import add_member, update_membership


class MembershipSerializer(serializers.ModelSerializer):
    has_write_permission = serializers.BooleanField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = (
            'id',
            'has_write_permission',
            'is_coordinator',
            'project',
            'user',
            'username',
        )
        read_only_fields = 'project',

    def get_username(self, membership):
        return membership.user.get_full_name()

    def create(self, validated_data):
        project = self.context['project']
        return add_member(project=project, **validated_data)

    def update(self, membership, validated_data):
        return update_membership(membership, validated_data.get('is_coordinator'),
                                 validated_data.get('has_write_permission'))
