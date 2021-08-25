# TODO: remove this all

BASE_PATH: str = "/ctlml_data"


def get_output_dir(base_path: str = BASE_PATH) -> str:
    return f"{base_path}/output"


def get_log_dir(base_path: str = BASE_PATH) -> str:
    return f"{get_output_dir(base_path=base_path)}/logs"


def get_tmp_dir(base_path: str = BASE_PATH) -> str:
    return f"{get_output_dir(base_path=base_path)}/tmp"
