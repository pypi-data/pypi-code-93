from django.contrib import admin

from ..models import Command, Message

from .command import CommandAdmin
from .message import MessageAdmin

admin.site.register(Command, CommandAdmin)
admin.site.register(Message, MessageAdmin)
