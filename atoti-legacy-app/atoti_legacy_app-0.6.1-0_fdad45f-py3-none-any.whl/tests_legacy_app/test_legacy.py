from http import HTTPStatus

import pytest
import requests

from atoti.session import Session


@pytest.mark.legacy_app
def test_legacy_url_returns_content(session: Session):
    res = requests.get(f"http://localhost:{session.port}/legacy/")
    assert res.status_code == HTTPStatus.OK
