# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    String,
    Boolean,
    ForeignKey,
    Enum,
    Table,
)

from sqlalchemy.orm import relationship

from .meta import Base

from ..nodes import PoolSsh, NodeController
from datetime import datetime

# ------------------------------------------------------------------------------

groups_projects_association = Table(
    'project_group_links', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('project_group_id', Integer, ForeignKey('project_group.id')))

# ------------------------------------------------------------------------------


class Project(Base):
    """
    The project item
    """
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user = Column(String(100))
    password = Column(String(100))
    host = Column(String(100))
    path = Column(Text)
    local_pkey = Column(Boolean)
    rev_init = Column(String(100))
    dvcs_release = Column(String(20))
    dashboard = Column(Boolean)
    no_scan = Column(Boolean)

    logs = relationship('RemoteLog', cascade='delete, delete-orphan')
    acls = relationship('Acl',
                        backref='project',
                        cascade='delete, delete-orphan')
    tasks = relationship('Task',
                         backref='project',
                         cascade='delete, delete-orphan')
    macros = relationship('Macro',
                          backref='project',
                          cascade='delete, delete-orphan')
    groups = relationship("ProjectGroup",
                          secondary=groups_projects_association,
                          back_populates="projects")

    def __init__(self, name, user, password, host, path, rev_init, dashboard,
                 dvcs_release, no_scan, local_pkey):
        """
        """
        self.name = name
        self.user = user
        self.password = password
        self.host = host
        self.path = path
        self.local_pkey = local_pkey
        self.rev_init = rev_init
        self.dashboard = dashboard
        self.no_scan = no_scan
        self.dvcs_release = dvcs_release

    @classmethod
    def set_group(cls, dbsession, project, group_label):
        # group_label shall exist and be length enough
        if group_label is not None and len(group_label.strip()) > 1:
            group = dbsession.query(ProjectGroup)\
                             .filter(ProjectGroup.name == group_label.strip())\
                             .scalar()
            if group is None:
                group = ProjectGroup(group_label.strip())
                dbsession.add(group)
            project.groups[0:] = [group]
        else:
            project.groups[0:] = []

    def __json__(self, request):
        """
        """
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'path': self.path,
            'user': self.user,
            'local_pkey': self.local_pkey,
            'password': '*' * len(self.password),
            'dashboard': self.dashboard,
            'no_scan': self.no_scan,
            'dvcs_release': self.dvcs_release
        }

    def get_uri(self):
        """
        uri as hg way ...
        """
        return "%s:%s@%s:%s" % (self.user, self.password, self.host, self.path)

    def get_ssh_node(self):
        """
        project id can't be None, because he will be pushed into pool
        and it's id will be required for logs and pool
        """
        uri = self.get_uri()

        if self.id is None:
            _e = "project needs to be serialized and"
            _e += " get an id before using it ..."
            raise Exception(_e)

        return PoolSsh.get_node(uri, self.id, local_pkey=self.local_pkey)

    def delete_nodes(self):
        """
          if project is deleted we should clean ssh nodes
          maybe this can be also done by an alchemy hook
        """
        uri = self.get_uri()
        return PoolSsh.delete_nodes(uri)

    def is_initial_revision_init(self):
        """
        """
        result = True
        if not self.rev_init or len(self.rev_init) < 35:
            result = False
        return result

    def init_initial_revision(self):
        """
        """
        if not self.is_initial_revision_init():
            with NodeController(self, silent=True) as ssh_node:
                _rev_init = ssh_node.get_initial_hash()
                if _rev_init != "0000000000000000000000000000000000000000":
                    self.rev_init = _rev_init


Index('project_unique', Project.host, Project.path, unique=True)
Index('project_root', Project.rev_init)

# ------------------------------------------------------------------------------


class RemoteLog(Base):
    """
    This table contains all logs entries
    which command user execute on which host and at what time
    """
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    id_project = Column(Integer, ForeignKey(Project.id))
    id_user = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref='logs')
    host = Column(String(100))
    path = Column(Text)
    command = Column(Text)
    creation_date = Column(DateTime)

    def __init__(self, id_project, id_user, host, path, command):
        """
        """
        self.id_project = id_project
        self.id_user = id_user
        self.creation_date = datetime.now()
        self.host = host
        self.path = path
        self.command = command

    def __json__(self, request):
        """
        """
        user_label = 'unknown'
        if self.user:
            user_label = self.user.email
        elif self.id_user == User.default_administrator_id:
            user_label = 'Administrator'

        return {
            'id': self.id,
            'user': user_label,
            'host': self.host,
            'path': self.path,
            'command': self.command.strip(),
            'creation_date': self.creation_date.strftime('%d/%m/%Y %H : %M')
        }


# ------------------------------------------------------------------------------


class Group(Base):
    """
    This table contains all users
    """
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    label = Column(String(100))
    creation_date = Column(DateTime)

    def __init__(self, label, creation_date):
        """
        """
        self.label = label
        self.creation_date = creation_date

    def __json__(self, request):
        """
        """
        return {
            'id': self.id,
            'label': self.label,
            'creation_date': self.creation_date.strftime('%d/%m/%Y %H : %M')
        }


