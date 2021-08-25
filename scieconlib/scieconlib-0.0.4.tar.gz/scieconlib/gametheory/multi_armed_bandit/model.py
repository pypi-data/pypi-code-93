import copy

import numpy as np
import plotly.express as px
import pandas as pd
from tqdm import tqdm


class Model:
    def __init__(self, agent, agent_num=200, epsilon=0.1, epochs=1000):
        """
        init the model
        :param agent: Agent object
        :param agent_num: number of agent to generate
        :param epsilon: primary parameter for epsilon-greedy algorithm
        :param epochs: epochs to train the model
        """
        self.agent = agent
        self.agent_num = agent_num
        self.epsilon = epsilon
        self.epochs = epochs
        self.history = None
        pass

    def _roll(self):
        random_num = np.random.uniform(0, 1)
        if random_num <= self.epsilon:
            return True
        else:
            # do exploit
            return False

    def train(self):
        """
        train the model
        :return: None
        """
        # generate agents
        history = {
            'avg_reward': [],
            'num': []
        }
        cnt = 0
        agents = [copy.deepcopy(self.agent) for _ in range(self.agent_num)]
        for _ in tqdm(range(self.epochs)):
            for agent in agents:
                explore = self._roll()
                if explore:
                    action_num = agent.pick_action()
                    agent.take(action_num)
                else:
                    action_num = agent.get_greedy()
                    agent.take(action_num)
            cnt += 1
            history['num'].append(cnt)
            avg_reward = np.average([agent.get_avg() for agent in agents])
            history['avg_reward'].append(avg_reward)
        self.history = history
        return

    def hist(self):
        df = pd.DataFrame(self.history)
        fig = px.line(df, x='num', y='avg_reward')
        fig.update_layout(
            title='Average Reward Curve',
            xaxis_title='epochs',
            yaxis_title='avg reward'
        )
        fig.show()
        return
