import datetime
from pmb_py.domain import model


def to_project_status(item):
    return model.ProjectStatus(item['id'], item['name'], item['colorCode'], item['code'], item['colorText'])


def to_project_type(item):
    return model.ProjectType(item['id'], item['name'])


def to_member_status(item):
    return model.MemberStatus(item['id'], item['name'], item['codeName'])


def to_project(item):
    return model.Project(**item)


def to_gantt_item(item):
    return model.GanttItem(id=item['id'], name=item['name'], start_datetime=item['start_datetime'], end_datetime=item['end_datetime'],
                           task_type=item['task_type'], parent_id=item['parent_id'], sg_task_id=item['sg_task_id'], legend=item['legend'],
                           read_only=item['read_only'], status=item['status'], project_id=item['project_id']
                           )

def to_task_group(item):
    return model.TaskGroup(item['id'], item['name'])


def to_task(item):
    return model.Task(item['id'], item['name'], item['gantt_item_id'], item['project_id'], item['task_group_id'], item['member_id'])


def to_block(item):
    the_datetime = datetime.datetime.strptime(item['date'], '%Y-%m-%d')
    return model.Block(item['id'], the_datetime.date(), item['duration'], item['member_id'], item['project_id'], item['group_id'], item['task_id'],item['type_id'])


def to_member(item):
    return model.Member(item['userId'], item['employeeId'], item['nameChinese'])
