#!/usr/bin/env python
# -*- coding:utf-8 -*-

import uuid

"""
Biz ID （Business ID） 业务 ID
设计理念：
    服务拆分之后，一个业务链条可能会涉及多个服务，需要一个标识对一个完整的业务链条进行跟踪，所以设计了biz id。
生命周期：
    应该在业务开始的时候产生，在整个业务流程中都需要携带，贯穿始终。
场景：
    1、如 gateway 收到客户端请求的时候，应该产生一个 id，并发往下游服务；
    2、在异步事件中， Consumer 应该在获取到事件的时候，产生一个 id，并且贯穿整个业务流；
        即使同一个事件的 retry 时，每次重试都应该产生一个新的 id。
    3、在 Cronjob 被触发的时候，也应该在收到 job 的时候产生一个 id；
"""


def generate_biz_id() -> str:
    """
    创建用于业务追踪的唯一 ID
    """
    return uuid.uuid4().hex
