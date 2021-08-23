# -*- coding: utf-8 -*-
#
# Copyright (C) 2003-2007  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under the
# terms of the M.I.T License.
#
import logging

from pyramid.security import (
    Allow,
    Everyone,
    authenticated_userid,
    )

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    String,
    Boolean,
    ForeignKey,
    )
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from .nodes import PoolSsh, NodeController, NodeException
log = logging.getLogger(__name__)
from datetime import datetime

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

#------------------------------------------------------------------------------

class Project(Base):
  """
  The project item
  """
  __tablename__ = 'projects'

  id           = Column(Integer, primary_key=True)
  name         = Column(String(100))
  user         = Column(String(100))
  password     = Column(String(100))
  host         = Column(String(100))
  path         = Column(Text)
  rev_init     = Column(String(100))
  dvcs_release = Column(String(20))
  dashboard    = Column(Boolean)

  logs         = relationship('RemoteLog', cascade='delete, delete-orphan')
  acls         = relationship('Acl', backref='project', cascade='delete, delete-orphan')
  tasks        = relationship('Task', backref='project', cascade='delete, delete-orphan')

  def __init__(self, name, user, password, host, path, rev_init, dashboard, dvcs_release):
    """
    """
    self.name         = name
    self.user         = user
    self.password     = password
    self.host         = host
    self.path         = path
    self.rev_init     = rev_init
    self.dashboard    = dashboard
    self.dvcs_release = dvcs_release

  def __json__(self, request):
    """
    """
    return { 'id'           : self.id,
             'name'         : self.name,
             'host'         : self.host,
             'path'         : self.path,
             'user'         : self.user,
             'password'     : '*'*len(self.password),
             'dashboard'    : self.dashboard,
             'dvcs_release' : self.dvcs_release }

  def get_uri(self):
    """
    uri as hg way ...
    """
    return "%s:%s@%s:%s"%(self.user, self.password, self.host, self.path)

  def get_ssh_node(self):
    """
    """
    uri = self.get_uri()
    return PoolSsh.get_node(uri, self.id)

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
    if not self.rev_init or len(self.rev_init)<35:
      result = False
    return result

  def init_initial_revision(self):
    """
    """
    if not self.is_initial_revision_init():
      with NodeController(self, silent=True) as ssh_node :
        _rev_init = ssh_node.get_initial_hash()
        if _rev_init != "0000000000000000000000000000000000000000" :
          self.rev_init = _rev_init

Index('project_unique', Project.host, Project.path, unique=True)
Index('project_root', Project.rev_init)

#------------------------------------------------------------------------------

class RemoteLog(Base):
  """
  This table contains all logs entries
  which command user execute on which host and at what time
  """
  __tablename__ = 'logs'

  id            = Column(Integer, primary_key=True)
  id_project    = Column(Integer, ForeignKey(Project.id))
  host          = Column(String(100))
  path          = Column(Text)
  command       = Column(Text)
  creation_date = Column(DateTime)

  def __init__(self, id_project, host, path, command):
    """
    """
    self.id_project    = id_project
    self.creation_date = datetime.now()
    self.host          = host
    self.path          = path
    self.command       = command

  def __json__(self, request):
    """
    """
    return { 'id'            : self.id,
             'host'          : self.host,
             'path'          : self.path,
             'command'       : self.command,
             'creation_date' : self.creation_date.strftime('%d/%m/%Y %H : %M')}

#------------------------------------------------------------------------------

class Group(Base):
  """
  This table contains all users
  """
  __tablename__ = 'group'

  id            = Column(Integer, primary_key = True)
  label         = Column(String(100))
  creation_date = Column(DateTime)

  def __init__(self, label, creation_date):
    """
    """
    self.label         = label
    self.creation_date = creation_date

  def __json__(self, request):
    """
    """
    return { 'id'            : self.id,
             'label'         : self.label,
             'creation_date' : self.creation_date.strftime('%d/%m/%Y %H : %M')}
#------------------------------------------------------------------------------

class User(Base):
  """
  This table contains all users
  """
  __tablename__ = 'user'

  id            = Column(Integer, primary_key=True)

  id_group      = Column(Integer, ForeignKey(Group.id))
  group         = relationship(Group, backref='users')
  acls          = relationship('Acl', backref='user', cascade = 'delete, delete-orphan')

  name          = Column(String(100))
  id_groupe     = Column(Integer)
  pwd           = Column(String(100))
  email         = Column(String(100), unique=True)
  creation_date = Column(DateTime)

  def __init__(self, name, pwd, email, creation_date=None):
    """
    """
    self.name  = name
    self.pwd   = pwd
    self.email = email

    if creation_date is None :
      self.creation_date = datetime.now()

  def __json__(self, request):
    """
    """
    creation_date = None
    if self.creation_date :
      creation_date = self.creation_date.strftime('%d/%m/%Y %H:%M')

    return { 'id'            : self.id,
             'name'          : self.name,
             'email'         : self.email,
             'pwd'           : self.pwd,
             'get_url'       : request.route_url(route_name='user_get',id=self.id),
             'delete_url'    : request.route_url(route_name='user_delete',id=self.id),
             'update_url'    : request.route_url(route_name='user_update',id=self.id),
             'group'         : self.group,
             'creation_date' : creation_date }

#------------------------------------------------------------------------------

class Acl(Base):
  """
  """
  __tablename__ = 'acl'

  known_acls = ['edit', 'read']

  id         = Column(Integer, primary_key=True)
  id_user    = Column(Integer, ForeignKey(User.id))
  id_project = Column(Integer, ForeignKey(Project.id))
  acl        = Column(String(30))

  def __init__(self, id_user, id_project, acl_label) :
    """
    Acl object constructor

    :param id_user: the id of the attached user
    :param id_project: the id of the attached project 
    :param acl_label: the label of the project
    """
    self.id_user    = id_user
    self.id_project = id_project
    self.acl        = acl_label

  def __json__(self, request):
    """
    """
    return { 'id'         : self.id,
             'id_project' : self.id_project,
             'id_user'    : self.id_user,
             'acl'        : self.acl
           }

#------------------------------------------------------------------------------

class Task(Base):
  """
  """
  __tablename__ = 'task'

  id         = Column(Integer, primary_key=True)
  id_project = Column(Integer, ForeignKey(Project.id))
  content    = Column(Text)

  def __init__(self, id_project, task_content) :
    """
    """
    self.id_project  = id_project
    self.content     = task_content

  def __json__(self, request):
    """
    """
    return { 'id'          : self.id,
             'content'     : self.content,
             'execute_url' : request.route_url(route_name='project_run_task', id=self.id),
             'delete_url'  : request.route_url(route_name='project_delete_task', id=self.id),
           }
#------------------------------------------------------------------------------

class RootFactory(object):
  """
  """
  
  __acl__ = [ (Allow, Everyone, 'view'),
              (Allow, 'group:editors', 'edit') ]

  def __init__(self, request):
    """
    """
    pass

#------------------------------------------------------------------------------

