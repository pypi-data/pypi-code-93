#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: fastapi_hook.py 
@time: 2021/08/09
@contact: 
@site:  
@software: PyCharm 
"""
import traceback
from loguru import logger

from rosetta_service_monitor.client.service.mq_service import mq_serveice
from rosetta_service_monitor.tasks.background_task import backgound_task


def register_hook(app, project_name, **kwargs) -> None:
    """
    请求响应拦截 hook
    https://fastapi.tiangolo.com/tutorial/middleware/
    :param project_name:
    :param app:
    :return:
    """

    @app.middleware("http")
    async def monitor(request, call_next):
        path = request.url.path
        try:
            response = await call_next(request)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as err:
            info = f'{err}:{err.__class__.__name__}\n{traceback.format_exc()}'
            logger.error(info)
            request_data = {
                'path': path,
                'body': "",
                'query_params': str(request.query_params),
                'form': ""
            }
            # logger.info(request_data)
            # backgound_task(mq_serveice.send_mq, project_name=project_name, err_msg=info, trace_id='',
            #                request=request_data, **kwargs)
            mq_serveice.send_msg_async(project_name=project_name, err_msg=info, trace_id='', request=request_data,
                                       **kwargs)
            raise err
        return response
