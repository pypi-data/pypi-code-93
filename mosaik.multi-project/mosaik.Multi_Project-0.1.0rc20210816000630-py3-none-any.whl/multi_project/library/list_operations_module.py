from typing import List


def list_operations() -> List[str]:
    operations_list: List[str] = [
        'git_clone',
        'git_remote',
        'git_fetch',
        'git_checkout',
        'git_pull',
        'init_remove',
        'venv_remove',
        'venv_create',
        'venv_ensure_pip',
        'venv_upgrade_pip',
        'venv_install_pur',
        'venv_pur',
        'venv_install',
        'venv_install_wheel',
        'tox_remove',
        'tox_create',
        'tox_install_pur',
        'tox_pur',
        'tox_create',
        'docker_build',
    ]

    return operations_list