# ------------------------------------------------------------------------------


class User(Base):
    """
    This table contains all users
    """
    __tablename__ = 'user'

    default_administrator_id = 666

    id = Column(Integer, primary_key=True)

    id_group = Column(Integer, ForeignKey(Group.id))
    group = relationship(Group, backref='users')
    acls = relationship('Acl', backref='user', cascade='delete, delete-orphan')

    name = Column(String(100))
    id_groupe = Column(Integer)
    pwd = Column(String(100))
    email = Column(String(100), unique=True)
    creation_date = Column(DateTime)

    def __init__(self, name, pwd, email, creation_date=None):
        """
        """
        self.name = name
        self.pwd = pwd
        self.email = email

        if creation_date is None:
            self.creation_date = datetime.now()

    def __json__(self, request):
        """
        """
        creation_date = None
        if self.creation_date:
            creation_date = self.creation_date.strftime('%d/%m/%Y %H:%M')

        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'pwd': self.pwd,
            'get_url': request.route_path(route_name='user_get', id=self.id),
            'delete_url': request.route_path(route_name='user_delete',
                                             id=self.id),
            'update_url': request.route_path(route_name='user_update',
                                             id=self.id),
            'group': self.group,
            'creation_date': creation_date
        }


# ------------------------------------------------------------------------------


class Acl(Base):
    """
    """
    __tablename__ = 'acl'

    known_acls = ['edit', 'read']

    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey(User.id))
    id_project = Column(Integer, ForeignKey(Project.id))
    acl = Column(String(30))

    def __init__(self, id_user, id_project, acl_label):
        """
        Acl object constructor

        :param id_user: the id of the attached user
        :param id_project: the id of the attached project
        :param acl_label: the label of the project
        """
        self.id_user = id_user
        self.id_project = id_project
        self.acl = acl_label

    def __json__(self, request):
        """
        """
        return {
            'id': self.id,
            'id_project': self.id_project,
            'id_user': self.id_user,
            'acl': self.acl
        }


# ------------------------------------------------------------------------------


class Task(Base):
    """
    """
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    id_project = Column(Integer, ForeignKey(Project.id))
    content = Column(Text)

    def __init__(self, id_project, task_content):
        """
        """
        self.id_project = id_project
        self.content = task_content

    def __json__(self, request):
        """
        """
        return {
            'id':
            self.id,
            'content':
            self.content,
            'execute_url':
            request.route_path(route_name='project_run_task', id=self.id),
            'delete_url':
            request.route_path(route_name='project_delete_task', id=self.id),
        }


# ------------------------------------------------------------------------------


class ProjectGroup(Base):
    """
    all groups user can define and associate a project.
    also a group can have a parent, then groups can be
    gathered under a unique group. So you'll get a pretty
    hierarchy
    """
    __tablename__ = 'project_group'

    id = Column(Integer, primary_key=True)
    id_parent = Column(Integer, ForeignKey('project_group.id'))
    parent = relationship('ProjectGroup', remote_side=[id], backref='children')
    name = Column(String(100))
    projects = relationship("Project",
                            secondary=groups_projects_association,
                            back_populates="groups")

    def __init__(self, name):
        """
        """
        self.name = name

    def __json__(self, request):
        """
        """
        return {
            'id': self.id,
            'name': self.name,
        }


Index('groupe_name_unique', ProjectGroup.name, unique=True)

# ------------------------------------------------------------------------------


class Macro(Base):
    """
    """
    __tablename__ = 'macro'

    id = Column(Integer, primary_key=True)
    id_project = Column(Integer, ForeignKey(Project.id))
    label = Column(String(100))
    relations = relationship('MacroRelations',
                             backref='macro',
                             cascade='delete, delete-orphan')

    def __init__(self, id_project, label):
        """
        """
        self.id_project = id_project
        self.label = label

    def get_description(self):
        """
         return a string description of the current macro
         This description shall be related to macro relations
         so usee could understood what this macro does ...
        """
        lst_relations_label = []
        for relation in self.relations:
            if relation.aim_project is not None:
                lst_relations_label.append(
                    "%s %s" % (relation.direction, relation.aim_project.name))

        return "that imply : %s" % (" then ".join(lst_relations_label))

    def __json__(self, request):
        """
        """
        return {
            'id': self.id,
            'id_macros': self.id_project,
            'label': self.label,
        }


# ------------------------------------------------------------------------------


class MacroRelations(Base):
    """
    """
    __tablename__ = 'macro_relations'

    id = Column(Integer, primary_key=True)
    id_macros = Column(Integer, ForeignKey(Macro.id))
    id_third_project = Column(Integer, ForeignKey(Project.id))
    aim_project = relationship(Project)

    # relation between main project and others ...
    direction = Column(Enum('push', 'pull'))

    def __init__(self, id_third_project, direction):
        """
        """
        self.id_third_project = id_third_project
        self.direction = direction

    def __json__(self, request):
        """
        """
        return {
            'id': self.id,
            'id_macros': self.id_project,
            'id_third_project': self.id_third_project,
            'direction': self.direction,
        }
