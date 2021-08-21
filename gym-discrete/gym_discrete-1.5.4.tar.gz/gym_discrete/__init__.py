#!/usr/bin/env python
# coding: utf-8

# In[1]:


from gym.envs.registration import register

register(
    id='discrete-v0',
    entry_point='gym_discrete.envs:DiscreteEnv',
)


# In[ ]:




