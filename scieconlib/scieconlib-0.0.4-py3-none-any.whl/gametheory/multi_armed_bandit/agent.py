import numpy as np
import copy
import pandas as pd

from .action import Action


class Agent:
    def __init__(self):
        # initial values
        self.Q = []
        self.T = []
        self.cum = []

        self.action_num = 0
        self.actions = []

    def add_action(self, action, verbose=0):
        """
        insert an action
        :param action: the action to insert
        :param verbose: verbose=0: show nothing. verbose=1: print the action info
        :return:
        """
        assert isinstance(action, Action)
        action = copy.deepcopy(action)
        self.action_num += 1
        action.set_num(self.action_num - 1)
        self.actions.append(action)
        self.Q = [0 for _ in range(self.action_num)]
        self.T = [0 for _ in range(self.action_num)]
        self.cum = [0 for _ in range(self.action_num)]

        if verbose == 1:
            print(f'Added: {action.get_num()}: ', action)
        return

    def take(self, action_num):
        """
        take an action
        :param action_num: action number to take
        :return: None
        """
        action = self.actions[action_num]
        reward = action.generate()
        self.T[action_num] += 1
        self.cum[action_num] += reward
        self.Q[action_num] = np.divide(self.cum[action_num], self.T[action_num])
        return

    def get_avg(self):
        """
        calculate the average value
        :return: average value
        """
        return sum(self.cum) / sum(self.T)

    def get_greedy(self):
        """
        rank the expected values and return the number of largest
        :return: number of largest expected action
        """
        return np.argmax(np.array(self.Q))

    def pick_action(self):
        """
        pick a random action
        :return: a random action number
        """
        num = np.random.randint(0, self.action_num)
        return num

    def get_info(self, printing=True, desc=False):
        """
        printing actions info
        :param desc: whether to sort the dataframe
        :param printing: whether to print
        :return: None
        """
        print(f'Number of actions: {self.action_num}')
        df = pd.DataFrame()
        df['Action counting'] = self.T
        df['No.'] = [x for x in range(self.action_num)]
        df['Total reward'] = self.cum
        df['Expected reward'] = self.Q
        df = df.set_index('No.')
        if desc:
            df.sort_values(by='Expected reward', inplace=True, ascending=False)
        if printing:
            print(df)
            return

        return df
