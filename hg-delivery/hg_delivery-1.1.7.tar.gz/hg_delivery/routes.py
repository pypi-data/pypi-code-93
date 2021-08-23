# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#
from hg_delivery.predicates import to_int
from hg_delivery.security import ProjectFactory, TaskFactory

# ------------------------------------------------------------------------------


def groups_include(config):
    """
      Add all routes about projects group management
      (crud way ...)
    """
    config.add_route('project_group_delete',
                     r'/delete/{id:\d+}',
                     custom_predicates=(to_int('id'), ))
    config.add_route('project_group_view',
                     r'/view/{id:\d+}',
                     custom_predicates=(to_int('id'), ))
    config.add_route('projects_list_global', '/projects_list')
    config.add_route('group_rename',
                     r'/rename/{id:\d+}',
                     custom_predicates=(to_int('id'), ))


# ------------------------------------------------------------------------------


def projects_include(config):
    """
      Add all routes about project management
      (crud way ...)
    """
    config.add_route('project_add', '/add')
    config.add_route('projects_list',
                     r'/lib/{id:\d+}/projects_list',
                     custom_predicates=(to_int('id'), ))

    config.add_route('group_detach',
                     r'/detach/{id:\d+}/group/{group_id:\d+}',
                     custom_predicates=(to_int('id'), to_int('group_id')),
                     factory=ProjectFactory)
    config.add_route('project_delete',
                     r'/delete/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_edit',
                     r'/edit/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_refresh_state',
                     r'/refresh/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_fetch',
                     r'/fetch/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_save_acls',
                     r'/acls/save/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)

    config.add_route('project_revision_details_json',
                     r'/detail/json/{id:\d+}/revision/{rev}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_revision_details',
                     r'/detail/{id:\d+}/revision/{rev}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)

    config.add_route('project_update',
                     r'/update/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('view_file_content',
                     r'/get/{id:\d+}/{rev}/*file_name',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)

    # push/pull from another project
    config.add_route('project_pull_test',
                     r'/pull/test/{id:\d+}/from/{source:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('source'),
                     ),
                     factory=ProjectFactory)
    config.add_route('project_pull_from',
                     r'/pull/{id:\d+}/from/{source:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('source'),
                     ),
                     factory=ProjectFactory)
    config.add_route('project_push_test',
                     r'/push/test/{id:\d+}/to/{target:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('target'),
                     ),
                     factory=ProjectFactory)
    config.add_route('project_push_to',
                     r'/push/{id:\d+}/to/{target:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('target'),
                     ),
                     factory=ProjectFactory)
    config.add_route('project_brothers',
                     r'/brothers/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_brothers_update_check',
                     r'/check/{id:\d+}/{rev}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)

    # macros linked to this project
    # project is mandatory to keep right management
    # on macro management ...
    config.add_route('macro_fetch',
                     r'/macros/{id:\d+}/fetch/{macro_id:\d+}',
                     custom_predicates=(to_int('id'), to_int('macro_id')),
                     factory=ProjectFactory)
    config.add_route('macro_add',
                     r'/macros/{id:\d+}/add',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('macro_refresh',
                     r'/macros/{id:\d+}/refresh',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('macro_update',
                     r'/macros/{id:\d+}/update/{macro_id:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('macro_id'),
                     ),
                     factory=ProjectFactory)
    config.add_route('macro_run',
                     r'/macros/{id:\d+}/run/{macro_id:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('macro_id'),
                     ),
                     factory=ProjectFactory)
    config.add_route('macro_delete',
                     r'/macros/{id:\d+}/delete/{macro_id:\d+}',
                     custom_predicates=(
                         to_int('id'),
                         to_int('macro_id'),
                     ),
                     factory=ProjectFactory)

    # move project to another revision
    # add a fizzle to get projects list target by the action
    config.add_route('project_change_to',
                     r'/update/{rev}/in/{id:\d+}/and/*brother_id',
                     custom_predicates=(
                         to_int('id'),
                         to_int('brother_id'),
                     ),
                     factory=ProjectFactory)
    config.add_route('project_logs',
                     r'/logs/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)

    # provide difference between two revision
    config.add_route('project_revisions_diff',
                     r'/{id:\d+}/diff',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)

    config.add_route('project_save_tasks',
                     r'/tasks/save/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=ProjectFactory)
    config.add_route('project_run_task',
                     r'/tasks/run/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=TaskFactory)
    config.add_route('project_delete_task',
                     r'/tasks/delete/{id:\d+}',
                     custom_predicates=(to_int('id'), ),
                     factory=TaskFactory)
    config.add_route('tasks', '/tasks')
    config.add_route('macros', '/macros')
    config.add_route('description', r'/description/{id:\d+}')


# ------------------------------------------------------------------------------


def users_include(config):
    """
      Users routes definitions
    """
    config.add_route('users', '/view')
    config.add_route('users_save_acls', '/acls/save')
    config.add_route('users_json', '/json')
    config.add_route('user_add', '/add')
    config.add_route('user_delete', r'/{id:\d+}/delete')
    config.add_route('user_update', r'/{id:\d+}/update')
    config.add_route('user_get', r'/{id:\d+}/get')
    config.add_route('user_acls',
                     r'/{id:\d+}/acls/get',
                     custom_predicates=(to_int('id'), ))


# ------------------------------------------------------------------------------


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('logs', '/logs')
    config.add_route('contact', '/contact')

    config.include(projects_include, '/project')
    config.include(groups_include, '/group')

    config.include(users_include, '/users')
