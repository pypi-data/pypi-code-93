from datetime import datetime
from sqlalchemy import Column, String, INTEGER, BLOB, FLOAT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Dag(Base):
    __tablename__ = 'dag'

    dag_id = Column(String, primary_key=True)
    is_paused = Column(INTEGER)
    is_subdag = Column(INTEGER)
    is_active = Column(INTEGER)
    last_scheduler_run = Column(String, default=datetime.now())
    last_pickled = Column(String, default=datetime.now())
    last_expired = Column(String, default=datetime.now())
    scheduler_lock = Column(INTEGER)
    pickle_id = Column(INTEGER)
    fileloc = Column(String)
    owners = Column(String)
    description = Column(String)
    default_view = Column(String)
    schedule_interval = Column(String)
    root_dag_id = Column(String)
    next_dagrun = Column(String, default=datetime.now())
    next_dagrun_create_after = Column(String, default=datetime.now())
    concurrency = Column(INTEGER)
    has_task_concurrency_limits = Column(INTEGER)

    def __repr__(self):
        return str(self.__dict__)


class DagRun(Base):
    __tablename__ = 'dag_run'

    id = Column(String, primary_key=True)
    dag_id = Column(String)
    execution_date = Column(String, default=datetime.now())
    state = Column(String)
    run_id = Column(String)
    external_trigger = Column(INTEGER)
    conf = Column(BLOB)
    end_date = Column(String, default=datetime.now())
    start_date = Column(String, default=datetime.now())
    run_type = Column(String)
    last_scheduling_decision = Column(String, default=datetime.now())
    dag_hash = Column(String)
    creating_job_id = Column(INTEGER)

    def __repr__(self):
        return str(self.__dict__)


class TaskInstance(Base):
    __tablename__ = 'task_instance'

    task_id = Column(String, primary_key=True)
    dag_id = Column(String, primary_key=True)
    execution_date = Column(String, default=datetime.now(), primary_key=True)
    start_date = Column(String, default=datetime.now())
    end_date = Column(String, default=datetime.now())
    duration = Column(FLOAT)
    state = Column(String)
    try_number = Column(INTEGER)
    hostname = Column(String)
    unixname = Column(String)
    job_id = Column(INTEGER)
    pool = Column(String)
    queue = Column(String)
    priority_weight = Column(INTEGER)
    operator = Column(String)
    queued_dttm = Column(String, default=datetime.now())
    pid = Column(INTEGER)
    max_tries = Column(INTEGER)
    executor_config = Column(BLOB)
    pool_slots = Column(INTEGER)
    queued_by_job_id = Column(INTEGER)
    external_executor_id = Column(String)

    def __repr__(self):
        return str(self.__dict__)
