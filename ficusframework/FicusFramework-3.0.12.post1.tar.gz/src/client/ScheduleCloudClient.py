import requests

from api.exceptions import ServiceInnerException, AuthException
from client import check_instance_avaliable, do_service


def count_tasks(task_type, status=[]) -> int:
    """
    获取某一个任务在某些状态下的数量
    :param task_type:
    :param status:
    :return:
    """
    if task_type is None or status is None:
        return 0

    check_instance_avaliable("SOBEYCLOUD-SCHEDULE-SERVICE")

    try:
        r = do_service(
            f"/v1.0/S1/tasks/count?task_type={task_type}" + (
                ("&" + "&".join(map(lambda x: f"status={x}", status))) if len(status) > 0 else ""),
            app_name="SOBEYCLOUD-SCHEDULE-SERVICE", method="get", return_type="int")
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
