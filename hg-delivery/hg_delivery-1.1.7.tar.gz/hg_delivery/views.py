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

import re
import time
import logging

from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest, HTTPError,\
    HTTPFound, HTTPServerError
from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from collections import OrderedDict

from pyramid.security import (
    Authenticated,
)

from threading import Thread, Event

from .models import (
    Project,
    RemoteLog,
    User,
    Acl,
    Task,
    Macro,
    ProjectGroup,
    MacroRelations,
)

from hg_delivery.nodes import (
    NodeException,
    HgNewBranchForbidden,
    HgNewHeadsForbidden,
    NodeController,
    OutputErrorCode,
    OutputError,
    UnavailableConnexion,
)

try:
    from paramiko.ssh_exception import NoValidConnectionsError
except BaseException:
    # before paramiko 1.6
    from paramiko.ssh_exception import SSHException as NoValidConnectionsError

mailer_available = True
try:
    from pyramid_mailer.message import Message
except Exception:
    mailer_available = False
    print("please install pyramid_mailer")

logging.getLogger("paramiko").setLevel(logging.WARNING)


log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


class SpeedThread(Thread):

    def __init__(self, project, rev):
        """
        we're looking for a project and targeting a specific revision

        :param project: an sqlalchemy models.Project instance
        :param rev: a string hash revision
        """
        self.project = project
        self.rev = rev
        self._is_stopped = Event()

    def is_stopped(self):
        return self._is_stopped.is_set()

# ------------------------------------------------------------------------------


class SpeedCrawler(SpeedThread):
    """
      a simple way to divide node jobs
    """

    def __init__(self, project, rev):
        """
        we're looking for a project and targeting a specific revision

        :param project: an sqlalchemy models.Project instance
        :param rev: a string hash revision
        """
        self.__linked = False
        SpeedThread.__init__(self, project, rev)

    def start(self):
        """
        Unleashed the dogs
        """
        try:
            # we check if this project has got this revision ...
            with NodeController(self.project) as ssh_node:
                node = ssh_node.get_revision_description(self.rev)
                if node is not None and 'rev' in node:
                    self.__linked = True
        except Exception as e:
            self.__linked = False
            log.debug(e)

        self._is_stopped.set()

    def is_linked(self):
        return self.__linked

# ------------------------------------------------------------------------------


class SpeedUpdater(SpeedThread):
    """
      a simple way to divide node jobs
    """

    def __init__(self, project, rev, run_task_flag=True):
        """
        we're looking for a project and targeting a specific revision

        :param project: an sqlalchemy models.Project instance
        :param rev: a string hash revision
        """
        self.__updated = False
        self.__tasks_exceptions = []
        self.__run_task_flag = run_task_flag

        SpeedThread.__init__(self, project, rev)

    def start(self):
        """
          update a project to a specific revision (a hash)
        """
        try:
            with NodeController(self.project, silent=False) as ssh_node:
                ssh_node.update_to(self.rev)
                current_rev = ssh_node.get_current_rev_hash()
                stop_at = 0
                while current_rev != self.rev and stop_at < 10:
                    # sleep 100 ms
                    time.sleep(0.100)
                    current_rev = ssh_node.get_current_rev_hash()
                    stop_at += 1

                if current_rev == self.rev:
                    self.__updated = True

                    # check whereas tasks have to to be triggered or not
                    if self.__run_task_flag:
                        for task in self.project.tasks:
                            try:
                                ssh_node.run_command(task.content, log=True)
                            except NodeException as e:
                                self.__tasks_exceptions.append(e.value)
                                log.error(e)
                            except UnavailableConnexion as e:
                                _msg = e.value
                                _msg += " (%s:%s)" % (self.project.host,
                                                      self.project.path)
                                self.__tasks_exceptions.append(_msg)
                                log.error(e)
                            except OutputErrorCode as e:
                                _msg = u"Task return an error code :"
                                _msg += u" %s (different than 0)"
                                self.__tasks_exceptions.append(_msg % e.value)
                                log.error(e)

        except Exception as e:
            log.debug(e)

        self._is_stopped.set()

    def get_tasks_exceptions(self):
        return self.__tasks_exceptions

    def project_updated(self):
        return self.__updated

# ------------------------------------------------------------------------------


@view_config(route_name='user_update', renderer='json', permission='edit')
def update_user(request):
    """
    update user ...
    """
    result = False
    explanation = None

    user_id = request.matchdict.get('id')
    if user_id is None:
        explanation = 'Bad parameter'
    elif 'name' not in request.params:
        explanation = 'Bad parameter'
    elif 'email' not in request.params:
        explanation = 'Bad parameter'
    else:
        try:
            user = request.dbsession.query(User)\
                .filter(User.id == user_id)\
                .scalar()

            if user is not None:
                try:
                    for attribute in request.params:
                        setattr(user, attribute, request.params[attribute])
                    request.dbsession.flush()
                    result = True
                    lb = u'This user : %s (%s) has been updated ...'
                    explanation = lb % (
                        request.params['name'], request.params['email'])
                except IntegrityError:
                    request.dbsession.rollback()
                    result = False
                    _msg = u"You can't update this user,"
                    _msg += u" this email is already used"
                    _msg += " (%s %s) ..."
                    explanation = _msg % (request.params['name'],
                                          request.params['email'])
            else:
                lb = u"This user is unknown or has already been deleted"
                explanation = lb
        except SQLAlchemyError as e:
            explanation = e.orig
        except Exception as e:
            explanation = str(e)

    return {'result': result,
            'explanation': explanation}

# ------------------------------------------------------------------------------


@view_config(route_name='user_delete', permission='edit')
def delete_user(request):
    """
    delete user ...
    """
    if 'id' not in request.matchdict:
        return HTTPError(400)

    user_id = request.matchdict['id']
    try:
        user = request.dbsession.query(User)\
            .filter(User.id == user_id)\
            .scalar()
        if user:
            request.dbsession.delete(user)
    except SQLAlchemyError as e:
        return HTTPServerError(e.orig)

    return HTTPFound(location=request.route_path(route_name='users'))

# ------------------------------------------------------------------------------


@view_config(route_name='user_get', renderer='json', permission='edit')
def get_user(request):
    """
    get user ...
    """
    error = None
    result = False
    user = None

    if 'id' not in request.matchdict:
        error = "Bad parameter"
    else:
        try:
            user_id = request.matchdict['id']
            user = request.dbsession.query(User)\
                .filter(User.id == user_id)\
                .scalar()
        except SQLAlchemyError as e:
            error = e.orig
        else:
            result = True

    return {'result': result,
            'error': error,
            'user': user}

# ------------------------------------------------------------------------------


@view_config(route_name='user_add', renderer='json', permission='edit')
def add_user(request):
    """
    manage users ...
    """
    result = False
    explanation = None

    name = request.params.get('name')
    email = request.params.get('email')
    password = request.params.get('pwd')

    d_login = request.registry.settings['hg_delivery.default_login']

    # email is the key, and password cannot be empty
    if not name:
        explanation = u'Your user profile should contain a valid name'
        result = False
    elif not email or not re.match('[^@]+@[^@]+', email):
        explanation = u'Your user profile should contain a valid email'
        result = False
    elif email and email == d_login:
        explanation = u'Your user profile should contain a valid email'
        result = False
    elif not password:
        explanation = u"Your user profile musn't be empty"
        result = False
    else:
        try:
            # folder should be unique
            user = User(**request.params)
            request.dbsession.add(user)
            request.dbsession.flush()
            result = True
            _msg = u'This user : %s (%s) has been added ...'
            explanation = _msg % (name, email)

            if hasattr(request, 'mailer'):
                mailer = request.mailer
                r = request.registry.settings
                email_sender = r.get('hg_delivery.email_sender')
                host_domain = r.get('hg_delivery.host_domain')
                if email_sender is not None\
                   and host_domain is not None:
                    subject = "hg_delivery account creation"
                    message_body = """Hello,

  We just create an account for you, allowing you to access the HG DELIVERY interface.
  Please find below your access details and your new password to log in

  Login : %s
  Password: %s

  Log in address  : %s
  thank you for not replying to this email

  Kind regards""" % (user.email, user.pwd, host_domain)

                    message = Message(subject=subject,
                                      sender=email_sender,
                                      recipients=[user.email],
                                      body=message_body)
                    mailer.send_immediately(message, fail_silently=False)

        except IntegrityError as e:
            log.error(e)
            result = False
            request.dbsession.rollback()
            _msg = u'This user and this email are already defined (%s %s) ...'
            explanation = _msg % (name, email)
        except SQLAlchemyError as e:
            result = False
            explanation = e.orig

    if not result:
        return HTTPBadRequest(detail=explanation)

    return {'result': result,
            'explanation': explanation}

