import yaml
from yaml.loader import Loader
from .configurable import Configurable
import multiprocessing

class Sorda:
    def __init__(self, actions: Configurable, gens: Configurable = None, multi_process: bool = False):
        self._actions = actions
        self._gens    = gens
        self._multi_process = multi_process

    def do(self, config, args, kwargs):
        if 'meta' not in config:
            raise Exception("`meta' key in configure required")
        if self._multi_process:
            p = multiprocessing.Process(target=self._actions(config, args=args, kwargs=kwargs))
            print('config', config)
            p.start()
            p.join()
        else:
            self._actions(config)(*args, **kwargs)

    def __call__(self, config_file, update_file = None, *args, **kwargs):
        with open(config_file, 'r') as f:
            configs = yaml.load_all(f.read(), Loader=yaml.FullLoader)

        if update_file is not None and self._gens is not None:
            with open(update_file, 'r') as f:
                updates = yaml.load_all(f.read(), Loader=yaml.FullLoader)
            for update in updates:
                gen = self._gen(update)
                for config in gen:
                    self.do(config, args, kwargs)
        else:
            for config in configs:
                self.do(config, args, kwargs)
