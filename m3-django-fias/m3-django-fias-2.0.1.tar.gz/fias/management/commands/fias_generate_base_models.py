# coding: utf-8
from django.conf import settings
from django.core.management.commands.inspectdb import Command as InspectDBCommand


class Command(InspectDBCommand):
    help = 'Утилита для генерации базовых моделей на основе XSD'
    usage_str = 'Usage: ./manage.py --dst <path>'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--dst',
            action='store',
            dest='dst',
            help='Результирующий .py файл',
        )

    def handle(self, **options):
        settings.DATABASES['xsd_folder'] = {
            'ENGINE': 'fias',
        }
        options['database'] = 'xsd_folder'

        with open(options['dst'], 'wb') as f:
            for line in self.handle_inspection(options):
                f.write("%s\n" % line)

    def get_field_type(self, connection, table_name, row):
        field_type, field_params, field_notes = super(
            Command, self).get_field_type(connection, table_name, row)
        field_params['verbose_name'] = row.description

        return field_type, field_params, field_notes

    def get_meta(self, table_name, constraints, column_to_field_name):
        result = super(Command, self).get_meta(
            table_name, constraints, column_to_field_name)

        for index, row in enumerate(result):
            if "managed = False" in row:
                result[index] = row.replace(
                    "managed = False",
                    "abstract = True",
                )
                break

        for index, row in enumerate(result):
            if "db_table" in row:
                del result[index]
                break

        return result