# ------------------------------------------------------------------------------


@view_config(route_name='users_json', renderer='json', permission='edit')
@view_config(
    route_name='users',
    renderer='templates/users.mako',
    permission='edit')
def manage_users(request):
    """
    manage users ...
    retrieve and publish user list and project list
    """
    result = False
    error = None
    lst_users = []
    project_acls = {}

    try:
        lst_users = request.dbsession.query(User).all()
        project_acls = {}
        for _p in request.dbsession.query(Project):
            project_acls[_p.id] = {_acl.id_user: _acl.acl for _acl in
                                   request.dbsession.query(Acl)
                                   .filter(Acl.id_project == _p.id)}
    except SQLAlchemyError as e:
        result = False
        error = e.orig
    else:
        result = True

    return {'result': result,
            'error': error,
            'lst_users': lst_users,
            'known_acls': Acl.known_acls,
            'project_acls': project_acls}

# ------------------------------------------------------------------------------


@view_config(route_name='contact', renderer='templates/contact.mako')
def contact(request):
    """
    contact information
    """
    return {}

# ------------------------------------------------------------------------------


@view_config(
    route_name='description',
    renderer='json',
    permission=Authenticated)
def node_description(request):
    """
    return node description
    """

    repository_error = None
    result = None
    node_desc = {}

    if 'id' not in request.matchdict:
        # why not a 400 ?
        repository_error = 'Bad Parameter'
    else:
        id_project = request.matchdict['id']

        try:
            project = request.dbsession.query(Project).get(id_project)
            if not project.is_initial_revision_init():
                project.init_initial_revision()
        except NoValidConnectionsError as e:
            repository_error = u'No valid connection error to host (%s)... ' % (
                project.host)
            log.error(
                u'No valid connection error to host (%s)... ' %
                (project.host))
            log.error(e)
        except ValueError as e:
            repository_error = u'No key available (%s)... ' % (
                project.host)
            log.error(
                u'No valid connection error to host (%s)... ' %
                (project.host))
            log.error(e)
        except SQLAlchemyError as e:
            repository_error = e.orig
            result = False
        except Exception as e:
            repository_error = u'No valid connection error to host (%s)... ' % (
                project.host)
            log.error(
                u'No valid connection error to host (%s)... ' %
                (project.host))
            log.error(e)
        except:
            repository_error = u'No valid connection error to host (%s)... ' % (
                project.host)
            log.error(
                u'No valid connection error to host (%s)... ' %
                (project.host))
        else:
            try:
                with NodeController(project, silent=True) as ssh_node:
                    node_desc = ssh_node.get_current_revision_description()
            except NodeException:
                # a paramiko error
                # linked to network error
                # File "....   venv/lib/python3.4/site-packages/
                #  paramiko-1.16.0-py3.4.egg/paramiko/
                #  ssh_exception.py", line 168, in __init__
                #   body = ', '.join([x[0] for x in addrs[:-1]])
                # TypeError: 'dict_keys' object is not subscriptable
                repository_error = 'Node Exception %s' % project.host
            except UnavailableConnexion as e:
                lb = u'No available connection to host (%s)... '
                node_desc = lb % (
                    project.host)
                _msg = u'No available connection to host (%s)... '
                log.error(_msg % (project.host))
                repository_error = _msg % (project.host)
                log.error(e)
            except NoValidConnectionsError as e:
                lb = u'No valid connection error to host (%s)... '
                node_desc = lb % (
                    project.host)
                _msg = u'No valid connection error to host (%s)... '
                log.error(_msg % (project.host))
                repository_error = _msg % (project.host)
                log.error(e)
            else:
                result = True

    return {'result': result,
            'node_description': node_desc,
            'repository_error': repository_error}

# ------------------------------------------------------------------------------


@view_config(route_name='home', renderer='templates/index.mako')
def default_view(request):
    """
    """
    error = request.params.get('error', '')

    dashboard_list = []
    nodes_description = {}
    projects_list = []

    if request.authenticated_userid:
        projects_list = []
        _default_login = request.registry.settings['hg_delivery.default_login']
        if _default_login == request.authenticated_userid:
            projects_list = request.dbsession.query(
                Project).order_by(Project.name.desc()).all()
        elif hasattr(request, 'user') and request.user is not None:
            projects_list = request.dbsession.query(Project)\
                .join(Acl)\
                .join(User)\
                .filter(User.id == request.user.id)\
                .order_by(Project.name.desc())\
                .all()

        for project in projects_list:
            try:
                if project.dashboard != 1:
                    continue

                dashboard_list.append(project)
                nodes_description[project.id] = {}

            except NodeException as e:
                nodes_description[project.id] = {}
                log.error(e)

    return {'projects_list': projects_list,
            'nodes_description': nodes_description,
            'dashboard_list': dashboard_list,
            'error': error
            }

# ------------------------------------------------------------------------------


@view_config(route_name='logs', renderer='json', permission='edit')
def logs(request):
    """
    fetch all logs, what ever the project
    """
    error = None
    try:
        lst_logs = request.dbsession.query(RemoteLog)\
            .order_by(RemoteLog.creation_date.desc())\
            .limit(50)\
            .all()
    except SQLAlchemyError as e:
        lst_logs = []
        error = e.orig
    except Exception as e:
        lst_logs = []
        error = str(e)

    return {'logs': lst_logs, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='project_logs', renderer='json', permission='edit')
def project_logs(request):
    """
    fetch logs linked to a project
    """
    error = None
    id_project = request.matchdict['id']
    try:
        lst_logs = request.dbsession.query(RemoteLog)\
            .filter(RemoteLog.id_project == id_project)\
            .order_by(RemoteLog.creation_date.desc())\
            .limit(50)\
            .all()
    except SQLAlchemyError as e:
        lst_logs = []
        error = e.orig
    except Exception as e:
        lst_logs = []
        error = str(e)

    return {'logs': lst_logs, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='project_push_test', renderer='json')
def shall_we_push(request):
    """
      test if push is available regarding to push query result
    """
    result = False
    error = None

    if 'id' not in request.matchdict:
        error = 'bad parameter'
    elif 'target' not in request.matchdict:
        error = 'bad parameter'
    else:
        id_project = request.matchdict['id']
        id_target = request.matchdict['target']

        try:
            project = request.dbsession.query(Project).get(id_project)
            target_project = request.dbsession.query(Project).get(id_target)
            result = False
            if project and target_project:
                with NodeController(project, silent=True) as ssh_node:
                    result = ssh_node.pushable(project, target_project)
            else:
                error = "Unknown project"
        except SQLAlchemyError as e:
            error = e.orig
        except Exception as e:
            error = str(e)

    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='project_pull_test', renderer='json')
