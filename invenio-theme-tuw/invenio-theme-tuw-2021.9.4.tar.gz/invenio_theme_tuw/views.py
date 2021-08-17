# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

import arrow
import requests
from edtf import parse_edtf
from flask import Blueprint, render_template
from invenio_cache import current_cache


def fetch_schemaorg_jsonld(doi_url):
    """Fetch the Schema.org metadata for the DOI."""
    key = f"schemaorg_{doi_url}"
    metadata = current_cache.get(key)

    if metadata is None:
        try:
            response = requests.get(
                doi_url,
                headers={"Accept": "application/vnd.schemaorg.ld+json"},
                timeout=2,
            )
            if response.status_code == 200:
                metadata = response.text.strip()
                current_cache.set(key, metadata)

        except Exception:
            pass

    return metadata


def create_blueprint(app):
    """Create a blueprint with routes and resources."""

    blueprint = Blueprint(
        "invenio_theme_tuw",
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    @blueprint.app_template_filter("tuw_doi_identifier")
    def tuw_doi_identifier(identifiers):
        """Extract DOI from sequence of identifiers."""
        if identifiers is not None:
            for identifier in identifiers:
                if identifier.get("scheme") == "doi":
                    return identifier.get("identifier")

    @blueprint.app_template_global("tuw_cite_as")
    def tuw_cite_as(record_metadata):
        """Create an APA citation text like Zenodo."""
        # fetch the raw values from the record (with fallback values)
        creators = record_metadata.get("creators")
        creator_entries = [creator.get("person_or_org", {}) for creator in creators]
        creator_names = [
            creator.get("name")
            if "name" in creator
            else "{}, {}".format(creator.get("family_name"), creator.get("given_name"))
            for creator in creator_entries
        ]
        publication_date = record_metadata.get("publication_date", arrow.utcnow().year)
        title = record_metadata.get("title")
        publisher = record_metadata.get("publisher", app.config.get("THEME_SITENAME"))
        version = record_metadata.get("version", "1.0")
        resource_type = record_metadata.get("resource_type", {"type": "dataset"})
        doi = tuw_doi_identifier(record_metadata.get("identifiers"))

        # format the values
        pub_date = parse_edtf(publication_date)
        pub_year_start = pub_date.lower_strict().tm_year
        pub_year_end = pub_date.upper_strict().tm_year
        if pub_year_start == pub_year_end:
            publication_year = str(pub_year_start)
        else:
            publication_year = "{}-{}".format(pub_year_start, pub_year_end)

        fmt_version = (
            version if version.lower().startswith("v") else "Version {}".format(version)
        )

        # TODO make this dependent on the configured language!
        titles = dict(resource_type).get("title")
        if "en" in titles:
            fmt_resource_type = titles["en"]
        elif "de" in titles:
            fmt_resource_type = titles["de"]
        elif titles:
            first_language = list(titles)[0]
            fmt_resource_type = titles[first_language]
        else:
            fmt_resource_type = "Unknown"

        fmt_doi = ""
        if doi is not None:
            fmt_doi = (
                doi
                if doi.lower().startswith("http")
                else "https://doi.org/{}".format(doi)
            )

        # format the author names roughly according to the APA logic:
        # https://research.moreheadstate.edu/c.php?g=107001&p=695202
        num_creators = len(creator_names)
        if num_creators <= 2:
            fmt_creators = " and ".join(creator_names)
        elif num_creators <= 5:
            fmt_creators = ", ".join(creator_names[:-1])
            fmt_creators += " & " + creator_names[-1]
        else:
            fmt_creators = "{} et al".format(creator_names[0])

        text = "{}. ({}). {} ({}) [{}]. {}. {}".format(
            fmt_creators,
            publication_year,
            title,
            fmt_version,
            fmt_resource_type,
            publisher,
            fmt_doi,
        ).strip()
        return text

    @blueprint.app_template_global("tuw_create_schemaorg_metadata")
    def tuw_create_schemaorg_metadata(record):
        """Create schema.org metadata to include in a <script> tag."""
        metadata = None

        # get the DOI from the managed PIDs, or from the metadata as fallback
        rec_pids = record.get("pids", {})
        if "doi" in rec_pids:
            doi = rec_pids["doi"].get("identifier")
        else:
            rec_meta = record.get("metadata", {})
            doi = tuw_doi_identifier(rec_meta.get("identifiers"))

        if doi is not None:
            doi_url = (
                doi if doi.startswith("https://") else ("https://doi.org/%s" % doi)
            )
            metadata = fetch_schemaorg_jsonld(doi_url)

        return metadata
    
    @blueprint.route('/tuw/policies')
    def tuw_policies():
        return render_template('invenio_theme_tuw/policies.html')

    @blueprint.route('/tuw/contact')
    def tuw_contact():
        return render_template('invenio_theme_tuw/contact.html')

    return blueprint
