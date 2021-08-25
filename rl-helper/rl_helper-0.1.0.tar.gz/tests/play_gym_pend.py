# print("please install mujoco-py")
import gym
from rlhelper import envhelper
if __name__=="__main__":

    env = gym.make('Pendulum-v0')
    print(env.metadata)
    gym_env_helper=envhelper()

    frames=[]
    for episode in range(2): 
        obs = env.reset()
        for step in range(30):
            action = env.action_space.sample()  # or given a custom model, action = policy(observation)
            nobs, reward, done, info = env.step(action)
            if done:
                break
            gym_env_helper.recording(env)
        env.close()

    gym_env_helper.save_gif(times=3)