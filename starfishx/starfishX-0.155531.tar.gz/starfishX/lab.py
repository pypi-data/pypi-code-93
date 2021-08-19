import gym
import numpy as np
env = gym.make('CartPole-v0')
#np.array([0.33627469, 0.54509137, 1.8459067 , 1.64283432])
#http://kvfrans.com/simple-algoritms-for-solving-cartpole/
for _ in range(10):
  observation = env.reset()  
  parameters = np.array([0.33627469, 0.54509137, 1.8459067 , 1.64283432]) #np.random.rand(4)
  for __ in range(200):  
    action = 0 if np.matmul(parameters,observation) < 0 else 1
    #action = np.random.randint(0,2)
    observation, reward, done, info = env.step(action)
    env.render()
    print(__)
    #if done:
    #   break