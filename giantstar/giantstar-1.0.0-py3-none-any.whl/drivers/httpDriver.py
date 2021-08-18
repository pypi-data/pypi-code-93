import allure

from giantstar.drivers.basicDriver import BaseDriver
from giantstar.globalSetting import plus_setting
from giantstar.sessionManage.requestsSession import HTTPSession
from giantstar.utils.logger import logger
from giantstar.utils.initTest import _Config


class HttpDriver(BaseDriver):
    session_class = HTTPSession
    header = plus_setting.HTTP_REQUEST_HEADER  # type: dict

    @classmethod
    def run(cls, step_name, user, param, assert_content, extract=()):
        param = cls.analyze(param)
        url = param.get("url")
        if not url.startswith('http'):
            url = _Config.environment.get("default")
        path_param = param.pop('key_path', {})
        param["url"] = url.format(**path_param)
        headers = param.get("headers", {})
        cls.header.update(headers)
        param["headers"] = cls.header

        with allure.step(step_name):
            logger.info(f"【请求信息】user={user}, param={param}")
            response = cls.session_class.send(
                user=user,
                **param
            )

        logger.info(f"【接口响应】response={response.text}")
        assert_content = cls.analyze(assert_content) or []
        cls.check(assert_content=assert_content, response=response)
        extract = cls.analyze(extract)
        extract_result = cls.extract(response, extract)
        logger.info(f"【提取结果】extract_result={extract_result}")
