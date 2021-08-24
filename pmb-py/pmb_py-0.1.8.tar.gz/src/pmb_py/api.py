import pmb_py.core as core
from pmb_py import PMB_MEMBER_STATUS, PmbError
from pmb_py.adapter import pmb_convert
from pmb_py.domain.query_result import QueryResult


class pmb_mixin:
    creator = None

    @classmethod
    def list(cls, *args, **kwargs) -> QueryResult:
        query_re = cls.get_query(*args, **kwargs)
        if not query_re:
            return None
        if type(query_re) == list:
            items = query_re
            _count = len(items) if items and len(items)<=1000 else 0
            query_re = QueryResult(limit=1000, next='', previous='', results=list(), start=1, total_count=_count)
        else:
            items = query_re.results
        objects = [cls.creator(item) for item in items]
        query_re.results = {object.id: object for object in objects}.values()
        return query_re


    @classmethod
    def get_query(cls, *args, **kwargs):
        pass

    @classmethod
    def get(cls, id_):
        pass
        # raise PmbError("no support for these keyword")

    @classmethod
    def create_one(cls, *args, **kwargs):
        return dict()

    @classmethod
    def create(cls, *args, **kwargs):
        item = cls.create_one(*args, **kwargs)
        if cls.creator:
            obj = cls.creator(item)
            return obj
        else:
            return item

    @classmethod
    def _update_one(cls, obj_id, **kwargs):
        return dict()

    @classmethod
    def update(cls, obj_id, **kwargs):
        try:
            item = cls._update_one(obj_id, **kwargs)
        except Exception as e:
            raise PmbError('Update Fail') from e
            # print(str(e))
            # return False
        if cls.creator:
            obj = cls.creator(item)
            return obj
        else:
            return item

    @classmethod
    def remove(cls, id_):
        pass

class ProjectStatus(pmb_mixin):
    creator = pmb_convert.to_project_status

    @classmethod
    def get_query(cls):
        api = "web_project_status_and_types"
        re = core._session.post(api)
        return re["data"]["projectStatus"]


class ProjectType(pmb_mixin):
    creator = pmb_convert.to_project_type

    @classmethod
    def get_query(cls):
        api = "web_project_status_and_types"
        re = core._session.post(api)
        return re["data"]["projectTypes"]


class MemberStatus(pmb_mixin):
    creator = pmb_convert.to_member_status

    @classmethod
    def get_query(cls):
        status_list = list()
        for k, v in PMB_MEMBER_STATUS.items():
            status_list.append({"id": v[0], "name": v[1], "codeName": k})
        return status_list


class Projects(pmb_mixin):
    creator = pmb_convert.to_project

    @classmethod
    def get_query(cls, *args, **kwargs):
        api = 'projects'
        re = core._session.get(api, params=kwargs)
        return re

    @classmethod
    def update_one(cls, obj_id, **kwargs):
        api = f'projects/{obj_id}'
        re = core._session.patch(api, data=kwargs)
        return re



class Tasks(pmb_mixin):
    creator = pmb_convert.to_task

    @classmethod
    def get_query(cls, *args, **kwargs):
        api = "tasks"
        re = core._session.get(api, params=kwargs)
        return re


class Blocks(pmb_mixin):
    creator = pmb_convert.to_block

    @classmethod
    def get_query(cls, *args, **kwargs):
        api = "blocks"
        re = core._session.get(api, params=kwargs)
        return re


class GanttItems(pmb_mixin):
    creator = pmb_convert.to_gantt_item

    @classmethod
    def get(cls, id_):
        api = 'gantt_items'
        re = core._session.get(api, params={'id':id_})
        if re.results:
            if cls.creator:
                return cls.creator(re.results[0])
            else:
                return re.results[0]
        else:
            raise PmbError('Not Found')
            

    @classmethod
    def get_query(cls, *args, **kwargs):
        api = 'gantt_items'
        re = core._session.get(api, params=kwargs)
        return re

    @classmethod
    def create_one(cls, *args, **kwargs):
        api = 'gantt_items'
        re = core._session.post(api, data=kwargs)
        return re

    @classmethod
    def _update_one(cls, id_, **kwargs):
        api = f'gantt_items/{id_}'
        re = core._session.patch(api, data=kwargs)
        return re

    @classmethod
    def remove(cls, id_):
        api = f'gantt_items/{id_}'
        re = core._session.delete(api,data={'id': id_})
        return re


class TaskGroup(pmb_mixin):
    creator = pmb_convert.to_task_group

    @classmethod
    def get_query(cls, *args, **kwargs):
        api = 'task_groups'
        re = core._session.get(api, params=kwargs)
        return re


class Member(pmb_mixin):
    creator = pmb_convert.to_member

    @classmethod
    def get_query(cls, *args, **kwargs):
        api = 'web_members'
        re = core._session.post(api, data=kwargs)
        return re['data']['lists']
