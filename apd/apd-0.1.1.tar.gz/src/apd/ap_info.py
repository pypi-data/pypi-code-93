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
# Tool to load and interpret information from the AnalysisProductions data endpoint
#
import json
import os
from pathlib import Path

import requests

import apd.cern_sso


class APDataDownloader:
    def __init__(self, api_url="https://lbap.app.cern.ch"):
        self.api_url = api_url
        self.token = None

    def _get_headers(self):
        return {"Authorization": f"Bearer {self._get_token()}"}

    def _get_token(self):
        """ Get the API token, authentification with the CERN SSO """
        # Getting the token using apd.cern_sso.
        # We have a copy of this module as it is not released on pypi.
        # N.B. This requires a kerberos token for an account that belongs to lhcb-general
        if not self.token:
            self.token = apd.cern_sso.get_sso_token(
                f"{self.api_url}",
                "lhcb-analysis-productions",
                True,
                "auth.cern.ch",
                "cern",
            )
        return self.token

    def get_ap_info(self, working_group, analysis):
        r = requests.get(
            f"{self.api_url}/stable/v1/{working_group}/{analysis}",
            headers=self._get_headers(),
        )
        r.raise_for_status()
        return r.json()

    def get_ap_tags(self, working_group, analysis):
        r = requests.get(
            f"{self.api_url}/stable/v1/{working_group}/{analysis}/tags",
            headers=self._get_headers(),
        )
        r.raise_for_status()
        return r.json()

    def get_user_info(self):
        r = requests.get(f"{self.api_url}/user", headers=self._get_headers())
        r.raise_for_status()
        return r.json()


def fetch_ap_info(
    working_group, analysis, loader=None, api_url="https://lbap.app.cern.ch"
):
    """ Fetch the API info from the service  """

    if not loader:
        loader = APDataDownloader(api_url)

    return SampleList(
        loader.get_ap_info(working_group, analysis),
        loader.get_ap_tags(working_group, analysis),
    )


def cache_ap_info(
    cache_dir, working_group, analysis, loader=None, api_url="https://lbap.app.cern.ch"
):
    """ Fetch the AP info and cache it locally  """
    cache_dir = Path(cache_dir)
    samples = fetch_ap_info(working_group, analysis, loader, api_url)
    wgdir = cache_dir / working_group
    anadir = wgdir / analysis
    datafile = wgdir / f"{analysis}.json"
    tagsfile = anadir / "tags.json"
    if not os.path.exists(anadir):
        os.makedirs(anadir)
    with open(datafile, "w") as f:
        json.dump(samples.info, f)
    with open(tagsfile, "w") as f:
        json.dump(samples.tags, f)
    return samples


def load_ap_info(cache_dir, working_group, analysis):
    """ Load the API info from a cache file """
    cache_dir = Path(cache_dir)
    wgdir = cache_dir / working_group
    anadir = wgdir / analysis
    datafile = wgdir / f"{analysis}.json"
    tagsfile = anadir / "tags.json"
    with open(datafile) as f:
        data = json.load(f)
    with open(tagsfile) as f:
        tags = json.load(f)
    return SampleList(data, tags)


def load_ap_info_from_single_file(filename):
    """ Load the API info from a cache file """

    if not os.path.exists(filename):
        raise Exception("Please specify a valid file as metadata cache")

    with open(filename) as f:
        apinfo = json.load(f)
        info = apinfo["info"]
        tags = apinfo["tags"]
        return SampleList(info, tags)


class SampleList:
    """Class wrapping the AnalysisProduction metadata."""

    def __init__(self, info=None, tags=None):

        self.info = info if info else []
        self.tags = tags if tags else {}

    def sampleTags(self, sample):
        sid = str(sample["sample_id"])
        return self.tags[sid]

    def filter(self, tag, value):
        """
        Filter the requests according to the tag value passed in parameter
        """
        if callable(value):
            matching = [
                sample
                for sample in self.info
                if value(self.sampleTags(sample).get(tag, None))
            ]
        else:
            matching = [
                sample
                for sample in self.info
                if self.sampleTags(sample).get(tag, None) == value
            ]
        return SampleList(matching, self.tags)

    def PFNs(self):
        """ Collects the PFNs """
        pfns = []
        for sample in self.info:
            for pfnlist in sample["lfns"].values():
                pfns.append(pfnlist[0])
        return pfns

    def union(self, samples):
        info = self.info + samples.info
        tags = {**(self.tags), **(samples.tags)}
        return SampleList(info, tags)
