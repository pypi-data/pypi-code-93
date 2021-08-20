from setuptools import setup

setup(
    name='django-command-debug',
    version='2021.8.20',
    packages=[
        'django_command_debug',
        'django_command_debug.admin',
        'django_command_debug.management',
        'django_command_debug.migrations',
        'django_command_debug.models'
    ]
)
