#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21
import re


class TemplateRender:
    _re = re.compile(r'\{\{\s*(?P<keyword>\S*)\s*\}\}')

    def __init__(self, content):
        self.content = content

    def render(self, **kwargs):
        replace_list = self._re.findall(self.content)
        for replace in replace_list:
            if replace in kwargs:
                self.content = self._re.sub(kwargs[replace], self.content)

        return self.content



if __name__ == '__main__':
    with open('F:\\pythonProject\\easy_automation_test\\src\\easy_automation\\project_templates\\api_template\\project_api\\project_api.py-tpl', 'r',  encoding='utf-8') as fh:
        content = fh.read()
    test = TemplateRender(content)
    test.render(project_name='Feishu')


