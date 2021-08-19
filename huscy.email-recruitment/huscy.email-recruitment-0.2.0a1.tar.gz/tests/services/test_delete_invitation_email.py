import pytest

from huscy.email_recruitment.models import InvitationEMail
from huscy.email_recruitment.services import delete_invitation_email

pytestmark = pytest.mark.django_db


def test_delete_invitation_email(invitation_email):
    assert InvitationEMail.objects.exists()

    delete_invitation_email(invitation_email)

    assert not InvitationEMail.objects.exists()