def shall_we_pull(request):
    """
      test if pull is available regarding to push query result
    """
    result = False
    error = None

    if 'id' not in request.matchdict:
        error = 'bad parameter'
    elif 'source' not in request.matchdict:
        error = 'bad parameter'
    else:
        id_project = request.matchdict['id']
        id_target = request.matchdict['source']
        try:
            project = request.dbsession.query(Project).get(id_project)
            source_project = request.dbsession.query(Project).get(id_target)

            if project and source_project:
                with NodeController(project, silent=True) as ssh_node:
                    result = ssh_node.pullable(project, source_project)
            else:
                error = "Unknown project"
        except SQLAlchemyError as e:
            error = e.orig
        except Exception as e:
            error = str(e)
    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='project_brothers', renderer='json')
def project_brothers(request):
    """
      check who is sharing this project
    """
    id_project = request.matchdict['id']

    project = request.dbsession.query(Project).get(id_project)
    projects_list = []

    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        projects_list = request.dbsession.query(Project)\
            .order_by(Project.name.desc())\
            .all()
    else:
        projects_list = request.dbsession.query(Project)\
            .join(Acl)\
            .join(User)\
            .filter(User.id == request.user.id)\
            .order_by(Project.name.desc())\
            .all()

    linked_projects = [p for p in projects_list
                       if (p.rev_init is not None and p
                            .rev_init == project.rev_init and p
                            .id != project.id)]
    return {'brothers': linked_projects}

# ------------------------------------------------------------------------------


@view_config(route_name='project_brothers_update_check', renderer='json')
def who_share_this_id(request):
    """
      check who is sharing this id
    """
    id_project = request.matchdict['id']
    rev = request.matchdict['rev']
    projects_sharing_that_rev = []

    result = False
    error = None

    try:
        project = request.dbsession.query(Project).get(id_project)
        projects_list = []

        _default_login = request.registry.settings['hg_delivery.default_login']
        if _default_login == request.authenticated_userid:
            projects_list = request.dbsession.query(Project)\
                .order_by(Project.name.desc())\
                .all()
        else:
            projects_list = request.dbsession.query(Project)\
                .join(Acl)\
                .filter(Acl.acl == 'edit')\
                .join(User)\
                .filter(User.id == request.user.id)\
                .order_by(Project.name.desc())\
                .all()

        linked_projects = [p for p in projects_list
                           if (p.rev_init is not None and p
                               .rev_init == project.rev_init and p
                               .id != project.id and not p.no_scan)]
        thread_stack = []

        for __p in linked_projects:
            new_thread = SpeedCrawler(__p, rev)
            thread_stack.append(new_thread)
            new_thread.start()

        t0 = time.time()
        t1 = t0 + 10 * 60
        while sum([e.is_stopped() for e in thread_stack]) != len(
                linked_projects) or time.time() > t1:
            time.sleep(0.005)

        # when threads finished their job
        # we filter linked projects
        projects_sharing_that_rev = [
            c.project for c in thread_stack if c.is_linked()]
    except SQLAlchemyError as e:
        error = e.orig
    except Exception as e:
        error = str(e)
    else:
        result = True

    # found linked projects
    return {'projects_sharing_that_rev': projects_sharing_that_rev,
            'result': result,
            'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='macro_fetch', renderer='json', permission='edit')
def edit_a_macro(request):
    """
    """
    result = False
    macro_id = request.matchdict['macro_id']

    macro = request.dbsession.query(Macro).options(
        joinedload(Macro.relations)).get(macro_id)
    macro_relations = macro.relations

    map_relations = {}

    if macro_relations is not None and len(macro_relations) > 0:
        for relation in macro_relations:
            direction = relation.direction
            id_third_project = relation.id_third_project
            map_relations[id_third_project] = direction
        result = True
    else:
        result = False

    return {'result': result,
            'map_relations': map_relations,
            'label': macro.label}

# ------------------------------------------------------------------------------


@view_config(
    route_name='macros',
    renderer='templates/macros.mako',
    permission='edit')
def view_all_macros(request):
    """
    """
    result = False
    error = None
    dict_project_to_macros = OrderedDict()

    try:
        _default_login = request.registry.settings['hg_delivery.default_login']
        if _default_login == request.authenticated_userid:
            macros = request.dbsession.query(Macro)\
                .join(Project)\
                .options(joinedload(Macro.relations))\
                .order_by(Project.name.desc())\
                .all()
        else:
            macros = request.dbsession.query(Macro)\
                .join(Project)\
                .join(Acl)\
                .filter(Acl.acl == 'edit')\
                .join(User)\
                .filter(User.id == request.user.id)\
                .options(joinedload(Macro.relations))\
                .order_by(Project.name.desc())\
                .all()

        for macro in macros:
            project = macro.project
            if project in dict_project_to_macros:
                dict_project_to_macros[project].append(macro)
            else:
                dict_project_to_macros[project] = [macro]
    except SQLAlchemyError as e:
        result = False
        error = e.orig
    except Exception as e:
        result = False
        error = str(e)
    else:
        result = True

    return {'result': result,
            'error': error,
            'dict_project_to_macros': dict_project_to_macros}

# ------------------------------------------------------------------------------


@view_config(
    route_name='macro_refresh',
    renderer='templates/edit#publish_project_macros.mako',
    permission='edit')
def refresh_macros(request):
    """
      re-publish the list of macros ....
    """
    id_project = request.matchdict['id']
    project = request.dbsession.query(Project).get(id_project)

    project_macros = request.dbsession.query(
        Macro).filter(Macro.id_project == id_project).all()

    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        projects_list = request.dbsession.query(Project)\
            .order_by(Project.name.desc())\
            .all()
    else:
        projects_list = request.dbsession.query(Project)\
            .join(Acl)\
            .filter(Acl.acl == 'edit')\
            .join(User)\
            .filter(User.id == request.user.id)\
            .order_by(Project.name.desc())\
            .all()

    linked_projects = [p for p in projects_list
                       if (p.rev_init is not None and p
                           .rev_init == project.rev_init and p
                           .id != project.id)]

    return {'project_macros': project_macros,
            'project': project,
            'linked_projects': linked_projects}

# ------------------------------------------------------------------------------


@view_config(route_name='macro_delete', renderer='json')
def delete_a_macro(request):
    """
      create a macro on a specific project.
      A macro is a list of bind project that shall be push or pull
    """
    error = None
    result = False
    try:
        macro_id = request.matchdict['macro_id']
        macro = request.dbsession.query(Macro).get(macro_id)
        request.dbsession.delete(macro)
        request.dbsession.flush()
        result = True
    except BaseException:
        request.dbsession.rollback()
        result = False
        error = 'Unable to delete macro'

    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='macro_update', renderer='json', permission='edit')
def update_a_macro(request):
    """
      update a specific macro on a specific project.
      A macro is a list of bind project that shall be push or pull
    """
    result = False
    explanation = None

    if 'macro_id' not in request.matchdict:
        explanation = "bad parameter"
    else:
        try:
            macro_id = request.matchdict['macro_id']
            macro = request.dbsession.query(Macro).options(
                joinedload(Macro.relations)).get(macro_id)

            # a name is mandatory for the macro ...
            macro_name = None
            if macro is not None and 'macro_name' in request.params:
                try:
                    macro_name = request.params['macro_name']
                    macro_content = {}

                    for _param in request.params:
                        if re.match(
                                '^direction_[0-9]{1,}',
                                _param) and request.params[_param] in {
                                'push',
                                'pull'}:
                            aim_id_project = _param.split('_')[1]
                            aim_value = request.params[_param]
                            macro_content[aim_id_project] = aim_value

                    if macro_name and len(macro_name) > 1\
                       and len(macro_content) > 0:
                        macro.label = macro_name

                        # delete previous relationship
                        for macro_relation in macro.relations:
                            request.dbsession.delete(macro_relation)

                        macro.relations[0:] = []

                        for _p_id in macro_content:
                            _dir = macro_content[_p_id]
                            macro_relation = MacroRelations(_p_id, _dir)
                            request.dbsession.add(macro_relation)
                            macro.relations.append(macro_relation)

                        request.dbsession.flush()
                        result = True
                except IntegrityError as e:
                    request.dbsession.rollback()
                    result = False
                    explanation = u'This macro has already been define  ...'
                    log.error(e)

        except SQLAlchemyError as e:
            request.dbsession.rollback()
            result = False
            explanation = e.orig

    return {'result': result, 'explanation': explanation}

