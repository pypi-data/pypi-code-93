from django.apps import AppConfig

__all__ = ["DjQiYuTplConfig"]


class DjQiYuTplConfig(AppConfig):
    name = "dj_qiyu_tpl"

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.label = "奇遇科技模版"
