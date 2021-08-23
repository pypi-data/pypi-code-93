#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#

import unittest
from datetime import datetime

# ------------------------------------------------------------------------------


class BasicDataIgnition(unittest.TestCase):

    def _add_some_user(self):
        from ..models import User
        # add a user
        user = User('test', 'test', 'test@france.fr', datetime.now())
        self.session.add(user)
        self.session.flush()
        return (user,)

    def _add_some_projects(self):
        from ..models import Project
        # add a project
        project_a = Project('project1', 'test', 'test', '127.0.0.1',
                            '/tmp/project_1', None, False, None, False, True)
        self.session.add(project_a)
        # add a project
        project_b = Project('project2', 'test', 'test', '127.0.0.1',
                            '/tmp/project_2', None, False, None, False, True)
        self.session.add(project_b)
        self.session.flush()
        return (project_a, project_b)

    def _add_some_logs(self, count=2):
        from ..models import RemoteLog
        # add some logs
        user = self.users_list[0]
        project_a, project_b = self.projects_list[0:2]
        for i in range(count):
            self.session.add(RemoteLog(project_a.id, user.id,
                                       '127.0.0.1', '/tmp/test', 'ls -al'))
            self.session.add(RemoteLog(project_b.id, user.id,
                                       '127.0.0.1', '/tmp/test', 'ls -al'))
        self.session.flush()
