import pytest

from huscy.email_recruitment.services import update_invitation_email

pytestmark = pytest.mark.django_db


def test_update_invitation_email(invitation_email):
    assert not invitation_email.text == 'text'
    assert not invitation_email.footer == 'footer'

    result = update_invitation_email(invitation_email, 'text', 'footer')

    assert result == invitation_email
    invitation_email.refresh_from_db()
    assert invitation_email.text == 'text'
    assert invitation_email.footer == 'footer'


def test_update_text_only(invitation_email):
    assert not invitation_email.text == 'text'

    result = update_invitation_email(invitation_email, 'text')

    assert result == invitation_email
    invitation_email.refresh_from_db()
    assert invitation_email.text == 'text'
    assert not invitation_email.footer == ''
