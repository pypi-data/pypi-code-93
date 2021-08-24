# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for TU Wien theme."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "invenio-theme-tuw-tracking": "./js/invenio_theme_tuw/tracking/index.js",
                "invenio-theme-tuw-mobilemenu": "./js/invenio_theme_tuw/mobilemenu/index.js",
                "invenio-theme-tuw-messages": "./js/invenio_theme_tuw/messages/index.js",
                "invenio-theme-tuw-pdf-preview": "./js/invenio_theme_tuw/pdf-preview/index.js",
            },
            "dependencies": {
                "jquery": "^3.2.1",
            },
            "aliases": {
                "themes/tuw": "less/invenio_theme_tuw/theme",
                "../../less/invenio_theme_tuw/theme/assets": "../static"
            }
        },
    },
)
