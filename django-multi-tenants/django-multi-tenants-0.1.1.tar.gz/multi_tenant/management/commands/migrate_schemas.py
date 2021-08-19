from django.core.management.base import CommandError
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.migrations.exceptions import MigrationSchemaMissing

from multi_tenant.constants import ALLOWED_BACKENDS
from multi_tenant.management.commands import SyncCommon
from multi_tenant.migration_executors import get_executor
from multi_tenant.utils import (
    get_engine_by_database,
    get_public_schema_name,
    get_tenant_model,
    schema_exists
)


def _check_backend(database):
    db_engine = get_engine_by_database(database)
    if db_engine not in ALLOWED_BACKENDS:
        raise CommandError(
            f'migrate has been disabled, for database {database}.'
            ' Use migrate_schemas instead. Please read the documentation'
            ' if you don\'t know why you shouldn\'t call migrate directly!'
        )


class Command(SyncCommon):
    help = """
    Updates database schema. Manages both apps
    with migrations and those without.
    """
    requires_system_checks = []

    def __init__(self, stdout=None, stderr=None, no_color=False):
        """
        Changes the option_list to use the options
        from the wrapped migrate command.
        """
        super(Command, self).__init__(stdout, stderr, no_color)

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        command = MigrateCommand()
        command.add_arguments(parser)

    def handle(self, *args, **options):
        database = options.get('database', 'default')
        _check_backend(database=database)

        super(Command, self).handle(*args, **options)

        self.PUBLIC_SCHEMA_NAME = get_public_schema_name()

        executor = get_executor(codename=self.executor)(
            self.args, self.options
        )

        if self.sync_public:
            self.schema_name = self.schema_name or self.PUBLIC_SCHEMA_NAME
            executor.run_migrations(tenants=[self.schema_name])

        if not self.sync_tenant:
            return

        TenantModel = get_tenant_model()

        if self.schema_name and self.schema_name != self.PUBLIC_SCHEMA_NAME:
            if not schema_exists(self.schema_name):
                raise MigrationSchemaMissing(
                    f'Schema {self.schema_name} does not exist.'
                )

            tenants_qs = TenantModel.objects.filter(
                schema_name=self.schema_name
            )
        else:
            tenants_qs = TenantModel.objects.exclude(
                schema_name=self.PUBLIC_SCHEMA_NAME
            )

        tenants_qs = tenants_qs.select_related('tenant')
        executor.run_migrations(tenants=tenants_qs)
