#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: monitor.py 
@time: 2021/08/09
@contact: 
@site:  
@software: PyCharm 
"""
import asyncio
from functools import wraps
import traceback
import time

from loguru import logger

# from rosetta_service_monitor.tasks.background_task import backgound_task
from rosetta_service_monitor.client.service.mq_service import mq_serveice


def service_monitor(project_name, **kwargs):
    logger.debug(f"Current Project is: {project_name}")
    service_kwargs = kwargs

    def monitor(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    start_time = time.time()
                    resp = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.info(f'{func.__name__} executed in {duration:.4f} s')
                    return resp
                except KeyboardInterrupt as e:
                    raise e
                except Exception as err:
                    logger.info(f"Get exception, send to mq...")
                    info = f'{err}:{err.__class__.__name__}, args:{args}, kwargs:{kwargs}\n{traceback.format_exc()}'
                    logger.error(info)
                    request_data = {}
                    # backgound_task(mq_serveice.send_mq, project_name=project_name, err_msg=info, trace_id='',
                    #                request=request_data, **service_kwargs)
                    mq_serveice.send_msg_async(project_name=project_name, err_msg=info, trace_id='',
                                               request=request_data,
                                               **service_kwargs)
                    raise err
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    start_time = time.time()
                    out = func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.info(f'{func.__name__} executed in {duration:.4f} s')
                    return out
                except KeyboardInterrupt as e:
                    raise e
                except Exception as err:
                    logger.info(f"Get exception, send to mq...")
                    info = f'{err}:{err.__class__.__name__}, args:{args}, kwargs:{kwargs}\n{traceback.format_exc()}'
                    logger.error(info)
                    request_data = {}
                    # backgound_task(mq_serveice.send_mq, project_name=project_name, err_msg=info, trace_id='',
                    #                request=request_data, **service_kwargs)
                    mq_serveice.send_msg_async(project_name=project_name, err_msg=info, trace_id='',
                                               request=request_data,
                                               **service_kwargs)
                    raise err

        return wrapper

    return monitor
