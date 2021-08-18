import os

from tools.model import GetModelInfo


GIANT_SETTING = {
    "BASE_DIR": os.path.dirname(os.path.realpath(__file__)),  # 这个是必不可少的
    "TEST_FILES": ["giantstar_api.json", "giantstar_web.json"],
    "DATA_FILES": {"default": "./dataTable/data.xlsx"},
    "PARAMETRIC_CLASS": [GetModelInfo],
    "REMOTE": False,
    "DEBUG": True,
}