# ------------------------------------------------------------------------------
@view_config(route_name='macro_add', renderer='json', permission='edit')
def create_a_macro(request):
    """
      create a macro on a specific project.
      A macro is a list of bind project that shall be push or pull
    """
    id_project = request.matchdict['id']
    result = False
    error = None

    # a name is mandatory for the macro ...
    macro_name = None
    try:
      if request.dbsession.query(Project)\
                .filter(Project.id == id_project)\
                .count() == 0:
          error = "source project is unknown"
      elif 'macro_name' in request.params:
          macro_name = request.params['macro_name']

          macro_content = {}

          for _param in request.params:
              if re.match(
                      '^direction_[0-9]{1,}',
                      _param) and request.params[_param] in {
                      'push',
                      'pull'}:
                  aim_id_project = _param.split('_')[1]
                  aim_value = request.params[_param]

                  if request.dbsession.query(Project)\
                                      .filter(Project.id == aim_id_project)\
                                      .count() == 1:
                      macro_content[aim_id_project] = aim_value
              elif re.match('^direction_.*$', _param) is not None:
                  error = 'wrong format'

          if macro_name and len(macro_name) > 1 and len(macro_content) > 0:
              macro = Macro(id_project, macro_name)
              request.dbsession.add(macro)

              for _p_id in macro_content:
                  macro_relation = MacroRelations(_p_id, macro_content[_p_id])
                  request.dbsession.add(macro_relation)
                  macro.relations.append(macro_relation)
              request.dbsession.flush()
              result = True
          elif error is None:
              error = "aim project is unknown"
      else:
          error = "macro label is mandatory"
    except BaseException:
        request.dbsession.rollback()
        result = False
        error = "database error"

    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='macro_run', renderer='json', permission='edit')
def run_a_macro(request):
    """
      Run a macro

      hum ... if push, could we push with thread ?
      shall we check to whom we need to push

      first ... : pull
      then  ....: all the push execution ...

    """
    result = True
    new_branch_stop = False
    new_head_stop = False
    force_branch = False
    lst_new_branches = []
    project_errors = []
    buffers_output = {}
    data = {}

    if 'force_branch' in request.params\
            and request.params['force_branch'] == 'true':
        force_branch = True

    id_project = request.matchdict['id']
    project = request.dbsession.query(Project).get(id_project)

    macro_id = request.matchdict['macro_id']
    macro = request.dbsession.query(Macro).options(
        joinedload(Macro.relations)).get(macro_id)

    projects_id_set = set()
    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        projects_id_set = {
            p.id for p in request.dbsession.query(Project).order_by(
                Project.name.desc())}
    else:
        projects_id_set = {p.id for p in request.dbsession.query(Project)
                           .join(Acl)
                           .filter(Acl.acl == 'edit')
                           .join(User)
                           .filter(User.id == request.user.id)
                           .order_by(Project.name.desc())}

    for relation in macro.relations:

        aim_project = relation.aim_project

        # user must have an access to this project
        if aim_project and aim_project.id not in projects_id_set:
            result = False
            project_errors.append(aim_project.name)
            _msg = u"user don't have access to %s" % aim_project.name
            buffers_output[aim_project.name] = _msg
            continue

        # if user don't have access to this project we just pass
        # because a macros is across several projects
        # it's meanless

        # shall we display a macro if user has access to all projects
        # included the source project ...

        direction = relation.direction
        __result = True
        data = {}

        if project and aim_project and direction == 'push':

            ssh_node = None
            ssh_node_remote = None

            try:
                with NodeController(project) as ssh_node:
                    data = ssh_node.push_to(project, aim_project, force_branch)
            except UnavailableConnexion as e:
                __result = False
                log.debug(e)
                project_errors.append(aim_project.name)
            except HgNewBranchForbidden as e:
                # we may inform user that he cannot push ...
                # maybe add a configuration parameter to fix this
                # and send --new-branch directly on the first time
                new_branch_stop = True
                __result = False

                set_local_branches = set()
                with NodeController(project, silent=True) as ssh_node:
                    set_local_branches = set(ssh_node.get_branches())

                try:
                    with NodeController(aim_project) as ssh_node_remote:
                        set_remote_branches = set(
                            ssh_node_remote.get_branches())
                        lst_new_branches = list(
                            set_local_branches - set_remote_branches)
                        data = e.value
                except BaseException as e:
                    log.error(e)

                project_errors.append(aim_project.name)
            except HgNewHeadsForbidden as e:
                # we may inform user that he cannot push ...
                # maybe add a configuration parameter to fix this
                # and send --new-branch directly on the first time
                new_head_stop = True
                __result = False
                lst_new_branches = []
                buffers_output[aim_project.name] = e.value.get('buff')
                project_errors.append(aim_project.name)
            except (OutputErrorCode, OutputError) as e:
                # we may inform user that push has not finished correctly :/
                __result = False
                project_errors.append(aim_project.name)
                buffers_output[aim_project.name] = e.value.get('buff')
            else:
                __result = True

        elif project and aim_project and direction == 'pull':

            with NodeController(project, silent=True) as ssh_node:
                ssh_node.pull_from(project, aim_project)
                __result = True

        result &= __result

    return {'new_branch_stop': new_branch_stop,
            'new_head_stop': new_head_stop,
            'lst_new_branches': lst_new_branches,
            'project_errors': project_errors,
            'buffers': buffers_output,
            'result': result,
            'data': data}

# ------------------------------------------------------------------------------


@view_config(route_name='project_push_to', renderer='json', permission='edit')
def push(request):
    """
    """
    id_project = request.matchdict['id']
    id_target_project = request.matchdict['target']

    project = request.dbsession.query(Project).get(id_project)
    target_project = request.dbsession.query(Project).get(id_target_project)

    new_branch_stop = False
    new_head_stop = False
    result = False
    force_branch = False
    lst_new_branches = []
    data = {'buff': ''}

    if project and target_project:

        if 'force_branch' in request.params\
                and request.params['force_branch'] == 'true':
            force_branch = True

        ssh_node = None
        ssh_node_remote = None

        try:
            with NodeController(project) as ssh_node:
                data = ssh_node.push_to(project, target_project, force_branch)
        except HgNewBranchForbidden as e:
            # we may inform user that he cannot push ...
            # maybe add a configuration parameter to fix this
            # and send --new-branch directly on the first time
            new_branch_stop = True
            result = False

            set_local_branches = set()
            with NodeController(project, silent=True) as ssh_node:
                set_local_branches = set(ssh_node.get_branches())

            try:
                with NodeController(target_project) as ssh_node_remote:
                    set_remote_branches = set(ssh_node_remote.get_branches())
                    lst_new_branches = list(
                        set_local_branches - set_remote_branches)
                    data = e.value
            except BaseException:
                data = {}
        except HgNewHeadsForbidden as e:
            # we may inform user that he cannot push ...
            # maybe add a configuration parameter to fix this
            # and send --new-branch directly on the first time
            new_head_stop = True
            result = False
            lst_new_branches = []
            data = e.value
        except (OutputErrorCode, OutputError) as e:
            # we may inform user that push has not finished correctly :/
            result = False
            data = e.value
        else:
            result = True

    return {'new_branch_stop': new_branch_stop,
            'new_head_stop': new_head_stop,
            'lst_new_branches': lst_new_branches,
            'buffer': data.get('buff'),
            'result': result}

