import pytest

from huscy.email_recruitment.services import update_reminder_email

pytestmark = pytest.mark.django_db


def test_update_reminder_email(reminder_email):
    assert not reminder_email.text == 'text'
    assert not reminder_email.footer == 'footer'

    result = update_reminder_email(reminder_email, 'text', 'footer')

    assert result == reminder_email
    reminder_email.refresh_from_db()
    assert reminder_email.text == 'text'
    assert reminder_email.footer == 'footer'


def test_update_text_only(reminder_email):
    assert not reminder_email.text == 'text'

    result = update_reminder_email(reminder_email, 'text')

    assert result == reminder_email
    reminder_email.refresh_from_db()
    assert reminder_email.text == 'text'
    assert not reminder_email.footer == ''
