class RequiredEnvNotSet(Exception):

    def __init__(self, env_name):
        self._env_name = env_name

    def __str__(self):
        return f"""Required environment variable {self._env_name} not set"""