# ------------------------------------------------------------------------------


@view_config(route_name='project_pull_from', renderer='json', permission='edit')
def pull(request):
    """
    """
    error = None
    result = False

    if 'id' not in request.matchdict:
      error = 'bad parameter'
    elif 'source' not in request.matchdict:
      error = 'bad parameter'
    else:
        try:
            id_project = request.matchdict['id']
            id_source = request.matchdict['source']

            project = request.dbsession.query(Project).get(id_project)
            source_project = request.dbsession.query(Project).get(id_source)

            with NodeController(project, silent=True) as ssh_node:
                ssh_node.pull_from(project, source_project)
        except SQLAlchemyError as e:
            request.dbsession.rollback()
            error = e.orig
        except Exception as e:
            request.dbsession.rollback()
            error = str(e)
        else:
            result = True
    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='project_add', renderer='json', permission='edit')
def add_project(request):
    """
    create a new project
    """
    result = False
    explanation = None

    name = request.params.get('name')
    user = request.params.get('user')
    password = request.params.get('password', '')
    host = request.params.get('host')
    path = request.params.get('path')

    if name is None or not name:
        explanation = "Missing project name"
    elif user is None or not user:
        explanation = "Missing project user"
    elif host is None or not host:
        explanation = "Missing project host"
    elif path is None or not path:
        explanation = "Missing project path"
    else:
        local_pkey = request.params.get('local_pkey', False)
        if local_pkey == '0':
            local_pkey = False
        elif local_pkey == '1':
            local_pkey = True
        else:
            local_pkey = False

        # if pkey is used : force password to 0
        if local_pkey is True or local_pkey == '1':
            password = ''

        rev_init = request.params.get('rev_init')

        dashboard = request.params.get('dashboard', False)
        if dashboard == '1' or dashboard == 1:
            dashboard = True
        else:
            dashboard = False

        dvcs_release = request.params.get('dvcs_release')
        no_scan = request.params.get('no_scan', False)
        if no_scan == '1' or no_scan == 1:
            no_scan = True
        else:
            no_scan = False

        group_label = request.params.get('group_label')

        if not host:
            explanation = u'Your project should contain a valid hostname'
        elif not path:
            explanation = u'Your project should contain a valid path'
        elif not user:
            explanation = u'Your project should contain a valid user'
        elif not name:
            explanation = u'Your project should contain a valid name'
        elif not local_pkey and not password:
            explanation = u'Your project should contains password or local pkey'
        else:
            try:
                # folder should be unique
                project = Project(
                    name,
                    user,
                    password,
                    host,
                    path,
                    rev_init,
                    dashboard,
                    dvcs_release,
                    no_scan,
                    local_pkey)

                request.dbsession.add(project)
                Project.set_group(request.dbsession, project, group_label)
                request.dbsession.flush()

                project.init_initial_revision()
                request.dbsession.flush()

                result = True
                _msg = u'This project : %s@%s/%s has been added ...'
                explanation = _msg % (user, host, path)
            except IntegrityError as e:
                request.dbsession.rollback()
                result = False
                _msg = u'This project and this path'
                _msg += u' are already defined (%s %s) ...'
                explanation = _msg % (host, path)
                log.error(e)
            except NodeException as e:
                request.dbsession.rollback()
                result = False
                _msg = u'Please check password, host, path (%s %s)'
                _msg += u' before adding this project... '
                explanation = _msg % (host, path)
                log.error(e)
            except UnavailableConnexion as e:
                request.dbsession.rollback()
                result = False
                log.debug(e)
                explanation = e.value + " (%s:%s)" % (host, path)
            except NoValidConnectionsError as e:
                request.dbsession.rollback()
                result = False
                lb = u'No valid connection error to host (%s)... '
                explanation = lb % (host)
                log.error(e)
            except Exception as e:
                request.dbsession.rollback()
                result = False
                if hasattr(e, 'value'):
                    explanation = e.value
                    log.error(e.value)
                else:
                    log.error(e)
                    # try to cast it as a string
                    try:
                        explanation = str(e)
                    except BaseException:
                        explanation = u"Project can't be added"
                result = False

    return {'result': result,
            'explanation': explanation}

# ------------------------------------------------------------------------------


@view_config(route_name='project_update', renderer='json', permission='edit')
def update_project(request):
    """
    update the project properties (host, path, password ...)
    """
    result = False
    id_project = request.matchdict['id']

    name = request.params['name']
    user = request.params['user']
    password = request.params.get('password', '')

    local_pkey = request.params.get('local_pkey', False)
    if local_pkey == '0':
        local_pkey = False
    elif local_pkey == '1':
        local_pkey = True
    else:
        local_pkey = False

    host = request.params['host']
    path = request.params['path']

    dashboard = request.params.get('dashboard', False)
    if dashboard == '1' or dashboard == 1:
        dashboard = True
    else:
        dashboard = False
    no_scan = request.params.get('no_scan', False)
    if no_scan == '1' or no_scan == 1:
        no_scan = True
    else:
        no_scan = False
    group_label = request.params.get('group_label', '').strip()

    project = None
    explanation = None

    if not host:
        explanation = u'Your project should contain a valid hostname'
    elif not path:
        explanation = u'Your project should contain a valid path'
    elif not user:
        explanation = u'Your project should contain a valid user'
    elif not name:
        explanation = u'Your project should contain a valid name'
    else:
        try:
            project = request.dbsession.query(Project).get(id_project)

            project.name = name
            project.user = user
            project.password = password
            project.host = host
            project.path = path
            project.dashboard = dashboard
            project.no_scan = no_scan
            project.local_pkey = local_pkey

            Project.set_group(request.dbsession, project, group_label)

            request.dbsession.flush()
            explanation = u'This project : %s@%s/%s has been updated ...' % (
                user, host, path)
            result = True
        except BaseException:
            request.dbsession.rollback()
            result = False

    return {'result': result,
            'project': project,
            'explanation': explanation}

# ------------------------------------------------------------------------------


@view_config(route_name='view_file_content', permission='edit')
def get_file_content(request):
    """
    view file content regarding to revision id
    """
    id_project = request.matchdict['id']
    revision = request.matchdict['rev']
    file_name = "/".join(request.matchdict['file_name'])
    project = request.dbsession.query(Project).get(id_project)
    data = ""
    with NodeController(project, silent=True) as ssh_node:
        data = ssh_node.get_content(revision, file_name)
    response = Response(data)
    return response

# ------------------------------------------------------------------------------


@view_config(route_name='project_delete', renderer='json', permission='edit')
def delete_project(request):
    """
    delete a project
    """
    result = False
    error = None
    if 'id' not in request.matchdict:
        error = 'bad parameter'
    else:
        try:
            id_project = request.matchdict['id']
            project = request.dbsession.query(Project).get(id_project)
            if project is not None:
                project.delete_nodes()
                # also delete macros or relation that target that project
                request.dbsession.delete(project)
                request.dbsession.flush()
                result = True
            else:
                error = 'unknown project'
        except SQLAlchemyError as e:
            request.dbsession.rollback()
            error = e.orig
        except Exception as e:
            request.dbsession.rollback()
            error = str(e)

    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(route_name='projects_list',
             renderer='templates/lib#publish_projects_list.mako')
@view_config(route_name='projects_list_global',
             renderer='templates/lib#publish_projects_list.mako')
