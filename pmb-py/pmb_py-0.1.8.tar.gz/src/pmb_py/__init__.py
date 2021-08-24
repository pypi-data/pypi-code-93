PMB_MEMBER_STATUS = {
    "leave": [0, '已離職'],
    "atWork": [1, '在職中'],
    "leaveOfAbsence": [2, '留職停薪'],
}


class PmbError(Exception):
    pass


from pmb_py.core import log_in, log_out
import pmb_py.api as api


if __name__ == '__main__':
    import os
    print(log_in(os.environ['TESTUSER'], os.environ['TESTPW']))
    print(api.ProjectStatus.list())
    print(api.MemberStatus.list())
    print(api.ProjectType.list())
    print(api.Projects.list())
    print(api.GanttItems.list())