import pytest
from model_bakery import baker

from rest_framework.test import APIClient


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='user', password='password',
                                                 first_name='Dennis', last_name='Ball')


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.login(username=admin_user.username, password='password')
    return client


@pytest.fixture
def client(user):
    client = APIClient()
    client.login(username=user.username, password='password')
    return client


@pytest.fixture
def anonymous_client():
    return APIClient()


@pytest.fixture
def project():
    return baker.make('projects.Project')


@pytest.fixture
def invitation_email(project):
    return baker.make('email_recruitment.InvitationEMail', project=project)


@pytest.fixture
def reminder_email(project):
    return baker.make('email_recruitment.ReminderEMail', project=project)
