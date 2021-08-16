import os

from django.core.management.templates import TemplateCommand
from django.conf import settings



class Command(TemplateCommand):
    help = (
            "Creates a Django app directory structure for the given app name in "
            "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        app_name = options.pop('name')
        target = options.pop('directory')
        template_dir = options.pop('template') or os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)),  '..', '..', 'code_tpl', 'app_tpl'))
        print(template_dir)

        apps_dir = settings.APPS_ROOT
        print(apps_dir)
        os.chdir(apps_dir)
        super().handle('app', app_name, target, template=template_dir, **options)
