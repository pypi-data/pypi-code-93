# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module containing the theme for TU Wien."""

from . import config
from .views import create_blueprint


class InvenioThemeTUW:
    """Invenio-Theme-TUW extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-theme-tuw"] = self

        # since invenio-app-rdm currently (april 2021) doesn't offer an easy way of
        # overriding the provided jinja templates, we have to perform a workaround:
        # the first blueprint that has a definition for a template (per name) gets
        # selected by 'render_template'
        # thus, we just have to make sure that our blueprint is inserted before the
        # 'invenio_app_rdm' blueprints
        bps = [bp for bp in app._blueprint_order if bp.name == "invenio_theme_tuw"]

        if not bps:
            # in case there's no 'invenio_theme_tuw' blueprint defined yet
            # (which is actually the expected case), we create and register it
            # thus, we can't specify the blueprint for auto-registration in setup.py,
            # unless we deal with the naming conflict somehow
            bp = create_blueprint(app)
            app.register_blueprint(bp)
            bps = [bp]

        for bp in bps:
            # move the found blueprints to the front of the list
            # (note that all items in 'bps' were either already contained in
            # 'app._blueprint_order' in the first place, or were added via
            # 'app.register_blueprint(...)')
            app._blueprint_order.pop(app._blueprint_order.index(bp))
            app._blueprint_order.insert(0, bp)

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        for k in dir(config):
            app.config.setdefault(k, getattr(config, k))
