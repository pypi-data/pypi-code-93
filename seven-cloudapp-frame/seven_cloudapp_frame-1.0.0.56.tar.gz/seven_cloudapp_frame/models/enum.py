# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 14:32:40
@LastEditTime: 2021-08-19 22:02:43
@LastEditors: HuangJianYi
:description: 枚举类
"""

from enum import Enum, unique

class OperationType(Enum):
    """
    :description: 用户操作日志类型
    """
    add = 1 #添加
    update = 2 #更新
    delete = 3 #删除
    review = 4 #还原

class TaskType(Enum):
    """
    docstring：任务类型 业务的自定义任务类型从200起
    """
    # 掌柜有礼、免费领取、新人有礼，格式：{"reward_value":0,"asset_object_id":""}
    free_gift = 1
    # 单次签到，格式：{"reward_value":0,"asset_object_id":""}
    one_sign = 2
    # 每周签到，格式：{"day_list":{"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0},"asset_object_id":""}
    weekly_sign = 3
    # 邀请新用户，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""}
    invite_new_user = 4
    # 邀请入会，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""}
    invite_join_member = 5
    # 关注店铺，格式：{"reward_value":0,"once_favor_reward":0,"asset_object_id":""}
    favor_store = 6
    # 加入店铺会员，格式：{"reward_value":0,"once_member_reward":0,"asset_object_id":""}
    join_member = 7
    # 收藏商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""}
    collect_goods = 8
    # 浏览商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""}
    browse_goods = 9