def view_projects_list(request):

    project = None

    if 'id' in request.matchdict:
        id_project = request.matchdict['id']
        project = request.dbsession.query(Project).get(id_project)

    projects_list = []

    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        projects_list = request.dbsession.query(Project)\
            .options(joinedload(Project.groups))\
            .order_by(Project.name.desc())\
            .all()
    else:
        projects_list = request.dbsession.query(Project)\
            .options(joinedload(Project.groups))\
            .join(Acl)\
            .join(User)\
            .filter(User.id == request.user.id)\
            .order_by(Project.name.desc())\
            .all()

    return {'project': project, 'projects_list': projects_list, 'result': True}

# ------------------------------------------------------------------------------


@view_config(route_name='project_refresh_state',
             renderer='json', permission='edit')
@view_config(route_name='project_edit', renderer='edit.mako', permission='read')
def edit_project(request):
    """
    """
    delivered = False
    id_project = request.matchdict['id']

    projects_list = []
    projects_list_protected = []

    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        projects_list = request.dbsession.query(Project)\
            .options(joinedload(Project.groups))\
            .order_by(Project.name.desc())\
            .all()
        projects_list_protected = projects_list
    else:
        projects_list = request.dbsession.query(Project)\
            .join(Acl)\
            .join(User)\
            .options(joinedload(Project.groups))\
            .filter(User.id == request.user.id)\
            .order_by(Project.name.desc())\
            .all()

        projects_list_protected = request.dbsession.query(Project)\
            .join(Acl)\
            .filter(Acl.acl == 'edit')\
            .join(User)\
            .filter(User.id == request.user.id)\
            .options(joinedload(Project.groups))\
            .order_by(Project.name.desc())\
            .all()

    projects_map = {p.id: p for p in projects_list}
    project = projects_map.get(id_project)

    if project is None:
        return HTTPFound(location=request.route_path(route_name='home'))

    repository_error = None
    try:
        if not project.is_initial_revision_init():
            project.init_initial_revision()
    except NoValidConnectionsError as e:
        repository_error = u'No valid connection error to host (%s)... ' % (
            project.host)
        log.error(
            u'No valid connection error to host (%s)... ' %
            (project.host))
        log.error(e)
    except ValueError as e:
        repository_error = u'No key available (%s)... ' % (
            project.host)
        log.error(
            u'No valid connection error to host (%s)... ' %
            (project.host))
        log.error(e)
    except Exception as e:
        repository_error = u'No valid connection error to host (%s)... ' % (
            project.host)
        log.error(
            u'No valid connection error to host (%s)... ' %
            (project.host))
        log.error(e)
    except:
        repository_error = u'No valid connection error to host (%s)... ' % (
            project.host)
        log.error(
            u'No valid connection error to host (%s)... ' %
            (project.host))

    # while editing this project, we also check non inited projects
    # shall we ?
    # for p in projects_list :
    #   if not p.is_initial_revision_init():
    #     p.init_initial_revision()

    delivered_hash = {}
    for l in request.dbsession.query(
        RemoteLog.command, RemoteLog.creation_date) .order_by(
        RemoteLog.creation_date.desc()) .filter(
            RemoteLog.id_project == id_project) .filter(
                RemoteLog.command.like('%hg update -C -r%')) .limit(200):
        if l.command.count('hg update -C -r'):
            hash_rev = l.command.split('hg update -C -r ')[1].strip()
            if hash_rev in delivered_hash:
                delivered_hash[hash_rev].append(
                    l.creation_date.strftime('%d/%m/%Y %H:%M:%S'))
            else:
                delivered_hash[hash_rev] = [
                    l.creation_date.strftime('%d/%m/%Y %H:%M:%S')]

    linked_projects = [p for p in projects_list_protected
                       if (p.rev_init is not None and p
                            .rev_init == project.rev_init and p
                            .id != project.id and p
                            .is_initial_revision_init())]

    branch = None
    if 'branch' in request.params:
        branch = request.params['branch']

    if 'delivered' in request.params:
        delivered = request.params['delivered']
        if delivered == 'on':
            delivered = True

    tag = None
    if 'tag' in request.params:
        tag = request.params['tag']
        if len(tag) > 0:
            delivered = False

    limit = 200
    settings = request.registry.settings
    if 'hg_delivery.default_log_limit' in settings\
            and settings['hg_delivery.default_log_limit'].isdigit():
        limit = int(settings['hg_delivery.default_log_limit'])

    request.registry.settings
    if 'limit' in request.params and request.params['limit'].isdigit():
        limit = int(request.params['limit'])

    users = request.dbsession.query(User).all()

    project_acls = {
        _acl.id_user: _acl.acl for _acl in request.dbsession.query(Acl).filter(
            Acl.id_project == id_project)}
    project_tasks = request.dbsession.query(
        Task).filter(Task.id_project == id_project).all()
    project_macros = request.dbsession.query(
        Macro).filter(Macro.id_project == id_project).all()

    try:
        with NodeController(project) as ssh_node:
            if not project.dvcs_release:
                project.dvcs_release = ssh_node.get_release()

            current_rev = ssh_node.get_current_rev_hash()

            if delivered and not tag:
                (last_hundred_change_list,
                 map_change_sets) = ssh_node.get_last_logs(
                    limit, branch_filter=branch,
                    revision_filter=iter(delivered_hash))
                last_hundred_change_list = sorted(
                    last_hundred_change_list, key=lambda e: int(
                        e['rev']), reverse=True)
            else:
                (last_hundred_change_list,
                 map_change_sets) = ssh_node.get_last_logs(
                    limit, branch_filter=branch, revision_filter=tag)

            list_branches = ssh_node.get_branches()
            list_tags = ssh_node.get_tags()

            current_node = map_change_sets.get(current_rev)
            if current_node is None:
                current_node = ssh_node.get_revision_description(current_rev)
    except NodeException as e:
        repository_error = e.value
        log.debug(e.value)
        current_node = None
        list_branches = []
        list_tags = []
        last_hundred_change_list, map_change_sets = [], {}
    except UnavailableConnexion as e:
        repository_error = e.value + " (%s:%s)" % (project.host, project.path)
        log.debug(e.value)
        current_node = None
        list_branches = []
        list_tags = []
        last_hundred_change_list, map_change_sets = [], {}
    except NoValidConnectionsError as e:
        repository_error = u'No valid connection error to host (%s)... ' % (
            project.host)
        log.error(
            u'No valid connection error to host (%s)... ' %
            (project.host))
        log.debug(e)
        current_node = None
        list_branches = []
        list_tags = []
        last_hundred_change_list, map_change_sets = [], {}
    except OSError as e:
        repository_error = "Host seems not available. Fix this network issue"
        log.error("Host seems not available. Fix this network issue")
        current_node = None
        list_branches = []
        list_tags = []
        last_hundred_change_list, map_change_sets = [], {}
        log.debug(e)
    except Exception as e:
        if hasattr(e, 'value'):
            repository_error = e.value
            log.debug(e.value)
        else:
            log.debug(e)

        current_node = None
        list_branches = []
        list_tags = []
        last_hundred_change_list, map_change_sets = [], {}

    allow_to_modify_acls = False
    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        allow_to_modify_acls = True

    for node in last_hundred_change_list:
        node['url_detail'] = request.route_path(
            route_name='project_revision_details_json',
            id=project.id,
            rev=node['node'])
        node['url_change_to'] = request.route_path(
            'project_change_to', id=project.id, rev=node['node'], brother_id=[])
        node['url_refresh'] = request.route_path(
            'project_refresh_state', id=project.id)
        node['url_brothers_update_check'] = request.route_path(
            'project_brothers_update_check', id=project.id, rev=node['node'])

    return {'project': project,
            'list_branches': list_branches,
            'list_tags': list_tags,
            'limit': limit,
            'projects_list': projects_list,
            'filter_tag': tag,
            'filter_branch': branch,
            'repository_error': repository_error,
            'current_node': current_node,
            'linked_projects': linked_projects,
            'last_hundred_change_list': last_hundred_change_list,
            'users': users,
            'allow_to_modify_acls': allow_to_modify_acls,
            'project_acls': project_acls,
            'project_tasks': project_tasks,
            'project_macros': project_macros,
            'knonwn_acl': Acl.known_acls,
            'delivered_hash': delivered_hash,
            'delivered': delivered}

