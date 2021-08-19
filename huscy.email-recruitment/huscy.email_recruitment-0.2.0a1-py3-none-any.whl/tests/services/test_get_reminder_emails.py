from itertools import cycle

import pytest
from model_bakery import baker

from huscy.email_recruitment.services import get_reminder_emails

pytestmark = pytest.mark.django_db


@pytest.fixture
def projects():
    return baker.make('projects.Project', _quantity=2)


@pytest.fixture
def reminder_emails(projects):
    return baker.make('email_recruitment.ReminderEMail', project=cycle(projects), _quantity=4)


def test_get_reminder_emails(reminder_emails):
    result = get_reminder_emails()

    assert len(result) == 4


def test_get_reminder_emails_filtered_by_project(projects, reminder_emails):
    result = get_reminder_emails(projects[0])

    assert len(result) == 2
