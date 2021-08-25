import sys

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Django runserver runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.django_runserver.RunnableThread()
                )
            }

        And you can make it not restart on crash with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.django_runserver.RunnableThread(
                        autorestart_on_crash=False)
                )
            }

    """
    default_autorestart_on_crash = True

    def __init__(self, host='127.0.0.1', port='8000', environment=None, **kwargs):
        """
        Args:
            host: The host to run the Django server on. Defaults to ``"127.0.0.1"``.
            port: The port to run the Django server on. Defaults to ``"8000"``.
            **kwargs: Sent to manage.py runserver as --<key> <value> arguments.
                If the value is True, we only send --<key>.
        """
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.environment = environment
        super(RunnableThread, self).__init__()

    def get_logger_name(self):
        return 'Django development server'

    def get_command_config(self):
        args = ['manage.py', 'runserver', '{}:{}'.format(self.host, self.port)]
        for key, value in self.kwargs.items():
            args.append(f'--{key}')
            if value != True:
                args.append(str(value))
        return {
            'executable': sys.executable,
            'args': args,
            'environment': self.environment
        }
