import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid() -> str:
    """
    Generates a random UUID.

    :return: UUID as string
    """
    return str(uuid.uuid4())


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer(), primary_key=True, nullable=False)
    client_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    client_name = Column(String(128), index=True, nullable=False, unique=True)
    client_active = Column(Boolean(), default=False, nullable=False)
    client_description = Column(String(255), nullable=True)
    client_remark = Column(String(1024), nullable=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    projects = relationship("Project", backref="client")

    def __repr__(self) -> str:
        return f"Client<client_id: {self.client_id}, client_uuid: {self.client_uuid}, " \
               f"client_name: {self.client_name}, client_active: {self.client_active}>"


class Contact(Base):
    __tablename__ = "contacts"

    client_id = Column(Integer(), ForeignKey("clients.client_id"), nullable=False)
    contact_id = Column(Integer(), primary_key=True, nullable=False)
    contact_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    contact_name = Column(String(128), index=True, nullable=False, unique=True)
    contact_description = Column(String(255), nullable=True)
    contact_remark = Column(String(1024), nullable=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self) -> str:
        return f"Contact<contact_id: {self.contact_id}, contact_uuid: {self.contact_uuid}, " \
               f"contact_name: {self.contact_name}, contact_active: {self.contact_active}>"


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint('client_id', 'project_name'),)

    client_id = Column(Integer(), ForeignKey("clients.client_id"), nullable=False)
    project_id = Column(Integer(), primary_key=True, nullable=False)
    project_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    project_name = Column(String(128), index=True, nullable=False)
    project_active = Column(Boolean(), default=False, nullable=False)
    project_description = Column(String(255), nullable=True)
    project_remark = Column(String(1024), nullable=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    tasks = relationship("Task", backref="project")

    def __repr__(self) -> str:
        return f"Project<project_id: {self.project_id}, project_uuid: {self.project_uuid}, " \
               f"client_name: {self.client.client_name}, project_name: {self.project_name}, " \
               f"project_active: {self.project_active}>"


class TaskState(enum.Enum):
    NEW = 1
    STARTED = 2
    STOPPED = 3

    def __str__(self):
        return self.name


class Task(Base):
    __tablename__ = "tasks"

    project_id = Column(Integer(), ForeignKey("projects.project_id"), nullable=False)
    task_id = Column(Integer(), primary_key=True, nullable=False)
    task_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    task_name = Column(String(128), nullable=True)
    task_active = Column(Boolean(), default=False, nullable=False)
    task_state = Column(Enum(TaskState), default=TaskState.NEW, nullable=False)
    task_start = Column(DateTime(), default=None, nullable=True)
    task_finish = Column(DateTime(), default=None, nullable=True)
    task_duration = Column(Integer(), default=0, nullable=False)
    task_description = Column(String(255), nullable=True)
    task_remark = Column(String(1024), nullable=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self) -> str:
        return f"Task<task_id: {self.task_id}, task_uuid: {self.task_uuid}, " \
               f"task_name: {self.task_name}, task_active: {self.task_active}>"


class Asset(Base):
    __tablename__ = "assets"

    period_id = Column(Integer(), ForeignKey("projects.project_id"), nullable=False)
    asset_id = Column(Integer(), primary_key=True, nullable=False)
    asset_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)


class Event(Base):
    __tablename__ = "events"

    period_id = Column(Integer(), ForeignKey("projects.project_id"), nullable=False)
    event_id = Column(Integer(), primary_key=True, nullable=False)
    event_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)


class Note(Base):
    __tablename__ = "notes"

    period_id = Column(Integer(), ForeignKey("projects.project_id"), nullable=False)
    note_id = Column(Integer(), primary_key=True, nullable=False)
    note_uuid = Column(String(128), index=True, default=generate_uuid, nullable=False, unique=True)
    note_description = Column(String(255), nullable=True)
    note_remark = Column(String(1024), nullable=True)
    created_on = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
