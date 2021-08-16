#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21
import os

import easy_automation
from easy_automation.utils.exception import CommandError
from easy_automation.utils.template_render import TemplateRender


class TemplateCommand:
    action_template_map = {
        'startWebProject': 'web_template',
        'startApiProject': 'api_template',
        'startAndroidProject': 'android_template',
        'startIosProject': 'ios_template'
    }

    action_project_folder_map = {
        'startWebProject': '_web_test',
        'startApiProject': '_api_test',
        'startAndroidProject': '_Android_test',
        'startIosProject': '_iOS_test',
    }

    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        ('.py-tpl', '.py'),
    )

    def __init__(self, action, project_name):
        self.action = action
        self.project_name = project_name

    def handle(self):
        base_name = self.project_name
        camel_case_name = ''.join([i.title() for i in self.project_name.split('_')])
        project_folder_name = base_name + self.action_project_folder_map[self.action]

        top_dir = os.path.join(os.getcwd(), project_folder_name)
        try:
            os.mkdir(top_dir)
        except FileExistsError:
            msg = "Path %s already exists" % top_dir
            raise CommandError(msg)
        except OSError as e:
            raise CommandError(e)

        template = self.action_template_map[self.action]
        template_dir = self.handle_template(template)
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace('project', base_name)
            if relative_dir:
                target_dir = os.path.join(top_dir, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(
                    top_dir, relative_dir, filename.replace('project', base_name)
                )
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[:-len(old_suffix)] + new_suffix
                        break

                if new_path.endswith(('.py', '.yml')):
                    with open(old_path, 'r', encoding='utf-8') as template_file:
                        content = template_file.read()
                        template_render = TemplateRender(content)
                        new_content = template_render.render(project_name=camel_case_name)

                    with open(new_path, 'w', encoding='utf-8') as new_file:
                        new_file.write(new_content)

    @staticmethod
    def handle_template(template):
        return os.path.join(easy_automation.__path__[0], 'project_templates', template)







