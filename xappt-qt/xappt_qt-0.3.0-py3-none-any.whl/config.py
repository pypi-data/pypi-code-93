launch_new_process = False
minimize_to_tray = True
console_line_limit = 1024
start_minimized = False


def load_settings():
    import json
    from xappt_qt.constants import APP_CONFIG_PATH
    config_path = APP_CONFIG_PATH.joinpath("settings.cfg")
    try:
        with open(config_path, "r") as fp:
            settings_raw = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    else:
        global console_line_limit
        console_line_limit = settings_raw.get('console_line_limit', 1024)


load_settings()
del load_settings
