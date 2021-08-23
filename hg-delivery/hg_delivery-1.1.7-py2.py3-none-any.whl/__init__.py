#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from hg_delivery.security import groupfinder, GROUPS, DEFAULT_USER, get_user

# ------------------------------------------------------------------------------


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['hg_delivery.secret'], callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    if 'hg_delivery.default_login' in settings:
        __login = settings['hg_delivery.default_login']
        __pwd = settings['hg_delivery.default_pwd']

        GROUPS[__login] = 'group:editors'
        DEFAULT_USER[__login] = __pwd

    config = Configurator(settings=settings,
                          root_factory='hg_delivery.security.RootFactory')
    config.include('.models')
    config.include('.routes')

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)

    config.scan()
    return config.make_wsgi_app()
