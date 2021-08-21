import os
import sys

from dotenv import dotenv_values


def build_env():
    for k, v in dotenv_values(".env").items():
        os.environ[k] = v

    t = os.environ["DJANGO_SETTINGS_MODULE"].split(".")
    os.environ["DJANGO_CONFIGURATION"] = t[-1].capitalize()
    os.environ["DJANGO_SETTINGS_MODULE"] = ".".join(t[:-1])
    print(  # noqa
        os.environ["DJANGO_CONFIGURATION"], os.environ["DJANGO_SETTINGS_MODULE"]
    )
    import configurations

    configurations.setup()


def run():
    from configurations.management import execute_from_command_line

    build_env()
    execute_from_command_line(sys.argv)


def run_example():
    from django.core.management import execute_from_command_line

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
    execute_from_command_line(sys.argv)


def wsgi():
    from configurations.wsgi import get_wsgi_application

    build_env()
    return get_wsgi_application()
