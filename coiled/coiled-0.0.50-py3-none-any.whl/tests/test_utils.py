import sys
from typing import Tuple

import pytest
from coiled.utils import (
    ParseIdentifierError,
    get_account_membership,
    get_platform,
    has_program_quota,
    normalize_server,
    parse_gcp_region_zone,
    parse_identifier,
)


@pytest.mark.parametrize(
    "identifier,expected",
    [
        ("coiled/xgboost:1efd34", ("coiled", "xgboost", "1efd34")),
        ("xgboost:1efd34", (None, "xgboost", "1efd34")),
        ("coiled/xgboost", ("coiled", "xgboost", None)),
        ("xgboost", (None, "xgboost", None)),
        ("coiled/xgboost-py37", ("coiled", "xgboost-py37", None)),
        ("xgboost_py38", (None, "xgboost_py38", None)),
    ],
)
def test_parse_good_names(identifier, expected: Tuple[str, str]):
    account, name, revision = parse_identifier(
        identifier, property_name="name_that_would_be_printed_in_error"
    )
    assert (account, name, revision) == expected


@pytest.mark.parametrize(
    "identifier",
    [
        "coiled/dan/xgboost",
        "coiled/dan?xgboost",
        "dan\\xgboost",
        "jimmy/xgbóst",
        "",
    ],
)
def test_parse_bad_names(identifier):
    with pytest.raises(ParseIdentifierError) as e:
        parse_identifier(identifier, property_name="software_environment")
    assert "software_environment" in e.value.args[0]


def test_get_platform(monkeypatch):
    with monkeypatch.context() as m:
        monkeypatch.setattr(sys, "platform", "linux")
        assert get_platform() == "linux"

    with monkeypatch.context() as m:
        m.setattr(sys, "platform", "darwin")
        assert get_platform() == "osx"

    with monkeypatch.context() as m:
        m.setattr(sys, "platform", "win32")
        assert get_platform() == "windows"

    with monkeypatch.context() as m:
        m.setattr(sys, "platform", "bad-platform")
        with pytest.raises(ValueError) as result:
            assert get_platform() == "windows"

        err_msg = str(result).lower()
        assert "invalid" in err_msg
        assert "bad-platform" in err_msg


def test_normalize_server():
    assert normalize_server("http://beta.coiledhq.com") == "https://cloud.coiled.io"
    assert normalize_server("https://beta.coiled.io") == "https://cloud.coiled.io"


def test_get_account_membership():

    assert get_account_membership({}, account=None) == {}

    response = {"membership_set": []}
    assert get_account_membership(response, account=None) == {}

    membership = {
        "account": {"slug": "coiled"},
    }
    response = {"membership_set": [membership], "username": "not-coiled"}
    assert get_account_membership(response, account="coiled") == membership
    assert get_account_membership(response, account="test_user") != membership

    response["username"] = "coiled"
    assert get_account_membership(response) == membership


def test_has_program_quota():
    assert has_program_quota({}) is False

    membership = {"account": {"active_program": {"has_quota": True}}}
    assert has_program_quota(membership) is True


def test_gcp_region_zone():
    region, zone = parse_gcp_region_zone(region="us-central1")

    assert region == "us-central1"
    assert zone == "us-central1-c"

    region, zone = parse_gcp_region_zone(zone="us-east1-c")

    assert region == "us-east1"
    assert zone == "us-east1-c"

    region, zone = parse_gcp_region_zone(region="test-region", zone="test-zone")

    assert region == "test-region"
    assert zone == "test-zone"

    region, zone = parse_gcp_region_zone(region="us-central1", zone="b")

    assert region == "us-central1"
    assert zone == "us-central1-b"

    region, zone = parse_gcp_region_zone(zone="a")

    assert region == "us-east1"
    assert zone == "us-east1-a"
