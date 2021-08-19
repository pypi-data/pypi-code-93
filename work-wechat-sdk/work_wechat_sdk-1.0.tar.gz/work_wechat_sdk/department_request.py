from work_wechat_sdk import url_settings
from work_wechat_sdk.base_request import BaseRequest


class DeptRequest(BaseRequest):
    """
    Description: The response of DeptUserRequest contains a department member's
    detail information specified by id

    parameter_R: <access_token>
    parameter_O: <id>

    post_data_R: None
    post_data_O: None

    Return: a department list briefed

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90208
    """
    request_url = url_settings.GET_DEPT

    def get_dept(self):
        dept_list = self.json_response.get("department", None)
        return dept_list
