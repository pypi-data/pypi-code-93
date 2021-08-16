#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/28

from src.easy_automation.core.template_command import TemplateCommand


class TestTemplateCreateProject:

    def test_create_project(self):
        action = 'startAndroidProject'
        project_name = 'test_project'
        template = TemplateCommand(action, project_name)
        template.handle()
