###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
#
#
#

import json
import os
from pathlib import Path

import pytest
import responses

import apd
from apd.ap_info import (
    cache_ap_info,
    fetch_ap_info,
    load_ap_info,
    load_ap_info_from_single_file,
)

DATA_DIR = Path(__file__).parent / "data"
APINFO_PATHS = DATA_DIR / "rds_ap_info.json"


@pytest.fixture
def apinfo():
    """ load the requests test data  """
    return load_ap_info_from_single_file(APINFO_PATHS)


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        with open(APINFO_PATHS) as f:
            data = json.load(f)

            rsps.add(
                responses.GET,
                "https://lbap.app.cern.ch/stable/v1/SL/RDs",
                body=json.dumps(data["info"]),
                status=200,
                content_type="application/json",
            )

            rsps.add(
                responses.GET,
                "https://lbap.app.cern.ch/stable/v1/SL/RDs/tags",
                body=json.dumps(data["tags"]),
                status=200,
                content_type="application/json",
            )

        yield rsps


@pytest.fixture
def apinfo_cache(tmp_path, mocked_responses, monkeypatch):
    """ load the requests test data and cache it in a temp dir  """

    def patched_get_sso_token(uri, app, a, b, c):
        return ""

    monkeypatch.setattr(apd.cern_sso, "get_sso_token", patched_get_sso_token)
    cachedir = tmp_path / "cache"
    os.makedirs(cachedir)
    cache_ap_info(cachedir, "SL", "RDs")
    return cachedir


def test_load_from_cache(apinfo_cache):
    pi = load_ap_info(apinfo_cache, "SL", "RDs")
    assert len(pi.PFNs()) == 58


def test_load_single_file():
    pi = load_ap_info_from_single_file(APINFO_PATHS)
    assert len(pi.PFNs()) == 58


def test_fetch(monkeypatch, mocked_responses):
    def patched_get_sso_token(uri, app, a, b, c):
        return ""

    monkeypatch.setattr(apd.cern_sso, "get_sso_token", patched_get_sso_token)

    pi = fetch_ap_info("SL", "RDs")
    assert len(pi.PFNs()) == 58


def test_cache(monkeypatch, mocked_responses, tmp_path):
    def patched_get_sso_token(uri, app, a, b, c):
        return ""

    monkeypatch.setattr(apd.cern_sso, "get_sso_token", patched_get_sso_token)

    cachedir = tmp_path / "cache"
    os.makedirs(cachedir)
    pi = cache_ap_info(cachedir, "SL", "RDs")
    assert len(pi.PFNs()) == 58
    assert os.path.exists(cachedir / "SL")
    assert os.path.exists(cachedir / "SL" / "RDs.json")
    assert os.path.exists(cachedir / "SL" / "RDs" / "tags.json")


def test_filter_samples(apinfo):
    pi = apinfo.filter("datatype", "2012")
    assert len(pi.PFNs()) == 11


def test_filter_samples_callable(apinfo):

    # from tabulate import tabulate
    # print("\n"+tabulate(pi.list_metadata(with_header=True)))
    assert len(apinfo.PFNs()) == 58

    fpi = apinfo.filter("polarity", lambda x: "magdown" in x)
    assert len(fpi.PFNs()) == 25