# ------------------------------------------------------------------------------


@view_config(route_name='project_run_task', renderer='json', permission='edit')
def run_task(request):
    """
    """
    id_task = request.matchdict['id']
    task = request.dbsession.query(Task).get(id_task)
    result = False
    explanation = u""

    if task:
        try:
            with NodeController(task.project) as ssh_node:
                ssh_node.run_command(task.content, log=True)
        except NodeException as e:
            result = False
            explanation = e.value
            log.debug(e)
        except UnavailableConnexion as e:
            result = False
            explanation = e.value + " (%s:%s)" % (task.project.host,
                                                  task.project.path)
            log.debug(e)
        except OutputErrorCode as e:
            result = False
            _msg = u"Task return an error code : %s (different than 0)"
            explanation = _msg % e.value
            log.debug(e)
        except IntegrityError as e:
            result = False
            explanation = u"wtf ?"
            log.debug(e)
        else:
            result = True

    return {'result': result, 'explanation': explanation}

# ------------------------------------------------------------------------------


@view_config(
    route_name='tasks',
    renderer='templates/tasks.mako',
    permission='edit')
def view_all_tasks(request):
    """
    """
    result = False
    error = None
    dict_project_to_tasks = OrderedDict()
    try:
        _default_login = request.registry.settings['hg_delivery.default_login']
        if _default_login == request.authenticated_userid:
            tasks = request.dbsession.query(Task)\
                .join(Project)\
                .options(joinedload(Task.project))\
                .order_by(Project.name.desc())\
                .all()
        else:
            tasks = request.dbsession.query(Task)\
                .join(Project)\
                .join(Acl)\
                .filter(Acl.acl == 'edit')\
                .join(User)\
                .filter(User.id == request.user.id)\
                .options(joinedload(Task.project))\
                .order_by(Project.name.desc())\
                .all()

        for task in tasks:
            project = task.project
            if project in dict_project_to_tasks:
                dict_project_to_tasks[project].append(task)
            else:
                dict_project_to_tasks[project] = [task]
    except SQLAlchemyError as e:
        error = e.orig
    except Exception as e:
        error = str(e)
    else:
        result = True

    return {'result': result,
            'dict_project_to_tasks': dict_project_to_tasks,
            'error': error}

# ------------------------------------------------------------------------------


@view_config(
    route_name='project_delete_task',
    renderer='json',
    permission='edit')
def remove_project_task(request):
    """
      remove some task on project
    """
    result = False
    error = None

    if 'id' not in request.matchdict:
        error = 'bad parameter'
    else:
        id_task = request.matchdict['id']
        try:
            task = request.dbsession.query(Task).get(id_task)
            request.dbsession.delete(task)
        except IntegrityError as e:
            result = False
            error = e.orig
            log.debug(e)
        except SQLAlchemyError as e:
            result = False
            error = e.orig
            log.debug(e)
        except Exception as e:
            result = False
            error = str(e)
            log.debug(e)
        else:
            result = True

    return {'result': result, 'error': error}

# ------------------------------------------------------------------------------


@view_config(
    route_name='project_save_tasks',
    renderer='json',
    permission='edit')
def save_project_tasks(request):
    """
    """
    id_project = request.matchdict['id']
    project = request.dbsession.query(Project).get(id_project)
    result = False

    if project:
        try:
            # we remove old tasks
            project.tasks[0:] = []
            for _task_content in request.params.getall('task_content'):
                if _task_content:
                    task = Task(id_project, _task_content.strip())
                    # make the link with request.dbsession ...
                    request.dbsession.add(task)
                    project.tasks.append(task)
            request.dbsession.flush()
            result = True
        except IntegrityError as e:
            result = False
            request.dbsession.rollback()
            log.debug(e)

    return {'result': result, 'tasks': project.tasks}

# ------------------------------------------------------------------------------


@view_config(route_name='user_acls', renderer='json', permission='edit')
def get_user_acls(request):
    """
    """
    id_user = request.matchdict['id']
    user = request.dbsession.query(User).get(id_user)

    result = False
    acls = []

    if user:
        result = True
        acls = user.acls

    return {'result': result,
            'acls': acls,
            'known_acls': Acl.known_acls}

# ------------------------------------------------------------------------------


@view_config(route_name='users_save_acls', renderer='json', permission='edit')
def save_users_acls(request):
    """
    """
    map_project_users_ace = {}

    try:
        for ele, _acl_label in request.params.iteritems():
            id_project, id_user = (int(_e) for _e in ele.split('__'))
            if id_project in map_project_users_ace:
                map_project_users_ace[id_project][id_user] = _acl_label
            else:
                map_project_users_ace[id_project] = {id_user: _acl_label}

        for id_project in map_project_users_ace:
            project = request.dbsession.query(Project).get(id_project)
            if project is not None:
                project.acls[0:] = []
                for id_user in map_project_users_ace[id_project]:
                    _acl_label = map_project_users_ace[id_project][id_user]
                    if _acl_label in Acl.known_acls:
                        acl = Acl(id_user, id_project, _acl_label)
                        request.dbsession.add(acl)
                        project.acls.append(acl)
        request.dbsession.flush()

    except IntegrityError as e:
        request.dbsession.rollback()
        log.debug(e)

    return HTTPFound(location=request.route_path(route_name='users'))

# ------------------------------------------------------------------------------


@view_config(route_name='project_save_acls', renderer='json', permission='edit')
def save_project_acls(request):
    """
    """
    id_project = request.matchdict['id']
    project = request.dbsession.query(Project).get(id_project)

    result = False

    if project:
        try:
            # we remove old ACLs
            project.acls[0:] = []
            for ele, _acl_label in request.params.iteritems():
                if ele.count('projectacl') and _acl_label in Acl.known_acls:

                    # create acl object
                    id_user = int(ele.split('_')[1])
                    acl = Acl(id_user, id_project, _acl_label)

                    # make the link with request.dbsession ...
                    request.dbsession.add(acl)
                    project.acls.append(acl)

            request.dbsession.flush()
            result = True
        except IntegrityError as e:
            log.debug(e)
            request.dbsession.rollback()
            result = False

    return {'result': result}

# ------------------------------------------------------------------------------


@view_config(route_name='project_fetch', renderer='json', permission='edit')
def fetch_project(request):
    """
    retrieve information about a project and send result in json
    this view is usable to compare projects
    """
    id_project = request.matchdict['id']
    project = request.dbsession.query(Project).get(id_project)

    branch = None
    if 'branch' in request.params:
        branch = request.params['branch']

    limit = 200
    if 'limit' in request.params and request.params['limit'].isdigit():
        limit = int(request.params['limit'])

    repository_error = None

    try:
        with NodeController(project) as ssh_node:
            last_hundred_change_list, map_change_sets = ssh_node.get_last_logs(
                limit, branch_filter=branch)
    except NodeException as e:
        repository_error = e.value
        last_hundred_change_list = []
        log.debug(e)
    except UnavailableConnexion as e:
        repository_error = e.value + " (%s:%s)" % (project.host, project.path)
        last_hundred_change_list = []
        log.debug(e)

    return {'repository_error': repository_error,
            'last_hundred_change_list': last_hundred_change_list}

