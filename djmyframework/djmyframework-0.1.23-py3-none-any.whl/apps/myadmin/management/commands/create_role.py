#coding:utf-8




from django.core.management.base import BaseCommand, CommandError

from myadmin.models.user import Role
from django.forms import ModelForm  

import pprint
from django.db.models.base import ModelBase
    
class Command(BaseCommand):
    help = '创建默认角色'

    def handle(self, *args, **options):
        Role.create_default_role()
