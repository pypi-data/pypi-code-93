from model_bakery import baker

from huscy.projects.serializer import MembershipSerializer
from huscy.projects.services import add_member


def test_project_serializer(django_user_model, project):
    user = baker.make(django_user_model, first_name='first_name', last_name='last_name')
    membership = add_member(project, user, is_coordinator=True)

    expected = {
        'id': membership.id,
        'is_coordinator': True,
        'has_write_permission': True,
        'project': project.id,
        'user': membership.user.pk,
        'username': 'first_name last_name',
    }

    assert expected == MembershipSerializer(instance=membership).data
