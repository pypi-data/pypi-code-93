import pytest

from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
)

pytestmark = pytest.mark.django_db


def test_admin_user_can_create_reminder_emails(admin_client, project):
    response = create_reminder_email(admin_client, project)

    assert response.status_code == HTTP_201_CREATED


def test_admin_user_can_delete_reminder_emails(admin_client, reminder_email):
    response = delete_reminder_email(admin_client, reminder_email)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_admin_user_can_list_reminder_emails(admin_client, project):
    response = list_reminder_emails(admin_client, project)

    assert response.status_code == HTTP_200_OK


def test_admin_user_can_update_reminder_emails(admin_client, reminder_email):
    response = update_reminder_email(admin_client, reminder_email)

    assert response.status_code == HTTP_200_OK


def test_user_without_permissions_can_create_reminder_emails(client, project):
    response = create_reminder_email(client, project)

    assert response.status_code == HTTP_201_CREATED


def test_user_without_permissions_can_delete_reminder_emails(client, reminder_email):
    response = delete_reminder_email(client, reminder_email)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_user_without_permissions_can_list_reminder_emails(client, project):
    response = list_reminder_emails(client, project)

    assert response.status_code == HTTP_200_OK


def test_user_without_permissions_can_update_reminder_emails(client, reminder_email):
    response = update_reminder_email(client, reminder_email)

    assert response.status_code == HTTP_200_OK


def test_anonymous_user_can_create_reminder_emails(anonymous_client, project):
    response = create_reminder_email(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_can_delete_reminder_emails(anonymous_client, reminder_email):
    response = delete_reminder_email(anonymous_client, reminder_email)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_can_list_reminder_emails(anonymous_client, project):
    response = list_reminder_emails(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_can_update_reminder_emails(anonymous_client, reminder_email):
    response = update_reminder_email(anonymous_client, reminder_email)

    assert response.status_code == HTTP_403_FORBIDDEN


def create_reminder_email(client, project):
    return client.post(
        reverse('reminderemail-list', kwargs=dict(project_pk=project.id)),
        data=dict(footer='footer', text='text')
    )


def delete_reminder_email(client, reminder_email):
    return client.delete(
        reverse(
            'reminderemail-detail',
            kwargs=dict(project_pk=reminder_email.project.id, pk=reminder_email.id)
        )
    )


def list_reminder_emails(client, project):
    return client.get(reverse('reminderemail-list', kwargs=dict(project_pk=project.id)))


def update_reminder_email(client, reminder_email):
    return client.put(
        reverse(
            'reminderemail-detail',
            kwargs=dict(project_pk=reminder_email.project.id, pk=reminder_email.id)
        ),
        data=dict(footer='new_footer', text='new_text')
    )
