#!/usr/bin/python3
# -*- coding: utf8 -*-

import app


class TestGlobal:
    def test_quit(self):
        apps = app.App()
        apps.main.template.active_template.quit_gui()
        assert apps.main.template is None
