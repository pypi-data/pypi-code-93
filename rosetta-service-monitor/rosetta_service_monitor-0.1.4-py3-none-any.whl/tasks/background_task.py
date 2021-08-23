#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: background_task.py 
@time: 2021/08/10
@contact: 
@site:  
@software: PyCharm 
"""

# 定义一个专门创建事件循环loop的函数，在另一个线程中启动它
import asyncio
import threading
# from concurrent.futures.thread import ThreadPoolExecutor
from loguru import logger
from traceback import format_exc
import asyncio

lock = threading.Lock()


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def backgound_task_old(func, *args, **kwargs):
    try:
        print(f"dddd {func}")
        if asyncio.iscoroutinefunction(func):
            coroutine1 = func(*args, **kwargs)
            new_loop = asyncio.new_event_loop()  # 在当前线程下创建时间循环，（未启用），在start_loop里面启动它
            t = threading.Thread(target=start_loop, args=(new_loop,))  # 通过当前线程开启新的线程去启动事件循环
            t.start()

            asyncio.run_coroutine_threadsafe(coroutine1, new_loop)  # 这几个是关键，代表在新线程中事件循环不断“游走”执行
        else:
            func(*args, **kwargs)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as err:
        info = f'{err.__class__.__name__}:{err}\n{format_exc()}\n'
        logger.warning(info)


def backgound_task(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        def run(func, *args, **kwargs):
            try:
                asyncio.run(func(*args, **kwargs))
            except Exception as err:
                info = f'{err.__class__.__name__}:{err}\n{format_exc()}\n'
                logger.warning(info)
    else:
        def run(func, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                info = f'{err.__class__.__name__}:{err}\n{format_exc()}\n'
                logger.warning(info)

    t = threading.Thread(target=run, args=(func, *args), kwargs=kwargs)
    t.start()