# ------------------------------------------------------------------------------


@view_config(
    route_name='project_revision_details',
    renderer='templates/revision.mako',
    permission='edit')
@view_config(
    route_name='project_revision_details_json',
    renderer='json',
    permission='edit')
def fetch_revision(request):
    """
    """
    id_project = request.matchdict['id']
    revision = request.matchdict['rev']

    project = request.dbsession.query(Project).get(id_project)

    diff = ""
    revision_description = {}

    with NodeController(project, silent=True) as ssh_node:
        diff = ssh_node.get_revision_diff(revision)
        revision_description = ssh_node.get_revision_description(revision)

    return {'diff': diff,
            'project': project,
            'revision': revision_description}

# ------------------------------------------------------------------------------


@view_config(route_name='project_change_to', permission='edit', renderer='json')
def update_project_to(request):
    """
    """
    id_project = request.matchdict['id']
    run_task_flag = request.params.get('run_task_flag', False)
    if run_task_flag == 'true':
        run_task_flag = True
    else:
        run_task_flag = False

    brothers_id_project = list(request.matchdict['brother_id'])
    brothers_id_project.append(id_project)

    revision = request.matchdict['rev']
    projects_to_update = [request.dbsession.query(Project).options(joinedload(
        Project.tasks)).get(_id_project) for _id_project in brothers_id_project]

    thread_stack = []

    for __p in projects_to_update:
        new_thread = SpeedUpdater(__p, revision, run_task_flag=run_task_flag)
        thread_stack.append(new_thread)
        new_thread.start()

    t0 = time.time()
    while sum([e.is_stopped() for e in thread_stack]) != len(
            projects_to_update) or time.time() > (t0 + 10 * 60):
        time.sleep(0.005)

    # harvest additional tasks exceptions
    task_abnormal = {}
    for thread in thread_stack:
        side_exceptions = thread.get_tasks_exceptions()
        if len(side_exceptions) > 0:
            task_abnormal[thread.project.id] = []
        for task_exception_value in side_exceptions:
            task_abnormal[thread.project.id].append(task_exception_value)

    result = {t.project.id: t.project_updated() for t in thread_stack}

    return {'result': result,
            'task_abnormal': task_abnormal}

# ------------------------------------------------------------------------------


@view_config(route_name='project_group_delete', permission='edit')
def delete_project_group(request):
    """
    delete a group (remove label and link between project and this group)
    """
    group_id = request.matchdict[u'id']
    group = request.dbsession.query(ProjectGroup).get(group_id)
    request.dbsession.delete(group)

    return HTTPFound(location=request.route_path(route_name='home'))

# ------------------------------------------------------------------------------


@view_config(route_name='group_detach', renderer='json')
def detach_project_from_that_group(request):
    """
    detach that group from the requested project
    """
    id_project = request.matchdict[u'id']
    id_group = request.matchdict[u'group_id']

    project = request.dbsession.query(Project).options(
        joinedload(Project.groups)).get(id_project)
    group = request.dbsession.query(ProjectGroup).get(id_group)

    redirect_url = None
    result = False

    if id_group in {g.id for g in project.groups}:
        project.groups[0:] = []
        result = True

        if group is not None and len(group.projects) == 0:
            request.dbsession.delete(group)
            redirect_url = request.route_path(route_name='home')

    request.dbsession.flush()

    return {'result': result, 'redirect_url': redirect_url}

# ------------------------------------------------------------------------------


@view_config(route_name='group_rename')
def rename_project(request):
    """
    rename the given group
    """
    group_id = request.matchdict[u'id']
    group = request.dbsession.query(ProjectGroup)\
        .get(group_id)
    group_name = request.params[u'name']

    response = HTTPFound(location=request.route_path(route_name='home'))

    if group is not None and group_name:
        response = HTTPFound(
            location=request.route_path(
                route_name='project_group_view',
                id=group.id))
        try:
            group.name = group_name
            request.dbsession.flush()
        except IntegrityError as e:
            log.debug(e)
    elif group:
        response = HTTPFound(
            location=request.route_path(
                route_name='project_group_view',
                id=group.id))
    else:
        response = HTTPFound(location=request.route_path(route_name='home'))

    return response

# ------------------------------------------------------------------------------


@view_config(
    route_name='project_group_view',
    renderer='view_group.mako',
    permission=Authenticated)
def view_project_group(request):
    """
    display a specific page for group content, description
    and related projects
    """
    group_id = request.matchdict[u'id']

    group = request.dbsession.query(ProjectGroup)\
        .options(joinedload(ProjectGroup.projects))\
        .get(group_id)

    _default_login = request.registry.settings['hg_delivery.default_login']
    if _default_login == request.authenticated_userid:
        projects_list = request.dbsession.query(Project)\
            .options(joinedload(Project.groups))\
            .order_by(Project.name.desc())\
            .all()
    else:
        projects_list = request.dbsession.query(Project)\
            .join(Acl)\
            .join(User)\
            .options(joinedload(Project.groups))\
            .filter(User.id == request.user.id)\
            .order_by(Project.name.desc())\
            .all()

    if _default_login == request.authenticated_userid:
        set_projects_list_id = {
            p_id for (
                p_id,
            ) in request.dbsession.query(
                Project.id)}
    else:
        set_projects_list_id = {
            p_id for (
                p_id,
            ) in request.dbsession.query(
                Project.id) .join(Acl) .join(User) .filter(
                User.id == request.user.id) .order_by(
                    Project.name.desc())}

    if group is not None:
        if _default_login == request.authenticated_userid:
            macros = request.dbsession.query(Macro)\
                .join(Project)\
                .filter(Project.id.in_((p.id for p in group.projects)))\
                .options(joinedload(Macro.relations))\
                .order_by(Project.name.desc())\
                .all()
        else:
            macros = request.dbsession.query(Macro)\
                .join(Project)\
                .join(Acl)\
                .filter(Acl.acl == 'edit')\
                .filter(Project.id.in_((p.id for p in group.projects)))\
                .join(User).filter(User.id == request.user.id)\
                .options(joinedload(Macro.relations))\
                .order_by(Project.name.desc())\
                .all()

        dict_project_to_macros = OrderedDict()
        for macro in macros:
            project = macro.project
            if project in dict_project_to_macros:
                dict_project_to_macros[project].append(macro)
            else:
                dict_project_to_macros[project] = [macro]

        if _default_login == request.authenticated_userid:
            tasks = request.dbsession.query(Task)\
                .join(Project)\
                .filter(Project.id.in_((p.id for p in group.projects)))\
                .options(joinedload(Task.project))\
                .order_by(Project.name.desc())\
                .all()
        else:
            tasks = request.dbsession.query(Task)\
                .join(Project)\
                .filter(Project.id.in_((p.id for p in group.projects)))\
                .join(Acl)\
                .filter(Acl.acl == 'edit')\
                .join(User)\
                .filter(User.id == request.user.id)\
                .options(joinedload(Task.project))\
                .order_by(Project.name.desc())\
                .all()

        dict_project_to_tasks = OrderedDict()
        for task in tasks:
            project = task.project
            if project in dict_project_to_tasks:
                dict_project_to_tasks[project].append(task)
            else:
                dict_project_to_tasks[project] = [task]

        # also load attached project into this group
        # also load tasks attached to all projects attached to this group
        # also load macros attached to all projects attached to this group

        return {'group': group,
                'dict_project_to_macros': dict_project_to_macros,
                'dict_project_to_tasks': dict_project_to_tasks,
                'set_projects_list_id': set_projects_list_id,
                'projects_list': projects_list
                }

    else:
        return HTTPFound(location=request.route_path(route_name='home'))

# ------------------------------------------------------------------------------
