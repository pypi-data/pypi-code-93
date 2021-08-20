import os
import sys
import traceback

from django.core.management.base import BaseCommand

from ..models import Command, Message


class DebugMixin:
    def debug(self,msg):
        module_name = type(self).__module__
        app, name = module_name.split('.')[-4], module_name.split('.')[-1]
        defaults = dict(app=app)
        command, created = Command.objects.get_or_create(defaults,name=name)
        if command.is_enabled:
            Message(name=name,app=app,msg=msg,pid=os.getpid()).save()

class DebugCommand(DebugMixin,BaseCommand):
    pass
