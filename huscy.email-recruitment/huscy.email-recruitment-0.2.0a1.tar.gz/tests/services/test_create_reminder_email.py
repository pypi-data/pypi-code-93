import pytest

from huscy.email_recruitment.models import ReminderEMail
from huscy.email_recruitment.services import create_reminder_email

pytestmark = pytest.mark.django_db


def test_create_reminder_email(project):
    result = create_reminder_email(project, 'text', 'footer')

    assert isinstance(result, ReminderEMail)
    assert result.project == project
    assert result.text == 'text'
    assert result.footer == 'footer'


def test_with_default_footer(project):
    result = create_reminder_email(project, 'text')

    assert result.footer == ''
