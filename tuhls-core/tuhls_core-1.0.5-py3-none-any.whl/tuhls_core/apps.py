import os
import sys
from pathlib import PosixPath

from django.apps import AppConfig
from django.utils.autoreload import autoreload_started


def dist_is_editable(dist):
    for path_item in sys.path:
        egg_link = os.path.join(path_item, dist.project_name + ".egg-link")
        if os.path.isfile(egg_link):
            return True
    return False


def my_watchdog(sender, *args, **kwargs):
    import pkg_resources

    for dist in pkg_resources.working_set:
        if dist_is_editable(dist):
            sender.directory_globs[PosixPath(dist.location)] = {"**/*.py"}
            print("additional watch dir", dist.location, dist.project_name)  # noqa


class TuhlsCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tuhls_core"

    def ready(self):
        autoreload_started.connect(my_watchdog)
