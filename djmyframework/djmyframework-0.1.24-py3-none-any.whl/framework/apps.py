from django.apps import AppConfig, apps


class FrameWrokConfig(AppConfig):
    name = 'framework'



def get_app_path(app_name):
    return apps.app_configs.get(app_name).path
