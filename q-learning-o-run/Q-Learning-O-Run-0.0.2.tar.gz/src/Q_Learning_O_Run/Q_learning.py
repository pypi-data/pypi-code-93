#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Q-learning的决策模块
"""

__author__ = 'Godw'

from typing import List

import numpy as np
import pandas as pd
from pandas import DataFrame


def build_Q_Table(Action: List[str], Size: int) -> DataFrame:
    """
    创建一个Q表
    :param Action: 每步可以采取的动作列表
    :param Size: Q表的行数，也就是大小
    :return: Q表
    """
    table = pd.DataFrame(
        np.zeros((Size, len(Action))),
        columns=Action
    )
    return table


class Brain(object):
    def __init__(self, Q_Table: DataFrame, Action: List[str], Epsilon: float = 0.9, Alpha: float = 0.1,
                 Gamma: float = 0.9) -> None:
        """
        初始化
        :param Q_Table: Q表
        :param Action: 每步可以采取的动作列表
        :param Epsilon: ε
        :param Alpha: α
        :param Gamma: γ
        """
        self._Q_Table = Q_Table
        self._Action = Action
        self._Epsilon = Epsilon
        self._Alpha = Alpha
        self._Gamma = Gamma

    def choose_Action(self, Step: int) -> str:
        """
        决策下一步要采取的动作值
        :param Step: 当前步
        :return: 下一步采取的动作值
        """
        if np.random.uniform() > self._Epsilon or ((self._Q_Table.iloc[Step, :] == 0).all()):
            action = np.random.choice(self._Action)
        else:
            action = self._Action[np.argmax(self._Q_Table.iloc[Step, :])]
        return action

    def update_Q_Table(self, Action: str, Step: int, Reward: float, Step_: int, Done: bool
                       ) -> None:
        """
        更新Q表
        :param Action: 当前步采取的动作值
        :param Step: 当前步
        :param Reward: 执行当前步获得的奖励值
        :param Step_: 下一步
        :param Done: 是否结束
        """
        if Done:
            self._Q_Table.loc[Step, Action] = self._Q_Table.loc[Step, Action] + self._Alpha * (
                    Reward - self._Q_Table.loc[Step, Action])
        else:
            self._Q_Table.loc[Step, Action] = self._Q_Table.loc[Step, Action] + self._Alpha * (
                    Reward + self._Gamma * np.max(self._Q_Table.loc[Step_, Action]) - self._Q_Table.loc[Step, Action])
