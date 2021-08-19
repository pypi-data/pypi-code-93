#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from gym.envs.registration import register

register(
    id='contin-v0',
    entry_point='gym_contin.envs:ContinEnv',
)

