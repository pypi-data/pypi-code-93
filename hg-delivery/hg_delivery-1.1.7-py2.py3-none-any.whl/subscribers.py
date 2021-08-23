#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it
# under the terms of the M.I.T License.
#

import logging
from sqlalchemy.orm import joinedload

from pyramid.events import (
    BeforeRender,
    ApplicationCreated,
    subscriber
)

from .models import (
    Project,
    RemoteLog,
    Acl,
    User
)

from .nodes import NodeSsh, PoolSsh

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@subscriber(BeforeRender)
def mysubscriber(event):

    request = event['request']

    event['url'] = request.route_path
    event['static_url'] = request.static_path
    event['logged_in'] = request.authenticated_userid

    if request.authenticated_userid\
       and 'projects_list' not in event.rendering_val:
        projects_list = []
        if request.registry.settings['hg_delivery.default_login']\
           == request.authenticated_userid:
            projects_list = request.dbsession.query(Project)\
                .options(joinedload(Project.groups))\
                .order_by(Project.name.desc())\
                .all()
        else:
            projects_list = request.dbsession.query(Project)\
                .join(Acl)\
                .join(User)\
                .options(joinedload(Project.groups))\
                .filter(User.email == request.authenticated_userid)\
                .order_by(Project.name.desc())\
                .all()
        event.rendering_val['projects_list'] = projects_list
    elif 'projects_list' not in event.rendering_val:
        event.rendering_val['projects_list'] = []

    # before any render we look if we need to
    # log data and flush them into database
    if NodeSsh.logs:
        if request.registry.settings['hg_delivery.default_login']\
           == request.authenticated_userid:
            webapp_user_id = User.default_administrator_id
        else:
            webapp_user_id = request.dbsession.query(User.id)\
                .filter(User.email == request.authenticated_userid)\
                .scalar()
        for (__id, __host, __path, __command) in NodeSsh.logs:
            request.dbsession.add(
                RemoteLog(
                    id_project=__id,
                    id_user=webapp_user_id,
                    host=__host,
                    path=__path,
                    command=__command))
        # also empty the list container
        del NodeSsh.logs[0:]

# ------------------------------------------------------------------------------


@subscriber(ApplicationCreated)
def app_start(event):
    """
    when the app start we declare a watchdog to check ssh connection
    that should be closed
    """
    if hasattr(event.app.registry, 'scheduler'):
        event.app.registry.scheduler.add_interval_job(
            PoolSsh.close_un_used_nodes, minutes=15)
    else:
        error_message = "please install pyramid_scheduler project"
        error_message += " and add reference inside your .ini file"
        log.error(error_message)
