SUCCESS_CODE = 3
FAILED_CODE = -1
DOING_CODE = 1

class AsyncServiceResponse:
    """
    异步的响应
    """

    def __init__(self, response_data = None, task_state: int = SUCCESS_CODE, task_desc: str = None,
                 response_kind: str = None):
        """

        :param response_data: 执行响应信息
        :param task_state: 任务状态
        :param task_desc: 任务描述,错误描述
        :param response_kind: 任务种类,可以不填
        """
        self.response_data = response_data
        self.task_state = task_state
        self.task_desc = task_desc
        self.response_kind = response_kind
