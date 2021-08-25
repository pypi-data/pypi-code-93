from dataclasses import dataclass
import datetime


@dataclass
class ProjectStatus:
    id: int
    name: str
    color: str
    code_name: str
    color_text: str


class Project:

    def __init__(self, id: int,
                 name: str,
                 alive: bool,
                 budget: float=None,
                 budget_tax: float=None,
                 cost: float=None,
                 profit: float=None,
                 money_received: float=None,
                 deadline: datetime.date=None,
                 status_id: int=None,
                 note: str = '',
                 time_start: datetime.date=None,
                 time_end: datetime.date=None,
                 time_update: datetime.date=None,
                 sort_num: float=None,
                 manager_id: int=None,
                 manager_assistant_id: int=None,
                 leader_id: int=None,
                 leader_agent_id: int=None,
                 director_id: int=None,
                 producer_id: int=None,
                 cg_lead_id: int=None,
                 project_coordinator_id: int=None,
                 extra_pm_id: int=None,
                 charge: float=None,
                 old_company: str=None,
                 payment_status_id: int=None,
                 company_id: int=None,
                 sg_project_id: int=None,
                 contracted: bool=None,
                 is_deleted: bool=None,
                 tank_name: str=None,
                 backup_unc: str=None,
                 type_id: int = None):
        self.id = id
        self.name = name
        self.type_id = type_id
        self.budget = budget
        self.budget_tax = budget_tax
        self.cost = cost
        self.profit = profit
        self.money_received = money_received
        self.alive = alive
        self.deadline = deadline
        self.status_id = status_id
        self.note = note
        self.time_start = time_start
        self.time_end = time_end
        self.time_update = time_update
        self.sort_num = sort_num

        self.manager_id = manager_id
        self.manager_assistant_id = manager_assistant_id
        self.leader_id = leader_id
        self.leader_agent_id = leader_agent_id
        self.director_id = director_id
        self.producer_id = producer_id
        self.cg_lead_id = cg_lead_id
        self.project_coordinator_id = project_coordinator_id
        self.extra_pm_id = extra_pm_id

        self.charge = charge
        self.old_company = old_company
        self.payment_status_id = payment_status_id
        self.company_id = company_id
        self.sg_project_id = sg_project_id
        self.contracted = contracted
        self.is_deleted = is_deleted
        self.tank_name = tank_name
        self.backup_unc = backup_unc

    def __eq__(self, obj_b):
        if type(obj_b) != Project:
            return False
        if self.id == obj_b.id:
            return True
        else:
            return False

    def __hash__(self):
        data = 'PmbProject_'+str(self.id)
        return hash(data)

    def __repr__(self):
        class_ = str(type(self)).split("'")[1]
        return f'{class_}({self.id}:{self.name}) at {id(self)}'


@dataclass
class ProjectType:
    id: int
    name: str


@dataclass
class MemberStatus:
    id: int
    name: str
    code_name: str


@dataclass
class Member:
    id: int
    name: str
    e_id: str
    email: str


@dataclass
class Task:
    id: int
    name: str
    gantt_item_id: int
    project_id: int
    task_group_id: int
    member_id: int


@dataclass
class Block:
    id: int
    date: datetime.date
    duration: int
    member_id: int
    project_id: int
    group_id: int
    task_id: int
    type_id: int


@dataclass
class BlockType:
    id: int
    name: str
    color: str
    color_text: str
    text: str


@dataclass
class GanttItem:
    id: int
    name: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    task_type: int
    parent_id: int
    project_id:int
    sg_task_id: int
    legend: str
    read_only: str
    status: str



@dataclass
class Member:
    id: int
    emp_id: str
    name: str


@dataclass
class TaskGroup:
    id: int
    name: str
