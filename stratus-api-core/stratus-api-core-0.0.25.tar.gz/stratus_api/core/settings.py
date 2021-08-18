__settings__ = None


def get_settings(settings_type='app', env_folder=None, refresh=False):
    import os
    import json
    from stratus_api.core.common import generate_random_id
    import logging

    global __settings__
    folder = os.getenv('ENV_FOLDER', '/apps/settings/')
    if env_folder is not None:
        folder = env_folder
    if __settings__ is None or refresh:
        settings = dict()

        for root, dirs, files in os.walk(folder, topdown=True):
            dirs.sort()
            for file in files:
                file_type = file.replace('.json', '')
                if file_type not in settings.keys():
                    settings[file_type] = dict()
                local_path = os.path.join(folder, '{0}/{1}'.format(root, file))
                try:
                    with open(local_path, 'rt') as f:
                        settings[file_type].update(json.load(f))
                except json.JSONDecodeError as e:
                    logging.error(local_path)
                    raise e
        __settings__ = {
            k: {key: format_setting_value(value) for key, value in v.items()} for k, v in settings.items()
        }
        prefix = ''
        if settings['app'].get('environment', 'test') == 'test':
            prefix = generate_random_id().split('-')[0]
        __settings__['app']['prefix'] = prefix
    return __settings__.get(settings_type, dict())


def get_app_settings(env_folder=None, refresh=False):
    return get_settings(env_folder=env_folder, refresh=refresh)


def format_setting_value(value):
    import json
    import logging
    formatted_value = value
    if isinstance(value, str) and (
            any([i in value for i in ['"', '[', '{']]) or value.lower() in ['true', 'false'] or value.isdigit()):
        try:
            formatted_value = json.loads(value)
        except json.JSONDecodeError as exc:
            logging.debug(exc)
    return formatted_value
