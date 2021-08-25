from gym.envs.registration import register

register(
    id='nf-v0',
    entry_point='nf_gym.envs:NFEnv',
)
