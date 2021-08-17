#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Q-learning的MDP环境模块,示例如下：
    o----T
    -o---T
    --o--T
    ---o-T
    ----oT
    智能体'o'的目标是触碰到’T‘，
    'o'可以采用的动作值为['left', 'right']
    'o'触碰到‘T’，奖励1分；否则奖励0分
"""

__author__ = 'Godw'

import time
from typing import Tuple


class Env(object):
    ACTION = ['left', 'right']

    def __init__(self, length: int = 6, init_postion: int = 0, fresh_time: float = 0.3) -> None:
        """
        初始化
        :param length: 智能体完成任务需要走的最大步数
        :param init_postion: 智能体的初始位置
        :param fresh_time: 每步花费时间
        """
        print("Env环境初始化")
        self.l = length
        self.env_list = ['-'] * self.l + ['T']
        self.position = init_postion
        self.FRESH_TIME = fresh_time

    def refresh(self, init_postion: int = 0) -> None:
        """
        重置环境
        :param init_postion: 环境重置后，智能体‘o’所处的位置
        """
        self.position = init_postion

    def update_env(self, action: str) -> Tuple[int, int, bool]:
        """
        更新环境
        :param action: 采取的动作值
        :return: 本步奖励、下步位置、是否终止
        """
        reward = 0
        termination = False
        if action == 'right':
            self.position = self.position + 1
            if self.position == self.l:
                reward = 1
                termination = True
                self.position = self.position - 1
        if action == 'left':
            self.position = self.position - 1
            if self.position == -1:
                self.position = 0

        self.env_list[self.position] = 'o'
        print(''.join(self.env_list))
        time.sleep(self.FRESH_TIME)
        self.env_list = ['-'] * self.l + ['T']

        return reward, self.position, termination
