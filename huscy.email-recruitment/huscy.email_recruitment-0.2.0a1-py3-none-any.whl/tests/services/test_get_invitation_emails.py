from itertools import cycle

import pytest
from model_bakery import baker

from huscy.email_recruitment.services import get_invitation_emails

pytestmark = pytest.mark.django_db


@pytest.fixture
def projects():
    return baker.make('projects.Project', _quantity=2)


@pytest.fixture
def invitation_emails(projects):
    return baker.make('email_recruitment.InvitationEMail', project=cycle(projects), _quantity=4)


def test_get_invitation_emails(invitation_emails):
    result = get_invitation_emails()

    assert len(result) == 4


def test_get_invitation_emails_filtered_by_project(projects, invitation_emails):
    result = get_invitation_emails(projects[0])

    assert len(result) == 2
