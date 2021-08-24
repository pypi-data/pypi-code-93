# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function

from yoctools import *


class Tag(Command):
    common = True
    helpSummary = "View current component tags"
    helpUsage = """
%prog [<compnent> ...]
"""
    helpDescription = """
View current component tags
"""

    def Execute(self, opt, args):
        yoc = YoC()
        components = ComponentGroup()
        for component in yoc.components:
            if len(args) > 0:
                if component.name not in args:
                    continue
            if os.path.exists(os.path.join(component.path, '.git')):
                components.add(component)
        if len(components) == 0:
            put_string("There no git repo found in your workspace.", level='error')
            exit(0)

        for component in components:
            git = GitRepo(component.path, component.repo_url)
            tags = git.GetRemoteTags()
            if len(tags) > 0:
                put_string(component.name + ':')
                for b in tags:
                    put_string('  %s' % b)
