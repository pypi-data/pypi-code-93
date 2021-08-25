#!/usr/bin/env python

from identity.models import Project
from identity.keystone import KeystoneNoRequest
from vault.utils import encrypt_password

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        keystone = KeystoneNoRequest()
        projects = keystone.project_list()
        print(len(projects))
        count = 1
        for project in projects:
            db_project = Project.objects.filter(project=project.id)

            if not db_project:
                user_name = 'u_vault_{}'.format(project.name)
                password = KeystoneNoRequest.create_password()
                password = encrypt_password(password)

                db_project = Project(
                    project=project.id,
                    user=user_name,
                    password=password.decode("utf-8")
                )
                db_project.save()
                count = count + 1
                print("{} ({}) - {} - {}".format(
                    project.id,
                    project.name,
                    user_name,
                    password.decode("utf-8"))
                )
        print(count)
