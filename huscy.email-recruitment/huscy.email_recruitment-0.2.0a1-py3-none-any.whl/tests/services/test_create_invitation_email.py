import pytest

from huscy.email_recruitment.models import InvitationEMail
from huscy.email_recruitment.services import create_invitation_email

pytestmark = pytest.mark.django_db


def test_create_invitation_email(project):
    result = create_invitation_email(project, 'text', 'footer')

    assert isinstance(result, InvitationEMail)
    assert result.project == project
    assert result.text == 'text'
    assert result.footer == 'footer'


def test_with_default_footer(project):
    result = create_invitation_email(project, 'text')

    assert result.footer == ''
