from wagtail.core.models import Page

import pytest


@pytest.fixture
def root_page():
    return Page.objects.filter(sites_rooted_here__is_default_site=True).get()
