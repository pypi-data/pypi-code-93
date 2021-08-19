import pytest

from huscy.email_recruitment.models import ReminderEMail
from huscy.email_recruitment.services import delete_reminder_email

pytestmark = pytest.mark.django_db


def test_delete_invitation_email(reminder_email):
    assert ReminderEMail.objects.exists()

    delete_reminder_email(reminder_email)

    assert not ReminderEMail.objects.exists()
