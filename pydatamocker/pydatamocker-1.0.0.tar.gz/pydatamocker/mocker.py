mocker_config_defaults = {
    'report_progress': False
}


mocker_config = {}


def reset_config():
    mocker_config.clear()
    mocker_config.update(mocker_config_defaults.copy())


def config(**kwargs):
    mocker_config.update(kwargs)


def get_config(key):
    return mocker_config.get(key)


def report_progress(func):
    def f():
        mocker_config['report_progress'] = True
        res = func()
        mocker_config['report_progress'] = False
        return res
    return f
