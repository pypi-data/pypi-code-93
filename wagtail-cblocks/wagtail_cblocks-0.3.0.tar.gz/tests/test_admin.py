import pytest
from pytest_django.asserts import assertContains


@pytest.mark.django_db
def test_insert_editor_css(admin_client, root_page):
    response = admin_client.get('/admin/pages/%d/edit/' % root_page.id)
    assertContains(response, 'wagtail_cblocks/css/editor.css')
